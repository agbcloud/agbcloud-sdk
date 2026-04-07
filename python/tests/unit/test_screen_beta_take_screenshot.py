"""
Unit tests for screen.beta_take_screenshot functionality.
"""

import base64
import json
import unittest
from unittest.mock import MagicMock, PropertyMock

from agb.modules.computer.screen import ScreenController
from agb.model.response import McpToolResult, ScreenshotResult
from agb.exceptions import ScreenError


def create_mock_session(has_link_url: bool = True):
    """Create a mock session for testing."""
    mock_session = MagicMock()
    if has_link_url:
        mock_session.get_link_url.return_value = "https://example.com/link"
    else:
        mock_session.get_link_url.return_value = ""
    mock_session.link_url = "https://example.com/link" if has_link_url else ""
    return mock_session


def create_valid_png_response():
    """Create a valid PNG screenshot response."""
    # PNG magic bytes
    png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    b64_data = base64.b64encode(png_data).decode()
    return json.dumps({
        "type": "screenshot",
        "mime_type": "image/png",
        "data": b64_data,
        "width": 1920,
        "height": 1080,
    })


def create_valid_jpeg_response():
    """Create a valid JPEG screenshot response."""
    # JPEG magic bytes
    jpeg_data = b"\xff\xd8\xff" + b"\x00" * 100
    b64_data = base64.b64encode(jpeg_data).decode()
    return json.dumps({
        "type": "screenshot",
        "mime_type": "image/jpeg",
        "data": b64_data,
        "width": 1920,
        "height": 1080,
    })


class TestBetaTakeScreenshotBasic(unittest.TestCase):
    """Test basic beta_take_screenshot functionality."""

    def test_beta_take_screenshot_png_success(self):
        """Test successful PNG screenshot."""
        mock_session = create_mock_session(has_link_url=True)
        mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="req-123",
            success=True,
            data=create_valid_png_response(),
        )

        controller = ScreenController(mock_session)
        result = controller.beta_take_screenshot(format="png")

        self.assertIsInstance(result, ScreenshotResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-123")
        self.assertEqual(result.mime_type, "image/png")
        self.assertEqual(result.type, "screenshot")
        self.assertEqual(result.width, 1920)
        self.assertEqual(result.height, 1080)
        self.assertIsInstance(result.data, bytes)
        self.assertTrue(result.data.startswith(b"\x89PNG\r\n\x1a\n"))

        mock_session.call_mcp_tool.assert_called_once_with(
            "screenshot", {"format": "png"}
        )

    def test_beta_take_screenshot_jpeg_success(self):
        """Test successful JPEG screenshot."""
        mock_session = create_mock_session(has_link_url=True)
        mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="req-456",
            success=True,
            data=create_valid_jpeg_response(),
        )

        controller = ScreenController(mock_session)
        result = controller.beta_take_screenshot(format="jpeg")

        self.assertTrue(result.success)
        self.assertEqual(result.mime_type, "image/jpeg")
        self.assertTrue(result.data.startswith(b"\xff\xd8\xff"))

        mock_session.call_mcp_tool.assert_called_once_with(
            "screenshot", {"format": "jpeg"}
        )

    def test_beta_take_screenshot_jpg_alias(self):
        """Test jpg is converted to jpeg."""
        mock_session = create_mock_session(has_link_url=True)
        mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="req-789",
            success=True,
            data=create_valid_jpeg_response(),
        )

        controller = ScreenController(mock_session)
        result = controller.beta_take_screenshot(format="jpg")

        self.assertTrue(result.success)
        mock_session.call_mcp_tool.assert_called_once_with(
            "screenshot", {"format": "jpeg"}
        )

    def test_beta_take_screenshot_default_format(self):
        """Test default format is png."""
        mock_session = create_mock_session(has_link_url=True)
        mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="req-default",
            success=True,
            data=create_valid_png_response(),
        )

        controller = ScreenController(mock_session)
        result = controller.beta_take_screenshot()

        self.assertTrue(result.success)
        mock_session.call_mcp_tool.assert_called_once_with(
            "screenshot", {"format": "png"}
        )


