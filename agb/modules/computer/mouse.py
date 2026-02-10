"""
Mouse controller for computer automation operations.
"""

from typing import Union, Tuple
import json

from agb.api.base_service import BaseService
from agb.model.response import BoolResult, OperationResult
from agb.logger import get_logger, log_operation_start, log_operation_success, log_operation_error
from agb.modules.computer import MouseButton, ScrollDirection

logger = get_logger(__name__)


class MouseController(BaseService):
    """Controller for mouse operations."""

    def click(self, x: int, y: int, button: Union[MouseButton, str] = MouseButton.LEFT) -> BoolResult:
        """
        Clicks the mouse at the specified screen coordinates.

        Args:
            x (int): X coordinate in pixels (0 is left edge of screen).
            y (int): Y coordinate in pixels (0 is top edge of screen).
            button (Union[MouseButton, str], optional): Mouse button to click. Options:
                - MouseButton.LEFT or "left": Single left click
                - MouseButton.RIGHT or "right": Right click (context menu)
                - MouseButton.MIDDLE or "middle": Middle click (scroll wheel)
                Defaults to MouseButton.LEFT.

        Returns:
            BoolResult: Object containing success status and error message if any.

        Raises:
            ValueError: If button is not one of the valid options.
        """
        button_str = button.value if isinstance(button, MouseButton) else button
        valid_buttons = [b.value for b in MouseButton]
        if button_str not in valid_buttons:
            error_msg = f"Invalid button '{button_str}'. Must be one of {valid_buttons}"
            log_operation_error("MouseController.click", error_msg)
            raise ValueError(error_msg)

        log_operation_start("MouseController.click", f"X={x}, Y={y}, Button={button_str}")
        try:
            args = {"x": x, "y": y, "button": button_str}
            result = self._call_mcp_tool("click_mouse", args)
            logger.debug(f"Click mouse response: {result}")

            if result.success:
                result_msg = f"X={x}, Y={y}, Button={button_str}, RequestId={result.request_id}"
                log_operation_success("MouseController.click", result_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=True,
                    data=True,
                )
            else:
                error_msg = result.error_message or "Failed to click mouse"
                log_operation_error("MouseController.click", error_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("MouseController.click", str(e), exc_info=True)
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to click mouse: {e}",
            )

    def move(self, x: int, y: int) -> BoolResult:
        """
        Moves the mouse to the specified coordinates.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            BoolResult: Result object containing success status and error message if any.
        """
        log_operation_start("MouseController.move", f"X={x}, Y={y}")
        try:
            args = {"x": x, "y": y}
            result = self._call_mcp_tool("move_mouse", args)
            logger.debug(f"Move mouse response: {result}")

            if result.success:
                result_msg = f"X={x}, Y={y}, RequestId={result.request_id}"
                log_operation_success("MouseController.move", result_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=True,
                    data=True,
                )
            else:
                error_msg = result.error_message or "Failed to move mouse"
                log_operation_error("MouseController.move", error_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("MouseController.move", str(e), exc_info=True)
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to move mouse: {e}",
            )

    def drag(self, x1: int, y1: int, x2: int, y2: int, button: Union[MouseButton, str] = MouseButton.LEFT) -> BoolResult:
        """
        Drags the mouse from one point to another.

        Args:
            x1 (int): Starting X coordinate.
            y1 (int): Starting Y coordinate.
            x2 (int): Ending X coordinate.
            y2 (int): Ending Y coordinate.
            button (Union[MouseButton, str], optional): Button type. Can be MouseButton enum or string.
                Valid values: MouseButton.LEFT, MouseButton.RIGHT, MouseButton.MIDDLE
                or their string equivalents. Defaults to MouseButton.LEFT.
                Note: DOUBLE_LEFT is not supported for drag operations.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Raises:
            ValueError: If button is not a valid option.

        Notes:
            - Performs a click-and-drag operation from start to end coordinates
            - Useful for selecting text, moving windows, or drawing
            - DOUBLE_LEFT button is not supported for drag operations
            - Use LEFT, RIGHT, or MIDDLE button only

        """
        button_str = button.value if isinstance(button, MouseButton) else button
        valid_buttons = ["left", "right", "middle"]
        if button_str not in valid_buttons:
            error_msg = f"Invalid button '{button_str}'. Must be one of {valid_buttons}"
            log_operation_error("MouseController.drag", error_msg)
            raise ValueError(error_msg)

        log_operation_start("MouseController.drag", f"FromX={x1}, FromY={y1}, ToX={x2}, ToY={y2}, Button={button_str}")
        try:
            args = {
                "from_x": x1,
                "from_y": y1,
                "to_x": x2,
                "to_y": y2,
                "button": button_str,
            }
            result = self._call_mcp_tool("drag_mouse", args)
            logger.debug(f"Drag mouse response: {result}")

            if result.success:
                result_msg = f"FromX={x1}, FromY={y1}, ToX={x2}, ToY={y2}, RequestId={result.request_id}"
                log_operation_success("MouseController.drag", result_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=True,
                    data=True,
                )
            else:
                error_msg = result.error_message or "Failed to drag mouse"
                log_operation_error("MouseController.drag", error_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("MouseController.drag", str(e), exc_info=True)
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to drag mouse: {e}",
            )

    def scroll(self, x: int, y: int, direction: Union[ScrollDirection, str] = ScrollDirection.UP, amount: int = 1) -> BoolResult:
        """
        Scrolls the mouse wheel at the specified coordinates.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.
            direction (Union[ScrollDirection, str], optional): Scroll direction. Can be ScrollDirection enum or string.
                Valid values: ScrollDirection.UP, ScrollDirection.DOWN, ScrollDirection.LEFT, ScrollDirection.RIGHT
                or their string equivalents. Defaults to ScrollDirection.UP.
            amount (int, optional): Scroll amount. Defaults to 1.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Raises:
            ValueError: If direction is not a valid option.

        Notes:
            - Scroll operations are performed at the specified coordinates
            - The amount parameter controls how many scroll units to move
            - Larger amounts result in faster scrolling
            - Useful for navigating long documents or web pages
        """
        direction_str = direction.value if isinstance(direction, ScrollDirection) else direction
        valid_directions = [d.value for d in ScrollDirection]
        if direction_str not in valid_directions:
            error_msg = f"Invalid direction '{direction_str}'. Must be one of {valid_directions}"
            log_operation_error("MouseController.scroll", error_msg)
            raise ValueError(error_msg)

        log_operation_start("MouseController.scroll", f"X={x}, Y={y}, Direction={direction_str}, Amount={amount}")
        try:
            args = {"x": x, "y": y, "direction": direction_str, "amount": amount}
            result = self._call_mcp_tool("scroll", args)
            logger.debug(f"Scroll response: {result}")

            if result.success:
                result_msg = f"X={x}, Y={y}, Direction={direction_str}, Amount={amount}, RequestId={result.request_id}"
                log_operation_success("MouseController.scroll", result_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=True,
                    data=True,
                )
            else:
                error_msg = result.error_message or "Failed to scroll"
                log_operation_error("MouseController.scroll", error_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to scroll: {e}",
            )

    def get_position(self) -> OperationResult:
        """
        Gets the current cursor position.

        Returns:
            OperationResult: Result object containing cursor position data
                with keys 'x' and 'y', and error message if any.

        Note:
            - Returns the absolute screen coordinates
            - Useful for verifying mouse movements
            - Position is in pixels from top-left corner (0, 0)
        """
        try:
            args = {}
            result = self._call_mcp_tool("get_cursor_position", args)
            logger.debug(f"Get cursor position response: {result}")

            if result.success:
                return OperationResult(
                    request_id=result.request_id,
                    success=True,
                    data=result.data,
                )
            else:
                return OperationResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to get cursor position",
                )
        except Exception as e:
            return OperationResult(
                request_id="",
                success=False,
                error_message=f"Failed to get cursor position: {e}",
            )
