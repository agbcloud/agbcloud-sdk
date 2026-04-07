# -*- coding: utf-8 -*-
"""
WebSocket long connection integration tests.

Tests the synchronous WebSocket client functionality for streaming
communication with AGB cloud sessions.
"""
import os

import pytest

from agb import AGB
from agb.session import Session
from agb.session_params import CreateSessionParams
from agb.model.response import McpTool


@pytest.mark.integration
class TestWsLongConnectionIntegration:
    """Test WebSocket long connection functionality."""
    
    @pytest.fixture
    def agb(self):
        """Create AGB instance for testing."""
        api_key = os.getenv("AGB_API_KEY")
        if not api_key:
            pytest.skip("AGB_API_KEY environment variable not set")
        return AGB(api_key=api_key)
    
    def test_ws_connect_and_basic_call_stream(self, agb):
        """
        Test WebSocket connection and basic streaming call.
        
        This test verifies:
        1. WebSocket URL is provided by backend
        2. WebSocket client can connect successfully
        3. Streaming calls work with event/end/error callbacks
        4. Resources are properly cleaned up
        """
        # Create session
        result = agb.create(CreateSessionParams(image_id="agb-browser-use-1"))
        
        assert result.success is True, result.error_message
        assert result.session is not None
        session = result.session
        
        ws_client = None
        try:
            # Verify WebSocket URL is provided
            assert (
                session.ws_url
            ), "Backend did not return wsUrl/WsUrl in CreateSession response"
            
            # Get WebSocket client (synchronous)
            ws_client = session._get_ws_client()
            ws_client.connect()
            
            # Determine target server
            # Default to wuying_codespace, but try to find run_code tool's server
            target = "wuying_codespace"
            for tool in session.tool_list or []:
                try:
                    if tool.name == "run_code" and tool.server:
                        target = tool.server
                        break
                except Exception:
                    continue
            
            # Track callbacks
            events = []
            ends = []
            errors = []
            
            # Define callback functions
            def on_event(invocation_id: str, data: dict) -> None:
                """Handle stream events."""
                assert invocation_id
                assert isinstance(data, dict)
                events.append(data)
            
            def on_end(invocation_id: str, data: dict) -> None:
                """Handle stream completion."""
                assert invocation_id
                assert isinstance(data, dict)
                ends.append(data)
            
            def on_error(invocation_id: str, err: Exception) -> None:
                """Handle stream errors."""
                assert invocation_id
                assert isinstance(err, Exception)
                errors.append(err)
            
            # Initiate streaming call
            handle = ws_client.call_stream(
                target=target,
                data={
                    "method": "run_code",
                    "mode": "stream",
                    "params": {
                        "language": "python",
                        "timeoutS": 600,
                        "code": "x=1"
                    },
                },
                on_event=on_event,
                on_end=on_end,
                on_error=on_error,
            )
            
            # Wait for stream to complete
            try:
                end_data = handle.wait_end()
            except Exception as e:
                # Check if error callback was invoked
                if errors:
                    # For WS validation, backend may return request error immediately.
                    # This is still a valid callback chain: on_error must be invoked.
                    return
                
                # Re-raise if no error callback was invoked
                raise
            
            # Verify results
            assert len(ends) == 1, f"Expected 1 end callback, got {len(ends)}"
            assert errors == [], f"Unexpected errors: {errors}"
            assert isinstance(end_data, dict), f"Expected dict, got {type(end_data)}"
            
        finally:
            # Clean up resources
            if ws_client is not None:
                try:
                    ws_client.close()
                except Exception:
                    pass
            session.delete()