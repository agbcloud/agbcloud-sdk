import unittest
from unittest.mock import MagicMock, Mock
import json

from agb.session import Session
from agb.api.models import CallMcpToolResponse, ListMcpToolsResponse
from agb.model.response import McpTool, McpToolResult, McpToolsResult
from agb.exceptions import AGBError


class DummyAGB:
    """Dummy AGB client for testing"""

    def __init__(self, api_key: str = "test_api_key"):
        self.api_key = api_key
        self._client = MagicMock()
        self.client = self._client  # Session.get_client() accesses self.agb.client

    def get_client(self):
        return self._client


class TestSessionCallMcpTool(unittest.TestCase):
    """Test Session.call_mcp_tool() method"""

    def setUp(self):
        self.agb = DummyAGB()
        self.session = Session(self.agb, "test_session_id")
        self.session.image_id = "test_image_id"

    def test_call_mcp_tool_success(self):
        """Test successful MCP tool call"""
        # Mock response
        response = CallMcpToolResponse.from_http_response(
            {
                "status_code": 200,
                "url": "http://example/mcp",
                "headers": {},
                "success": True,
                "request_id": "req-123",
                "json": {
                    "success": True,
                    "code": "OK",
                    "message": "",
                    "data": {
                        "isError": False,
                        "content": [{"type": "text", "text": '{"result": "success"}'}],
                    },
                    "requestId": "req-123",
                },
            }
        )

        self.agb._client.call_mcp_tool.return_value = response

        # Call method
        result = self.session.call_mcp_tool("test_tool", {"param": "value"})

        # Assertions
        self.assertIsInstance(result, McpToolResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-123")
        self.assertEqual(result.data, '{"result": "success"}')
        self.assertEqual(result.error_message, "")

        # Verify client was called correctly
        call_args = self.agb._client.call_mcp_tool.call_args
        self.assertIsNotNone(call_args)
        request = call_args[0][0]
        self.assertEqual(request.name, "test_tool")
        self.assertEqual(request.session_id, "test_session_id")
        self.assertIn("param", json.loads(request.args))


    def test_call_mcp_tool_api_failure(self):
        """Test MCP tool call when API returns failure"""
        response = CallMcpToolResponse.from_http_response(
            {
                "status_code": 200,
                "url": "http://example/mcp",
                "headers": {},
                "success": True,
                "request_id": "req-789",
                "json": {
                    "success": False,
                    "code": "InvalidSession.NotFound",
                    "message": "Session not found",
                    "data": {},
                    "requestId": "req-789",
                },
            }
        )

        self.agb._client.call_mcp_tool.return_value = response

        result = self.session.call_mcp_tool("test_tool", {})

        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "req-789")
        self.assertIn("Session not found", result.error_message)

    def test_call_mcp_tool_tool_execution_failure(self):
        """Test MCP tool call when tool execution fails"""
        response = CallMcpToolResponse.from_http_response(
            {
                "status_code": 200,
                "url": "http://example/mcp",
                "headers": {},
                "success": True,
                "request_id": "req-999",
                "json": {
                    "success": True,
                    "code": "OK",
                    "message": "",
                    "data": {
                        "isError": True,
                        "content": [{"type": "text", "text": "Tool execution failed"}],
                    },
                    "requestId": "req-999",
                },
            }
        )

        self.agb._client.call_mcp_tool.return_value = response

        result = self.session.call_mcp_tool("test_tool", {})

        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "req-999")

    def test_call_mcp_tool_none_response(self):
        """Test MCP tool call when client returns None"""
        self.agb._client.call_mcp_tool.return_value = None

        result = self.session.call_mcp_tool("test_tool", {})

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "OpenAPI client returned None response")

    def test_call_mcp_tool_exception(self):
        """Test MCP tool call when exception occurs"""
        self.agb._client.call_mcp_tool.side_effect = Exception("Network error")

        result = self.session.call_mcp_tool("test_tool", {})

        self.assertFalse(result.success)
        self.assertIn("Network error", result.error_message)

    def test_call_mcp_tool_agb_error(self):
        """Test MCP tool call when AGBError occurs"""
        self.agb._client.call_mcp_tool.side_effect = AGBError("AGB error")

        result = self.session.call_mcp_tool("test_tool", {})

        self.assertFalse(result.success)
        self.assertIn("AGB error", result.error_message)

    def test_call_mcp_tool_with_timeouts(self):
        """Test MCP tool call with custom timeouts"""
        response = CallMcpToolResponse.from_http_response(
            {
                "status_code": 200,
                "url": "http://example/mcp",
                "headers": {},
                "success": True,
                "request_id": "req-timeout",
                "json": {
                    "success": True,
                    "code": "OK",
                    "message": "",
                    "data": {
                        "isError": False,
                        "content": [{"type": "text", "text": "ok"}],
                    },
                    "requestId": "req-timeout",
                },
            }
        )

        self.agb._client.call_mcp_tool.return_value = response

        result = self.session.call_mcp_tool(
            "test_tool", {}, read_timeout=5000, connect_timeout=3000
        )

        self.assertTrue(result.success)
        # Verify timeouts were passed
        call_kwargs = self.agb._client.call_mcp_tool.call_args[1]
        self.assertEqual(call_kwargs.get("read_timeout"), 5000)
        self.assertEqual(call_kwargs.get("connect_timeout"), 3000)


