import os
import pytest
from agb import AGB
from agb.session_params import CreateSessionParams


def test_link_url_session_mcp_tools_and_call_tool():
    """
    Integration test for LinkUrl session with MCP tools and direct call_mcp_tool.
    Requires environment variable: AGB_API_KEY
    """
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        pytest.skip("AGB_API_KEY environment variable not set")

    agb = AGB(api_key=api_key)

    image_id = "agb-browser-use-1"
    params = CreateSessionParams(
        image_id=image_id,
        labels={"test-type": "link-url-integration"},
    )

    result = agb.create(params)
    assert result.success, result.error_message
    assert result.session is not None

    session = result.session
    
    try:
        # Check if LinkUrl/token are available
        if not session.link_url or not session.token:
            pytest.skip("LinkUrl/token not provided by CreateSession response in this environment")

        # Test command execution through LinkUrl route
        cmd_result = session.command.execute("echo link-url-route-ok")
        assert cmd_result.success, cmd_result.error_message
        assert "link-url-route-ok" in cmd_result.output

        # Test session restoration with get()
        restored_result = agb.get(session.session_id)
        assert restored_result.success, restored_result.error_message
        assert restored_result.session is not None
        
        restored_session = restored_result.session

        assert restored_session.get_token() != ""
        assert restored_session.get_link_url() != ""

        # Test direct call_mcp_tool on restored session
        restored_direct = restored_session.call_mcp_tool(
            "shell",
            {"command": "echo restored-direct-link-url-route-ok"},
        )
        assert restored_direct.success, restored_direct.error_message
        assert "restored-direct-link-url-route-ok" in restored_direct.data

        # Test direct call_mcp_tool on original session
        direct = session.call_mcp_tool(
            "shell",
            {"command": "echo direct-link-url-route-ok"},
        )
        assert direct.success, direct.error_message
        assert "direct-link-url-route-ok" in direct.data

    finally:
        delete_result = session.delete()
        assert delete_result.success, f"Delete session failed: {delete_result.error_message}"

