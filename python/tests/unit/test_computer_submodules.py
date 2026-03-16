#!/usr/bin/env python3
"""
Unit tests for Computer submodule controllers (MouseController, KeyboardController,
WindowManager, ApplicationManager, ScreenController).
Exercises the modular API (session.computer.mouse.*, .keyboard.*, etc.) with mocked _call_mcp_tool.
"""

import json
import unittest
from unittest.mock import MagicMock

from agb.model.response import (
    BoolResult,
    OperationResult,
    WindowListResult,
    WindowInfoResult,
    AppOperationResult,
    ProcessListResult,
    InstalledAppListResult,
)
from agb.modules.computer import (
    Computer,
    MouseButton,
    ScrollDirection,
    MouseController,
    KeyboardController,
    WindowManager,
    ApplicationManager,
    ScreenController,
)


class DummySession:
    """Dummy session for testing."""

    def __init__(self):
        self.session_id = "test_session_id"
        self.client = MagicMock()

    def get_api_key(self) -> str:
        return "test_api_key"

    def get_session_id(self) -> str:
        return self.session_id

    def get_client(self):
        return self.client

    def find_server_for_tool(self, tool_name: str) -> str:
        return "default-server"


class TestMouseController(unittest.TestCase):
    """Tests for MouseController (session.computer.mouse)."""

    def setUp(self):
        self.session = DummySession()
        self.computer = Computer(self.session)
        self.mouse = self.computer.mouse

    def test_click_success(self):
        mock_result = OperationResult(request_id="r1", success=True, data=True)
        self.mouse._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.mouse.click(10, 20)
        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)
        self.mouse._call_mcp_tool.assert_called_once_with(
            "click_mouse", {"x": 10, "y": 20, "button": "left"}
        )

    def test_click_with_button_enum(self):
        mock_result = OperationResult(request_id="r1", success=True, data=True)
        self.mouse._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.mouse.click(10, 20, button=MouseButton.RIGHT)
        self.assertTrue(result.success)
        self.mouse._call_mcp_tool.assert_called_once_with(
            "click_mouse", {"x": 10, "y": 20, "button": "right"}
        )

    def test_click_invalid_button_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.mouse.click(10, 20, button="invalid")
        self.assertIn("Invalid button", str(ctx.exception))

    def test_click_failure(self):
        mock_result = OperationResult(
            request_id="r1", success=False, error_message="tool failed"
        )
        self.mouse._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.mouse.click(10, 20)
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "tool failed")

    def test_click_exception(self):
        self.mouse._call_mcp_tool = MagicMock(side_effect=RuntimeError("network error"))
        result = self.mouse.click(10, 20)
        self.assertFalse(result.success)
        self.assertIn("network error", result.error_message)

    def test_move_success(self):
        mock_result = OperationResult(request_id="r1", success=True, data=True)
        self.mouse._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.mouse.move(100, 200)
        self.assertTrue(result.success)
        self.mouse._call_mcp_tool.assert_called_once_with(
            "move_mouse", {"x": 100, "y": 200}
        )

    def test_move_failure(self):
        mock_result = OperationResult(
            request_id="r1", success=False, error_message="move failed"
        )
        self.mouse._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.mouse.move(100, 200)
        self.assertFalse(result.success)

    def test_drag_success(self):
        mock_result = OperationResult(request_id="r1", success=True, data=True)
        self.mouse._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.mouse.drag(0, 0, 100, 100)
        self.assertTrue(result.success)
        self.mouse._call_mcp_tool.assert_called_once_with(
            "drag_mouse",
            {"from_x": 0, "from_y": 0, "to_x": 100, "to_y": 100, "button": "left"},
        )

    def test_drag_invalid_button_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.mouse.drag(0, 0, 10, 10, button="double_left")
        self.assertIn("Invalid button", str(ctx.exception))

    def test_scroll_success(self):
        mock_result = OperationResult(request_id="r1", success=True, data=True)
        self.mouse._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.mouse.scroll(50, 50, direction=ScrollDirection.DOWN, amount=3)
        self.assertTrue(result.success)
        self.mouse._call_mcp_tool.assert_called_once_with(
            "scroll", {"x": 50, "y": 50, "direction": "down", "amount": 3}
        )

    def test_scroll_invalid_direction_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.mouse.scroll(50, 50, direction="invalid")
        self.assertIn("Invalid direction", str(ctx.exception))

    def test_scroll_failure(self):
        mock_result = OperationResult(
            request_id="r1", success=False, error_message="scroll failed"
        )
        self.mouse._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.mouse.scroll(50, 50)
        self.assertFalse(result.success)

    def test_scroll_exception(self):
        self.mouse._call_mcp_tool = MagicMock(side_effect=Exception("err"))
        result = self.mouse.scroll(50, 50)
        self.assertFalse(result.success)

    def test_get_position_success(self):
        mock_result = OperationResult(
            request_id="r1", success=True, data={"x": 100, "y": 200}
        )
        self.mouse._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.mouse.get_position()
        self.assertTrue(result.success)
        self.assertEqual(result.data, {"x": 100, "y": 200})
        self.mouse._call_mcp_tool.assert_called_once_with("get_cursor_position", {})

    def test_get_position_failure(self):
        mock_result = OperationResult(
            request_id="r1", success=False, error_message="failed"
        )
        self.mouse._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.mouse.get_position()
        self.assertFalse(result.success)


