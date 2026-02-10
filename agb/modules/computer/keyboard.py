"""
Keyboard controller for computer automation operations.
"""

from typing import List, Union

from agb.api.base_service import BaseService
from agb.model.response import BoolResult
from agb.logger import get_logger, log_operation_start, log_operation_success, log_operation_error

logger = get_logger(__name__)


class KeyboardController(BaseService):
    """Controller for keyboard operations."""

    def type(self, text: str) -> BoolResult:
        """
        Types text into the currently focused input field.

        Args:
            text (str): Text to input.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Note:
            - Text is typed at the current focus location
            - Useful for filling forms or typing in text fields
            - Make sure the target input field is focused before calling
        """
        log_operation_start("KeyboardController.type", f"Text={text}")
        try:
            args = {"text": text}
            result = self._call_mcp_tool("input_text", args)
            logger.debug(f"Input text response: {result}")

            if result.success:
                result_msg = f"TextLength={len(text)}, RequestId={result.request_id}"
                log_operation_success("KeyboardController.type", result_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=True,
                    data=True,
                )
            else:
                error_msg = result.error_message or "Failed to input text"
                log_operation_error("KeyboardController.type", error_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("KeyboardController.type", str(e), exc_info=True)
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to input text: {e}",
            )

    def press(self, keys: List[str], hold: bool = False) -> BoolResult:
        """
        Presses the specified keys.

        Args:
            keys (List[str]): List of keys to press (e.g., ["Ctrl", "a"]).
            hold (bool, optional): Whether to hold the keys. Defaults to False.
                When hold=True, remember to call release() afterwards.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Note:
            - Key names are case-sensitive
            - Supports modifier keys like Ctrl, Alt, Shift
            - Can press multiple keys simultaneously for shortcuts
            - When hold=True, you must manually call release() to release the keys
        """
        log_operation_start("KeyboardController.press", f"Keys={keys}, Hold={hold}")
        try:
            args = {"keys": keys, "hold": hold}
            result = self._call_mcp_tool("press_keys", args)
            logger.debug(f"Press keys response: {result}")

            if result.success:
                result_msg = f"Keys={keys}, Hold={hold}, RequestId={result.request_id}"
                log_operation_success("KeyboardController.press", result_msg)
                if hold:
                    logger.warning("Keys are being held. Remember to call release() to release them.")
                return BoolResult(
                    request_id=result.request_id,
                    success=True,
                    data=True,
                )
            else:
                error_msg = result.error_message or "Failed to press keys"
                log_operation_error("KeyboardController.press", error_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("KeyboardController.press", str(e), exc_info=True)
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to press keys: {e}",
            )

    def release(self, keys: List[str]) -> BoolResult:
        """
        Releases the specified keys.

        Args:
            keys (List[str]): List of keys to release (e.g., ["Ctrl", "a"]).

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Note:
            - Should be used after press() with hold=True
            - Key names are case-sensitive
            - Releases all keys specified in the list
        """
        try:
            args = {"keys": keys}
            result = self._call_mcp_tool("release_keys", args)
            logger.debug(f"Release keys response: {result}")

            if result.success:
                return BoolResult(
                    request_id=result.request_id,
                    success=True,
                    data=True,
                )
            else:
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to release keys",
                )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to release keys: {e}",
            )
