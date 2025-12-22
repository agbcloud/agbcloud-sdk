import json
from enum import Enum
from typing import Union
from typing import Union,List, Optional, Any, Dict

from agb.api.base_service import BaseService
from agb.model.response import BoolResult, OperationResult,WindowInfoResult,AppOperationResult, ProcessListResult, InstalledAppListResult, WindowListResult
from agb.logger import get_logger, log_operation_start, log_operation_success, log_operation_error

logger = get_logger(__name__)


class MouseButton(str, Enum):
    """Mouse button types for click and drag operations."""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"
    DOUBLE_LEFT = "double_left"


class ScrollDirection(str, Enum):
    """Scroll direction for scroll operations."""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

class Window:
    """Represents a window in the system."""

    def __init__(
        self,
        window_id: int,
        title: str,
        absolute_upper_left_x: Optional[int] = None,
        absolute_upper_left_y: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        pid: Optional[int] = None,
        pname: Optional[str] = None,
        child_windows: Optional[List["Window"]] = None,
    ):
        self.window_id = window_id
        self.title = title
        self.absolute_upper_left_x = absolute_upper_left_x
        self.absolute_upper_left_y = absolute_upper_left_y
        self.width = width
        self.height = height
        self.pid = pid
        self.pname = pname
        self.child_windows = child_windows or []

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "Window":
        child_windows = []
        if "child_windows" in data and data["child_windows"]:
            child_windows = [cls._from_dict(child) for child in data["child_windows"]]
        return cls(
            window_id=data.get("window_id", 0),
            title=data.get("title", ""),
            absolute_upper_left_x=data.get("absolute_upper_left_x"),
            absolute_upper_left_y=data.get("absolute_upper_left_y"),
            width=data.get("width"),
            height=data.get("height"),
            pid=data.get("pid"),
            pname=data.get("pname"),
            child_windows=child_windows,
        )

class InstalledApp:
    """Represents an installed application."""

    def __init__(
        self,
        name: str,
        start_cmd: str,
        stop_cmd: Optional[str] = None,
        work_directory: Optional[str] = None,
    ):
        self.name = name
        self.start_cmd = start_cmd
        self.stop_cmd = stop_cmd
        self.work_directory = work_directory

    @classmethod
    def _from_dict(cls, data: dict) -> "InstalledApp":
        return cls(
            name=data.get("name", ""),
            start_cmd=data.get("start_cmd", ""),
            stop_cmd=data.get("stop_cmd"),
            work_directory=data.get("work_directory"),
        )
class Process:
    """Represents a running process."""

    def __init__(self, pname: str, pid: int, cmdline: Optional[str] = None):
        self.pname = pname
        self.pid = pid
        self.cmdline = cmdline

    @classmethod
    def _from_dict(cls, data: dict) -> "Process":
        return cls(
            pname=data.get("pname", ""),
            pid=data.get("pid", 0),
            cmdline=data.get("cmdline"),
        )


