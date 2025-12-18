import json
from typing import TYPE_CHECKING, Dict, Optional

from agb.api.models import (
    GetMcpResourceRequest,
    SetLabelRequest,
    GetLabelRequest,
    PauseSessionRequest,
    ResumeSessionRequest,
    DeleteSessionAsyncRequest,
)
from agb.exceptions import SessionError
from agb.model.response import OperationResult, DeleteResult, SessionPauseResult, SessionResumeResult
from agb.modules.browser import Browser
from agb.modules.code import Code
from agb.modules.command import Command
from agb.modules.computer import Computer
from agb.modules.file_system import FileSystem
from agb.context_manager import ContextManager
from agb.logger import get_logger, log_operation_start, log_operation_success, log_warning, log_operation_error


logger = get_logger(__name__)

if TYPE_CHECKING:
    from agb.agb import AGB


class Session:
    """
    Session represents a session in the AGB cloud environment.
    """

    def __init__(self, agb: "AGB", session_id: str):
        self.agb = agb
        self.session_id = session_id
        self.resource_url = ""
        self.image_id = ""
        self.app_instance_id = ""
        self.resource_id = ""

        # Initialize all modules
        self._init_modules()

    def _init_modules(self):
        """Initialize all available modules"""
        self.command = Command(self)
        self.file_system = FileSystem(self)
        self.code = Code(self)
        self.browser = Browser(self)
        self.computer = Computer(self)

        # Initialize context manager
        self.context = ContextManager(self)

    def get_api_key(self) -> str:
        """
        Return the API key for this session.

        Returns:
            str: The API key.
        """
        return self.agb.api_key

    def get_session_id(self) -> str:
        """
        Return the session_id for this session.

        Returns:
            str: The session ID.
        """
        return self.session_id

    def get_client(self):
        """
        Return the HTTP client for this session.

        Returns:
            Client: The HTTP client instance.
        """
        return self.agb.client

    def _validate_labels(self, labels: Dict[str, str]) -> Optional[OperationResult]:
        """
        Validates labels parameter for label operations.

        Args:
            labels (Dict[str, str]): The labels to validate.

        Returns:
            Optional[OperationResult]: None if validation passes, or OperationResult with error if validation fails.
        """
        # Check if labels is None
        if labels is None:
            return OperationResult(
                request_id="",
                success=False,
                error_message="Labels cannot be null, undefined, or invalid type. Please provide a valid labels object.",
            )

        # Check if labels is a list (array equivalent) - check this before dict check
        if isinstance(labels, list):
            return OperationResult(
                request_id="",
                success=False,
                error_message="Labels cannot be an array. Please provide a valid labels object.",
            )

        # Check if labels is not a dict (after checking for list)
        if not isinstance(labels, dict):
            return OperationResult(
                request_id="",
                success=False,
                error_message="Labels cannot be null, undefined, or invalid type. Please provide a valid labels object.",
            )

        # Check if labels object is empty
        if len(labels) == 0:
            return OperationResult(
                request_id="",
                success=False,
                error_message="Labels cannot be empty. Please provide at least one label.",
            )

        for key, value in labels.items():
            # Check key validity
            if not key or (isinstance(key, str) and key.strip() == ""):
                return OperationResult(
                    request_id="",
                    success=False,
                    error_message="Label keys cannot be empty Please provide valid keys.",
                )

            # Check value is not None or empty
            if value is None or (isinstance(value, str) and value.strip() == ""):
                return OperationResult(
                    request_id="",
                    success=False,
                    error_message="Label values cannot be empty Please provide valid values.",
                )

        # Validation passed
        return None

    def set_labels(self, labels: Dict[str, str]) -> OperationResult:
        """
        Sets the labels for this session.

        Args:
            labels (Dict[str, str]): The labels to set for the session.

        Returns:
            OperationResult: Result indicating success or failure with request ID.

        Raises:
            SessionError: If the operation fails.
        """
        try:
            # Validate labels using the extracted validation function
            validation_result = self._validate_labels(labels)
            if validation_result is not None:
                return validation_result

            # Convert labels to JSON string
            labels_json = json.dumps(labels)

            request = SetLabelRequest(
                authorization=f"Bearer {self.get_api_key()}",
                session_id=self.session_id,
                labels=labels_json,
            )

            response = self.get_client().set_label(request)

            # Check if response is successful
            if response.is_successful():
                return OperationResult(
                    request_id=response.request_id or "",
                    success=True
                )
            else:
                # Get error message from response
                error_message = response.get_error_message() or "Failed to set labels"
                return OperationResult(
                    request_id=response.request_id or "",
                    success=False,
                    error_message=error_message,
                )

        except Exception as e:
            logger.error(f"Error calling set_label: {e}")
            raise SessionError(
                f"Failed to set labels for session {self.session_id}: {e}"
            )

    def get_labels(self) -> OperationResult:
        """
        Gets the labels for this session.

        Returns:
            OperationResult: Result containing the labels as data and request ID.

        Raises:
            SessionError: If the operation fails.
        """
        try:
            request = GetLabelRequest(
                authorization=f"Bearer {self.get_api_key()}",
                session_id=self.session_id,
            )

            response = self.get_client().get_label(request)

            # Check if response is successful
            if response.is_successful():
                # Get labels data from response
                labels_data = response.get_labels_data()
                labels = {}

                if labels_data and labels_data.labels:
                    # Parse JSON string to dictionary
                    labels = json.loads(labels_data.labels)

                return OperationResult(
                    request_id=response.request_id or "",
                    success=True,
                    data=labels
                )
            else:
                # Get error message from response
                error_message = response.get_error_message() or "Failed to get labels"
                return OperationResult(
                    request_id=response.request_id or "",
                    success=False,
                    error_message=error_message,
                )

        except Exception as e:
            logger.error(f"Error calling get_label: {e}")
            raise SessionError(
                f"Failed to get labels for session {self.session_id}: {e}"
            )

    def info(self) -> OperationResult:
        """
        Get session information including resource details.

        Returns:
            OperationResult: Result containing the session information as data and
                request ID.
        """
        try:
            # Create request to get MCP resource
            request = GetMcpResourceRequest(
                authorization=f"Bearer {self.get_api_key()}",
                session_id=self.get_session_id(),
            )

            # Make API call
            response = self.agb.client.get_mcp_resource(request)

            # Check if response is empty
            if response is None:
                return OperationResult(
                    request_id="",
                    success=False,
                    error_message="OpenAPI client returned None response",
                )

            # Check response type, if it's GetMcpResourceResponse, use new parsing method
            if hasattr(response, "is_successful"):
                # This is GetMcpResourceResponse object
                request_id = response.request_id or ""

                if response.is_successful():
                    try:
                        # Get resource data from the new response format
                        resource_data = response.get_resource_data()
                        if resource_data:
                            # Extract information from resource data
                            result_data = {
                                "session_id": resource_data.session_id,
                                "resource_url": resource_data.resource_url,
                            }

                            # Add desktop info if available
                            if resource_data.desktop_info:
                                desktop_info = resource_data.desktop_info
                                result_data.update(
                                    {
                                        "app_id": desktop_info.app_id,
                                        "auth_code": desktop_info.auth_code,
                                        "connection_properties": desktop_info.connection_properties,
                                        "resource_id": desktop_info.resource_id,
                                        "resource_type": desktop_info.resource_type,
                                        "ticket": desktop_info.ticket,
                                    }
                                )

                            return OperationResult(
                                request_id=request_id, success=True, data=result_data
                            )
                        else:
                            return OperationResult(
                                request_id=request_id,
                                success=False,
                                error_message="No resource data found in response",
                            )

                    except Exception as e:
                        return OperationResult(
                            request_id=request_id,
                            success=False,
                            error_message=f"Error parsing resource data: {e}",
                        )
                else:
                    error_msg = (
                        response.get_error_message() or "Failed to get MCP resource"
                    )
                    return OperationResult(
                        request_id=request_id, success=False, error_message=error_msg
                    )
            else:
                # Handle case where response doesn't have is_successful method
                return OperationResult(
                    request_id="",
                    success=False,
                    error_message="Unsupported response type",
                )
        except Exception as e:
            return OperationResult(
                request_id="",
                success=False,
                error_message=f"Failed to get session info for session {self.session_id}: {e}",
            )

    def get_link(
        self, protocol_type: Optional[str] = None, port: Optional[int] = None
    ) -> OperationResult:
        """
        Get a link associated with the current session.

        Args:
            protocol_type (Optional[str]): The protocol type to use for the
                link. Defaults to None.
            port (Optional[int]): The port to use for the link.

        Returns:
            OperationResult: Result containing the link as data and request ID.

        Raises:
            SessionError: If the request fails or the response is invalid.
        """
        try:
            from agb.api.models import GetLinkRequest

            request = GetLinkRequest(
                authorization=f"Bearer {self.get_api_key()}",
                session_id=self.get_session_id(),
                protocol_type=protocol_type,
                port=port,
            )

            # Use the new HTTP client implementation
            response = self.agb.client.get_link(request)

            # Check if response is successful
            if response.is_successful():
                # Get URL from response
                url = response.get_url()
                request_id = response.request_id

                if url:
                    return OperationResult(
                        request_id=request_id or "", success=True, data=url
                    )
                else:
                    return OperationResult(
                        request_id=request_id or "",
                        success=False,
                        error_message="No URL found in response",
                    )
            else:
                # Get error message from response
                error_message = response.get_error_message() or "Failed to get link"
                return OperationResult(
                    request_id=response.request_id or "",
                    success=False,
                    error_message=error_message,
                )

        except Exception as e:
            raise SessionError(f"Failed to get link: {e}")

    def delete(self, sync_context: bool = False) -> DeleteResult:
        """
        Delete this session and release all associated resources.

        Args:
            sync_context (bool, optional): Whether to sync context data (trigger file uploads)
                before deleting the session. Defaults to False.

        Returns:
            DeleteResult: Result indicating success or failure with request ID.
                - success (bool): True if deletion succeeded
                - error_message (str): Error details if deletion failed
                - request_id (str): Unique identifier for this API request

        """
        try:
            import time
            import asyncio

            # Perform context synchronization if needed
            if sync_context:
                log_operation_start(
                    "Context synchronization", "Before session deletion"
                )
                sync_start_time = time.time()

                try:
                    # Check if we're in an async context
                    import asyncio
                    try:
                        # Try to get the current event loop
                        loop = asyncio.get_running_loop()
                        # If we're in an async context, we can't use asyncio.run()
                        # Instead, we'll create a task and wait for it
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, self.context.sync())
                            sync_result = future.result()
                    except RuntimeError:
                        # No event loop running, safe to use asyncio.run()
                        sync_result = asyncio.run(self.context.sync())

                    logger.info("🔄 Synced all contexts")
                    sync_duration = time.time() - sync_start_time

                    if sync_result.success:
                        log_operation_success("Context sync")
                        logger.info(
                            f"⏱️  Context sync completed in {sync_duration:.2f} seconds"
                        )
                    else:
                        log_warning("Context sync completed with failures")
                        logger.warning(
                            f"⏱️  Context sync failed after {sync_duration:.2f} seconds"
                        )

                except Exception as e:
                    sync_duration = time.time() - sync_start_time
                    log_warning(f"Failed to trigger context sync: {e}")
                    logger.warning(
                        f"⏱️  Context sync failed after {sync_duration:.2f} seconds"
                    )
                    # Continue with deletion even if sync fails

            # Proceed with session deletion
            request = DeleteSessionAsyncRequest(
                authorization=f"Bearer {self.get_api_key()}",
                session_id=self.session_id,
            )

            client = self.get_client()
            response = client.delete_session_async(request)

            # Extract request ID from response body
            request_id = response.body.request_id or response.request_id or ""

            # Check if the response is success
            response_map = response.to_map()
            body = response_map.get("json", {})

            # Check if the API call was successful
            if not response.is_successful():
                # Format error message according to reference code
                body = response.body
                error_message = f"[{body.code or 'Unknown'}] {body.message or 'Failed to delete session'}"
                logger.error(f"Failed to delete session {self.session_id}: {error_message}")
                logger.debug(f"Full response: {json.dumps(response.to_map(), ensure_ascii=False, indent=2)}")
                return DeleteResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_message,
                )

            # Poll for session deletion status
            logger.info(f"🔄 Waiting for session {self.session_id} to be deleted...")
            poll_timeout = 50.0  # 50 seconds timeout
            poll_interval = 1.0  # Poll every 1 second
            poll_start_time = time.time()

            while True:
                # Check timeout
                elapsed_time = time.time() - poll_start_time
                if elapsed_time >= poll_timeout:
                    error_message = f"Timeout waiting for session deletion after {poll_timeout}s"
                    logger.warning(f"⏱️  {error_message}")
                    return DeleteResult(
                        request_id=request_id,
                        success=False,
                        error_message=error_message,
                    )

                # Get session status
                session_result = self.agb.get_session(self.session_id)

                # Check if session is deleted (NotFound error)
                if not session_result.success:
                    error_code = session_result.code or ""
                    error_message = session_result.error_message or ""
                    http_status_code = session_result.http_status_code or 0

                    # Check for InvalidMcpSession.NotFound, 400 with "not found", or error_message containing "not found"
                    is_not_found = (
                        error_code == "InvalidMcpSession.NotFound" or
                        (http_status_code == 400 and (
                            "not found" in error_message.lower() or
                            "NotFound" in error_message or
                            "not found" in error_code.lower()
                        )) or
                        "not found" in error_message.lower()
                    )

                    if is_not_found:
                        # Session is deleted
                        logger.info(f"✅ Session {self.session_id} successfully deleted (NotFound)")
                        break
                    else:
                        # Other error, continue polling
                        logger.debug(f"⚠️  Get session error (will retry): {error_message}")
                        # Continue to next poll iteration

                # Check session status if we got valid data
                elif session_result.data and session_result.data.status:
                    status = session_result.data.status
                    logger.debug(f"📊 Session status: {status}")

                    if status == "FINISH":
                        logger.info(f"✅ Session {self.session_id} successfully deleted")
                        break

                # Wait before next poll
                time.sleep(poll_interval)

            # Log successful deletion
            logger.info(f"DeleteSession API response - RequestID: {request_id}, Success: True")
            logger.debug(f"Key fields: {{'session_id': '{self.session_id}'}}")

            # Return success result with request ID
            return DeleteResult(request_id=request_id, success=True)

        except Exception as e:
            log_operation_error("delete_session", str(e))
            # In case of error, return failure result with error message
            return DeleteResult(
                success=False,
                error_message=f"Failed to delete session {self.session_id}: {e}",
            )

    def pause(self, timeout: int = 600, poll_interval: float = 2.0) -> SessionPauseResult:
        """
        Synchronously pause this session, putting it into a dormant state.

        This method internally calls the pause_session_async API and then polls the get_session API
        to check the session status until it becomes PAUSED or until timeout.

        Args:
            timeout (int, optional): Timeout in seconds to wait for the session to pause.
                Defaults to 600 seconds.
            poll_interval (float, optional): Interval in seconds between status polls.
                Defaults to 2.0 seconds.

        Returns:
            SessionPauseResult: Result containing the request ID, success status, and final session status.
                - success (bool): True if the session was successfully paused
                - request_id (str): Unique identifier for this API request
                - error_message (str): Error description (if success is False)
        """
        try:
            # Use asyncio.run to call the async pause API and poll for status
            # This allows us to reuse the async implementation in a synchronous context
            import asyncio
            import threading

            # Create a new event loop if there isn't one already
            try:
                loop = asyncio.get_running_loop()
                # If we're already in an event loop, run in a new thread with a new event loop
                # This prevents deadlock when calling synchronous pause() from async context
                result_container = []
                exception_container = []

                def run_in_thread():
                    try:
                        # Create a new event loop for this thread
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        try:
                            result = new_loop.run_until_complete(self.pause_async(timeout, poll_interval))
                            result_container.append(result)
                        finally:
                            new_loop.close()
                    except Exception as e:
                        exception_container.append(e)

                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()

                if exception_container:
                    raise exception_container[0]
                if result_container:
                    return result_container[0]

            except RuntimeError:
                # No event loop running, we can use asyncio.run
                result = asyncio.run(self.pause_async(timeout, poll_interval))
                return result
        except Exception as e:
            logger.error(f"Error pausing session {self.session_id}: {e}")
            return SessionPauseResult(
                request_id="",
                success=False,
                error_message=f"Unexpected error pausing session: {e}",
            )

    async def pause_async(self, timeout: int = 600, poll_interval: float = 2.0) -> SessionPauseResult:
        """
        Asynchronously pause this session, putting it into a dormant state.

        This method directly calls the pause_session_async API and then polls the get_session API
        asynchronously to check the session status until it becomes PAUSED or until timeout.

        Args:
            timeout (int, optional): Timeout in seconds to wait for the session to pause.
                Defaults to 600 seconds.
            poll_interval (float, optional): Interval in seconds between status polls.
                Defaults to 2.0 seconds.

        Returns:
            SessionPauseResult: Result containing the request ID, success status, and final session status.
                - success (bool): True if the session was successfully paused
                - request_id (str): Unique identifier for this API request
                - error_message (str): Error description (if success is False)
        """
        try:
            import asyncio

            request = PauseSessionRequest(
                authorization=f"Bearer {self.get_api_key()}",
                session_id=self.session_id,
            )

            logger.info(f"Pausing session {self.session_id}")
            response = await self.agb.client.pause_session_async(request)

            # Extract request ID
            request_id = response.request_id or ""

            # Check for API-level errors
            if not response.is_successful():
                error_message = response.get_error_message() or "Unknown error"
                logger.error(f"Failed to pause session {self.session_id}: {error_message}")
                return SessionPauseResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_message
                )

            logger.info(f"Session pause initiated successfully for session {self.session_id}, request ID: {request_id}")


            # Poll for session status until PAUSED or timeout
            import time
            start_time = time.time()
            max_attempts = int(timeout / poll_interval)
            attempt = 0

            while attempt < max_attempts:
                # Get session status
                get_result = self.agb.get_session(self.session_id)
                if not get_result.success:
                    error_msg = f"Failed to get session status: {get_result.error_message}"
                    logger.error(error_msg)
                    return SessionPauseResult(
                        request_id=get_result.request_id,
                        success=False,
                        error_message=error_msg,
                    )

                # Check session status
                if get_result.data:
                    status = getattr(get_result.data, 'status', None) or "UNKNOWN"
                    logger.info(f"Session status: {status} (attempt {attempt + 1}/{max_attempts})")

                    # Check if session is paused
                    if status == "PAUSED":
                        elapsed = time.time() - start_time
                        logger.info(f"Session paused successfully in {elapsed:.2f} seconds")
                        return SessionPauseResult(
                            request_id=get_result.request_id,
                            success=True
                        )
                    elif status == "PAUSING":
                        # Normal transitioning state, continue polling
                        pass
                    else:
                        # Any other status is unexpected - pause API succeeded but session is not pausing/paused
                        elapsed = time.time() - start_time
                        error_msg = f"Session pause failed: unexpected state '{status}' after {elapsed:.2f} seconds"
                        logger.error(error_msg)
                        return SessionPauseResult(
                            request_id=get_result.request_id,
                            success=False,
                            error_message=error_msg,
                        )

                # Wait before next query (using asyncio.sleep to avoid blocking)
                # Only wait if we're not at the last attempt
                attempt += 1
                if attempt < max_attempts:
                    await asyncio.sleep(poll_interval)

            # Timeout
            elapsed = time.time() - start_time
            error_msg = f"Session pause timed out after {elapsed:.2f} seconds"
            logger.error(error_msg)
            return SessionPauseResult(
                request_id="",
                success=False,
                error_message=error_msg,
            )

        except Exception as e:
            logger.error(f"Error pausing session {self.session_id}: {e}")
            return SessionPauseResult(
                request_id="",
                success=False,
                error_message=f"Unexpected error pausing session: {e}",
            )

    def resume(self, timeout: int = 600, poll_interval: float = 2.0) -> SessionResumeResult:
        """
        Synchronously resume this session from a paused state.

        This method internally calls the resume_session_async API and then polls the get_session API
        to check the session status until it becomes RUNNING or until timeout.

        Args:
            timeout (int, optional): Timeout in seconds to wait for the session to resume.
                Defaults to 600 seconds.
            poll_interval (float, optional): Interval in seconds between status polls.
                Defaults to 2.0 seconds.

        Returns:
            SessionResumeResult: Result containing the request ID, success status, and final session status.
                - success (bool): True if the session was successfully resumed
                - request_id (str): Unique identifier for this API request
                - error_message (str): Error description (if success is False)
        """
        try:
            # Use asyncio.run to call the async resume API and poll for status
            # This allows us to reuse the async implementation in a synchronous context
            import asyncio
            import threading

            # Create a new event loop if there isn't one already
            try:
                loop = asyncio.get_running_loop()
                # If we're already in an event loop, run in a new thread with a new event loop
                # This prevents deadlock when calling synchronous resume() from async context
                result_container = []
                exception_container = []

                def run_in_thread():
                    try:
                        # Create a new event loop for this thread
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        try:
                            result = new_loop.run_until_complete(self.resume_async(timeout, poll_interval))
                            result_container.append(result)
                        finally:
                            new_loop.close()
                    except Exception as e:
                        exception_container.append(e)

                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()

                if exception_container:
                    raise exception_container[0]
                if result_container:
                    return result_container[0]

            except RuntimeError:
                # No event loop running, we can use asyncio.run
                result = asyncio.run(self.resume_async(timeout, poll_interval))
                return result
        except Exception as e:
            logger.error(f"Error resuming session {self.session_id}: {e}")
            return SessionResumeResult(
                request_id="",
                success=False,
                error_message=f"Unexpected error resuming session: {e}",
            )

    async def resume_async(self, timeout: int = 600, poll_interval: float = 2.0) -> SessionResumeResult:
        """
        Asynchronously resume this session from a paused state.

        This method directly calls the resume_session_async API and then polls the get_session API
        asynchronously to check the session status until it becomes RUNNING or until timeout.

        Args:
            timeout (int, optional): Timeout in seconds to wait for the session to resume.
                Defaults to 600 seconds.
            poll_interval (float, optional): Interval in seconds between status polls.
                Defaults to 2.0 seconds.

        Returns:
            SessionResumeResult: Result containing the request ID, success status, and final session status.
                - success (bool): True if the session was successfully resumed
                - request_id (str): Unique identifier for this API request
                - error_message (str): Error description (if success is False)
        """
        try:
            import asyncio

            request = ResumeSessionRequest(
                authorization=f"Bearer {self.get_api_key()}",
                session_id=self.session_id,
            )

            logger.info(f"Resuming session {self.session_id}")
            response = await self.agb.client.resume_session_async(request)

            # Extract request ID
            request_id = response.request_id or ""

            # Check for API-level errors
            if not response.is_successful():
                error_message = response.get_error_message() or "Unknown error"
                logger.error(f"Failed to resume session {self.session_id}: {error_message}")
                return SessionResumeResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_message
                )

            logger.info(f"Session resume initiated successfully for session {self.session_id},request ID: {request_id}")

            # Poll for session status until RUNNING or timeout
            import time
            start_time = time.time()
            max_attempts = int(timeout / poll_interval)
            attempt = 0

            while attempt < max_attempts:
                # Get session status
                get_result = self.agb.get_session(self.session_id)
                if not get_result.success:
                    error_msg = f"Failed to get session status: {get_result.error_message}"
                    logger.error(error_msg)
                    return SessionResumeResult(
                        request_id=get_result.request_id,
                        success=False,
                        error_message=error_msg,
                    )

                # Check session status
                if get_result.data:
                    status = getattr(get_result.data, 'status', None) or "UNKNOWN"
                    logger.info(f"Session status: {status} (attempt {attempt + 1}/{max_attempts})")

                    # Check if session is running
                    if status == "RUNNING":
                        elapsed = time.time() - start_time
                        logger.info(f"Session resumed successfully in {elapsed:.2f} seconds")
                        return SessionResumeResult(
                            request_id=get_result.request_id,
                            success=True
                        )
                    elif status == "RESUMING":
                        # Normal transitioning state, continue polling
                        pass
                    else:
                        # Any other status is unexpected - resume API succeeded but session is not resuming/running
                        elapsed = time.time() - start_time
                        error_msg = f"Session resume failed: unexpected state '{status}' after {elapsed:.2f} seconds"
                        logger.error(error_msg)
                        return SessionResumeResult(
                            request_id=get_result.request_id,
                            success=False,
                            error_message=error_msg,
                        )

                # Wait before next query (using asyncio.sleep to avoid blocking)
                # Only wait if we're not at the last attempt
                attempt += 1
                if attempt < max_attempts:
                    await asyncio.sleep(poll_interval)

            # Timeout
            elapsed = time.time() - start_time
            error_msg = f"Session resume timed out after {elapsed:.2f} seconds"
            logger.error(error_msg)
            return SessionResumeResult(
                request_id="",
                success=False,
                error_message=error_msg,
            )

        except Exception as e:
            logger.error(f"Error resuming session {self.session_id}: {e}")
            return SessionResumeResult(
                request_id="",
                success=False,
                error_message=f"Unexpected error resuming session: {e}",
            )
