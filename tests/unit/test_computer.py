#!/usr/bin/env python3
"""
Unit tests for Computer module in AGB SDK.
Tests computer UI automation functionality with success and failure scenarios.
"""

import unittest
from unittest.mock import MagicMock
import json

from agb.modules.computer import Computer, MouseButton, ScrollDirection, Window, Process, InstalledApp
from agb.model.response import BoolResult, OperationResult, WindowListResult, WindowInfoResult, AppOperationResult, ProcessListResult, InstalledAppListResult

class DummySession:
    """Dummy session class for testing."""

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

class TestComputer(unittest.TestCase):
    """Test Computer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.session = DummySession()
        self.computer = Computer(self.session)

    # Mouse Operations Tests
    def test_click_mouse_success(self):
        """Test successful mouse click."""
        # Mock the _call_mcp_tool response
        mock_result = OperationResult(
            request_id="req-123",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        # Execute click
        result = self.computer.click_mouse(100, 200)

        # Assertions
        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)
        self.assertTrue(result.data)
        self.assertEqual(result.request_id, "req-123")
        self.computer._call_mcp_tool.assert_called_once_with(
            "click_mouse",
            {"x": 100, "y": 200, "button": "left"}
        )

    def test_click_mouse_with_button(self):
        """Test mouse click with specific button."""
        mock_result = OperationResult(
            request_id="req-456",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.click_mouse(100, 200, button="right")

        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with(
            "click_mouse",
            {"x": 100, "y": 200, "button": "right"}
        )

    def test_click_mouse_with_enum(self):
        """Test mouse click with MouseButton enum."""
        mock_result = OperationResult(
            request_id="req-enum",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.click_mouse(100, 200, button=MouseButton.RIGHT)

        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with(
            "click_mouse",
            {"x": 100, "y": 200, "button": "right"}
        )

    def test_click_mouse_double_left(self):
        """Test mouse double click."""
        mock_result = OperationResult(
            request_id="req-double",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.click_mouse(100, 200, button=MouseButton.DOUBLE_LEFT)

        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with(
            "click_mouse",
            {"x": 100, "y": 200, "button": "double_left"}
        )

    def test_click_mouse_invalid_button(self):
        """Test mouse click with invalid button."""
        with self.assertRaises(ValueError) as context:
            self.computer.click_mouse(100, 200, button="invalid")

        self.assertIn("Invalid button", str(context.exception))

    def test_move_mouse_success(self):
        """Test successful mouse move."""
        mock_result = OperationResult(
            request_id="req-move",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.move_mouse(150, 250)

        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)
        self.assertTrue(result.data)
        self.computer._call_mcp_tool.assert_called_once_with(
            "move_mouse",
            {"x": 150, "y": 250}
        )

    def test_drag_mouse_success(self):
        """Test successful mouse drag."""
        mock_result = OperationResult(
            request_id="req-drag",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.drag_mouse(100, 100, 200, 200)

        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with(
            "drag_mouse",
            {
                "from_x": 100, "from_y": 100,
                "to_x": 200, "to_y": 200,
                "button": "left"
            }
        )

    def test_drag_mouse_with_enum(self):
        """Test drag mouse with MouseButton enum."""
        mock_result = OperationResult(
            request_id="req-drag-enum",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.drag_mouse(100, 100, 200, 200, button=MouseButton.MIDDLE)

        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with(
            "drag_mouse",
            {
                "from_x": 100, "from_y": 100,
                "to_x": 200, "to_y": 200,
                "button": "middle"
            }
        )

    def test_drag_mouse_invalid_button(self):
        """Test drag mouse with invalid button."""
        with self.assertRaises(ValueError) as context:
            self.computer.drag_mouse(100, 100, 200, 200, button="double_left")

        self.assertIn("Invalid button", str(context.exception))

    def test_scroll_success(self):
        """Test successful scroll."""
        mock_result = OperationResult(
            request_id="req-scroll",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.scroll(300, 300)

        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with(
            "scroll",
            {"x": 300, "y": 300, "direction": "up", "amount": 1}
        )

    def test_scroll_with_params(self):
        """Test scroll with custom parameters."""
        mock_result = OperationResult(
            request_id="req-scroll-params",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.scroll(300, 300, direction="down", amount=3)

        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with(
            "scroll",
            {"x": 300, "y": 300, "direction": "down", "amount": 3}
        )

    def test_scroll_with_enum(self):
        """Test scroll with ScrollDirection enum."""
        mock_result = OperationResult(
            request_id="req-scroll-enum",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.scroll(300, 300, direction=ScrollDirection.DOWN, amount=5)

        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with(
            "scroll",
            {"x": 300, "y": 300, "direction": "down", "amount": 5}
        )

    def test_scroll_invalid_direction(self):
        """Test scroll with invalid direction."""
        with self.assertRaises(ValueError) as context:
            self.computer.scroll(100, 100, direction="invalid")

        self.assertIn("Invalid direction", str(context.exception))

    def test_get_cursor_position_success(self):
        """Test successful cursor position retrieval."""
        mock_result = OperationResult(
            request_id="req-cursor",
            success=True,
            data={"x": 150, "y": 250},
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.get_cursor_position()

        self.assertIsInstance(result, OperationResult)
        self.assertTrue(result.success)
        self.assertEqual(result.data, {"x": 150, "y": 250})
        self.computer._call_mcp_tool.assert_called_once_with("get_cursor_position", {})

    # Error Handling Tests
    def test_click_mouse_mcp_failure(self):
        """Test mouse click when MCP tool fails."""
        mock_result = OperationResult(
            request_id="req-fail",
            success=False,
            error_message="MCP tool failed",
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.click_mouse(100, 200)

        self.assertIsInstance(result, BoolResult)
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "MCP tool failed")

    def test_click_mouse_exception(self):
        """Test mouse click when exception occurs."""
        self.computer._call_mcp_tool = MagicMock(side_effect=Exception("Network error"))

        result = self.computer.click_mouse(100, 200)

        self.assertIsInstance(result, BoolResult)
        self.assertFalse(result.success)
        self.assertIn("Failed to click mouse", result.error_message)
        self.assertIn("Network error", result.error_message)

    def test_move_mouse_failure(self):
        """Test mouse move when MCP tool fails."""
        mock_result = OperationResult(
            request_id="req-move-fail",
            success=False,
            error_message="Move failed",
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.move_mouse(150, 250)

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Move failed")

    def test_drag_mouse_exception(self):
        """Test drag mouse when exception occurs."""
        self.computer._call_mcp_tool = MagicMock(side_effect=Exception("Drag error"))

        result = self.computer.drag_mouse(100, 100, 200, 200)

        self.assertFalse(result.success)
        self.assertIn("Failed to drag mouse", result.error_message)

    def test_scroll_exception(self):
        """Test scroll when exception occurs."""
        self.computer._call_mcp_tool = MagicMock(side_effect=Exception("Scroll error"))

        result = self.computer.scroll(300, 300)

        self.assertFalse(result.success)
        self.assertIn("Failed to scroll", result.error_message)

    def test_get_cursor_position_failure(self):
        """Test cursor position when MCP tool fails."""
        mock_result = OperationResult(
            request_id="req-cursor-fail",
            success=False,
            error_message="Cursor position failed",
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.get_cursor_position()

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Cursor position failed")

    # Test various mouse button combinations
    def test_various_mouse_buttons(self):
        """Test various mouse button types."""
        buttons = [
            (MouseButton.LEFT, "left"),
            (MouseButton.RIGHT, "right"),
            (MouseButton.MIDDLE, "middle"),
            (MouseButton.DOUBLE_LEFT, "double_left"),
        ]

        for button_enum, button_str in buttons:
            with self.subTest(button=button_enum):
                mock_result = OperationResult(
                    request_id=f"req-{button_str}",
                    success=True,
                    data=True,
                )
                self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

                result = self.computer.click_mouse(100, 100, button=button_enum)

                self.assertTrue(result.success)
                self.computer._call_mcp_tool.assert_called_with(
                    "click_mouse",
                    {"x": 100, "y": 100, "button": button_str}
                )

    # Test various scroll directions
    def test_various_scroll_directions(self):
        """Test various scroll directions."""
        directions = [
            (ScrollDirection.UP, "up"),
            (ScrollDirection.DOWN, "down"),
            (ScrollDirection.LEFT, "left"),
            (ScrollDirection.RIGHT, "right"),
        ]

        for direction_enum, direction_str in directions:
            with self.subTest(direction=direction_enum):
                mock_result = OperationResult(
                    request_id=f"req-{direction_str}",
                    success=True,
                    data=True,
                )
                self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

                result = self.computer.scroll(100, 100, direction=direction_enum)

                self.assertTrue(result.success)
                self.computer._call_mcp_tool.assert_called_with(
                    "scroll",
                    {"x": 100, "y": 100, "direction": direction_str, "amount": 1}
                )

    # Screen Operations Tests
    def test_get_screen_size_success(self):
        """Test successful screen size retrieval."""
        mock_result = OperationResult(
            request_id="req-screen-size",
            success=True,
            data={"width": 1920, "height": 1080, "dpiScalingFactor": 1.0},
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.get_screen_size()

        self.assertIsInstance(result, OperationResult)
        self.assertTrue(result.success)
        self.assertEqual(result.data, {"width": 1920, "height": 1080, "dpiScalingFactor": 1.0})
        self.computer._call_mcp_tool.assert_called_once_with("get_screen_size", {})

    def test_get_screen_size_failure(self):
        """Test screen size retrieval failure."""
        mock_result = OperationResult(
            request_id="req-screen-size-fail",
            success=False,
            error_message="Screen size failed",
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.get_screen_size()

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Screen size failed")

    def test_screenshot_success(self):
        """Test successful screenshot."""
        mock_result = OperationResult(
            request_id="req-screenshot",
            success=True,
            data="https://example.com/screenshot.png",
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.screenshot()

        self.assertIsInstance(result, OperationResult)
        self.assertTrue(result.success)
        self.assertEqual(result.data, "https://example.com/screenshot.png")
        self.computer._call_mcp_tool.assert_called_once_with("system_screenshot", {})

    def test_screenshot_exception(self):
        """Test screenshot when exception occurs."""
        self.computer._call_mcp_tool = MagicMock(side_effect=Exception("Screenshot error"))

        result = self.computer.screenshot()

        self.assertFalse(result.success)
        self.assertIn("Failed to take screenshot", result.error_message)

    # Keyboard Operations Tests
    def test_input_text_success(self):
        """Test successful text input."""
        mock_result = OperationResult(
            request_id="req-input-text",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.input_text("Hello World")

        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)
        self.assertTrue(result.data)
        self.computer._call_mcp_tool.assert_called_once_with("input_text", {"text": "Hello World"})

    def test_input_text_failure(self):
        """Test text input failure."""
        mock_result = OperationResult(
            request_id="req-input-text-fail",
            success=False,
            error_message="Input text failed",
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.input_text("Hello World")

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Input text failed")

    def test_press_keys_success(self):
        """Test successful key press."""
        mock_result = OperationResult(
            request_id="req-press-keys",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.press_keys(["Ctrl", "a"])

        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with("press_keys", {"keys": ["Ctrl", "a"], "hold": False})

    def test_press_keys_with_hold(self):
        """Test key press with hold."""
        mock_result = OperationResult(
            request_id="req-press-keys-hold",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.press_keys(["Shift"], hold=True)

        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with("press_keys", {"keys": ["Shift"], "hold": True})

    def test_release_keys_success(self):
        """Test successful key release."""
        mock_result = OperationResult(
            request_id="req-release-keys",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.release_keys(["Shift"])

        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with("release_keys", {"keys": ["Shift"]})

    def test_release_keys_exception(self):
        """Test key release when exception occurs."""
        self.computer._call_mcp_tool = MagicMock(side_effect=Exception("Release keys error"))

        result = self.computer.release_keys(["Shift"])

        self.assertFalse(result.success)
        self.assertIn("Failed to release keys", result.error_message)

    # Window Management Tests
    def test_list_root_windows_success(self):
        """Test successful root windows listing."""
        windows_data = [
            {
                "window_id": 1,
                "title": "Test Window 1",
                "absolute_upper_left_x": 100,
                "absolute_upper_left_y": 100,
                "width": 800,
                "height": 600,
                "pid": 1234,
                "pname": "test.exe"
            },
            {
                "window_id": 2,
                "title": "Test Window 2",
                "absolute_upper_left_x": 200,
                "absolute_upper_left_y": 200,
                "width": 1024,
                "height": 768,
                "pid": 5678,
                "pname": "app.exe"
            }
        ]
        mock_result = OperationResult(
            request_id="req-list-windows",
            success=True,
            data=json.dumps(windows_data),
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.list_root_windows()

        self.assertIsInstance(result, WindowListResult)
        self.assertTrue(result.success)
        self.assertEqual(len(result.windows), 2)
        self.assertEqual(result.windows[0].title, "Test Window 1")
        self.assertEqual(result.windows[1].window_id, 2)
        self.computer._call_mcp_tool.assert_called_once_with("list_root_windows", {"timeout_ms": 3000})

    def test_list_root_windows_with_timeout(self):
        """Test root windows listing with custom timeout."""
        mock_result = OperationResult(
            request_id="req-list-windows-timeout",
            success=True,
            data="[]",
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.list_root_windows(timeout_ms=5000)

        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with("list_root_windows", {"timeout_ms": 5000})

    def test_list_root_windows_json_error(self):
        """Test root windows listing with JSON parse error."""
        mock_result = OperationResult(
            request_id="req-list-windows-json-error",
            success=True,
            data="invalid json",
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.list_root_windows()

        self.assertFalse(result.success)
        self.assertIn("Failed to parse windows JSON", result.error_message)

    def test_get_active_window_success(self):
        """Test successful active window retrieval."""
        window_data = {
            "window_id": 1,
            "title": "Active Window",
            "absolute_upper_left_x": 0,
            "absolute_upper_left_y": 0,
            "width": 1920,
            "height": 1080,
            "pid": 9999,
            "pname": "active.exe"
        }
        mock_result = OperationResult(
            request_id="req-active-window",
            success=True,
            data=json.dumps(window_data),
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.get_active_window()

        self.assertIsInstance(result, WindowInfoResult)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.window)
        self.assertEqual(result.window.title, "Active Window")
        self.computer._call_mcp_tool.assert_called_once_with("get_active_window", {})

    def test_activate_window_success(self):
        """Test successful window activation."""
        mock_result = OperationResult(
            request_id="req-activate-window",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.activate_window("window_123")

        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with("activate_window", {"window_id": "window_123"})

    def test_close_window_success(self):
        """Test successful window closing."""
        mock_result = OperationResult(
            request_id="req-close-window",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.close_window("window_456")

        self.assertIsInstance(result, BoolResult)
        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with("close_window", {"window_id": "window_456"})

    def test_maximize_window_success(self):
        """Test successful window maximization."""
        mock_result = OperationResult(
            request_id="req-maximize-window",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.maximize_window("window_789")

        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with("maximize_window", {"window_id": "window_789"})

    def test_minimize_window_failure(self):
        """Test window minimization failure."""
        mock_result = OperationResult(
            request_id="req-minimize-window-fail",
            success=False,
            error_message="Minimize failed",
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.minimize_window("window_101")

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Minimize failed")

    def test_restore_window_success(self):
        """Test successful window restoration."""
        mock_result = OperationResult(
            request_id="req-restore-window",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.restore_window("window_202")

        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with("restore_window", {"window_id": "window_202"})

    def test_resize_window_success(self):
        """Test successful window resizing."""
        mock_result = OperationResult(
            request_id="req-resize-window",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.resize_window("window_303", 1024, 768)

        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with(
            "resize_window",
            {"window_id": "window_303", "width": 1024, "height": 768}
        )

    def test_fullscreen_window_success(self):
        """Test successful window fullscreen."""
        mock_result = OperationResult(
            request_id="req-fullscreen-window",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.fullscreen_window("window_404")

        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with("fullscreen_window", {"window_id": "window_404"})

    def test_focus_mode_success(self):
        """Test successful focus mode toggle."""
        mock_result = OperationResult(
            request_id="req-focus-mode",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.focus_mode(True)

        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with("focus_mode", {"on": True})

    # Application Management Tests
    def test_get_installed_apps_success(self):
        """Test successful installed apps retrieval."""
        apps_data = [
            {
                "name": "Test App 1",
                "start_cmd": "testapp1.exe",
                "stop_cmd": "taskkill /f /im testapp1.exe",
                "work_directory": "C:\\TestApp1"
            },
            {
                "name": "Test App 2",
                "start_cmd": "testapp2.exe",
                "stop_cmd": None,
                "work_directory": None
            }
        ]
        mock_result = OperationResult(
            request_id="req-installed-apps",
            success=True,
            data=json.dumps(apps_data),
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.get_installed_apps()

        self.assertIsInstance(result, InstalledAppListResult)
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 2)
        self.assertEqual(result.data[0].name, "Test App 1")
        self.assertEqual(result.data[1].start_cmd, "testapp2.exe")
        self.computer._call_mcp_tool.assert_called_once_with(
            "get_installed_apps",
            {"start_menu": True, "desktop": False, "ignore_system_apps": True}
        )

    def test_get_installed_apps_with_params(self):
        """Test installed apps retrieval with custom parameters."""
        mock_result = OperationResult(
            request_id="req-installed-apps-params",
            success=True,
            data="[]",
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.get_installed_apps(start_menu=False, desktop=True, ignore_system_apps=False)

        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with(
            "get_installed_apps",
            {"start_menu": False, "desktop": True, "ignore_system_apps": False}
        )

    def test_start_app_success(self):
        """Test successful app start."""
        processes_data = [
            {
                "pname": "testapp.exe",
                "pid": 12345,
                "cmdline": "C:\\TestApp\\testapp.exe"
            }
        ]
        mock_result = OperationResult(
            request_id="req-start-app",
            success=True,
            data=json.dumps(processes_data),
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.start_app("testapp.exe")

        self.assertIsInstance(result, ProcessListResult)
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0].pname, "testapp.exe")
        self.assertEqual(result.data[0].pid, 12345)
        self.computer._call_mcp_tool.assert_called_once_with("start_app", {"start_cmd": "testapp.exe"})

    def test_start_app_with_work_directory(self):
        """Test app start with work directory."""
        mock_result = OperationResult(
            request_id="req-start-app-workdir",
            success=True,
            data="[]",
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.start_app("app.exe", work_directory="C:\\MyApp")

        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with(
            "start_app",
            {"start_cmd": "app.exe", "work_directory": "C:\\MyApp"}
        )

    def test_list_visible_apps_success(self):
        """Test successful visible apps listing."""
        processes_data = [
            {
                "pname": "chrome.exe",
                "pid": 1111,
                "cmdline": "chrome.exe --new-window"
            },
            {
                "pname": "notepad.exe",
                "pid": 2222,
                "cmdline": "notepad.exe test.txt"
            }
        ]
        mock_result = OperationResult(
            request_id="req-visible-apps",
            success=True,
            data=json.dumps(processes_data),
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.list_visible_apps()

        self.assertIsInstance(result, ProcessListResult)
        self.assertTrue(result.success)
        self.assertEqual(len(result.data), 2)
        self.assertEqual(result.data[0].pname, "chrome.exe")
        self.computer._call_mcp_tool.assert_called_once_with("list_visible_apps", {})

    def test_stop_app_by_pname_success(self):
        """Test successful app stop by process name."""
        mock_result = OperationResult(
            request_id="req-stop-pname",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.stop_app_by_pname("testapp.exe")

        self.assertIsInstance(result, AppOperationResult)
        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with("stop_app_by_pname", {"pname": "testapp.exe"})

    def test_stop_app_by_pid_success(self):
        """Test successful app stop by process ID."""
        mock_result = OperationResult(
            request_id="req-stop-pid",
            success=True,
            data=True,
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.stop_app_by_pid(12345)

        self.assertIsInstance(result, AppOperationResult)
        self.assertTrue(result.success)
        self.computer._call_mcp_tool.assert_called_once_with("stop_app_by_pid", {"pid": 12345})

    def test_stop_app_by_cmd_failure(self):
        """Test app stop by command failure."""
        mock_result = OperationResult(
            request_id="req-stop-cmd-fail",
            success=False,
            error_message="Stop command failed",
        )
        self.computer._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.computer.stop_app_by_cmd("stop_command.bat")

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Stop command failed")

    def test_stop_app_by_cmd_exception(self):
        """Test app stop by command when exception occurs."""
        self.computer._call_mcp_tool = MagicMock(side_effect=Exception("Stop cmd error"))

        result = self.computer.stop_app_by_cmd("stop_command.bat")

        self.assertFalse(result.success)
        self.assertIn("Failed to stop app by cmd", result.error_message)

if __name__ == "__main__":
    unittest.main()
