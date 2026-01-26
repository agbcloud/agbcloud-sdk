"""
Example demonstrating how to use MCP tool calling methods in Session.

This example shows:
1. Listing available MCP tools for a session
2. Calling MCP tools with different arguments
3. Handling tool call results and errors
"""

import os
import sys
import json

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, project_root)

from agb import AGB
from agb.session_params import CreateSessionParams


def list_mcp_tools_example(session):
    """Example: List available MCP tools"""
    print("=" * 60)
    print("Example 1: List Available MCP Tools")
    print("=" * 60)

    result = session.list_mcp_tools()
    if not result.success:
        print(f"Failed to list MCP tools: {result.error_message}")
        return

    print(f"\nFound {len(result.tools)} available tools:")
    print(f"Request ID: {result.request_id}\n")

    for i, tool in enumerate(result.tools, 1):
        print(f"{i}. {tool.name}")
        print(f"   Description: {tool.description}")
        print(f"   Server: {tool.server}")
        print(f"   Type: {tool.tool}")
        if tool.input_schema:
            print(f"   Input Schema: {json.dumps(tool.input_schema, indent=2)}")
        print()


def list_mcp_tools_with_image_id_example(session):
    """Example: List MCP tools for a specific image"""
    print("=" * 60)
    print("Example 2: List MCP Tools for Specific Image")
    print("=" * 60)

    # List tools for a specific image (e.g., code space)
    result = session.list_mcp_tools(image_id="agb-code-space-1")
    if not result.success:
        print(f"Failed to list MCP tools: {result.error_message}")
        return

    print(f"\nFound {len(result.tools)} tools for image 'agb-code-space-1':")
    for tool in result.tools:
        print(f"  - {tool.name}: {tool.description}")


def call_mcp_tool_example(session):
    """Example: Call an MCP tool"""
    print("=" * 60)
    print("Example 3: Call MCP Tool")
    print("=" * 60)

    # First, list available tools to see what we can call
    list_result = session.list_mcp_tools()
    if not list_result.success or not list_result.tools:
        print("No tools available or failed to list tools")
        return

    # Use the first available tool as an example
    # Note: In practice, you should know which tool you want to call
    if list_result.tools:
        tool = list_result.tools[0]
        print(f"\nCalling tool: {tool.name}")
        print(f"Description: {tool.description}")

        # Example: Call tool with empty args (adjust based on actual tool requirements)
        # In real usage, you would provide appropriate arguments based on the tool's input_schema
        result = session.call_mcp_tool(tool.name, {})
        if result.success:
            print(f"\nTool call succeeded!")
            print(f"Request ID: {result.request_id}")
            if result.data:
                try:
                    # Try to parse and pretty-print the result
                    data = json.loads(result.data)
                    print(f"Result: {json.dumps(data, indent=2)}")
                except json.JSONDecodeError:
                    print(f"Result (raw): {result.data}")
        else:
            print(f"\nTool call failed: {result.error_message}")
            print(f"Request ID: {result.request_id}")


def call_mcp_tool_with_timeouts_example(session):
    """Example: Call MCP tool with custom timeouts"""
    print("=" * 60)
    print("Example 4: Call MCP Tool with Custom Timeouts")
    print("=" * 60)

    list_result = session.list_mcp_tools()
    if not list_result.success or not list_result.tools:
        print("No tools available")
        return

    if list_result.tools:
        tool = list_result.tools[0]
        print(f"\nCalling tool '{tool.name}' with custom timeouts...")

        # Call with custom read and connect timeouts (in milliseconds)
        result = session.call_mcp_tool(
            tool.name,
            {},
            read_timeout=30000,  # 30 seconds
            connect_timeout=5000,  # 5 seconds
        )

        if result.success:
            print("Tool call succeeded with custom timeouts!")
        else:
            print(f"Tool call failed: {result.error_message}")


def main():
    """Main function demonstrating MCP tool usage"""
    # Get API key from environment variable
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        raise ValueError("AGB_API_KEY environment variable is not set")

    # Initialize AGB client
    agb = AGB(api_key=api_key)

    try:
        # Create a session
        print("Creating session...")
        params = CreateSessionParams(image_id="agb-code-space-1")
        create_result = agb.create(params)
        if not create_result.success:
            raise RuntimeError(f"Failed to create session: {create_result.error_message}")

        session = create_result.session
        print(f"Session created: {session.session_id}\n")

        # Run examples
        list_mcp_tools_example(session)
        list_mcp_tools_with_image_id_example(session)
        call_mcp_tool_example(session)
        call_mcp_tool_with_timeouts_example(session)

    finally:
        # Clean up: Delete the session when done
        print("\n" + "=" * 60)
        print("Cleaning up...")
        if "session" in locals():
            delete_result = agb.delete(session)
            if delete_result.success:
                print("Session deleted successfully")
            else:
                print(f"Failed to delete session: {delete_result.error_message}")


if __name__ == "__main__":
    main()
