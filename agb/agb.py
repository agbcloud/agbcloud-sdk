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
    GetSessionRequest,
    ListSessionRequest,
)
from agb.config import Config, load_config
from agb.model.response import DeleteResult, SessionResult, GetSessionResult, GetSessionData, SessionListResult
from agb.session import Session
from agb.session_params import CreateSessionParams
from agb.context import ContextService
from agb.logger import get_logger, log_operation_start, log_operation_success, log_warning
from agb.version_utils import get_sdk_version, is_release_version

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
            params (Optional[CreateSessionParams]): Parameters for creating the session.
                Defaults to None.

        Returns:
            SessionResult: Result containing the created session and request ID.
        """
        try:
            if params is None:
                error_msg = "params is required and cannot be None"
                logger.error(error_msg)
                return SessionResult(
                    request_id="",
                    success=False,
                    error_message=error_msg,
                )

            # Validate image_id is required
            if not params.image_id or (isinstance(params.image_id, str) and not params.image_id.strip()):
                error_msg = "image_id is required and cannot be empty or None"
                logger.error(error_msg)
                return SessionResult(
                    request_id="",
                    success=False,
                    error_message=error_msg,
                )

            request = CreateSessionRequest(authorization=f"Bearer {self.api_key}")
            request.image_id = params.image_id

            # Add labels if provided
            if params.labels:
                # Convert labels to JSON string
                request.labels = json.dumps(params.labels)

            # Add SDK stats for telemetry
            sdk_version = get_sdk_version()
            is_release = is_release_version()
            sdk_stats = {
                "source": "sdk",
                "sdk_language": "python",
                "sdk_version": sdk_version,
                "is_release": is_release
            }
            request.sdk_stats = sdk_stats

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

            if response.data:
                session.app_instance_id = response.data.app_instance_id or ""
                session.resource_id = response.data.resource_id or ""

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

    def list(
        self,
        labels: Optional[Dict[str, str]] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> SessionListResult:
        """
        Returns paginated list of session IDs filtered by labels.

        Args:
            labels (Optional[Dict[str, str]]): Labels to filter sessions.
                Defaults to None (empty dict).
            page (Optional[int]): Page number for pagination (starting from 1).
                Defaults to None (returns first page).
            limit (Optional[int]): Maximum number of items per page.
                Defaults to None (uses default of 10).

        Returns:
            SessionListResult: Paginated list of session IDs that match the labels,
                including request_id, success status, and pagination information.
        """
        try:
            # Set default values
            if labels is None:
                labels = {}
            if limit is None:
                limit = 10

            # Validate page number
            if page is not None and page < 1:
                return SessionListResult(
                    request_id="",
                    success=False,
                    error_message=f"Cannot reach page {page}: Page number must be >= 1",
                    session_ids=[],
                    next_token="",
                    max_results=limit,
                    total_count=0,
                )

            # Calculate next_token based on page number
            # Page 1 or None means no next_token (first page)
            # For page > 1, we need to make multiple requests to get to that page
            next_token = ""
            if page is not None and page > 1:
                # We need to fetch pages 1 through page-1 to get the next_token
                current_page = 1
                while current_page < page:
                    # Make API call to get next_token
                    labels_json = json.dumps(labels)
                    request = ListSessionRequest(
                        authorization=f"Bearer {self.api_key}",
                        labels=labels_json,
                        max_results=limit,
                    )
                    if next_token:
                        request.next_token = next_token

                    response = self.client.list_sessions(request)
                    request_id = getattr(response, "request_id", "") or ""

                    if not response.is_successful():
                        error_message = response.get_error_message() or "Unknown error"
                        return SessionListResult(
                            request_id=request_id,
                            success=False,
                            error_message=f"Cannot reach page {page}: {error_message}",
                            session_ids=[],
                            next_token="",
                            max_results=limit,
                            total_count=0,
                        )

                    next_token = response.get_next_token() or ""
                    if not next_token:
                        # No more pages available
                        return SessionListResult(
                            request_id=request_id,
                            success=False,
                            error_message=f"Cannot reach page {page}: No more pages available",
                            session_ids=[],
                            next_token="",
                            max_results=limit,
                            total_count=response.get_count() or 0,
                        )
                    current_page += 1

            # Make the actual request for the desired page
            labels_json = json.dumps(labels)
            request = ListSessionRequest(
                authorization=f"Bearer {self.api_key}",
                labels=labels_json,
                max_results=limit,
            )
            if next_token:
                request.next_token = next_token
                logger.debug(f"NextToken={request.next_token}")

            logger.info(f"Making list_sessions API call - Labels={labels_json}, MaxResults={limit}")

            # Make the API call
            response = self.client.list_sessions(request)

            # Extract request ID
            request_id = getattr(response, "request_id", "") or ""

            # Check for errors in the response
            if not response.is_successful():
                error_message = response.get_error_message() or "Unknown error"
                return SessionListResult(
                    request_id=request_id,
                    success=False,
                    error_message=f"Failed to list sessions: {error_message}",
                    session_ids=[],
                    next_token="",
                    max_results=limit,
                    total_count=0,
                )

            session_ids = []
            next_token = response.get_next_token() or ""
            max_results = response.get_max_results() or limit
            total_count = response.get_count() or 0

            # Extract session data
            session_data_list = response.get_session_data()

            # Process session data
            for session_data in session_data_list:
                if session_data.session_id:
                    session_ids.append(session_data.session_id)

            # Log API response with key details
            logger.info(f"ListSessions API response - RequestID: {request_id}, Success: True")
            logger.info(f"Total count: {total_count}, Returned count: {len(session_ids)}")
            logger.info(f"Has more: {'yes' if next_token else 'no'}")

            # Return SessionListResult with request ID and pagination info
            return SessionListResult(
                request_id=request_id,
                success=True,
                session_ids=session_ids,
                next_token=next_token,
                max_results=max_results,
                total_count=total_count,
            )

        except Exception as e:
            logger.error(f"Error calling list_sessions: {e}")
            return SessionListResult(
                request_id="",
                success=False,
                session_ids=[],
                error_message=f"Failed to list sessions: {e}",
            )

    def delete(self, session: Session, sync_context: bool = False) -> DeleteResult:
        """
        Delete a session by session object.

        Args:
            session (Session): The session to delete.
            sync_context (bool): Whether to sync context before deletion. Defaults to False.

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

    def get_session(self, session_id: str) -> GetSessionResult:
        """
        Get session information by session ID.

        Args:
            session_id (str): The ID of the session to retrieve.

        Returns:
            GetSessionResult: Result containing session information.
        """
        try:
            logger.info(f"Getting session information for session_id: {session_id}")

            request = GetSessionRequest(
                authorization=f"Bearer {self.api_key}",
                session_id=session_id
            )

            response = self.client.get_mcp_session(request)

            # Extract request ID from response
            request_id = getattr(response, "request_id", "") or ""

            try:
                response_body = json.dumps(
                    response.to_dict(), ensure_ascii=False, indent=2
                )
            except Exception:
                response_body = str(response)

            # Extract response information using your current architecture
            http_status_code = getattr(response, 'status_code', 0)
            code = getattr(response, 'code', "")
            success = response.is_successful() if hasattr(response, 'is_successful') else False
            message = response.get_error_message() if hasattr(response, 'get_error_message') else ""

                # Check for API-level errors
            if not success:
                return GetSessionResult(
                    request_id=request_id,
                    http_status_code=http_status_code,
                    code=code,
                    success=False,
                    data=None,
                    error_message=message or "Unknown error",
                )

            # Create GetSessionData from the API response using your architecture
            data = None
            if hasattr(response, 'data') and response.data:
                data = GetSessionData(
                    app_instance_id=response.data.app_instance_id or "",
                    resource_id=response.data.resource_id or "",
                    session_id=response.data.session_id or session_id,
                    success=True,
                    resource_url=response.data.resource_url or "",
                )

            # Log API response with key details
            key_fields = {}
            if data:
                key_fields["session_id"] = data.session_id

            logger.info(f"GetSession API response - RequestID: {request_id}, Success: {success}")
            if key_fields:
                logger.debug(f"Key fields: {key_fields}")
            logger.debug(f"Full response: {response_body}")

            return GetSessionResult(
                request_id=request_id,
                http_status_code=http_status_code,
                code=code,
                success=success,
                data=data,
                error_message="",
            )

        except Exception as e:
            logger.error(f"Error calling GetSession: {e}")
            return GetSessionResult(
                request_id="",
                success=False,
                error_message=f"Failed to get session {session_id}: {e}",
            )

    def get(self, session_id: str) -> SessionResult:
        """
        Get a session by its ID.

        This method retrieves a session by calling the GetSession API
        and returns a SessionResult containing the Session object and request ID.

        Args:
            session_id (str): The ID of the session to retrieve.

        Returns:
            SessionResult: Result containing the Session instance, request ID, and success status.
        """
        # Validate input
        if not session_id or (isinstance(session_id, str) and not session_id.strip()):
            return SessionResult(
                request_id="",
                success=False,
                error_message="session_id is required",
            )

        # Call GetSession API
        get_result = self.get_session(session_id)

        # Check if the API call was successful
        if not get_result.success:
            error_msg = get_result.error_message or "Unknown error"
            return SessionResult(
                request_id=get_result.request_id,
                success=False,
                error_message=f"Failed to get session {session_id}: {error_msg}",
            )

        # Create the Session object
        session = Session(self, session_id)

        # Set session information from GetSession response
        if get_result.data:
            session.resource_url = get_result.data.resource_url or ""
            # Store additional session data - set attributes directly
            session.app_instance_id = get_result.data.app_instance_id or ""
            session.resource_id = get_result.data.resource_id or ""

        logger.info(f"Successfully retrieved session: {session_id}")

        return SessionResult(
            request_id=get_result.request_id or "",
            success=True,
            session=session,
        )