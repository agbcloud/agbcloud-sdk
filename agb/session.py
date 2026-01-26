import json
from typing import TYPE_CHECKING, Any, Dict, Optional

from agb.api.models import (
    GetMcpResourceRequest,
    SetLabelRequest,
    GetLabelRequest,
    DeleteSessionAsyncRequest,
    GetSessionDetailRequest,
    CallMcpToolRequest,
    ListMcpToolsRequest,
)
from agb.exceptions import SessionError, AGBError
from agb.model.response import (
    OperationResult,
    DeleteResult,
    SessionStatusResult,
    McpTool,
    McpToolResult,
    McpToolsResult,
    SessionMetrics,
    SessionMetricsResult,
)
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
        self.file = FileSystem(self)
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
                error_msg = validation_result.error_message or "Validation failed"
                log_operation_error("Session.set_labels", error_msg)
                return validation_result

            log_operation_start("Session.set_labels", f"SessionId={self.session_id}, LabelsCount={len(labels)}")
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
                result_msg = f"SessionId={self.session_id}, RequestId={response.request_id}"
                log_operation_success("Session.set_labels", result_msg)
                return OperationResult(
                    request_id=response.request_id or "",
                    success=True
                )
            else:
                # Get error message from response
                error_message = response.get_error_message() or "Failed to set labels"
                log_operation_error("Session.set_labels", error_message)
                return OperationResult(
                    request_id=response.request_id or "",
                    success=False,
                    error_message=error_message,
                )

        except Exception as e:
            log_operation_error("Session.set_labels", str(e), exc_info=True)
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
        log_operation_start("Session.get_labels", f"SessionId={self.session_id}")
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

                result_msg = f"SessionId={self.session_id}, LabelsCount={len(labels)}, RequestId={response.request_id}"
                log_operation_success("Session.get_labels", result_msg)
                return OperationResult(
                    request_id=response.request_id or "",
                    success=True,
                    data=labels
                )
            else:
                # Get error message from response
                error_message = response.get_error_message() or "Failed to get labels"
                log_operation_error("Session.get_labels", error_message)
                return OperationResult(
                    request_id=response.request_id or "",
                    success=False,
                    error_message=error_message,
                )

        except Exception as e:
            log_operation_error("Session.get_labels", str(e), exc_info=True)
            raise SessionError(
                f"Failed to get labels for session {self.session_id}: {e}"
            )

    def info(self) -> OperationResult:
        """
        Get session information including resource details.

        Returns:
            OperationResult: Result containing the session information as data and
                request ID.
                - success (bool): True if the operation succeeded
                - data (dict): Session information dictionary containing:
                    - session_id (str): The session ID
                    - resource_url (str): Resource URL for the session
                    - app_id (str, optional): Application ID (if desktop session)
                    - auth_code (str, optional): Authentication code (if desktop session)
                    - connection_properties (dict, optional): Connection properties
                    - resource_id (str, optional): Resource ID
                    - resource_type (str, optional): Resource type
                    - ticket (str, optional): Ticket for connection
                - error_message (str): Error details if the operation failed
                - request_id (str): Unique identifier for this API request
        """
        log_operation_start("Session.info", f"SessionId={self.get_session_id()}")
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
                error_msg = "OpenAPI client returned None response"
                log_operation_error("Session.info", error_msg)
                return OperationResult(
                    request_id="",
                    success=False,
                    error_message=error_msg,
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

                            result_msg = f"SessionId={self.get_session_id()}, RequestId={request_id}, ResourceUrl={result_data.get('resource_url', 'None')}"
                            log_operation_success("Session.info", result_msg)
                            return OperationResult(
                                request_id=request_id, success=True, data=result_data
                            )
                        else:
                            error_msg = "No resource data found in response"
                            log_operation_error("Session.info", error_msg)
                            return OperationResult(
                                request_id=request_id,
                                success=False,
                                error_message=error_msg,
                            )

                    except Exception as e:
                        log_operation_error("Session.info", f"Error parsing resource data: {str(e)}", exc_info=True)
                        return OperationResult(
                            request_id=request_id,
                            success=False,
                            error_message=f"Error parsing resource data: {e}",
                        )
                else:
                    error_msg = (
                        response.get_error_message() or "Failed to get MCP resource"
                    )
                    log_operation_error("Session.info", error_msg)
                    return OperationResult(
                        request_id=request_id, success=False, error_message=error_msg
                    )
            else:
                # Handle case where response doesn't have is_successful method
                error_msg = "Unsupported response type"
                log_operation_error("Session.info", error_msg)
                return OperationResult(
                    request_id="",
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("Session.info", str(e), exc_info=True)
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
            protocol_type (Optional[str], optional): The protocol type to use for the
                link. Defaults to None.
            port (Optional[int], optional): The port to use for the link.
                Defaults to None.

        Returns:
            OperationResult: Result containing the link URL as data and request ID.
                - success (bool): True if the operation succeeded
                - data (str): The link URL (when success is True)
                - error_message (str): Error details if the operation failed
                - request_id (str): Unique identifier for this API request

        Raises:
            SessionError: If the request fails or the response is invalid.
        """
        op_details = f"SessionId={self.get_session_id()}"
        if protocol_type:
            op_details += f", ProtocolType={protocol_type}"
        if port:
            op_details += f", Port={port}"
        log_operation_start("Session.get_link", op_details)
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
                    result_msg = f"SessionId={self.get_session_id()}, URL={url}, RequestId={request_id}"
                    log_operation_success("Session.get_link", result_msg)
                    return OperationResult(
                        request_id=request_id or "", success=True, data=url
                    )
                else:
                    error_msg = "No URL found in response"
                    log_operation_error("Session.get_link", error_msg)
                    return OperationResult(
                        request_id=request_id or "",
                        success=False,
                        error_message=error_msg,
                    )
            else:
                # Get error message from response
                error_message = response.get_error_message() or "Failed to get link"
                log_operation_error("Session.get_link", error_message)
                return OperationResult(
                    request_id=response.request_id or "",
                    success=False,
                    error_message=error_message,
                )

        except Exception as e:
            log_operation_error("Session.get_link", str(e), exc_info=True)
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
        log_operation_start("Session.delete", f"SessionId={self.session_id}, SyncContext={sync_context}")
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
                log_operation_error("Session.delete", error_message)
                logger.debug(f"Full response: {json.dumps(response.to_map(), ensure_ascii=False, indent=2)}")
                return DeleteResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_message,
                )

            # Poll for session deletion status
            logger.info(f"🔄 Waiting for session {self.session_id} to be deleted...")
            poll_timeout = 300.0  # 300 seconds timeout
            poll_interval = 1.0  # Poll every 1 second
            poll_start_time = time.time()

            while True:
                # Check timeout
                elapsed_time = time.time() - poll_start_time
                if elapsed_time >= poll_timeout:
                    error_message = f"Timeout waiting for session deletion after {poll_timeout}s"
                    log_operation_error("Session.delete", error_message)
                    return DeleteResult(
                        request_id=request_id,
                        success=False,
                        error_message=error_message,
                    )

                # Get session status (status only)
                status_result = self.get_status()

                # Check if session is deleted (NotFound error)
                if not status_result.success:
                    error_code = status_result.code or ""
                    error_message = status_result.error_message or ""
                    http_status_code = status_result.http_status_code or 0

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
                elif status_result.status:
                    status = status_result.status
                    logger.debug(f"📊 Session status: {status}")

                    if status == "FINISH":
                        logger.info(f"✅ Session {self.session_id} successfully deleted")
                        break

                # Wait before next poll
                time.sleep(poll_interval)

            # Log successful deletion
            result_msg = f"SessionId={self.session_id}, RequestId={request_id}"
            log_operation_success("Session.delete", result_msg)

            # Return success result with request ID
            return DeleteResult(request_id=request_id, success=True)

        except Exception as e:
            log_operation_error("Session.delete", str(e), exc_info=True)
            # In case of error, return failure result with error message
            return DeleteResult(
                success=False,
                error_message=f"Failed to delete session {self.session_id}: {e}",
            )

    def get_status(self) -> "SessionStatusResult":
        """
        Get basic session status.

        Returns:
            SessionStatusResult: Result containing session status information.
                - success (bool): True if the operation succeeded
                - status (str): Current session status
                - http_status_code (int): HTTP status code from the API response
                - code (str): Response code
                - error_message (str): Error details if the operation failed
                - request_id (str): Unique identifier for this API request
        """
        log_operation_start("Session.get_status", f"SessionId={self.session_id}")
        try:
            request = GetSessionDetailRequest(
                authorization=f"Bearer {self.get_api_key()}",
                session_id=self.session_id,
            )
            response = self.get_client().get_session_detail(request)

            request_id = getattr(response, "request_id", "") or ""
            http_status_code = getattr(response, "http_status_code", 0) or 0
            code = getattr(response, "code", "") or ""

            if not response.is_successful():
                error_msg = response.get_error_message() or "Unknown error"
                log_warning(f"Session.get_status: {error_msg}")
                return SessionStatusResult(
                    request_id=request_id,
                    http_status_code=http_status_code,
                    code=code,
                    success=False,
                    status="",
                    error_message=error_msg,
                )

            status = response.get_status()
            log_operation_success(
                "Session.get_status",
                f"SessionId={self.session_id}, RequestId={request_id}, Status={status}",
            )
            return SessionStatusResult(
                request_id=request_id,
                http_status_code=http_status_code,
                code=code,
                success=True,
                status=status,
                error_message="",
            )
        except Exception as e:
            log_operation_error("Session.get_status", str(e), exc_info=True)
            return SessionStatusResult(
                request_id="",
                success=False,
                error_message=f"Failed to get session status {self.session_id}: {e}",
            )

    def call_mcp_tool(
        self,
        tool_name: str,
        args: Dict[str, Any],
        read_timeout: Optional[int] = None,
        connect_timeout: Optional[int] = None,
    ) -> McpToolResult:
        """
        Call the specified MCP tool.

        Args:
            tool_name (str): Tool name (e.g., "tap", "get_ui_elements").
            args (Dict[str, Any]): Tool arguments dictionary.
            read_timeout (Optional[int], optional): Read timeout in milliseconds.
                Defaults to None.
            connect_timeout (Optional[int], optional): Connection timeout in milliseconds.
                Defaults to None.

        Returns:
            McpToolResult: Tool call result, data field contains tool return data in JSON string format.
                - success (bool): True if tool call succeeded
                - data (str): Tool return data in JSON string format (when success is True)
                - error_message (str): Error details if tool call failed
                - request_id (str): Unique identifier for this API request

        Raises:
            SessionError: If the tool call fails.

        Example:
            ```python
            # Call mobile device tap tool
            result = session.call_mcp_tool("tap", {"x": 100, "y": 200})

            # Call get UI elements tool
            result = session.call_mcp_tool("get_ui_elements", {})
            ```
        """
        log_operation_start(
            "Session.call_mcp_tool",
            f"SessionId={self.session_id}, ToolName={tool_name}",
        )
        try:
            # Serialize arguments
            args_json = json.dumps(args, ensure_ascii=False)

            # Build request
            request = CallMcpToolRequest(
                authorization=f"Bearer {self.get_api_key()}",
                session_id=self.get_session_id(),
                name=tool_name,
                args=args_json,
            )

            # Call Client API
            response = self.get_client().call_mcp_tool(
                request,
                read_timeout=read_timeout,
                connect_timeout=connect_timeout,
            )

            # Check if response is None
            if response is None:
                log_operation_error(
                    "Session.call_mcp_tool",
                    "OpenAPI client returned None response",
                )
                return McpToolResult(
                    request_id="",
                    success=False,
                    error_message="OpenAPI client returned None response",
                )

            request_id = response.request_id or ""

            # Parse response using CallMcpToolResponse methods
            if hasattr(response, "is_successful"):
                if response.is_successful():
                    result = response.get_tool_result()
                    log_operation_success(
                        "Session.call_mcp_tool",
                        f"SessionId={self.session_id}, RequestId={request_id}, ToolName={tool_name}",
                    )
                    return McpToolResult(
                        request_id=request_id,
                        success=True,
                        data=result,
                        error_message="",
                    )
                else:
                    error_msg = response.get_error_message() or "Tool execution failed"
                    log_warning(
                        f"Session.call_mcp_tool failed: {error_msg}, RequestId={request_id}"
                    )
                    return McpToolResult(
                        request_id=request_id,
                        success=False,
                        error_message=error_msg,
                    )
            else:
                log_operation_error(
                    "Session.call_mcp_tool",
                    "Unsupported response type",
                )
                return McpToolResult(
                    request_id=request_id,
                    success=False,
                    error_message="Unsupported response type",
                )

        except AGBError as e:
            log_operation_error("Session.call_mcp_tool", str(e), exc_info=True)
            return McpToolResult(
                request_id="",
                success=False,
                error_message=str(e),
            )
        except Exception as e:
            log_operation_error("Session.call_mcp_tool", str(e), exc_info=True)
            return McpToolResult(
                request_id="",
                success=False,
                error_message=f"Failed to call MCP tool {tool_name}: {e}",
            )

    def list_mcp_tools(self, image_id: Optional[str] = None) -> McpToolsResult:
        """
        List MCP tools available for the current session.

        Args:
            image_id (Optional[str], optional): Image ID. Defaults to current session's
                image_id or "agb-code-space-1" if not specified.

        Returns:
            McpToolsResult: Result containing the list of available MCP tools.
                - success (bool): True if the operation succeeded
                - tools (List[McpTool]): List of MCP tool objects, each containing name,
                    description, input_schema, server, and tool fields
                - error_message (str): Error details if the operation failed
                - request_id (str): Unique identifier for this API request

        Example:
            ```python
            # List available tools
            result = session.list_mcp_tools()
            if result.success:
                for tool in result.tools:
                    print(f"{tool.name}: {tool.description}")
            ```
        """
        log_operation_start(
            "Session.list_mcp_tools",
            f"SessionId={self.session_id}, ImageId={image_id or 'default'}",
        )
        try:
            # Determine image_id to use, ensure it's a string type
            if image_id is None:
                image_id = getattr(self, "image_id", "") or "agb-code-space-1"

            # Ensure image_id is a string type (handle possible None case)
            image_id_str: str = str(image_id) if image_id else "agb-code-space-1"

            # Build request
            request = ListMcpToolsRequest(
                authorization=f"Bearer {self.get_api_key()}",
                image_id=image_id_str,
            )

            # Call API
            response = self.get_client().list_mcp_tools(request)
            request_id = response.request_id or ""

            # Check if response is successful
            if not response.is_successful():
                error_msg = response.get_error_message() or "Failed to list MCP tools"
                log_warning(
                    f"Session.list_mcp_tools failed: {error_msg}, RequestId={request_id}"
                )
                return McpToolsResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_msg,
                )

            # Parse tools list
            tools = []
            tools_data_str = response.get_tools_list()

            if tools_data_str:
                try:
                    tools_data = json.loads(tools_data_str)
                    if isinstance(tools_data, list):
                        for tool_data in tools_data:
                            tool = McpTool(
                                name=tool_data.get("name", ""),
                                description=tool_data.get("description", ""),
                                input_schema=tool_data.get("inputSchema", {}),
                                server=tool_data.get("server", ""),
                                tool=tool_data.get("tool", ""),
                            )
                            tools.append(tool)
                except json.JSONDecodeError as e:
                    log_operation_error(
                        "Session.list_mcp_tools",
                        f"Failed to parse tools list: {e}",
                    )
                    return McpToolsResult(
                        request_id=request_id,
                        success=False,
                        error_message=f"Failed to parse tools list: {e}",
                    )

            log_operation_success(
                "Session.list_mcp_tools",
                f"SessionId={self.session_id}, RequestId={request_id}, ToolsCount={len(tools)}",
            )
            return McpToolsResult(
                request_id=request_id,
                success=True,
                tools=tools,
            )

        except Exception as e:
            log_operation_error("Session.list_mcp_tools", str(e), exc_info=True)
            return McpToolsResult(
                request_id="",
                success=False,
                error_message=f"Failed to list MCP tools: {e}",
            )

    def get_metrics(
        self,
        read_timeout: Optional[int] = None,
        connect_timeout: Optional[int] = None,
    ) -> SessionMetricsResult:
        """
        Get runtime metrics for this session.

        Args:
            read_timeout (Optional[int]): Read timeout in milliseconds.
            connect_timeout (Optional[int]): Connect timeout in milliseconds.

        Returns:
            SessionMetricsResult: Result containing session metrics data.
        """
        log_operation_start(
            "Session.get_metrics",
            f"SessionId={self.session_id}",
        )

        # Use Session's call_mcp_tool method
        tool_result = self.call_mcp_tool(
            tool_name="get_metrics",
            args={},
            read_timeout=read_timeout,
            connect_timeout=connect_timeout,
        )

        if not tool_result.success:
            log_operation_error(
                "Session.get_metrics",
                tool_result.error_message or "Failed to get metrics",
            )
            return SessionMetricsResult(
                request_id=tool_result.request_id,
                success=False,
                metrics=None,
                error_message=tool_result.error_message,
                raw={},
            )

        try:
            # Parse the JSON response data
            raw = (
                json.loads(tool_result.data)
                if isinstance(tool_result.data, str)
                else tool_result.data
            )
            if not isinstance(raw, dict):
                raise ValueError("get_metrics returned non-object JSON")

            def _float_from_first_key(data: dict, keys: list, default: float = 0.0) -> float:
                """Helper function to get float value from first available key."""
                for k in keys:
                    if k in data and data.get(k) is not None:
                        try:
                            return float(data.get(k) or 0.0)
                        except Exception:
                            pass
                return float(default)

            # Create SessionMetrics object with parsed data
            metrics = SessionMetrics(
                cpu_count=int(raw.get("cpu_count", 0) or 0),
                cpu_used_pct=float(raw.get("cpu_used_pct", 0.0) or 0.0),
                disk_total=int(raw.get("disk_total", 0) or 0),
                disk_used=int(raw.get("disk_used", 0) or 0),
                mem_total=int(raw.get("mem_total", 0) or 0),
                mem_used=int(raw.get("mem_used", 0) or 0),
                rx_rate_kbyte_per_s=_float_from_first_key(
                    raw,
                    ["rx_rate_kbyte_per_s", "rx_rate_kbps", "rx_rate_KBps"],
                ),
                tx_rate_kbyte_per_s=_float_from_first_key(
                    raw,
                    ["tx_rate_kbyte_per_s", "tx_rate_kbps", "tx_rate_KBps"],
                ),
                rx_used_kbyte=_float_from_first_key(
                    raw, ["rx_used_kbyte", "rx_used_kb", "rx_used_KB"]
                ),
                tx_used_kbyte=_float_from_first_key(
                    raw, ["tx_used_kbyte", "tx_used_kb", "tx_used_KB"]
                ),
                timestamp=str(raw.get("timestamp", "") or ""),
            )

            log_operation_success(
                "Session.get_metrics",
                f"SessionId={self.session_id}, RequestId={tool_result.request_id}",
            )

            return SessionMetricsResult(
                request_id=tool_result.request_id,
                success=True,
                metrics=metrics,
                error_message="",
                raw=raw,
            )

        except Exception as e:
            error_msg = f"Failed to parse get_metrics response: {e}"
            log_operation_error("Session.get_metrics", error_msg, exc_info=True)
            return SessionMetricsResult(
                request_id=tool_result.request_id,
                success=False,
                metrics=None,
                error_message=error_msg,
                raw={},
            )