class TestKeyboardController(unittest.TestCase):
    """Tests for KeyboardController (session.computer.keyboard)."""

    def setUp(self):
        self.session = DummySession()
        self.computer = Computer(self.session)
        self.keyboard = self.computer.keyboard

    def test_type_success(self):
        mock_result = OperationResult(request_id="r1", success=True, data=True)
        self.keyboard._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.keyboard.type("hello")
        self.assertTrue(result.success)
        self.keyboard._call_mcp_tool.assert_called_once_with(
            "input_text", {"text": "hello"}
        )

    def test_type_failure(self):
        mock_result = OperationResult(
            request_id="r1", success=False, error_message="failed"
        )
        self.keyboard._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.keyboard.type("hello")
        self.assertFalse(result.success)

    def test_type_exception(self):
        self.keyboard._call_mcp_tool = MagicMock(side_effect=Exception("err"))
        result = self.keyboard.type("hello")
        self.assertFalse(result.success)

    def test_press_success(self):
        mock_result = OperationResult(request_id="r1", success=True, data=True)
        self.keyboard._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.keyboard.press(["Ctrl", "c"])
        self.assertTrue(result.success)
        self.keyboard._call_mcp_tool.assert_called_once_with(
            "press_keys", {"keys": ["Ctrl", "c"], "hold": False}
        )

    def test_press_hold_success(self):
        mock_result = OperationResult(request_id="r1", success=True, data=True)
        self.keyboard._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.keyboard.press(["Shift"], hold=True)
        self.assertTrue(result.success)
        self.keyboard._call_mcp_tool.assert_called_once_with(
            "press_keys", {"keys": ["Shift"], "hold": True}
        )

    def test_press_failure(self):
        mock_result = OperationResult(
            request_id="r1", success=False, error_message="failed"
        )
        self.keyboard._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.keyboard.press(["a"])
        self.assertFalse(result.success)

    def test_release_success(self):
        mock_result = OperationResult(request_id="r1", success=True, data=True)
        self.keyboard._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.keyboard.release(["Ctrl", "c"])
        self.assertTrue(result.success)
        self.keyboard._call_mcp_tool.assert_called_once_with(
            "release_keys", {"keys": ["Ctrl", "c"]}
        )

    def test_release_failure(self):
        mock_result = OperationResult(
            request_id="r1", success=False, error_message="failed"
        )
        self.keyboard._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.keyboard.release(["Ctrl"])
        self.assertFalse(result.success)


