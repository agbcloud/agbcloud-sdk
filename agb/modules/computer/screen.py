"""
Screen controller for computer automation operations.
"""

import json

from agb.api.base_service import BaseService
from agb.model.response import OperationResult
from agb.logger import get_logger, log_operation_start, log_operation_success, log_operation_error

logger = get_logger(__name__)


class ScreenController(BaseService):
    """Controller for screen operations."""

    def capture(self) -> OperationResult:
        """
        Takes a screenshot of the current screen.

        Returns:
            OperationResult: Result object containing the path to the screenshot
                and error message if any.

        Note:
            - Returns an OSS URL to the screenshot image
            - Screenshot captures the entire screen
            - Useful for debugging and verification
            - Image format is typically PNG

        See Also:
            get_size
        """
        log_operation_start("ScreenController.capture", "")
        try:
            args = {}
            result = self._call_mcp_tool("system_screenshot", args)
            logger.debug(f"Screenshot response: {result}")

            if result.success:
                result_msg = f"RequestId={result.request_id}, ImageUrl={result.data if result.data else 'None'}"
                log_operation_success("ScreenController.capture", result_msg)
                return OperationResult(
                    request_id=result.request_id,
                    success=True,
                    data=result.data,
                )
            else:
                error_msg = result.error_message or "Failed to take screenshot"
                log_operation_error("ScreenController.capture", error_msg)
                return OperationResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("ScreenController.capture", str(e), exc_info=True)
            return OperationResult(
                request_id="",
                success=False,
                error_message=f"Failed to take screenshot: {e}",
            )

    def get_size(self) -> OperationResult:
        """
        Gets the screen size and DPI scaling factor.

        Returns:
            OperationResult: Result object containing screen size data (keys 'width', 'height', 'dpiScalingFactor')
                in result.data, and error message if any.

        Note:
            - Returns the full screen dimensions in pixels
            - DPI scaling factor affects coordinate calculations on high-DPI displays
            - Use this to determine valid coordinate ranges for mouse operations
        """
        log_operation_start("ScreenController.get_size", "")
        try:
            args = {}
            result = self._call_mcp_tool("get_screen_size", args)
            logger.debug(f"Get screen size response: {result}")

            if result.success:
                if isinstance(result.data, str):
                    screen_data = json.loads(result.data)
                elif isinstance(result.data, dict):
                    screen_data = result.data
                else:
                    screen_data = {}

                result_msg = f"Width={screen_data.get('width', 'N/A')}, Height={screen_data.get('height', 'N/A')}, RequestId={result.request_id}"
                log_operation_success("ScreenController.get_size", result_msg)
                return OperationResult(
                    request_id=result.request_id,
                    success=True,
                    data=screen_data,
                )
            else:
                error_msg = result.error_message or "Failed to get screen size"
                log_operation_error("ScreenController.get_size", error_msg)
                return OperationResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            error_msg = f"Failed to get screen size: {e}"
            log_operation_error("ScreenController.get_size", error_msg, exc_info=True)
            return OperationResult(
                request_id="",
                success=False,
                error_message=error_msg,
            )
