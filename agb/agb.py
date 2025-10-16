# -*- coding: utf-8 -*-
"""
AGB represents the main client for interacting with the AGB cloud runtime
environment.
"""

import json
import os
from threading import Lock
from typing import Dict, List, Optional, Union

from agb.api.client import Client as mcp_client
from agb.api.models import (
    CreateSessionRequest,
    CreateSessionResponse,
    CreateMcpSessionRequestPersistenceDataList,
)
from agb.config import Config, load_config
from agb.model.response import DeleteResult, SessionResult
from agb.session import BaseSession, Session
from agb.session_params import CreateSessionParams
from agb.context import ContextService
from agb.logger import get_logger, log_operation_start, log_operation_success, log_warning

logger = get_logger(__name__)


class AGB:
    """
    AGB represents the main client for interacting with the AGB cloud runtime
    environment.
    """

    def __init__(self, api_key: str = "", cfg: Optional[Config] = None):
        """
        Initialize the AGB client.

        Args:
            api_key (str): API key for authentication. If not provided, it will be
                loaded from the AGB_API_KEY environment variable.
            cfg (Optional[Config]): Configuration object. If not provided, default
                configuration will be used.
        """
        if not api_key:
            api_key_env = os.getenv("AGB_API_KEY")
            if not api_key_env:
                raise ValueError(
                    "API key is required. Provide it as a parameter or set the "
                    "AGB_API_KEY environment variable"
                )
            api_key = api_key_env

        # Load configuration
        self.config = load_config(cfg)

        self.api_key = api_key
        self.endpoint = self.config.endpoint
        self.timeout_ms = self.config.timeout_ms

        # Initialize the HTTP API client with the complete config
        self.client = mcp_client(self.config)
        self._sessions: Dict[str, Session] = {}
        self._lock = Lock()

        # Initialize context service
        self.context = ContextService(self)

    def create(self, params: Optional[CreateSessionParams] = None) -> SessionResult:
        """
        Create a new session in the AGB cloud environment.

        Args:
            params (Optional[CreateSessionParams], optional): Parameters for
              creating the session.Defaults to None.

        Returns:
            SessionResult: Result containing the created session and request ID.
        """
        try:
            if params is None:
                params = CreateSessionParams()

            request = CreateSessionRequest(authorization=f"Bearer {self.api_key}")

            if params.image_id:
                request.image_id = params.image_id

            # Flag to indicate if we need to wait for context synchronization
            needs_context_sync = False

            if params.context_syncs:
                persistence_data_list = []
                for context_sync in params.context_syncs:
                    if context_sync.policy:
                        policy_json = json.dumps(context_sync.policy.to_dict(), ensure_ascii=False)
                        persistence_data_list.append(CreateMcpSessionRequestPersistenceDataList(
                            context_id=context_sync.context_id,
                            path=context_sync.path,
                            policy=policy_json,
                        ))

                request.persistence_data_list = persistence_data_list
                needs_context_sync = len(persistence_data_list) > 0

            response: CreateSessionResponse = self.client.create_mcp_session(request)

            try:
                logger.debug("Response body:")
                logger.debug(response.to_dict())
            except Exception:
                logger.debug(f"Response: {response}")

            # Extract request ID
            request_id_attr = getattr(response, "request_id", "")
            request_id = request_id_attr or ""

            # Check if the session creation was successful
            if response.data and response.data.success is False:
                error_msg = response.data.err_msg
                if error_msg is None:
                    error_msg = "Unknown error"
                return SessionResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_msg,
                )

            session_id = response.get_session_id()
            if not session_id:
                return SessionResult(
                    request_id=request_id,
                    success=False,
                    error_message=response.get_error_message(),
                )

            # ResourceUrl is optional in CreateMcpSession response
            resource_url = response.get_resource_url()

            logger.info(f"session_id = {session_id}")
            logger.info(f"resource_url = {resource_url}")

            # Create Session object
            session = Session(self, session_id)
            if resource_url is not None:
                session.resource_url = resource_url

            # Store image_id used for this session
            session.image_id = params.image_id or ""

            with self._lock:
                self._sessions[session_id] = session

            # If we have persistence data, wait for context synchronization
            if needs_context_sync:
                log_operation_start("Context synchronization", "Waiting for completion")

                # Wait for context synchronization to complete
                max_retries = 150  # Maximum number of retries
                retry_interval = 2  # Seconds to wait between retries

                import time
                for retry in range(max_retries):
                    # Get context status data
                    info_result = session.context.info()

                    # Check if all context items have status "Success" or "Failed"
                    all_completed = True
                    has_failure = False

                    for item in info_result.context_status_data:
                        logger.info(f"📁 Context {item.context_id} status: {item.status}, path: {item.path}")

                        if item.status != "Success" and item.status != "Failed":
                            all_completed = False
                            break

                        if item.status == "Failed":
                            has_failure = True
                            logger.error(f"❌ Context synchronization failed for {item.context_id}: {item.error_message}")

                    if all_completed or not info_result.context_status_data:
                        if has_failure:
                            log_warning("Context synchronization completed with failures")
                        else:
                            log_operation_success("Context synchronization")
                        break

                    logger.info(f"⏳ Waiting for context synchronization, attempt {retry+1}/{max_retries}")
                    time.sleep(retry_interval)

            # Return SessionResult with request ID
            return SessionResult(request_id=request_id, success=True, session=session)

        except Exception as e:
            logger.error(f"Error calling create_mcp_session: {e}")
            return SessionResult(
                request_id="",
                success=False,
                error_message=f"Failed to create session: {e}",
            )

    def list(self) -> List[BaseSession]:
        """
        List all available sessions.

        Returns:
            List[BaseSession]: A list of all available sessions.
        """
        with self._lock:
            return list(self._sessions.values())

    def delete(self, session: BaseSession, sync_context: bool = False) -> DeleteResult:
        """
        Delete a session by session object.

        Args:
            session (BaseSession): The session to delete.
            sync_context (bool, optional): Whether to sync context before deletion. Defaults to False.

        Returns:
            DeleteResult: Result indicating success or failure and request ID.
        """
        try:
            # Delete the session and get the result
            delete_result = session.delete(sync_context=sync_context)

            with self._lock:
                self._sessions.pop(session.session_id, None)

            return delete_result

        except Exception as e:
            logger.error(f"Error calling delete_mcp_session: {e}")
            return DeleteResult(
                request_id="",
                success=False,
                error_message=f"Failed to delete session: {e}",
            )