class TestBetaTakeScreenshotEnvironmentCheck(unittest.TestCase):
    """Test environment validation for beta_take_screenshot."""

    def test_raises_screen_error_without_link_url(self):
        """Test raises ScreenError when link_url is not available."""
        mock_session = create_mock_session(has_link_url=False)

        controller = ScreenController(mock_session)

        with self.assertRaises(ScreenError) as context:
            controller.beta_take_screenshot()

        self.assertIn("does not support", str(context.exception))
        self.assertIn("capture()", str(context.exception))

    def test_raises_screen_error_when_get_link_url_raises(self):
        """Test raises ScreenError when get_link_url raises exception."""
        mock_session = MagicMock()
        mock_session.get_link_url.side_effect = Exception("Connection error")
        mock_session.link_url = ""  # Fallback also empty

        controller = ScreenController(mock_session)

        with self.assertRaises(ScreenError) as context:
            controller.beta_take_screenshot()

        self.assertIn("does not support", str(context.exception))


class TestBetaTakeScreenshotFormatValidation(unittest.TestCase):
    """Test format validation for beta_take_screenshot."""

    def test_invalid_format_raises_value_error(self):
        """Test invalid format raises ValueError."""
        mock_session = create_mock_session(has_link_url=True)

        controller = ScreenController(mock_session)

        with self.assertRaises(ValueError) as context:
            controller.beta_take_screenshot(format="gif")

        self.assertIn("Invalid format", str(context.exception))

    def test_invalid_format_bmp_raises_value_error(self):
        """Test bmp format raises ValueError."""
        mock_session = create_mock_session(has_link_url=True)

        controller = ScreenController(mock_session)

        with self.assertRaises(ValueError) as context:
            controller.beta_take_screenshot(format="bmp")

        self.assertIn("Invalid format", str(context.exception))

    def test_format_case_insensitive(self):
        """Test format is case insensitive."""
        mock_session = create_mock_session(has_link_url=True)
        mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="req-case",
            success=True,
            data=create_valid_png_response(),
        )

        controller = ScreenController(mock_session)
        result = controller.beta_take_screenshot(format="PNG")

        self.assertTrue(result.success)
        mock_session.call_mcp_tool.assert_called_once_with(
            "screenshot", {"format": "png"}
        )