class TestWindowManager(unittest.TestCase):
    """Tests for WindowManager (session.computer.window)."""

    def setUp(self):
        self.session = DummySession()
        self.computer = Computer(self.session)
        self.window = self.computer.window

    def test_list_root_windows_success(self):
        windows_data = [{"window_id": 1, "title": "w1"}]
        mock_result = OperationResult(
            request_id="r1", success=True, data=json.dumps(windows_data)
        )
        self.window._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.window.list_root_windows(timeout_ms=5000)
        self.assertIsInstance(result, WindowListResult)
        self.assertTrue(result.success)
        self.assertEqual(len(result.windows), 1)
        self.assertEqual(result.windows[0].window_id, 1)
        self.assertEqual(result.windows[0].title, "w1")

    def test_list_root_windows_success_empty(self):
        mock_result = OperationResult(
            request_id="r1", success=True, data=json.dumps([])
        )
        self.window._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.window.list_root_windows()
        self.assertTrue(result.success)
        self.assertEqual(result.windows, [])

    def test_list_root_windows_failure(self):
        mock_result = OperationResult(
            request_id="r1", success=False, error_message="failed"
        )
        self.window._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.window.list_root_windows()
        self.assertFalse(result.success)
        self.assertEqual(result.windows, [])

    def test_list_root_windows_json_error(self):
        mock_result = OperationResult(request_id="r1", success=True, data="not json")
        self.window._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.window.list_root_windows()
        self.assertFalse(result.success)
        self.assertIn("parse", result.error_message)

    def test_get_active_window_success(self):
        win_data = {"window_id": 42, "title": "active"}
        mock_result = OperationResult(
            request_id="r1", success=True, data=json.dumps(win_data)
        )
        self.window._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.window.get_active_window()
        self.assertIsInstance(result, WindowInfoResult)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.window)
        self.assertEqual(result.window.window_id, 42)

    def test_get_active_window_failure(self):
        mock_result = OperationResult(
            request_id="r1", success=False, error_message="failed"
        )
        self.window._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.window.get_active_window()
        self.assertFalse(result.success)
        self.assertIsNone(result.window)

    def test_activate_success(self):
        mock_result = OperationResult(request_id="r1", success=True, data=True)
        self.window._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.window.activate(123)
        self.assertTrue(result.success)
        self.window._call_mcp_tool.assert_called_once_with(
            "activate_window", {"window_id": 123}
        )

    def test_close_success(self):
        mock_result = OperationResult(request_id="r1", success=True, data=True)
        self.window._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.window.close(456)
        self.assertTrue(result.success)

    def test_maximize_minimize_restore_success(self):
        mock_result = OperationResult(request_id="r1", success=True, data=True)
        self.window._call_mcp_tool = MagicMock(return_value=mock_result)
        self.assertTrue(self.window.maximize(1).success)
        self.assertTrue(self.window.minimize(1).success)
        self.assertTrue(self.window.restore(1).success)

    def test_resize_success(self):
        mock_result = OperationResult(request_id="r1", success=True, data=True)
        self.window._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.window.resize(1, 800, 600)
        self.assertTrue(result.success)
        self.window._call_mcp_tool.assert_called_once_with(
            "resize_window", {"window_id": 1, "width": 800, "height": 600}
        )

    def test_fullscreen_success(self):
        mock_result = OperationResult(request_id="r1", success=True, data=True)
        self.window._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.window.fullscreen(1)
        self.assertTrue(result.success)

    def test_focus_mode_success(self):
        mock_result = OperationResult(request_id="r1", success=True, data=True)
        self.window._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.window.focus_mode(True)
        self.assertTrue(result.success)
        self.window._call_mcp_tool.assert_called_once_with("focus_mode", {"on": True})

    def test_focus_mode_failure(self):
        mock_result = OperationResult(
            request_id="r1", success=False, error_message="failed"
        )
        self.window._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.window.focus_mode(False)
        self.assertFalse(result.success)


