# -*- coding: utf-8 -*-
"""
AGB represents the main client for interacting with the AGB cloud runtime
environment.
"""

import json
import os
from typing import Dict, List, Optional, Union
from threading import Lock

from agb.api.client import Client as mcp_client
from agb.api.models import (
    CreateSessionRequest,
    ReleaseSessionRequest,
    CreateSessionResponse,
)
from agb.config import load_config, Config
from agb.session import Session, BaseSession
from agb.session_params import CreateSessionParams
from agb.model.response import SessionResult, DeleteResult


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
            api_key = os.getenv("AGB_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key is required. Provide it as a parameter or set the "
                    "AGB_API_KEY environment variable"
                )

        # Load configuration
        self.config = load_config(cfg)

        self.api_key = api_key
        self.endpoint = self.config.endpoint
        self.timeout_ms = self.config.timeout_ms

        # Initialize the HTTP API client with the complete config
        self.client = mcp_client(self.config)
        self._sessions = {}
        self._lock = Lock()


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

            response : CreateSessionResponse = self.client.create_mcp_session(request)

            # Check if response is empty
            if response is None:
                return SessionResult(
                    request_id="",
                    success=False,
                    error_message="OpenAPI client returned None response",
                )

            try:
                print("Response body:")
                print(response.to_dict())
            except Exception:
                print(f"Response: {response}")

            # Extract request ID
            request_id = getattr(response, 'request_id', '') or ''

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

            print("session_id =", session_id)
            print("resource_url =", resource_url)

            # Create Session object
            session = Session(self, session_id)
            if resource_url is not None:
                session.resource_url = resource_url

            # Store image_id used for this session
            session.image_id = params.image_id

            with self._lock:
                self._sessions[session_id] = session

            # Return SessionResult with request ID
            return SessionResult(request_id=request_id, success=True, session=session)

        except Exception as e:
            print("Error calling create_mcp_session:", e)
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


    def delete(self, session: Session) -> DeleteResult:
        """
        Delete a session by session object.

        Args:
            session (Session): The session to delete.

        Returns:
            DeleteResult: Result indicating success or failure and request ID.
        """
        try:
            # Create request to release the session
            request = ReleaseSessionRequest(
                authorization=f"Bearer {self.api_key}",
                session_id=session.session_id,
            )

            # Make the API call
            response = self.client.release_mcp_session(request)

            # Check if response is empty
            if response is None:
                return DeleteResult(
                    request_id="",
                    success=False,
                    error_message="OpenAPI client returned None response",
                )

            # Check response type, if it's ReleaseSessionResponse, use new parsing method
            if hasattr(response, 'is_successful'):
                # This is a ReleaseSessionResponse object
                if response.is_successful():
                    # Remove from local cache
                    with self._lock:
                        self._sessions.pop(session.session_id, None)

                    return DeleteResult(request_id=response.request_id or "", success=True)
                else:
                    error_msg = response.get_error_message() or "Failed to delete session"
                    return DeleteResult(
                        request_id=response.request_id or "",
                        success=False,
                        error_message=error_msg,
                    )
            else:
                return DeleteResult(
                    request_id=response.request_id or "",
                    success=False,
                    error_message="Failed to delete session",
                )

        except Exception as e:
            print("Error calling release_mcp_session:", e)
            # In case of error, return failure result with error message
            return DeleteResult(
                success=False,
                error_message=f"Failed to delete session {session.session_id}: {e}",
            )