class TestBetaTakeScreenshotErrorHandling(unittest.TestCase):
    """Test error handling for beta_take_screenshot."""

    def test_mcp_tool_failure(self):
        """Test handles MCP tool failure."""
        mock_session = create_mock_session(has_link_url=True)
        mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="req-fail",
            success=False,
            error_message="Tool execution failed",
        )

        controller = ScreenController(mock_session)

        with self.assertRaises(ScreenError) as context:
            controller.beta_take_screenshot()

        self.assertIn("Tool execution failed", str(context.exception))

    def test_empty_response_data(self):
        """Test handles empty response data."""
        mock_session = create_mock_session(has_link_url=True)
        mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="req-empty",
            success=True,
            data="",
        )

        controller = ScreenController(mock_session)

        with self.assertRaises(ScreenError) as context:
            controller.beta_take_screenshot()

        self.assertIn("empty data", str(context.exception))

    def test_non_json_response(self):
        """Test handles non-JSON response."""
        mock_session = create_mock_session(has_link_url=True)
        mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="req-nonjson",
            success=True,
            data="not json data",
        )

        controller = ScreenController(mock_session)

        with self.assertRaises(ScreenError) as context:
            controller.beta_take_screenshot()

        self.assertIn("non-JSON", str(context.exception))

    def test_invalid_json_response(self):
        """Test handles invalid JSON response."""
        mock_session = create_mock_session(has_link_url=True)
        mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="req-invalid",
            success=True,
            data="{invalid json}",
        )

        controller = ScreenController(mock_session)

        with self.assertRaises(ScreenError) as context:
            controller.beta_take_screenshot()

        self.assertIn("Invalid screenshot JSON", str(context.exception))

    def test_missing_base64_field(self):
        """Test handles missing base64 data field."""
        mock_session = create_mock_session(has_link_url=True)
        mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="req-nodata",
            success=True,
            data=json.dumps({
                "type": "screenshot",
                "mime_type": "image/png",
                "width": 100,
                "height": 100,
            }),
        )

        controller = ScreenController(mock_session)

        with self.assertRaises(ScreenError) as context:
            controller.beta_take_screenshot()

        self.assertIn("missing base64", str(context.exception))

    def test_missing_type_field(self):
        """Test handles missing type field."""
        mock_session = create_mock_session(has_link_url=True)
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="req-notype",
            success=True,
            data=json.dumps({
                "mime_type": "image/png",
                "data": base64.b64encode(png_data).decode(),
            }),
        )

        controller = ScreenController(mock_session)

        with self.assertRaises(ScreenError) as context:
            controller.beta_take_screenshot()

        self.assertIn("non-empty string 'type'", str(context.exception))

    def test_missing_mime_type_field(self):
        """Test handles missing mime_type field."""
        mock_session = create_mock_session(has_link_url=True)
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="req-nomime",
            success=True,
            data=json.dumps({
                "type": "screenshot",
                "data": base64.b64encode(png_data).decode(),
            }),
        )

        controller = ScreenController(mock_session)

        with self.assertRaises(ScreenError) as context:
            controller.beta_take_screenshot()

        self.assertIn("non-empty string 'mime_type'", str(context.exception))

    def test_invalid_base64_data(self):
        """Test handles invalid base64 data."""
        mock_session = create_mock_session(has_link_url=True)
        mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="req-badb64",
            success=True,
            data=json.dumps({
                "type": "screenshot",
                "mime_type": "image/png",
                "data": "not-valid-base64!!!",
            }),
        )

        controller = ScreenController(mock_session)

        with self.assertRaises(ScreenError) as context:
            controller.beta_take_screenshot()

        self.assertIn("Failed to decode", str(context.exception))

    def test_wrong_magic_bytes(self):
        """Test handles wrong magic bytes for format."""
        mock_session = create_mock_session(has_link_url=True)
        # Send JPEG data but request PNG
        jpeg_data = b"\xff\xd8\xff" + b"\x00" * 100
        mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="req-wrongmagic",
            success=True,
            data=json.dumps({
                "type": "screenshot",
                "mime_type": "image/png",
                "data": base64.b64encode(jpeg_data).decode(),
            }),
        )

        controller = ScreenController(mock_session)

        with self.assertRaises(ScreenError) as context:
            controller.beta_take_screenshot(format="png")

        self.assertIn("does not match expected format", str(context.exception))

    def test_wrong_mime_type(self):
        """Test handles wrong mime type for format."""
        mock_session = create_mock_session(has_link_url=True)
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="req-wrongmime",
            success=True,
            data=json.dumps({
                "type": "screenshot",
                "mime_type": "image/jpeg",  # Wrong mime type for PNG
                "data": base64.b64encode(png_data).decode(),
            }),
        )

        controller = ScreenController(mock_session)

        with self.assertRaises(ScreenError) as context:
            controller.beta_take_screenshot(format="png")

        self.assertIn("mime_type does not match", str(context.exception))


class TestBetaTakeScreenshotOptionalFields(unittest.TestCase):
    """Test optional fields handling for beta_take_screenshot."""

    def test_width_height_optional(self):
        """Test width and height are optional."""
        mock_session = create_mock_session(has_link_url=True)
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="req-nosize",
            success=True,
            data=json.dumps({
                "type": "screenshot",
                "mime_type": "image/png",
                "data": base64.b64encode(png_data).decode(),
                # No width/height
            }),
        )

        controller = ScreenController(mock_session)
        result = controller.beta_take_screenshot()

        self.assertTrue(result.success)
        self.assertIsNone(result.width)
        self.assertIsNone(result.height)

    def test_invalid_width_type(self):
        """Test handles invalid width type."""
        mock_session = create_mock_session(has_link_url=True)
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="req-badwidth",
            success=True,
            data=json.dumps({
                "type": "screenshot",
                "mime_type": "image/png",
                "data": base64.b64encode(png_data).decode(),
                "width": "not an int",
            }),
        )

        controller = ScreenController(mock_session)

        with self.assertRaises(ScreenError) as context:
            controller.beta_take_screenshot()

        self.assertIn("expected integer 'width'", str(context.exception))

    def test_invalid_height_type(self):
        """Test handles invalid height type."""
        mock_session = create_mock_session(has_link_url=True)
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        mock_session.call_mcp_tool.return_value = McpToolResult(
            request_id="req-badheight",
            success=True,
            data=json.dumps({
                "type": "screenshot",
                "mime_type": "image/png",
                "data": base64.b64encode(png_data).decode(),
                "width": 100,
                "height": "not an int",
            }),
        )

        controller = ScreenController(mock_session)

        with self.assertRaises(ScreenError) as context:
            controller.beta_take_screenshot()

        self.assertIn("expected integer 'height'", str(context.exception))


if __name__ == "__main__":
    unittest.main()