class TestApplicationManager(unittest.TestCase):
    """Tests for ApplicationManager (session.computer.app)."""

    def setUp(self):
        self.session = DummySession()
        self.computer = Computer(self.session)
        self.app = self.computer.app

    def test_start_success(self):
        processes_data = [{"pname": "app", "pid": 1234, "cmdline": "app.exe"}]
        mock_result = OperationResult(
            request_id="r1", success=True, data=json.dumps(processes_data)
        )
        self.app._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.app.start("app.exe", work_directory="/tmp")
        self.assertIsInstance(result, ProcessListResult)
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0].pid, 1234)

    def test_start_failure(self):
        mock_result = OperationResult(
            request_id="r1", success=False, error_message="failed"
        )
        self.app._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.app.start("app.exe")
        self.assertFalse(result.success)

    def test_start_json_error(self):
        mock_result = OperationResult(request_id="r1", success=True, data="not json")
        self.app._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.app.start("app.exe")
        self.assertFalse(result.success)
        self.assertIn("parse", result.error_message)

    def test_stop_by_pname_success(self):
        mock_result = OperationResult(request_id="r1", success=True)
        self.app._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.app.stop_by_pname("app.exe")
        self.assertIsInstance(result, AppOperationResult)
        self.assertTrue(result.success)

    def test_stop_by_pname_failure(self):
        mock_result = OperationResult(
            request_id="r1", success=False, error_message="failed"
        )
        self.app._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.app.stop_by_pname("app.exe")
        self.assertFalse(result.success)

    def test_stop_by_pid_success(self):
        mock_result = OperationResult(request_id="r1", success=True)
        self.app._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.app.stop_by_pid(1234)
        self.assertTrue(result.success)

    def test_stop_by_cmd_success(self):
        mock_result = OperationResult(request_id="r1", success=True)
        self.app._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.app.stop_by_cmd("kill -9 1234")
        self.assertTrue(result.success)

    def test_list_installed_success(self):
        apps_data = [{"name": "App1", "start_cmd": "app1.exe"}]
        mock_result = OperationResult(
            request_id="r1", success=True, data=json.dumps(apps_data)
        )
        self.app._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.app.list_installed(start_menu=True, desktop=False)
        self.assertIsInstance(result, InstalledAppListResult)
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0].name, "App1")

    def test_list_installed_failure(self):
        mock_result = OperationResult(
            request_id="r1", success=False, error_message="failed"
        )
        self.app._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.app.list_installed()
        self.assertFalse(result.success)

    def test_get_visible_success(self):
        procs_data = [{"pname": "chrome", "pid": 999, "cmdline": "chrome"}]
        mock_result = OperationResult(
            request_id="r1", success=True, data=json.dumps(procs_data)
        )
        self.app._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.app.get_visible()
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 1)

    def test_get_visible_failure(self):
        mock_result = OperationResult(
            request_id="r1", success=False, error_message="failed"
        )
        self.app._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.app.get_visible()
        self.assertFalse(result.success)


class TestScreenController(unittest.TestCase):
    """Tests for ScreenController (session.computer.screen)."""

    def setUp(self):
        self.session = DummySession()
        self.computer = Computer(self.session)
        self.screen = self.computer.screen

    def test_capture_success(self):
        mock_result = OperationResult(
            request_id="r1", success=True, data="https://oss.example/shot.png"
        )
        self.screen._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.screen.capture()
        self.assertTrue(result.success)
        self.assertEqual(result.data, "https://oss.example/shot.png")
        self.screen._call_mcp_tool.assert_called_once_with("system_screenshot", {})

    def test_capture_failure(self):
        mock_result = OperationResult(
            request_id="r1", success=False, error_message="failed"
        )
        self.screen._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.screen.capture()
        self.assertFalse(result.success)

    def test_capture_exception(self):
        self.screen._call_mcp_tool = MagicMock(side_effect=Exception("err"))
        result = self.screen.capture()
        self.assertFalse(result.success)

    def test_get_size_success_dict(self):
        size_data = {"width": 1920, "height": 1080, "dpiScalingFactor": 1.0}
        mock_result = OperationResult(request_id="r1", success=True, data=size_data)
        self.screen._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.screen.get_size()
        self.assertTrue(result.success)
        self.assertEqual(result.data, size_data)
        self.screen._call_mcp_tool.assert_called_once_with("get_screen_size", {})

    def test_get_size_success_string(self):
        size_data = {"width": 1920, "height": 1080}
        mock_result = OperationResult(
            request_id="r1", success=True, data=json.dumps(size_data)
        )
        self.screen._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.screen.get_size()
        self.assertTrue(result.success)
        self.assertEqual(result.data, size_data)

    def test_get_size_failure(self):
        mock_result = OperationResult(
            request_id="r1", success=False, error_message="failed"
        )
        self.screen._call_mcp_tool = MagicMock(return_value=mock_result)
        result = self.screen.get_size()
        self.assertFalse(result.success)

    def test_get_size_exception(self):
        self.screen._call_mcp_tool = MagicMock(side_effect=Exception("err"))
        result = self.screen.get_size()
        self.assertFalse(result.success)
