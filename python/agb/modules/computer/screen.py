"""
Screen controller for computer automation operations.
"""

import base64
import json
from typing import Any

from agb.api.base_service import BaseService
from agb.model.response import OperationResult, ScreenshotResult
from agb.exceptions import ScreenError
from agb.logger import (
    get_logger,
    log_operation_start,
    log_operation_success,
    log_operation_error,
)

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

        # Check if this environment supports direct screenshot
        link_url = ""
        try:
            link_url = self.session.get_link_url() or ""
        except Exception:
            link_url = getattr(self.session, "link_url", "") or ""
        if link_url:
            error_msg = (
                "This cloud environment does not support `screen.capture()`. "
                "Please use `beta_take_screenshot()` instead."
            )
            log_operation_error("ScreenController.capture", error_msg)
            return OperationResult(
                request_id="",
                success=False,
                data=None,
                error_message=error_msg,
            )

        try:
            args: dict[str, Any] = {}
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
            log_operation_error("ScreenController.capture",
                                str(e), exc_info=True)
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
            args: dict[str, Any] = {}
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
            log_operation_error("ScreenController.get_size",
                                error_msg, exc_info=True)
            return OperationResult(
                request_id="",
                success=False,
                error_message=error_msg,
            )

    def beta_take_screenshot(self, format: str = "png") -> ScreenshotResult:
        """
        Takes a screenshot of the Computer and returns raw binary image data.

        This API uses the MCP tool `screenshot` (wuying_capture) and returns raw
        binary image data. The backend also returns the captured image dimensions
        (width/height in pixels), which are exposed on `ScreenshotResult.width`
        and `ScreenshotResult.height`. The backend metadata fields `type` and
        `mime_type` are exposed on `ScreenshotResult.type` and `ScreenshotResult.mime_type`.

        Args:
            format: The desired image format (default: "png"). Supported: "png", "jpeg", "jpg".

        Returns:
            ScreenshotResult: Object containing the screenshot image data (bytes) and metadata
                including `type`, `mime_type`, `width`, and `height` when provided by the backend.

        Raises:
            ScreenError: If screenshot fails or response cannot be decoded.
            ValueError: If `format` is invalid.

        Note:
            This method only works in environments with link_url (e.g., Browser Use images).
            For other environments, use `capture()` instead.
        """
        log_operation_start(
            "ScreenController.beta_take_screenshot", f"format={format}")

        # Check if this environment supports beta_take_screenshot
        link_url = ""
        try:
            link_url = self.session.get_link_url() or ""
        except Exception:
            link_url = getattr(self.session, "link_url", "") or ""
        if not link_url:
            raise ScreenError(
                "This cloud environment does not support `beta_take_screenshot()`. "
                "Please use `capture()` instead."
            )

        # Validate format
        fmt = (format or "").strip().lower()
        if fmt == "jpg":
            fmt = "jpeg"
        if fmt not in ("png", "jpeg"):
            raise ValueError("Invalid format: must be 'png', 'jpeg', or 'jpg'")

        # Call MCP tool
        args = {"format": fmt}
        result = self.session.call_mcp_tool("screenshot", args)

        if not result.success:
            error_msg = f"Failed to take screenshot via MCP tool 'screenshot': {result.error_message}"
            log_operation_error(
                "ScreenController.beta_take_screenshot", error_msg)
            raise ScreenError(error_msg)

        if not isinstance(result.data, str) or not result.data.strip():
            error_msg = "Screenshot tool returned empty data"
            log_operation_error(
                "ScreenController.beta_take_screenshot", error_msg)
            raise ScreenError(error_msg)

        text = result.data.strip()

        # Backend contract: screenshot tool returns a JSON object string with
        # top-level field "data" containing base64.
        if not text.startswith("{"):
            error_msg = "Screenshot tool returned non-JSON data"
            log_operation_error(
                "ScreenController.beta_take_screenshot", error_msg)
            raise ScreenError(error_msg)

        try:
            obj = json.loads(text)
        except Exception as e:
            error_msg = f"Invalid screenshot JSON: {e}"
            log_operation_error(
                "ScreenController.beta_take_screenshot", error_msg)
            raise ScreenError(error_msg) from e

        if not isinstance(obj, dict):
            error_msg = "Invalid screenshot JSON: expected object"
            log_operation_error(
                "ScreenController.beta_take_screenshot", error_msg)
            raise ScreenError(error_msg)

        shot_type = obj.get("type")
        mime_type = obj.get("mime_type")
        b64 = obj.get("data")

        if not isinstance(b64, str) or not b64.strip():
            error_msg = "Screenshot JSON missing base64 field"
            log_operation_error(
                "ScreenController.beta_take_screenshot", error_msg)
            raise ScreenError(error_msg)

        if not isinstance(shot_type, str) or not shot_type.strip():
            error_msg = "Invalid screenshot JSON: expected non-empty string 'type'"
            log_operation_error(
                "ScreenController.beta_take_screenshot", error_msg)
            raise ScreenError(error_msg)

        if not isinstance(mime_type, str) or not mime_type.strip():
            error_msg = "Invalid screenshot JSON: expected non-empty string 'mime_type'"
            log_operation_error(
                "ScreenController.beta_take_screenshot", error_msg)
            raise ScreenError(error_msg)

        width = obj.get("width")
        height = obj.get("height")

        if width is not None and not isinstance(width, int):
            error_msg = "Invalid screenshot JSON: expected integer 'width'"
            log_operation_error(
                "ScreenController.beta_take_screenshot", error_msg)
            raise ScreenError(error_msg)

        if height is not None and not isinstance(height, int):
            error_msg = "Invalid screenshot JSON: expected integer 'height'"
            log_operation_error(
                "ScreenController.beta_take_screenshot", error_msg)
            raise ScreenError(error_msg)

        # Decode base64 data
        try:
            raw = base64.b64decode(b64, validate=True)
        except Exception as e:
            error_msg = f"Failed to decode screenshot data: {e}"
            log_operation_error(
                "ScreenController.beta_take_screenshot", error_msg)
            raise ScreenError(error_msg) from e

        # Verify magic bytes
        if fmt == "jpeg":
            magic = b"\xff\xd8\xff"
        else:
            magic = b"\x89PNG\r\n\x1a\n"

        if not raw.startswith(magic):
            error_msg = f"Screenshot data does not match expected format '{fmt}'"
            log_operation_error(
                "ScreenController.beta_take_screenshot", error_msg)
            raise ScreenError(error_msg)

        # Verify MIME type
        expected_mime_type = "image/png" if fmt == "png" else "image/jpeg"
        if mime_type.strip().lower() != expected_mime_type:
            error_msg = (
                f"Screenshot JSON mime_type does not match expected format: "
                f"expected {expected_mime_type!r}, got {mime_type!r}"
            )
            log_operation_error(
                "ScreenController.beta_take_screenshot", error_msg)
            raise ScreenError(error_msg)

        log_operation_success(
            "ScreenController.beta_take_screenshot",
            f"RequestId={result.request_id}, Size={len(raw)} bytes, "
            f"Dimensions={width}x{height}, Format={fmt}"
        )

        return ScreenshotResult(
            request_id=result.request_id,
            success=True,
            error_message="",
            type=shot_type,
            data=raw,
            mime_type=mime_type,
            width=width,
            height=height,
        )
