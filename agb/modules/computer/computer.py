"""
Computer module main class - container for all computer automation controllers.
"""

import warnings
from typing import TYPE_CHECKING

from agb.api.base_service import BaseService
from agb.modules.computer.mouse import MouseController
from agb.modules.computer.keyboard import KeyboardController
from agb.modules.computer.window import WindowManager
from agb.modules.computer.app import ApplicationManager
from agb.modules.computer.screen import ScreenController

if TYPE_CHECKING:
    from agb.session import Session


class Computer(BaseService):
    """
    Handles computer UI automation operations in the AGB cloud environment.

    This class acts as a container for specialized controllers:
    - mouse: Mouse operations (click, move, drag, scroll)
    - keyboard: Keyboard operations (type, press, release)
    - window: Window management (list, activate, close, resize, etc.)
    - app: Application management (start, stop, list installed/visible)
    - screen: Screen operations (capture, size)
    """

    def __init__(self, session: "Session"):
        """
        Initialize Computer with all sub-controllers.

        Args:
            session: The session instance.
        """
        super().__init__(session)

        # Initialize sub-controllers
        self.mouse = MouseController(session)
        self.keyboard = KeyboardController(session)
        self.window = WindowManager(session)
        self.app = ApplicationManager(session)
        self.screen = ScreenController(session)

    # ========== Deprecated methods for backward compatibility ==========
    # These methods will be removed in v0.11.0

    def click_mouse(self, x: int, y: int, button=None, **kwargs):
        """Deprecated: Use computer.mouse.click() instead."""
        warnings.warn(
            "computer.click_mouse() is deprecated. Use computer.mouse.click() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.modules.computer import MouseButton
        from agb.model.response import BoolResult
        from agb.logger import log_operation_start, log_operation_success, log_operation_error

        if button is None:
            button = kwargs.get('button', MouseButton.LEFT)

        # Call MCP tool directly for backward compatibility
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

    def move_mouse(self, x: int, y: int, **kwargs):
        """Deprecated: Use computer.mouse.move() instead."""
        warnings.warn(
            "computer.move_mouse() is deprecated. Use computer.mouse.move() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.model.response import BoolResult
        from agb.logger import log_operation_start, log_operation_success, log_operation_error
        log_operation_start("Computer.move_mouse", f"X={x}, Y={y}")
        try:
            args = {"x": x, "y": y}
            result = self._call_mcp_tool("move_mouse", args)
            if result.success:
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                return BoolResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to move mouse")
        except Exception as e:
            return BoolResult(request_id="", success=False, error_message=f"Failed to move mouse: {e}")

    def drag_mouse(self, from_x: int, from_y: int, to_x: int, to_y: int, button=None, **kwargs):
        """Deprecated: Use computer.mouse.drag() instead."""
        warnings.warn(
            "computer.drag_mouse() is deprecated. Use computer.mouse.drag() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.modules.computer import MouseButton
        from agb.model.response import BoolResult
        from agb.logger import log_operation_start, log_operation_error
        button_str = (button.value if isinstance(button, MouseButton) else button) if button else kwargs.get('button', 'left')
        valid_buttons = ["left", "right", "middle"]
        if button_str not in valid_buttons:
            raise ValueError(f"Invalid button '{button_str}'. Must be one of {valid_buttons}")
        log_operation_start("Computer.drag_mouse", f"FromX={from_x}, FromY={from_y}, ToX={to_x}, ToY={to_y}, Button={button_str}")
        try:
            args = {"from_x": from_x, "from_y": from_y, "to_x": to_x, "to_y": to_y, "button": button_str}
            result = self._call_mcp_tool("drag_mouse", args)
            if result.success:
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                return BoolResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to drag mouse")
        except Exception as e:
            return BoolResult(request_id="", success=False, error_message=f"Failed to drag mouse: {e}")

    def scroll(self, x: int, y: int, direction=None, amount: int = 1, **kwargs):
        """Deprecated: Use computer.mouse.scroll() instead."""
        warnings.warn(
            "computer.scroll() is deprecated. Use computer.mouse.scroll() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.modules.computer import ScrollDirection
        from agb.model.response import BoolResult
        from agb.logger import log_operation_start, log_operation_error
        direction_str = (direction.value if isinstance(direction, ScrollDirection) else direction) if direction else kwargs.get('direction', ScrollDirection.UP.value)
        valid_directions = [d.value for d in ScrollDirection]
        if direction_str not in valid_directions:
            raise ValueError(f"Invalid direction '{direction_str}'. Must be one of {valid_directions}")
        log_operation_start("Computer.scroll", f"X={x}, Y={y}, Direction={direction_str}, Amount={amount}")
        try:
            args = {"x": x, "y": y, "direction": direction_str, "amount": amount}
            result = self._call_mcp_tool("scroll", args)
            if result.success:
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                return BoolResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to scroll")
        except Exception as e:
            return BoolResult(request_id="", success=False, error_message=f"Failed to scroll: {e}")

    def get_cursor_position(self):
        """Deprecated: Use computer.mouse.get_position() instead."""
        warnings.warn(
            "computer.get_cursor_position() is deprecated. Use computer.mouse.get_position() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.model.response import OperationResult
        try:
            args = {}
            result = self._call_mcp_tool("get_cursor_position", args)
            if result.success:
                return OperationResult(request_id=result.request_id, success=True, data=result.data)
            else:
                return OperationResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to get cursor position")
        except Exception as e:
            return OperationResult(request_id="", success=False, error_message=f"Failed to get cursor position: {e}")

    def input_text(self, text: str, **kwargs):
        """Deprecated: Use computer.keyboard.type() instead."""
        warnings.warn(
            "computer.input_text() is deprecated. Use computer.keyboard.type() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.model.response import BoolResult
        from agb.logger import log_operation_start, log_operation_success, log_operation_error
        log_operation_start("Computer.input_text", f"Text={text}")
        try:
            args = {"text": text}
            result = self._call_mcp_tool("input_text", args)
            if result.success:
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                return BoolResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to input text")
        except Exception as e:
            return BoolResult(request_id="", success=False, error_message=f"Failed to input text: {e}")

    def press_keys(self, keys, hold: bool = False, **kwargs):
        """Deprecated: Use computer.keyboard.press() instead."""
        warnings.warn(
            "computer.press_keys() is deprecated. Use computer.keyboard.press() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.model.response import BoolResult
        from agb.logger import log_operation_start, log_operation_success, log_operation_error
        log_operation_start("Computer.press_keys", f"Keys={keys}, Hold={hold}")
        try:
            args = {"keys": keys, "hold": hold}
            result = self._call_mcp_tool("press_keys", args)
            if result.success:
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                return BoolResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to press keys")
        except Exception as e:
            return BoolResult(request_id="", success=False, error_message=f"Failed to press keys: {e}")

    def release_keys(self, keys, **kwargs):
        """Deprecated: Use computer.keyboard.release() instead."""
        warnings.warn(
            "computer.release_keys() is deprecated. Use computer.keyboard.release() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.model.response import BoolResult
        try:
            args = {"keys": keys}
            result = self._call_mcp_tool("release_keys", args)
            if result.success:
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                return BoolResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to release keys")
        except Exception as e:
            return BoolResult(request_id="", success=False, error_message=f"Failed to release keys: {e}")

    def list_root_windows(self, timeout_ms: int = 3000, **kwargs):
        """Deprecated: Use computer.window.list_root_windows() instead."""
        warnings.warn(
            "computer.list_root_windows() is deprecated. Use computer.window.list_root_windows() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        import json
        from agb.model.response import WindowListResult
        from agb.modules.computer import Window
        try:
            args = {"timeout_ms": timeout_ms}
            result = self._call_mcp_tool("list_root_windows", args)
            if result.success:
                windows = []
                if result.data:
                    try:
                        windows_data = json.loads(result.data)
                        for window_data in windows_data:
                            windows.append(Window._from_dict(window_data))
                    except json.JSONDecodeError as e:
                        return WindowListResult(request_id=result.request_id, success=False, windows=[], error_message=f"Failed to parse windows JSON: {e}")
                return WindowListResult(request_id=result.request_id, success=True, windows=windows)
            else:
                return WindowListResult(request_id=result.request_id, success=False, windows=[], error_message=result.error_message or "Failed to list root windows")
        except Exception as e:
            return WindowListResult(request_id="", success=False, windows=[], error_message=f"Failed to list root windows: {e}")

    def get_active_window(self, **kwargs):
        """Deprecated: Use computer.window.get_active_window() instead."""
        warnings.warn(
            "computer.get_active_window() is deprecated. Use computer.window.get_active_window() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        import json
        from agb.model.response import WindowInfoResult
        from agb.modules.computer import Window
        try:
            args = {}
            result = self._call_mcp_tool("get_active_window", args)
            if result.success:
                window = None
                if result.data:
                    try:
                        window_data = json.loads(result.data)
                        window = Window._from_dict(window_data)
                    except json.JSONDecodeError as e:
                        return WindowInfoResult(request_id=result.request_id, success=False, window=None, error_message=f"Failed to parse window JSON: {e}")
                return WindowInfoResult(request_id=result.request_id, success=True, window=window)
            else:
                return WindowInfoResult(request_id=result.request_id, success=False, window=None, error_message=result.error_message or "Failed to get active window")
        except Exception as e:
            return WindowInfoResult(request_id="", success=False, window=None, error_message=f"Failed to get active window: {e}")

    def activate_window(self, window_id: int, **kwargs):
        """Deprecated: Use computer.window.activate() instead."""
        warnings.warn(
            "computer.activate_window() is deprecated. Use computer.window.activate() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.model.response import BoolResult
        from agb.logger import log_operation_start, log_operation_success, log_operation_error
        log_operation_start("Computer.activate_window", f"WindowId={window_id}")
        try:
            args = {"window_id": window_id}
            result = self._call_mcp_tool("activate_window", args)
            if result.success:
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                return BoolResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to activate window")
        except Exception as e:
            return BoolResult(request_id="", success=False, error_message=f"Failed to activate window: {e}")

    def close_window(self, window_id: int, **kwargs):
        """Deprecated: Use computer.window.close() instead."""
        warnings.warn(
            "computer.close_window() is deprecated. Use computer.window.close() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.model.response import BoolResult
        from agb.logger import log_operation_start, log_operation_success
        log_operation_start("Computer.close_window", f"WindowId={window_id}")
        try:
            args = {"window_id": window_id}
            result = self._call_mcp_tool("close_window", args)
            if result.success:
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                return BoolResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to close window")
        except Exception as e:
            return BoolResult(request_id="", success=False, error_message=f"Failed to close window: {e}")

    def maximize_window(self, window_id: int, **kwargs):
        """Deprecated: Use computer.window.maximize() instead."""
        warnings.warn(
            "computer.maximize_window() is deprecated. Use computer.window.maximize() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.model.response import BoolResult
        try:
            args = {"window_id": window_id}
            result = self._call_mcp_tool("maximize_window", args)
            if result.success:
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                return BoolResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to maximize window")
        except Exception as e:
            return BoolResult(request_id="", success=False, error_message=f"Failed to maximize window: {e}")

    def minimize_window(self, window_id: int, **kwargs):
        """Deprecated: Use computer.window.minimize() instead."""
        warnings.warn(
            "computer.minimize_window() is deprecated. Use computer.window.minimize() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.model.response import BoolResult
        try:
            args = {"window_id": window_id}
            result = self._call_mcp_tool("minimize_window", args)
            if result.success:
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                return BoolResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to minimize window")
        except Exception as e:
            return BoolResult(request_id="", success=False, error_message=f"Failed to minimize window: {e}")

    def restore_window(self, window_id: int, **kwargs):
        """Deprecated: Use computer.window.restore() instead."""
        warnings.warn(
            "computer.restore_window() is deprecated. Use computer.window.restore() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.model.response import BoolResult
        try:
            args = {"window_id": window_id}
            result = self._call_mcp_tool("restore_window", args)
            if result.success:
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                return BoolResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to restore window")
        except Exception as e:
            return BoolResult(request_id="", success=False, error_message=f"Failed to restore window: {e}")

    def resize_window(self, window_id: int, width: int, height: int, **kwargs):
        """Deprecated: Use computer.window.resize() instead."""
        warnings.warn(
            "computer.resize_window() is deprecated. Use computer.window.resize() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.model.response import BoolResult
        from agb.logger import log_operation_start, log_operation_success
        log_operation_start("Computer.resize_window", f"WindowId={window_id}, Width={width}, Height={height}")
        try:
            args = {"window_id": window_id, "width": width, "height": height}
            result = self._call_mcp_tool("resize_window", args)
            if result.success:
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                return BoolResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to resize window")
        except Exception as e:
            return BoolResult(request_id="", success=False, error_message=f"Failed to resize window: {e}")

    def fullscreen_window(self, window_id: int, **kwargs):
        """Deprecated: Use computer.window.fullscreen() instead."""
        warnings.warn(
            "computer.fullscreen_window() is deprecated. Use computer.window.fullscreen() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.model.response import BoolResult
        try:
            args = {"window_id": window_id}
            result = self._call_mcp_tool("fullscreen_window", args)
            if result.success:
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                return BoolResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to fullscreen window")
        except Exception as e:
            return BoolResult(request_id="", success=False, error_message=f"Failed to fullscreen window: {e}")

    def focus_mode(self, on: bool, **kwargs):
        """Deprecated: Use computer.window.focus_mode() instead."""
        warnings.warn(
            "computer.focus_mode() is deprecated. Use computer.window.focus_mode() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.model.response import BoolResult
        try:
            args = {"on": on}
            result = self._call_mcp_tool("focus_mode", args)
            if result.success:
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                return BoolResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to toggle focus mode")
        except Exception as e:
            return BoolResult(request_id="", success=False, error_message=f"Failed to toggle focus mode: {e}")

    def get_installed_apps(self, start_menu: bool = True, desktop: bool = False, ignore_system_apps: bool = True, **kwargs):
        """Deprecated: Use computer.app.list_installed() instead."""
        warnings.warn(
            "computer.get_installed_apps() is deprecated. Use computer.app.list_installed() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        import json
        from agb.model.response import InstalledAppListResult
        from agb.modules.computer import InstalledApp
        try:
            args = {"start_menu": start_menu, "desktop": desktop, "ignore_system_apps": ignore_system_apps}
            result = self._call_mcp_tool("get_installed_apps", args)
            if not result.success:
                return InstalledAppListResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to get installed apps")
            try:
                apps_json = json.loads(result.data)
                installed_apps = [InstalledApp._from_dict(app_data) for app_data in apps_json]
                return InstalledAppListResult(request_id=result.request_id, success=True, data=installed_apps)
            except json.JSONDecodeError as e:
                return InstalledAppListResult(request_id=result.request_id, success=False, error_message=f"Failed to parse applications JSON: {e}")
        except Exception as e:
            return InstalledAppListResult(success=False, error_message=f"Failed to get installed apps: {e}")

    def list_visible_apps(self, **kwargs):
        """Deprecated: Use computer.app.get_visible() instead."""
        warnings.warn(
            "computer.list_visible_apps() is deprecated. Use computer.app.get_visible() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        import json
        from agb.model.response import ProcessListResult
        from agb.modules.computer import Process
        try:
            result = self._call_mcp_tool("list_visible_apps", {})
            if not result.success:
                return ProcessListResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to list visible apps")
            try:
                processes_json = json.loads(result.data)
                processes = [Process._from_dict(process_data) for process_data in processes_json]
                return ProcessListResult(request_id=result.request_id, success=True, data=processes)
            except json.JSONDecodeError as e:
                return ProcessListResult(request_id=result.request_id, success=False, error_message=f"Failed to parse processes JSON: {e}")
        except Exception as e:
            return ProcessListResult(success=False, error_message=f"Failed to list visible apps: {e}")

    def start_app(self, start_cmd: str, work_directory: str = "", activity: str = "", **kwargs):
        """Deprecated: Use computer.app.start() instead."""
        warnings.warn(
            "computer.start_app() is deprecated. Use computer.app.start() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        import json
        from agb.model.response import ProcessListResult
        from agb.modules.computer import Process
        from agb.logger import log_operation_start, log_operation_success, log_operation_error
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
            if not result.success:
                return ProcessListResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to start app")
            try:
                processes_json = json.loads(result.data)
                processes = [Process._from_dict(process_data) for process_data in processes_json]
                log_operation_success("Computer.start_app", f"StartCmd={start_cmd}, ProcessesCount={len(processes)}, RequestId={result.request_id}")
                return ProcessListResult(request_id=result.request_id, success=True, data=processes)
            except json.JSONDecodeError as e:
                return ProcessListResult(request_id=result.request_id, success=False, error_message=f"Failed to parse processes JSON: {e}")
        except Exception as e:
            return ProcessListResult(success=False, error_message=f"Failed to start app: {e}")

    def stop_app_by_pname(self, pname: str, **kwargs):
        """Deprecated: Use computer.app.stop_by_pname() instead."""
        warnings.warn(
            "computer.stop_app_by_pname() is deprecated. Use computer.app.stop_by_pname() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.model.response import AppOperationResult
        from agb.logger import log_operation_start, log_operation_success, log_operation_error
        log_operation_start("Computer.stop_app_by_pname", f"PName={pname}")
        try:
            args = {"pname": pname}
            result = self._call_mcp_tool("stop_app_by_pname", args)
            if result.success:
                log_operation_success("Computer.stop_app_by_pname", f"PName={pname}, RequestId={result.request_id}")
            else:
                log_operation_error("Computer.stop_app_by_pname", result.error_message or "Failed to stop app by pname")
            return AppOperationResult(request_id=result.request_id, success=result.success, error_message=result.error_message or ("Failed to stop app by pname" if not result.success else ""))
        except Exception as e:
            return AppOperationResult(success=False, error_message=f"Failed to stop app by pname: {e}")

    def stop_app_by_pid(self, pid: int, **kwargs):
        """Deprecated: Use computer.app.stop_by_pid() instead."""
        warnings.warn(
            "computer.stop_app_by_pid() is deprecated. Use computer.app.stop_by_pid() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.model.response import AppOperationResult
        from agb.logger import log_operation_start, log_operation_success, log_operation_error
        log_operation_start("Computer.stop_app_by_pid", f"PID={pid}")
        try:
            args = {"pid": pid}
            result = self._call_mcp_tool("stop_app_by_pid", args)
            if result.success:
                log_operation_success("Computer.stop_app_by_pid", f"PID={pid}, RequestId={result.request_id}")
            else:
                log_operation_error("Computer.stop_app_by_pid", result.error_message or "Failed to stop app by pid")
            return AppOperationResult(request_id=result.request_id, success=result.success, error_message=result.error_message or ("Failed to stop app by pid" if not result.success else ""))
        except Exception as e:
            return AppOperationResult(success=False, error_message=f"Failed to stop app by pid: {e}")

    def stop_app_by_cmd(self, stop_cmd: str, **kwargs):
        """Deprecated: Use computer.app.stop_by_cmd() instead."""
        warnings.warn(
            "computer.stop_app_by_cmd() is deprecated. Use computer.app.stop_by_cmd() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.model.response import AppOperationResult
        from agb.logger import log_operation_start, log_operation_success, log_operation_error
        log_operation_start("Computer.stop_app_by_cmd", f"StopCmd={stop_cmd}")
        try:
            args = {"stop_cmd": stop_cmd}
            result = self._call_mcp_tool("stop_app_by_cmd", args)
            if result.success:
                log_operation_success("Computer.stop_app_by_cmd", f"StopCmd={stop_cmd}, RequestId={result.request_id}")
            else:
                log_operation_error("Computer.stop_app_by_cmd", result.error_message or "Failed to stop app by cmd")
            return AppOperationResult(request_id=result.request_id, success=result.success, error_message=result.error_message or ("Failed to stop app by cmd" if not result.success else ""))
        except Exception as e:
            return AppOperationResult(success=False, error_message=f"Failed to stop app by cmd: {e}")

    def get_screen_size(self, **kwargs):
        """Deprecated: Use computer.screen.get_size() instead."""
        warnings.warn(
            "computer.get_screen_size() is deprecated. Use computer.screen.get_size() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.model.response import OperationResult
        from agb.logger import log_operation_start, log_operation_success, log_operation_error
        log_operation_start("Computer.get_screen_size", "")
        try:
            args = {}
            result = self._call_mcp_tool("get_screen_size", args)
            if result.success:
                screen_data = result.data if isinstance(result.data, dict) else {}
                log_operation_success("Computer.get_screen_size", f"Width={screen_data.get('width', 'N/A')}, Height={screen_data.get('height', 'N/A')}, RequestId={result.request_id}")
                return OperationResult(request_id=result.request_id, success=True, data=result.data)
            else:
                return OperationResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to get screen size")
        except Exception as e:
            return OperationResult(request_id="", success=False, error_message=f"Failed to get screen size: {e}")

    def screenshot(self, **kwargs):
        """Deprecated: Use computer.screen.capture() instead."""
        warnings.warn(
            "computer.screenshot() is deprecated. Use computer.screen.capture() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        from agb.model.response import OperationResult
        from agb.logger import log_operation_start, log_operation_success, log_operation_error
        log_operation_start("Computer.screenshot", "")
        try:
            args = {}
            result = self._call_mcp_tool("system_screenshot", args)
            if result.success:
                log_operation_success("Computer.screenshot", f"RequestId={result.request_id}, ImageUrl={result.data if result.data else 'None'}")
                return OperationResult(request_id=result.request_id, success=True, data=result.data)
            else:
                return OperationResult(request_id=result.request_id, success=False, error_message=result.error_message or "Failed to take screenshot")
        except Exception as e:
            return OperationResult(request_id="", success=False, error_message=f"Failed to take screenshot: {e}")
