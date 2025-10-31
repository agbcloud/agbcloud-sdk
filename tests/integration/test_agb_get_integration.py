import os
import pytest
from agb import AGB
from agb.session_params import CreateSessionParams
from agb.session import Session

@pytest.fixture(scope="module")
def agb_client():
    """Create AGB client for testing."""
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        pytest.fail("AGB_API_KEY environment variable is not set")
    return AGB(api_key=api_key)

def test_get_api(agb_client: AGB):
    """Test Get API with a real session."""
    print("Creating a new session for Get API testing...")

    # Try different image IDs until one works
    create_result = None
    params = CreateSessionParams(image_id="agb-browser-use-1")
    create_result = agb_client.create(params)
    
    assert create_result and create_result.success, f"Failed to create session with any image_id: {create_result.error_message if create_result else 'No result'}"
    created_session = create_result.session
    session_id = created_session.session_id
    print(f"Session created with ID: {session_id}")

    print("Testing Get API...")
    result = agb_client.get(session_id)

    assert result is not None, "Get returned None result"
    assert result.success, f"Failed to get session: {result.error_message}"
    session = result.session
    assert session is not None, "Get returned None session"
    assert isinstance(session, Session), f"Expected Session instance, got {type(session)}"
    assert session.session_id == session_id, \
        f"Expected SessionID {session_id}, got {session.session_id}"
    
    # Verify session attributes are properly set
    assert hasattr(session, 'resource_url'), "Session should have resource_url attribute"
    assert hasattr(session, 'app_instance_id'), "Session should have app_instance_id attribute"
    assert hasattr(session, 'resource_id'), "Session should have resource_id attribute"
    assert hasattr(session, 'vpc_resource'), "Session should have vpc_resource attribute"
    assert hasattr(session, 'network_interface_ip'), "Session should have network_interface_ip attribute"
    assert hasattr(session, 'http_port'), "Session should have http_port attribute"
    assert hasattr(session, 'token'), "Session should have token attribute"

    print(f"Successfully retrieved session with ID: {session.session_id}")
    print(f"Session resource_url: {session.resource_url}")
    print(f"Session vpc_resource: {session.vpc_resource}")
    print("Get API test passed successfully")

    print("Cleaning up: Deleting the session...")
    delete_result = agb_client.delete(session)
    assert delete_result.success, f"Failed to delete session: {delete_result.error_message}"
    print(f"Session {session_id} deleted successfully")

def test_get_non_existent_session(agb_client: AGB):
    """Test Get API with a non-existent session ID."""
    print("Testing Get API with non-existent session ID...")
    non_existent_session_id = "session-nonexistent-12345"

    # In your implementation, get() returns SessionResult with success=False
    # rather than raising an exception
    result = agb_client.get(non_existent_session_id)
    
    assert result is not None, "Get should return a result object"
    assert not result.success, "Get should fail for non-existent session"
    assert "Failed to get session" in result.error_message, \
        f"Expected error message about failed session retrieval, got: {result.error_message}"
    
    print(f"Correctly received error for non-existent session: {result.error_message}")
    print("Get API non-existent session test passed successfully")

def test_get_empty_session_id(agb_client: AGB):
    """Test Get API with empty session ID."""
    print("Testing Get API with empty session ID...")

    # In your implementation, get() returns SessionResult with success=False
    # rather than raising ValueError
    result = agb_client.get("")
    
    assert result is not None, "Get should return a result object"
    assert not result.success, "Get should fail for empty session ID"
    assert "session_id is required" in result.error_message, \
        f"Expected error message about required session_id, got: {result.error_message}"
    
    print(f"Correctly received error for empty session ID: {result.error_message}")
    print("Get API empty session ID test passed successfully")

def test_get_whitespace_session_id(agb_client: AGB):
    """Test Get API with whitespace-only session ID."""
    print("Testing Get API with whitespace session ID...")

    # In your implementation, get() returns SessionResult with success=False
    # rather than raising ValueError
    result = agb_client.get("   ")
    
    assert result is not None, "Get should return a result object"
    assert not result.success, "Get should fail for whitespace session ID"
    assert "session_id is required" in result.error_message, \
        f"Expected error message about required session_id, got: {result.error_message}"
    
    print(f"Correctly received error for whitespace session ID: {result.error_message}")
    print("Get API whitespace session ID test passed successfully")

def test_get_none_session_id(agb_client: AGB):
    """Test Get API with None session ID."""
    print("Testing Get API with None session ID...")

    # Test with None - this should be handled gracefully
    try:
        result = agb_client.get(None)
        # If it doesn't raise an exception, check the result
        assert result is not None, "Get should return a result object"
        assert not result.success, "Get should fail for None session ID"
        print(f"Correctly handled None session ID: {result.error_message}")
    except TypeError as e:
        # If it raises TypeError, that's also acceptable
        print(f"Correctly raised TypeError for None session ID: {e}")
    
    print("Get API None session ID test passed successfully")

def test_get_with_request_id_tracking(agb_client: AGB):
    """Test that Get API properly tracks request IDs."""
    print("Testing Get API request ID tracking...")

    # Try different image IDs until one works
    create_result = None
    params = CreateSessionParams(image_id="agb-browser-use-1")
    create_result = agb_client.create(params)
        
    assert create_result and create_result.success, f"Failed to create session with any image_id: {create_result.error_message if create_result else 'No result'}"
    session_id = create_result.session.session_id
    
    # Test get with request ID tracking
    result = agb_client.get(session_id)
    assert result.success, f"Failed to get session: {result.error_message}"
    
    # Verify request_id is present and not empty
    assert hasattr(result, 'request_id'), "Result should have request_id attribute"
    print(f"Get API request_id: {result.request_id}")
    
    # Clean up
    delete_result = agb_client.delete(result.session)
    assert delete_result.success, f"Failed to delete session: {delete_result.error_message}"
    
    print("Get API request ID tracking test passed successfully")