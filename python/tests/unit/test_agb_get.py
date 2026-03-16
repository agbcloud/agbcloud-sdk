import pytest
from agb import AGB
from agb.session import Session
from agb.model.response import SessionResult

class TestAGBGet:
    """Unit tests for AGB.get method."""

    def test_get_empty_session_id(self):
        """Test get with empty session ID."""
        agb = AGB(api_key="test-api-key")

        result = agb.get("")

        assert isinstance(result, SessionResult)
        assert not result.success
        assert "session_id is required" in result.error_message

    def test_get_none_session_id(self):
        """Test get with None session ID."""
        agb = AGB(api_key="test-api-key")

        result = agb.get(None)

        assert isinstance(result, SessionResult)
        assert not result.success
        assert "session_id is required" in result.error_message

    def test_get_whitespace_session_id(self):
        """Test get with whitespace-only session ID."""
        agb = AGB(api_key="test-api-key")

        result = agb.get("   ")

        assert isinstance(result, SessionResult)
        assert not result.success
        assert "session_id is required" in result.error_message

    def test_get_method_exists(self):
        """Test that get method exists and has correct signature."""
        agb = AGB(api_key="test-api-key")

        # Verify method exists
        assert hasattr(agb, "get")
        assert callable(getattr(agb, "get"))

    def test_get_returns_session_result_type(self):
        """Test that get method returns SessionResult."""
        agb = AGB(api_key="test-api-key")

        # Check the method exists and is callable
        get_method = getattr(agb, "get", None)
        assert get_method is not None
        assert callable(get_method)

        # Test with invalid input to verify it returns SessionResult
        result = agb.get("")
        assert isinstance(result, SessionResult)

    def test_get_error_message_format(self):
        """Test error message formatting for various invalid inputs."""
        agb = AGB(api_key="test-api-key")

        test_cases = [
            ("", "session_id is required"),
            (None, "session_id is required"),
            ("   ", "session_id is required"),
        ]

        for session_id, expected_error in test_cases:
            result = agb.get(session_id)
            assert isinstance(result, SessionResult)
            assert not result.success
            assert expected_error in result.error_message

class TestAGBGetValidation:
    """Validation tests for AGB.get method."""

    def test_get_requires_api_key(self):
        """Test that AGB requires an API key."""
        import os
        # Temporarily remove environment variable
        old_api_key = os.environ.get("AGB_API_KEY")
        if old_api_key:
            del os.environ["AGB_API_KEY"]

        try:
            with pytest.raises(ValueError):
                AGB(api_key="")
        finally:
            # Restore environment variable if it existed
            if old_api_key:
                os.environ["AGB_API_KEY"] = old_api_key

    def test_get_interface_compliance(self):
        """Test that get method has the expected interface."""
        agb = AGB(api_key="test-key")

        # Method should exist
        assert hasattr(agb, "get")

        # Method should be callable
        get_method = getattr(agb, "get")
        assert callable(get_method)

def test_get_documentation():
    """Test that get method is properly documented."""
    agb = AGB(api_key="test-key")

    get_method = getattr(agb, "get", None)
    assert get_method is not None

    # Method should have docstring
    assert get_method.__doc__ is not None
    assert len(get_method.__doc__.strip()) > 0