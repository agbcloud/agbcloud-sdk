#!/usr/bin/env python3
"""
Integration tests for Session MCP tool calling functionality.
Tests require AGB_API_KEY environment variable to be set.
"""

import os
import time
import unittest
import json

from agb import AGB
from agb.session_params import CreateSessionParams
from agb.model.response import McpToolResult, McpToolsResult


class TestSessionMcpIntegration(unittest.TestCase):
    """Integration tests for Session MCP tool methods"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        api_key = os.environ.get("AGB_API_KEY")
        if not api_key:
            raise AssertionError("Integration test failed: No API key available")

        cls.agb = AGB(api_key)

        # Create a shared session for all tests
        params = CreateSessionParams(image_id="agb-code-space-2")
        session_result = cls.agb.create(params)
        if not session_result.success or not session_result.session:
            raise AssertionError("Failed to create session for integration tests")

        cls.session = session_result.session
        assert cls.session is not None
        print(f"Created shared session for tests: {cls.session.session_id}")

    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures"""
        if hasattr(cls, "session") and cls.session:
            try:
                delete_result = cls.agb.delete(cls.session)
                if delete_result.success:
                    print(f"Deleted shared session: {cls.session.session_id} (RequestID: {delete_result.request_id})")
                else:
                    print(f"Warning: Failed to delete session: {delete_result.error_message}")
            except Exception as e:
                print(f"Warning: Exception while deleting session: {e}")

    def test_list_mcp_tools(self):
        """Test listing MCP tools in real environment"""
        print("===== Test list_mcp_tools =====")

        # List MCP tools using shared session
        result = self.session.list_mcp_tools()
        self.assertIsInstance(result, McpToolsResult)
        self.assertTrue(result.success, f"Failed to list MCP tools: {result.error_message}")
        self.assertIsNotNone(result.request_id, "Request ID should not be None")

        print(f"Found {len(result.tools)} MCP tools (RequestID: {result.request_id})")

        # If tools are available, verify structure
        if result.tools:
            for i, tool in enumerate(result.tools):
                print(f"Tool {i+1}: {tool.name} - {tool.description}")
                self.assertIsNotNone(tool.name, "Tool name should not be None")
                self.assertIsNotNone(tool.description, "Tool description should not be None")
        else:
            print("No tools available (this is acceptable)")

    def test_list_mcp_tools_with_custom_image_id(self):
        """Test listing MCP tools with custom image_id"""
        print("===== Test list_mcp_tools with custom image_id =====")

        # List tools with custom image_id using shared session
        result = self.session.list_mcp_tools(image_id="agb-code-space-2")
        self.assertIsInstance(result, McpToolsResult)
        self.assertTrue(result.success, f"Failed to list MCP tools: {result.error_message}")
        print(f"Listed tools with custom image_id (RequestID: {result.request_id})")

    def test_call_mcp_tool_basic(self):
        """Test calling a basic MCP tool (if available)"""
        print("===== Test call_mcp_tool basic =====")

        # First, list available tools using shared session
        tools_result = self.session.list_mcp_tools()
        if not tools_result.success or not tools_result.tools:
            self.skipTest("No MCP tools available for testing")

        # Try to call the first available tool (if it has no required parameters)
        available_tool = None
        for tool in tools_result.tools:
            # Look for a tool that might not require parameters
            schema = tool.input_schema
            if isinstance(schema, dict):
                required = schema.get("required", [])
                if len(required) == 0:
                    available_tool = tool
                    break

        if not available_tool:
            print("No tools available without required parameters, skipping call test")
            return

        print(f"Calling tool: {available_tool.name}")

        # Call the tool with empty args using shared session
        result = self.session.call_mcp_tool(available_tool.name, {})
        self.assertIsInstance(result, McpToolResult)
        self.assertIsNotNone(result.request_id, "Request ID should not be None")

        print(f"Tool call result: success={result.success}, RequestID={result.request_id}")
        if result.success:
            print(f"Tool returned data: {result.data}")
        else:
            print(f"Tool call failed: {result.error_message}")

        # Note: We don't assert success here because the tool might fail for various reasons
        # We just verify that the call was made and we got a proper response

    def test_call_mcp_tool_with_timeouts(self):
        """Test calling MCP tool with custom timeouts"""
        print("===== Test call_mcp_tool with timeouts =====")

        # List tools first using shared session
        tools_result = self.session.list_mcp_tools()
        if not tools_result.success or not tools_result.tools:
            self.skipTest("No MCP tools available for testing")

        # Find a tool without required parameters
        available_tool = None
        for tool in tools_result.tools:
            schema = tool.input_schema
            if isinstance(schema, dict):
                required = schema.get("required", [])
                if len(required) == 0:
                    available_tool = tool
                    break

        if not available_tool:
            print("No tools available without required parameters, skipping timeout test")
            return

        # Call with custom timeouts using shared session
        result = self.session.call_mcp_tool(
            available_tool.name,
            {},
            read_timeout=30000,
            connect_timeout=10000,
        )

        self.assertIsInstance(result, McpToolResult)
        print(f"Tool call with timeouts: success={result.success}, RequestID={result.request_id}")

    def test_call_mcp_tool_invalid_tool_name(self):
        """Test calling a non-existent MCP tool"""
        print("===== Test call_mcp_tool with invalid tool name =====")

        # Try to call a non-existent tool using shared session
        result = self.session.call_mcp_tool("non_existent_tool_12345", {})

        self.assertIsInstance(result, McpToolResult)
        # The call should fail
        self.assertFalse(result.success, "Calling non-existent tool should fail")
        self.assertIsNotNone(result.error_message, "Error message should be provided")
        print(f"Invalid tool call failed as expected: {result.error_message}")


if __name__ == "__main__":
    unittest.main()
