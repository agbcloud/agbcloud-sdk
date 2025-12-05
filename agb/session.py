import json
from typing import TYPE_CHECKING, Dict, Optional

from agb.api.models import (
    GetMcpResourceRequest,
    ReleaseSessionRequest,
    SetLabelRequest,
    GetLabelRequest,
)
from agb.exceptions import SessionError
from agb.model.response import OperationResult, DeleteResult
from agb.modules.browser import Browser
from agb.modules.code import Code
from agb.modules.command import Command
from agb.modules.file_system import FileSystem
from agb.context_manager import ContextManager
from agb.logger import get_logger

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
        Delete a session by session object.

        Args:
            sync_context (bool): Whether to sync context before deletion. Defaults to False.

        Returns:
            DeleteResult: Result indicating success or failure and request ID.
        """
        try:
            # Handle context synchronization before deletion if requested
            if sync_context:
                logger.info("Syncing context before session deletion...")
                import time
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

                    sync_duration = time.time() - sync_start_time

                    if sync_result.success:
                        logger.info("Context sync completed successfully")
                        logger.info(f"⏱️  Context sync completed in {sync_duration:.2f} seconds")
                    else:
                        logger.warning("Context sync completed with failures")
                        logger.warning(f"⏱️  Context sync failed after {sync_duration:.2f} seconds")

                except Exception as e:
                    sync_duration = time.time() - sync_start_time
                    logger.error(f"Failed to trigger context sync: {e}")
                    logger.error(f"⏱️  Context sync failed after {sync_duration:.2f} seconds")
                    # Continue with deletion even if sync fails

            # Create request to release the session
            request = ReleaseSessionRequest(
                authorization=f"Bearer {self.get_api_key()}",
                session_id=self.session_id,
            )

            # Make the API call
            response = self.get_client().release_mcp_session(request)

            # Check if response is empty
            if response is None:
                return DeleteResult(
                    request_id="",
                    success=False,
                    error_message="OpenAPI client returned None response",
                )

            # Check response type, if it's ReleaseSessionResponse, use new parsing method
            if hasattr(response, "is_successful"):
                # This is a ReleaseSessionResponse object
                if response.is_successful():
                    return DeleteResult(request_id=response.request_id or "", success=True)
                else:
                    error_msg = (
                        response.get_error_message() or "Failed to delete session"
                    )
                    request_id_attr = getattr(response, "request_id", "")
                    return DeleteResult(
                        request_id=request_id_attr or "",
                        success=False,
                        error_message=error_msg,
                    )
            else:
                request_id_attr = getattr(response, "request_id", "")
                return DeleteResult(
                    request_id=request_id_attr or "",
                    success=False,
                    error_message="Failed to delete session",
                )

        except Exception as e:
            logger.error(f"Error calling release_mcp_session: {e}")
            # In case of error, return failure result with error message
            return DeleteResult(
                success=False,
                error_message=f"Failed to delete session {self.session_id}: {e}",
            )