class TestSessionListMcpTools(unittest.TestCase):
    """Test Session.list_mcp_tools() method"""

    def setUp(self):
        self.agb = DummyAGB()
        self.session = Session(self.agb, "test_session_id")
        self.session.image_id = "test_image_id"

    def test_list_mcp_tools_success(self):
        """Test successful MCP tools listing"""
        tools_data = [
            {
                "name": "tap",
                "description": "Tap on screen",
                "inputSchema": {"type": "object", "properties": {"x": {"type": "number"}}},
                "server": "mobile_server",
                "tool": "tap",
            },
            {
                "name": "get_ui_elements",
                "description": "Get UI elements",
                "inputSchema": {},
                "server": "mobile_server",
                "tool": "get_ui_elements",
            },
        ]

        response = ListMcpToolsResponse.from_http_response(
            {
                "status_code": 200,
                "url": "http://example/mcp/tools",
                "headers": {},
                "success": True,
                "request_id": "req-list",
                "json": {
                    "success": True,
                    "code": "OK",
                    "message": "",
                    "data": json.dumps(tools_data),
                    "requestId": "req-list",
                },
            }
        )

        self.agb._client.list_mcp_tools.return_value = response

        result = self.session.list_mcp_tools()

        # Assertions
        self.assertIsInstance(result, McpToolsResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-list")
        self.assertEqual(len(result.tools), 2)

        # Check first tool
        tool1 = result.tools[0]
        self.assertIsInstance(tool1, McpTool)
        self.assertEqual(tool1.name, "tap")
        self.assertEqual(tool1.description, "Tap on screen")
        self.assertEqual(tool1.server, "mobile_server")

        # Check second tool
        tool2 = result.tools[1]
        self.assertEqual(tool2.name, "get_ui_elements")

        # Verify client was called correctly
        call_args = self.agb._client.list_mcp_tools.call_args
        self.assertIsNotNone(call_args)
        request = call_args[0][0]
        self.assertEqual(request.image_id, "test_image_id")

    def test_list_mcp_tools_with_custom_image_id(self):
        """Test listing tools with custom image_id"""
        response = ListMcpToolsResponse.from_http_response(
            {
                "status_code": 200,
                "url": "http://example/mcp/tools",
                "headers": {},
                "success": True,
                "request_id": "req-custom",
                "json": {
                    "success": True,
                    "code": "OK",
                    "message": "",
                    "data": "[]",
                    "requestId": "req-custom",
                },
            }
        )

        self.agb._client.list_mcp_tools.return_value = response

        result = self.session.list_mcp_tools(image_id="custom_image_id")

        self.assertTrue(result.success)
        # Verify custom image_id was used
        call_args = self.agb._client.list_mcp_tools.call_args
        request = call_args[0][0]
        self.assertEqual(request.image_id, "custom_image_id")

    def test_list_mcp_tools_default_image_id(self):
        """Test listing tools with default image_id"""
        # Remove image_id from session
        delattr(self.session, "image_id")

        response = ListMcpToolsResponse.from_http_response(
            {
                "status_code": 200,
                "url": "http://example/mcp/tools",
                "headers": {},
                "success": True,
                "request_id": "req-default",
                "json": {
                    "success": True,
                    "code": "OK",
                    "message": "",
                    "data": "[]",
                    "requestId": "req-default",
                },
            }
        )

        self.agb._client.list_mcp_tools.return_value = response

        result = self.session.list_mcp_tools()

        self.assertTrue(result.success)
        call_args = self.agb._client.list_mcp_tools.call_args
        request = call_args[0][0]
        self.assertEqual(request.image_id, "agb-code-space-1")

    def test_list_mcp_tools_api_failure(self):
        """Test listing tools when API returns failure"""
        response = ListMcpToolsResponse.from_http_response(
            {
                "status_code": 200,
                "url": "http://example/mcp/tools",
                "headers": {},
                "success": True,
                "request_id": "req-fail",
                "json": {
                    "success": False,
                    "code": "InvalidRequest",
                    "message": "Invalid image_id",
                    "data": None,
                    "requestId": "req-fail",
                },
            }
        )

        self.agb._client.list_mcp_tools.return_value = response

        result = self.session.list_mcp_tools()

        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "req-fail")
        self.assertIn("Invalid image_id", result.error_message)

    def test_list_mcp_tools_empty_list(self):
        """Test listing tools when no tools are available"""
        response = ListMcpToolsResponse.from_http_response(
            {
                "status_code": 200,
                "url": "http://example/mcp/tools",
                "headers": {},
                "success": True,
                "request_id": "req-empty",
                "json": {
                    "success": True,
                    "code": "OK",
                    "message": "",
                    "data": "[]",
                    "requestId": "req-empty",
                },
            }
        )

        self.agb._client.list_mcp_tools.return_value = response

        result = self.session.list_mcp_tools()

        self.assertTrue(result.success)
        self.assertEqual(len(result.tools), 0)

    def test_list_mcp_tools_invalid_json(self):
        """Test listing tools when tools data is invalid JSON"""
        response = ListMcpToolsResponse.from_http_response(
            {
                "status_code": 200,
                "url": "http://example/mcp/tools",
                "headers": {},
                "success": True,
                "request_id": "req-invalid",
                "json": {
                    "success": True,
                    "code": "OK",
                    "message": "",
                    "data": "invalid json",
                    "requestId": "req-invalid",
                },
            }
        )

        self.agb._client.list_mcp_tools.return_value = response

        result = self.session.list_mcp_tools()

        self.assertFalse(result.success)
        self.assertIn("Failed to parse tools list", result.error_message)

    def test_list_mcp_tools_exception(self):
        """Test listing tools when exception occurs"""
        self.agb._client.list_mcp_tools.side_effect = Exception("Network error")

        result = self.session.list_mcp_tools()

        self.assertFalse(result.success)
        self.assertIn("Network error", result.error_message)


if __name__ == "__main__":
    unittest.main()