class Computer(BaseService):
    """
    Handles computer UI automation operations in the AGB cloud environment.
    """
    # Mouse Operations
    def click_mouse(self, x: int, y: int, button: Union[MouseButton, str] = MouseButton.LEFT) -> BoolResult:
        """
        Clicks the mouse at the specified screen coordinates.

        Args:
            x (int): X coordinate in pixels (0 is left edge of screen).
            y (int): Y coordinate in pixels (0 is top edge of screen).
            button (Union[MouseButton, str], optional): Mouse button to click. Options:
                - MouseButton.LEFT or "left": Single left click
                - MouseButton.RIGHT or "right": Right click (context menu)
                - MouseButton.MIDDLE or "middle": Middle click (scroll wheel)
                - MouseButton.DOUBLE_LEFT or "double_left": Double left click
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
            log_operation_error("Computer.click_mouse", error_msg)
            raise ValueError(error_msg)

        log_operation_start("Computer.click_mouse", f"X={x}, Y={y}, Button={button_str}")
        try:
            args = {"x": x, "y": y, "button": button_str}
            result = self._call_mcp_tool("click_mouse", args)
            logger.debug(f"Click mouse response: {result}")

            if result.success:
                result_msg = f"X={x}, Y={y}, Button={button_str}, RequestId={result.request_id}"
                log_operation_success("Computer.click_mouse", result_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=True,
                    data=True,
                )
            else:
                error_msg = result.error_message or "Failed to click mouse"
                log_operation_error("Computer.click_mouse", error_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("Computer.click_mouse", str(e), exc_info=True)
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to click mouse: {e}",
            )

    def move_mouse(self, x: int, y: int) -> BoolResult:
        """
        Moves the mouse to the specified coordinates.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            BoolResult: Result object containing success status and error message if any.
        """
        log_operation_start("Computer.move_mouse", f"X={x}, Y={y}")
        try:
            args = {"x": x, "y": y}
            result = self._call_mcp_tool("move_mouse", args)
            logger.debug(f"Move mouse response: {result}")

            if result.success:
                result_msg = f"X={x}, Y={y}, RequestId={result.request_id}"
                log_operation_success("Computer.move_mouse", result_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=True,
                    data=True,
                )
            else:
                error_msg = result.error_message or "Failed to move mouse"
                log_operation_error("Computer.move_mouse", error_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("Computer.move_mouse", str(e), exc_info=True)
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to move mouse: {e}",
            )

    def drag_mouse(
        self, from_x: int, from_y: int, to_x: int, to_y: int, button: Union[MouseButton, str] = MouseButton.LEFT
    ) -> BoolResult:
        """
        Drags the mouse from one point to another.

        Args:
            from_x (int): Starting X coordinate.
            from_y (int): Starting Y coordinate.
            to_x (int): Ending X coordinate.
            to_y (int): Ending Y coordinate.
            button (Union[MouseButton, str], optional): Button type. Can be MouseButton enum or string.
                Valid values: MouseButton.LEFT, MouseButton.RIGHT, MouseButton.MIDDLE
                or their string equivalents. Defaults to MouseButton.LEFT.
                Note: DOUBLE_LEFT is not supported for drag operations.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Raises:
            ValueError: If button is not a valid option.
        Note:
            - Performs a click-and-drag operation from start to end coordinates
            - Useful for selecting text, moving windows, or drawing
            - DOUBLE_LEFT button is not supported for drag operations
            - Use LEFT, RIGHT, or MIDDLE button only

        See Also:
            click_mouse, move_mouse
        """
        button_str = button.value if isinstance(button, MouseButton) else button
        valid_buttons = ["left", "right", "middle"]
        if button_str not in valid_buttons:
            error_msg = f"Invalid button '{button_str}'. Must be one of {valid_buttons}"
            log_operation_error("Computer.drag_mouse", error_msg)
            raise ValueError(error_msg)

        log_operation_start("Computer.drag_mouse", f"FromX={from_x}, FromY={from_y}, ToX={to_x}, ToY={to_y}, Button={button_str}")
        try:
            args = {
                "from_x": from_x,
                "from_y": from_y,
                "to_x": to_x,
                "to_y": to_y,
                "button": button_str,
            }
            result = self._call_mcp_tool("drag_mouse", args)
            logger.debug(f"Drag mouse response: {result}")

            if result.success:
                result_msg = f"FromX={from_x}, FromY={from_y}, ToX={to_x}, ToY={to_y}, RequestId={result.request_id}"
                log_operation_success("Computer.drag_mouse", result_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=True,
                    data=True,
                )
            else:
                error_msg = result.error_message or "Failed to drag mouse"
                log_operation_error("Computer.drag_mouse", error_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("Computer.drag_mouse", str(e), exc_info=True)
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to drag mouse: {e}",
            )

    def scroll(
        self, x: int, y: int, direction: Union[ScrollDirection, str] = ScrollDirection.UP, amount: int = 1
    ) -> BoolResult:
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
        Note:
            - Scroll operations are performed at the specified coordinates
            - The amount parameter controls how many scroll units to move
            - Larger amounts result in faster scrolling
            - Useful for navigating long documents or web pages

        See Also:
            click_mouse, move_mouse
        """
        direction_str = direction.value if isinstance(direction, ScrollDirection) else direction
        valid_directions = [d.value for d in ScrollDirection]
        if direction_str not in valid_directions:
            error_msg = f"Invalid direction '{direction_str}'. Must be one of {valid_directions}"
            log_operation_error("Computer.scroll", error_msg)
            raise ValueError(error_msg)

        log_operation_start("Computer.scroll", f"X={x}, Y={y}, Direction={direction_str}, Amount={amount}")
        try:
            args = {"x": x, "y": y, "direction": direction_str, "amount": amount}
            result = self._call_mcp_tool("scroll", args)
            logger.debug(f"Scroll response: {result}")

            if result.success:
                result_msg = f"X={x}, Y={y}, Direction={direction_str}, Amount={amount}, RequestId={result.request_id}"
                log_operation_success("Computer.scroll", result_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=True,
                    data=True,
                )
            else:
                error_msg = result.error_message or "Failed to scroll"
                log_operation_error("Computer.scroll", error_msg)
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

    def get_cursor_position(self) -> OperationResult:
        """
        Gets the current cursor position.

        Returns:
            OperationResult: Result object containing cursor position data
                with keys 'x' and 'y', and error message if any.
        Note:
            - Returns the absolute screen coordinates
            - Useful for verifying mouse movements
            - Position is in pixels from top-left corner (0, 0)

        See Also:
            move_mouse, click_mouse, get_screen_size
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

    # Screen Operations
    def get_screen_size(self) -> OperationResult:
        """
        Gets the screen size and DPI scaling factor.

        Returns:
            OperationResult: Result object containing screen size data
                with keys 'width', 'height', and 'dpiScalingFactor',
                and error message if any.

        Note:
            - Returns the full screen dimensions in pixels
            - DPI scaling factor affects coordinate calculations on high-DPI displays
            - Use this to determine valid coordinate ranges for mouse operations

        See Also:
            click_mouse, move_mouse, screenshot
        """
        log_operation_start("Computer.get_screen_size", "")
        try:
            args = {}
            result = self._call_mcp_tool("get_screen_size", args)
            logger.debug(f"Get screen size response: {result}")

            if result.success:
                screen_data = result.data if isinstance(result.data, dict) else {}
                result_msg = f"Width={screen_data.get('width', 'N/A')}, Height={screen_data.get('height', 'N/A')}, RequestId={result.request_id}"
                log_operation_success("Computer.get_screen_size", result_msg)
                return OperationResult(
                    request_id=result.request_id,
                    success=True,
                    data=result.data,
                )
            else:
                error_msg = result.error_message or "Failed to get screen size"
                log_operation_error("Computer.get_screen_size", error_msg)
                return OperationResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("Computer.get_screen_size", str(e), exc_info=True)
            return OperationResult(
                request_id="",
                success=False,
                error_message=f"Failed to get screen size: {e}",
            )

    def screenshot(self) -> OperationResult:
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
            get_screen_size
        """
        log_operation_start("Computer.screenshot", "")
        try:
            args = {}
            result = self._call_mcp_tool("system_screenshot", args)
            logger.debug(f"Screenshot response: {result}")

            if result.success:
                result_msg = f"RequestId={result.request_id}, ImageUrl={result.data if result.data else 'None'}"
                log_operation_success("Computer.screenshot", result_msg)
                return OperationResult(
                    request_id=result.request_id,
                    success=True,
                    data=result.data,
                )
            else:
                error_msg = result.error_message or "Failed to take screenshot"
                log_operation_error("Computer.screenshot", error_msg)
                return OperationResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("Computer.screenshot", str(e), exc_info=True)
            return OperationResult(
                request_id="",
                success=False,
                error_message=f"Failed to take screenshot: {e}",
            )

    # Keyboard Operations
    def input_text(self, text: str) -> BoolResult:
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

        See Also:
            press_keys, release_keys
        """
        log_operation_start("Computer.input_text", f"Text={text}")
        try:
            args = {"text": text}
            result = self._call_mcp_tool("input_text", args)
            logger.debug(f"Input text response: {result}")

            if result.success:
                result_msg = f"TextLength={len(text)}, RequestId={result.request_id}"
                log_operation_success("Computer.input_text", result_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=True,
                    data=True,
                )
            else:
                error_msg = result.error_message or "Failed to input text"
                log_operation_error("Computer.input_text", error_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("Computer.input_text", str(e), exc_info=True)
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to input text: {e}",
            )

    def press_keys(self, keys: list, hold: bool = False) -> BoolResult:
        """
        Presses the specified keys.

        Args:
            keys (List[str]): List of keys to press (e.g., ["Ctrl", "a"]).
            hold (bool, optional): Whether to hold the keys. Defaults to False.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Note:
            - Key names are case-sensitive
            - When hold=True, remember to call release_keys() afterwards
            - Supports modifier keys like Ctrl, Alt, Shift
            - Can press multiple keys simultaneously for shortcuts

        See Also:
            release_keys, input_text
        """
        log_operation_start("Computer.press_keys", f"Keys={keys}, Hold={hold}")
        try:
            args = {"keys": keys, "hold": hold}
            result = self._call_mcp_tool("press_keys", args)
            logger.debug(f"Press keys response: {result}")

            if result.success:
                result_msg = f"Keys={keys}, Hold={hold}, RequestId={result.request_id}"
                log_operation_success("Computer.press_keys", result_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=True,
                    data=True,
                )
            else:
                error_msg = result.error_message or "Failed to press keys"
                log_operation_error("Computer.press_keys", error_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("Computer.press_keys", str(e), exc_info=True)
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to press keys: {e}",
            )

    def release_keys(self, keys: list) -> BoolResult:
        """
        Releases the specified keys.

        Args:
            keys (List[str]): List of keys to release (e.g., ["Ctrl", "a"]).

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Note:
            - Should be used after press_keys() with hold=True
            - Key names are case-sensitive
            - Releases all keys specified in the list

        See Also:
            press_keys, input_text
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

    # Window Management Operations
    def list_root_windows(self, timeout_ms: int = 3000) -> WindowListResult:
        """
        Lists all root windows.

        Args:
            timeout_ms (int, optional): Timeout in milliseconds. Defaults to 3000.

        Returns:
            WindowListResult: Result object containing list of windows and error message if any.

        Note:
            - Returns all top-level windows in the system
            - Each window contains ID, title, position, and size information
            - Useful for discovering available windows to interact with

        See Also:
            get_active_window, activate_window
        """
        try:
            args = {"timeout_ms": timeout_ms}
            result = self._call_mcp_tool("list_root_windows", args)
            logger.debug(f"List root windows response: {result}")

            if result.success:
                windows = []

                if result.data:
                    try:
                        windows_data = json.loads(result.data)
                        for window_data in windows_data:
                            windows.append(Window._from_dict(window_data))
                    except json.JSONDecodeError as e:
                        return WindowListResult(
                            request_id=result.request_id,
                            success=False,
                            windows=[],
                            error_message=f"Failed to parse windows JSON: {e}",
                        )

                return WindowListResult(
                    request_id=result.request_id,
                    success=True,
                    windows=windows,
                )
            else:
                return WindowListResult(
                    request_id=result.request_id,
                    success=False,
                    windows=[],
                    error_message=result.error_message or "Failed to list root windows",
                )
        except Exception as e:
            return WindowListResult(
                request_id="",
                success=False,
                windows=[],
                error_message=f"Failed to list root windows: {e}",
            )

    def get_active_window(self) -> WindowInfoResult:
        """
        Gets the currently active window.

        Args:
            timeout_ms (int, optional): Timeout in milliseconds. Defaults to 3000.

        Returns:
            WindowInfoResult: Result object containing active window info and error message if any.

        Note:
            - Returns the window that currently has focus
            - Active window receives keyboard input
            - Useful for determining which window is currently in use

        See Also:
            list_root_windows, activate_window
        """
        try:
            args = {}
            result = self._call_mcp_tool("get_active_window", args)
            logger.debug(f"Get active window response: {result}")

            if result.success:
                window = None

                if result.data:
                    try:
                        window_data = json.loads(result.data)
                        window = Window._from_dict(window_data)
                    except json.JSONDecodeError as e:
                        return WindowInfoResult(
                            request_id=result.request_id,
                            success=False,
                            window=None,
                            error_message=f"Failed to parse window JSON: {e}",
                        )

                return WindowInfoResult(
                    request_id=result.request_id,
                    success=True,
                    window=window,
                )
            else:
                return WindowInfoResult(
                    request_id=result.request_id,
                    success=False,
                    window=None,
                    error_message=result.error_message or "Failed to get active window",
                )
        except Exception as e:
            return WindowInfoResult(
                request_id="",
                success=False,
                window=None,
                error_message=f"Failed to get active window: {e}",
            )

    def activate_window(self, window_id: int) -> BoolResult:
        """
        Activates the specified window.

        Args:
            window_id (str): The ID of the window to activate.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Note:
            - The window must exist in the system
            - Use list_root_windows() to get available window IDs
            - Activating a window brings it to the foreground and gives it focus

        See Also:
            list_root_windows, get_active_window, close_window
        """
        log_operation_start("Computer.activate_window", f"WindowId={window_id}")
        try:
            args = {"window_id": window_id}
            result = self._call_mcp_tool("activate_window", args)
            logger.debug(f"Activate window response: {result}")

            if result.success:
                result_msg = f"WindowId={window_id}, RequestId={result.request_id}"
                log_operation_success("Computer.activate_window", result_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=True,
                    data=True,
                )
            else:
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    data=None,
                    error_message=result.error_message or "Failed to activate window",
                )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to activate window: {e}",
            )

    def close_window(self, window_id: int) -> BoolResult:
        """
        Closes the specified window.

        Args:
            window_id (str): The ID of the window to close.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Note:
            - The window must exist in the system
            - Use list_root_windows() to get available window IDs
            - Closing a window terminates it permanently

        See Also:
            list_root_windows, activate_window, minimize_window
        """
        try:
            args = {"window_id": window_id}
            result = self._call_mcp_tool("close_window", args)
            logger.debug(f"Close window response: {result}")

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
                    data=None,
                    error_message=result.error_message or "Failed to close window",
                )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to close window: {e}",
            )

    def maximize_window(self, window_id: int) -> BoolResult:
        """
        Maximizes the specified window.

        Args:
            window_id (str): The ID of the window to maximize.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Note:
            - The window must exist in the system
            - Maximizing expands the window to fill the screen
            - Use restore_window() to return to previous size

        See Also:
            minimize_window, restore_window, fullscreen_window, resize_window
        """
        try:
            args = {"window_id": window_id}
            result = self._call_mcp_tool("maximize_window", args)
            logger.debug(f"Maximize window response: {result}")

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
                    data=None,
                    error_message=result.error_message or "Failed to maximize window",
                )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to maximize window: {e}",
            )

    def minimize_window(self, window_id: int) -> BoolResult:
        """
        Minimizes the specified window.

        Args:
            window_id (str): The ID of the window to minimize.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Note:
            - The window must exist in the system
            - Minimizing hides the window in the taskbar
            - Use restore_window() or activate_window() to bring it back

        See Also:
            maximize_window, restore_window, activate_window
        """
        try:
            args = {"window_id": window_id}
            result = self._call_mcp_tool("minimize_window", args)
            logger.debug(f"Minimize window response: {result}")

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
                    data=None,
                    error_message=result.error_message or "Failed to minimize window",
                )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to minimize window: {e}",
            )

    def restore_window(self, window_id: int) -> BoolResult:
        """
        Restores the specified window.

        Args:
            window_id (str): The ID of the window to restore.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Note:
            - The window must exist in the system
            - Restoring returns a minimized or maximized window to its normal state
            - Works for windows that were previously minimized or maximized

        See Also:
            minimize_window, maximize_window, activate_window
        """
        try:
            args = {"window_id": window_id}
            result = self._call_mcp_tool("restore_window", args)
            logger.debug(f"Restore window response: {result}")

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
                    data=None,
                    error_message=result.error_message or "Failed to restore window",
                )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to restore window: {e}",
            )

    def resize_window(self, window_id: int, width: int, height: int) -> BoolResult:
        """
        Resizes the specified window.

        Args:
            window_id (str): The ID of the window to resize.
            width (int): New width of the window in pixels.
            height (int): New height of the window in pixels.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Note:
            - The window must exist in the system
            - Width and height are in pixels
            - Some windows may have minimum or maximum size constraints

        See Also:
            maximize_window, restore_window, get_screen_size
        """
        try:
            args = {"window_id": window_id, "width": width, "height": height}
            result = self._call_mcp_tool("resize_window", args)
            logger.debug(f"Resize window response: {result}")

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
                    data=None,
                    error_message=result.error_message or "Failed to resize window",
                )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to resize window: {e}",
            )

    def fullscreen_window(self, window_id: int) -> BoolResult:
        """
        Makes the specified window fullscreen.

        Args:
            window_id (str): The ID of the window to make fullscreen.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Note:
            - The window must exist in the system
            - Fullscreen mode hides window borders and taskbar
            - Different from maximize_window() which keeps window borders
            - Press F11 or ESC to exit fullscreen in most applications

        See Also:
            maximize_window, restore_window
        """
        try:
            args = {"window_id": window_id}
            result = self._call_mcp_tool("fullscreen_window", args)
            logger.debug(f"Fullscreen window response: {result}")

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
                    data=None,
                    error_message=result.error_message or "Failed to fullscreen window",
                )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to fullscreen window: {e}",
            )

    def focus_mode(self, on: bool) -> BoolResult:
        """
        Toggles focus mode on or off.

        Args:
            on (bool): True to enable focus mode, False to disable it.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Note:
            - Focus mode helps reduce distractions by managing window focus
            - When enabled, may prevent background windows from stealing focus
            - Behavior depends on the window manager and OS settings

        See Also:
            activate_window, get_active_window
        """
        try:
            args = {"on": on}
            result = self._call_mcp_tool("focus_mode", args)
            logger.debug(f"Focus mode response: {result}")

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
                    data=None,
                    error_message=result.error_message or "Failed to toggle focus mode",
                )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to toggle focus mode: {e}",
            )

    # Application Management Operations
    def get_installed_apps(
        self,
        start_menu: bool = True,
        desktop: bool = False,
        ignore_system_apps: bool = True,
    ) -> InstalledAppListResult:
        """
        Gets the list of installed applications.

        Args:
            start_menu (bool, optional): Whether to include start menu applications. Defaults to True.
            desktop (bool, optional): Whether to include desktop applications. Defaults to False.
            ignore_system_apps (bool, optional): Whether to ignore system applications. Defaults to True.

        Returns:
            InstalledAppListResult: Result object containing list of installed apps and error message if any.

        Note:
            - start_menu parameter includes applications from Windows Start Menu
            - desktop parameter includes shortcuts from Desktop
            - ignore_system_apps parameter filters out system applications
            - Each app object contains name, start_cmd, stop_cmd, and work_directory

        See Also:
            start_app, list_visible_apps, stop_app_by_pname
        """
        try:
            args = {
                "start_menu": start_menu,
                "desktop": desktop,
                "ignore_system_apps": ignore_system_apps,
            }

            result = self._call_mcp_tool("get_installed_apps", args)
            logger.debug(f"Get installed apps response: {result}")

            if not result.success:
                return InstalledAppListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to get installed apps",
                )

            try:
                apps_json = json.loads(result.data)
                installed_apps = []

                for app_data in apps_json:
                    app = InstalledApp._from_dict(app_data)
                    installed_apps.append(app)

                return InstalledAppListResult(
                    request_id=result.request_id,
                    success=True,
                    data=installed_apps,
                )
            except json.JSONDecodeError as e:
                return InstalledAppListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=f"Failed to parse applications JSON: {e}",
                )
        except Exception as e:
            return InstalledAppListResult(
                success=False,
                error_message=f"Failed to get installed apps: {e}"
            )

    def start_app(
        self, start_cmd: str, work_directory: str = "", activity: str = ""
    ) -> ProcessListResult:
        """
        Starts the specified application.

        Args:
            start_cmd (str): The command to start the application.
            work_directory (str, optional): Working directory for the application. Defaults to "".
            activity (str, optional): Activity name to launch (for mobile apps). Defaults to "".

        Returns:
            ProcessListResult: Result object containing list of processes started and error message if any.

        Note:
            - The start_cmd can be an executable name or full path
            - work_directory is optional and defaults to the system default
            - activity parameter is for mobile apps (Android)
            - Returns process information for all started processes

        See Also:
            get_installed_apps, stop_app_by_pname, list_visible_apps
        """
        op_details = f"StartCmd={start_cmd}"
        if work_directory:
            op_details += f", WorkDirectory={work_directory}"
        if activity:
            op_details += f", Activity={activity}"
        log_operation_start("Computer.start_app", op_details)
        try:
            args = {"start_cmd": start_cmd}
            if work_directory:
                args["work_directory"] = work_directory
            if activity:
                args["activity"] = activity

            result = self._call_mcp_tool("start_app", args)
            logger.debug(f"Start app response: {result}")

            if not result.success:
                error_msg = result.error_message or "Failed to start app"
                log_operation_error("Computer.start_app", error_msg)
                return ProcessListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )

            try:
                processes_json = json.loads(result.data)
                processes = []

                for process_data in processes_json:
                    process = Process._from_dict(process_data)
                    processes.append(process)

                result_msg = f"StartCmd={start_cmd}, ProcessesCount={len(processes)}, RequestId={result.request_id}"
                log_operation_success("Computer.start_app", result_msg)
                return ProcessListResult(
                    request_id=result.request_id,
                    success=True,
                    data=processes
                )
            except json.JSONDecodeError as e:
                log_operation_error("Computer.start_app", f"Failed to parse processes JSON: {str(e)}", exc_info=True)
                return ProcessListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=f"Failed to parse processes JSON: {e}",
                )
        except Exception as e:
            log_operation_error("Computer.start_app", str(e), exc_info=True)
            return ProcessListResult(
                success=False,
                error_message=f"Failed to start app: {e}"
            )

    def list_visible_apps(self) -> ProcessListResult:
        """
        Lists all applications with visible windows.

        Returns detailed process information for applications that have visible windows,
        including process ID, name, command line, and other system information.
        This is useful for system monitoring and process management tasks.

        Returns:
            ProcessListResult: Result object containing list of visible applications
                with detailed process information.

        Note:
            - Only returns applications with visible windows
            - Hidden or minimized windows may not appear
            - Useful for monitoring currently active applications
            - Process information includes PID, name, and command line

        See Also:
            get_installed_apps, start_app, stop_app_by_pname, stop_app_by_pid
        """
        try:
            result = self._call_mcp_tool("list_visible_apps", {})
            logger.debug(f"List visible apps response: {result}")

            if not result.success:
                return ProcessListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to list visible apps",
                )

            try:
                processes_json = json.loads(result.data)
                processes = []

                for process_data in processes_json:
                    process = Process._from_dict(process_data)
                    processes.append(process)

                return ProcessListResult(
                    request_id=result.request_id,
                    success=True,
                    data=processes
                )
            except json.JSONDecodeError as e:
                return ProcessListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=f"Failed to parse processes JSON: {e}",
                )
        except Exception as e:
            return ProcessListResult(
                success=False,
                error_message=f"Failed to list visible apps: {e}"
            )

    def stop_app_by_pname(self, pname: str) -> AppOperationResult:
        """
        Stops an application by process name.

        Args:
            pname (str): The process name of the application to stop.

        Returns:
            AppOperationResult: Result object containing success status and error message if any.

        Note:
            - The process name should match exactly (case-sensitive on some systems)
            - This will stop all processes matching the given name
            - If multiple instances are running, all will be terminated
            - The .exe extension may be required on Windows

        See Also:
            start_app, stop_app_by_pid, stop_app_by_cmd, list_visible_apps
        """
        log_operation_start("Computer.stop_app_by_pname", f"PName={pname}")
        try:
            args = {"pname": pname}
            result = self._call_mcp_tool("stop_app_by_pname", args)
            logger.debug(f"Stop app by pname response: {result}")

            if result.success:
                result_msg = f"PName={pname}, RequestId={result.request_id}"
                log_operation_success("Computer.stop_app_by_pname", result_msg)
            else:
                error_msg = result.error_message or "Failed to stop app by pname"
                log_operation_error("Computer.stop_app_by_pname", error_msg)

            return AppOperationResult(
                request_id=result.request_id,
                success=result.success,
                error_message=result.error_message or ("Failed to stop app by pname" if not result.success else ""),
            )
        except Exception as e:
            log_operation_error("Computer.stop_app_by_pname", str(e), exc_info=True)
            return AppOperationResult(
                success=False,
                error_message=f"Failed to stop app by pname: {e}"
            )

    def stop_app_by_pid(self, pid: int) -> AppOperationResult:
        """
        Stops an application by process ID.

        Args:
            pid (int): The process ID of the application to stop.

        Returns:
            AppOperationResult: Result object containing success status and error message if any.

        Note:
            - PID must be a valid process ID
            - More precise than stopping by name (only stops specific process)
            - The process must be owned by the session or have appropriate permissions
            - PID can be obtained from start_app() or list_visible_apps()

        See Also:
            start_app, stop_app_by_pname, stop_app_by_cmd, list_visible_apps
        """
        log_operation_start("Computer.stop_app_by_pid", f"PID={pid}")
        try:
            args = {"pid": pid}
            result = self._call_mcp_tool("stop_app_by_pid", args)
            logger.debug(f"Stop app by pid response: {result}")

            if result.success:
                result_msg = f"PID={pid}, RequestId={result.request_id}"
                log_operation_success("Computer.stop_app_by_pid", result_msg)
            else:
                error_msg = result.error_message or "Failed to stop app by pid"
                log_operation_error("Computer.stop_app_by_pid", error_msg)

            return AppOperationResult(
                request_id=result.request_id,
                success=result.success,
                error_message=result.error_message or ("Failed to stop app by pid" if not result.success else ""),
            )
        except Exception as e:
            log_operation_error("Computer.stop_app_by_pid", str(e), exc_info=True)
            return AppOperationResult(
                success=False,
                error_message=f"Failed to stop app by pid: {e}"
            )

    def stop_app_by_cmd(self, stop_cmd: str) -> AppOperationResult:
        """
        Stops an application by stop command.

        Args:
            stop_cmd (str): The command to stop the application.

        Returns:
            AppOperationResult: Result object containing success status and error message if any.

        Note:
            - The stop_cmd should be the command registered to stop the application
            - Typically obtained from get_installed_apps() which returns app metadata
            - Some applications may not have a stop command defined
            - The command is executed as-is without shell interpretation

        See Also:
            get_installed_apps, start_app, stop_app_by_pname, stop_app_by_pid
        """
        log_operation_start("Computer.stop_app_by_cmd", f"StopCmd={stop_cmd}")
        try:
            args = {"stop_cmd": stop_cmd}
            result = self._call_mcp_tool("stop_app_by_cmd", args)
            logger.debug(f"Stop app by cmd response: {result}")

            if result.success:
                result_msg = f"StopCmd={stop_cmd}, RequestId={result.request_id}"
                log_operation_success("Computer.stop_app_by_cmd", result_msg)
            else:
                error_msg = result.error_message or "Failed to stop app by cmd"
                log_operation_error("Computer.stop_app_by_cmd", error_msg)

            return AppOperationResult(
                request_id=result.request_id,
                success=result.success,
                error_message=result.error_message or ("Failed to stop app by cmd" if not result.success else ""),
            )
        except Exception as e:
            log_operation_error("Computer.stop_app_by_cmd", str(e), exc_info=True)
            return AppOperationResult(
                success=False,
                error_message=f"Failed to stop app by cmd: {e}"
            )
