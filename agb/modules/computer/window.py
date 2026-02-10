"""
Window manager for computer automation operations.
"""

import json
from agb.api.base_service import BaseService
from agb.model.response import BoolResult, WindowListResult, WindowInfoResult
from agb.logger import get_logger, log_operation_start, log_operation_success
from agb.modules.computer import Window

logger = get_logger(__name__)


class WindowManager(BaseService):
    """Manager for window operations."""

    def list_root_windows(self, timeout_ms: int = 3000) -> WindowListResult:
        """
        Lists all root windows.

        Args:
            timeout_ms (int, optional): Timeout in milliseconds. Defaults to 3000.

        Returns:
            WindowListResult: Result object containing list of windows and error message if any.
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

        Returns:
            WindowInfoResult: Result object containing active window info and error message if any.

        Note:
            - Returns the window that currently has focus
            - Active window receives keyboard input
            - Useful for determining which window is currently in use
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

    def activate(self, window_id: int) -> BoolResult:
        """
        Activates the specified window.

        Args:
            window_id (int): The ID of the window to activate.

        Returns:
            BoolResult: Result object containing success status and error message if any.

         Note:
            - The window must exist in the system
            - Restoring returns a minimized or maximized window to its normal state
            - Works for windows that were previously minimized or maximized
        """
        log_operation_start("WindowManager.activate", f"WindowId={window_id}")
        try:
            args = {"window_id": window_id}
            result = self._call_mcp_tool("activate_window", args)
            logger.debug(f"Activate window response: {result}")

            if result.success:
                result_msg = f"WindowId={window_id}, RequestId={result.request_id}"
                log_operation_success("WindowManager.activate", result_msg)
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

    def close(self, window_id: int) -> BoolResult:
        """
        Closes the specified window.

        Args:
            window_id (int): The ID of the window to close.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Note:
            - The window must exist in the system
            - Use list_root_windows() to get available window IDs
            - Closing a window terminates it permanently
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

    def maximize(self, window_id: int) -> BoolResult:
        """
        Maximizes the specified window.

        Args:
            window_id (int): The ID of the window to maximize.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Note:
            - The window must exist in the system
            - Maximizing expands the window to fill the screen
            - Use restore() to return to previous size
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

    def minimize(self, window_id: int) -> BoolResult:
        """
        Minimizes the specified window.

        Args:
            window_id (int): The ID of the window to minimize.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Note:
            - The window must exist in the system
            - Minimizing hides the window in the taskbar
            - Use restore() or activate() to bring it back
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

    def restore(self, window_id: int) -> BoolResult:
        """
        Restores the specified window.

        Args:
            window_id (int): The ID of the window to restore.

        Returns:
            BoolResult: Result object containing success status and error message if any.
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

    def resize(self, window_id: int, width: int, height: int) -> BoolResult:
        """
        Resizes the specified window.

        Args:
            window_id (int): The ID of the window to resize.
            width (int): New width of the window in pixels.
            height (int): New height of the window in pixels.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Note:
            - The window must exist in the system
            - Width and height are in pixels
            - Some windows may have minimum or maximum size constraints
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

    def fullscreen(self, window_id: int) -> BoolResult:
        """
        Makes the specified window fullscreen.

        Args:
            window_id (int): The ID of the window to make fullscreen.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Note:
            - The window must exist in the system
            - Fullscreen mode hides window borders and taskbar
            - Different from maximize_window() which keeps window borders
            - Press F11 or ESC to exit fullscreen in most applications
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
