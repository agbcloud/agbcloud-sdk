# -*- coding: utf-8 -*-
"""
AGB represents the main client for interacting with the AGB cloud runtime
environment.
"""

import json
import os
import copy
from typing import Dict, Optional

from agb.api.client import Client as mcp_client
from agb.api.models import (
    CreateSessionRequest,
    CreateSessionResponse,
    CreateMcpSessionRequestPersistenceDataList,
    GetSessionRequest,
    ListSessionRequest,
)
from agb.config import Config, load_config, BROWSER_DATA_PATH
from agb.context_sync import ContextSync, WhiteList, UploadPolicy, BWList, RecyclePolicy, SyncPolicy
from agb.model.response import DeleteResult, SessionResult, GetSessionResult, GetSessionData, SessionListResult
from agb.session import Session
from agb.session_params import CreateSessionParams
from agb.context import ContextService
from agb.logger import get_logger, log_operation_start, log_operation_success, log_operation_error, log_warning
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

        # Initialize context service
        self.context = ContextService(self)

    def _normalize_context_syncs(self, params) -> list:
        # define browser context whitelist
        BROWSER_WHITELIST_PATHS = [
            WhiteList(path="/Local State", exclude_paths=[]),
            WhiteList(path="/Default/Cookies", exclude_paths=[]),
            WhiteList(path="/Default/Cookies-journal", exclude_paths=[]),
        ]

        # create browser context sync policy
        def create_browser_sync_policy(auto_upload: bool) -> SyncPolicy:
            return SyncPolicy(
                upload_policy=UploadPolicy(auto_upload=auto_upload),
                bw_list=BWList(white_lists=BROWSER_WHITELIST_PATHS),
                recycle_policy=RecyclePolicy(),
            )

        # combine context_syncs with browser_context
        syncs = list(params.context_syncs or [])

        if params.browser_context:
            syncs.append(ContextSync(
                context_id=params.browser_context.context_id,
                path=BROWSER_DATA_PATH,
                policy=create_browser_sync_policy(params.browser_context.auto_upload),
            ))

        return syncs

    def _create_persistence_data_list(self, context_syncs:list) -> list:
        persistence_data_list = []
        for context_sync in context_syncs:
            if context_sync.policy:
                policy_json = json.dumps(context_sync.policy.to_dict(), ensure_ascii=False)
                persistence_data_list.append(CreateMcpSessionRequestPersistenceDataList(
                    context_id=context_sync.context_id,
                    path=context_sync.path,
                    policy=policy_json,
                ))
        return persistence_data_list

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
                log_operation_error("AGB.create", error_msg)
                return SessionResult(
                    request_id="",
                    success=False,
                    error_message=error_msg,
                )

            # To avoid mutating the caller-provided params when create() performs any
            # normalization or augmentation (e.g., appending auto-generated context syncs),
            # we operate on a deep-copied params object.
            try:
                params = copy.deepcopy(params)
            except Exception as e:
                error_msg = f"Failed to copy params: {e}"
                log_operation_error("AGB.create", error_msg, exc_info=True)
                return SessionResult(
                    request_id="",
                    success=False,
                    error_message=error_msg,
                )

            # Validate image_id is required
            if not params.image_id or (isinstance(params.image_id, str) and not params.image_id.strip()):
                error_msg = "image_id is required and cannot be empty or None"
                log_operation_error("AGB.create", error_msg)
                return SessionResult(
                    request_id="",
                    success=False,
                    error_message=error_msg,
                )

            op_details = f"ImageId={params.image_id}"
            if params.labels:
                op_details += f", LabelsCount={len(params.labels)}"
            if params.context_syncs:
                op_details += f", ContextSyncsCount={len(params.context_syncs)}"
            if params.browser_context:
                op_details += f", BrowserContext={params.browser_context.context_id}"
            log_operation_start("AGB.create", op_details)

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

            # Controle browser_context and context_syncs together
            persistence_data_list = self._create_persistence_data_list(self._normalize_context_syncs(params))
            if persistence_data_list:
                request.persistence_data_list = persistence_data_list
                needs_context_sync = True

            response: CreateSessionResponse = self.client.create_mcp_session(request)

            try:
                logger.info("Response body:")
                logger.info(response.to_dict())
            except Exception:
                logger.info(f"Response: {response}")

            # Extract request ID
            request_id_attr = getattr(response, "request_id", "")
            request_id = request_id_attr or ""

            # Check if the session creation was successful
            if response.data and response.data.success is False:
                error_msg = response.data.err_msg
                if error_msg is None:
                    error_msg = "Unknown error"
                log_operation_error("AGB.create", error_msg)
                return SessionResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_msg,
                )

            session_id = response.get_session_id()
            if not session_id:
                error_msg = response.get_error_message() or "Session ID not found in response"
                log_operation_error("AGB.create", error_msg)
                return SessionResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_msg,
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

            # If we have persistence data, wait for context synchronization
            if needs_context_sync:
                self._wait_for_context_synchronization(session)

            # Return SessionResult with request ID
            result_msg = f"SessionId={session_id}, RequestId={request_id}"
            if resource_url:
                result_msg += f", ResourceUrl={resource_url}"
            log_operation_success("AGB.create", result_msg)
            return SessionResult(request_id=request_id, success=True, session=session)

        except Exception as e:
            log_operation_error("AGB.create", str(e), exc_info=True)
            return SessionResult(
                request_id="",
                success=False,
                error_message=f"Failed to create session: {e}",
            )

    def _wait_for_context_synchronization(
        self,
        session: "Session",
        *,
        max_retries: int = 150,
        retry_interval_s: int = 2,
    ) -> None:
        """
        Wait for context synchronization to complete for a newly created session.

        This polls `session.context.info()` until all sync items are in terminal states
        ("Success" or "Failed"), or until the retry limit is reached.
        """
        log_operation_start("Context synchronization", "Waiting for completion")

        import time

        for retry in range(max_retries):
            info_result = session.context.info()

            # Check if all context items have status "Success" or "Failed"
            all_completed = True
            has_failure = False

            for item in info_result.context_status_data:
                logger.info(
                    f"📁 Context {item.context_id} status: {item.status}, path: {item.path}"
                )

                if item.status not in {"Success", "Failed"}:
                    all_completed = False
                    break

                if item.status == "Failed":
                    has_failure = True
                    logger.error(
                        f"❌ Context synchronization failed for {item.context_id}: {item.error_message}"
                    )

            if all_completed or not info_result.context_status_data:
                if has_failure:
                    log_warning("Context synchronization completed with failures")
                else:
                    log_operation_success("Context synchronization")
                return

            logger.info(
                f"⏳ Waiting for context synchronization, attempt {retry + 1}/{max_retries}"
            )
            time.sleep(retry_interval_s)

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

            op_details = f"LabelsCount={len(labels)}, Page={page or 1}, Limit={limit}"
            log_operation_start("AGB.list", op_details)

            # Validate page number
            if page is not None and page < 1:
                error_msg = f"Cannot reach page {page}: Page number must be >= 1"
                log_operation_error("AGB.list", error_msg)
                return SessionListResult(
                    request_id="",
                    success=False,
                    error_message=error_msg,
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
                        error_msg = f"Cannot reach page {page}: {error_message}"
                        log_operation_error("AGB.list", error_msg)
                        return SessionListResult(
                            request_id=request_id,
                            success=False,
                            error_message=error_msg,
                            session_ids=[],
                            next_token="",
                            max_results=limit,
                            total_count=0,
                        )

                    next_token = response.get_next_token() or ""
                    if not next_token:
                        # No more pages available
                        error_msg = f"Cannot reach page {page}: No more pages available"
                        log_operation_error("AGB.list", error_msg)
                        return SessionListResult(
                            request_id=request_id,
                            success=False,
                            error_message=error_msg,
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
                error_msg = f"Failed to list sessions: {error_message}"
                log_operation_error("AGB.list", error_msg)
                return SessionListResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_msg,
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
            result_msg = f"RequestId={request_id}, TotalCount={total_count}, ReturnedCount={len(session_ids)}, HasMore={'yes' if next_token else 'no'}"
            log_operation_success("AGB.list", result_msg)

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
            log_operation_error("AGB.list", str(e), exc_info=True)
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
        log_operation_start("AGB.delete", f"SessionId={session.session_id}, SyncContext={sync_context}")
        try:
            # Delete the session and get the result
            delete_result = session.delete(sync_context=sync_context)

            if delete_result.success:
                result_msg = f"SessionId={session.session_id}, RequestId={delete_result.request_id}"
                log_operation_success("AGB.delete", result_msg)
            else:
                error_msg = delete_result.error_message or "Unknown error"
                log_operation_error("AGB.delete", error_msg)

            return delete_result

        except Exception as e:
            log_operation_error("AGB.delete", str(e), exc_info=True)
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
        log_operation_start("AGB.get_session", f"SessionId={session_id}")
        try:
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
                error_msg = message or "Unknown error"
                log_warning(f"AGB.get_session: {error_msg}")
                return GetSessionResult(
                    request_id=request_id,
                    http_status_code=http_status_code,
                    code=code,
                    success=False,
                    data=None,
                    error_message=error_msg,
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
                    status=response.data.status or "",
                )

            # Log API response with key details
            result_msg = f"SessionId={session_id}, RequestId={request_id}"
            if data:
                result_msg += f", ResourceUrl={data.resource_url}, Status={data.status}"
            log_operation_success("AGB.get_session", result_msg)

            return GetSessionResult(
                request_id=request_id,
                http_status_code=http_status_code,
                code=code,
                success=success,
                data=data,
                error_message="",
            )

        except Exception as e:
            log_operation_error("AGB.get_session", str(e), exc_info=True)
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
        log_operation_start("AGB.get", f"SessionId={session_id}")
        # Validate input
        if not session_id or (isinstance(session_id, str) and not session_id.strip()):
            error_msg = "session_id is required"
            log_operation_error("AGB.get", error_msg)
            return SessionResult(
                request_id="",
                success=False,
                error_message=error_msg,
            )

        # Call GetSession API
        get_result = self.get_session(session_id)

        # Check if the API call was successful
        if not get_result.success:
            error_msg = get_result.error_message or "Unknown error"
            log_operation_error("AGB.get", f"Failed to get session: {error_msg}")
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

        result_msg = f"SessionId={session_id}, RequestId={get_result.request_id}"
        log_operation_success("AGB.get", result_msg)

        return SessionResult(
            request_id=get_result.request_id or "",
            success=True,
            session=session,
        )