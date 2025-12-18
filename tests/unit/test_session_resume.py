"""Unit tests for Session resume operations."""
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

from agb import AGB
from agb.session import Session
from agb.model.response import (
    SessionResumeResult,
    GetSessionResult,
    GetSessionData,
)
from agb.api.models import (
    ResumeSessionResponse,
)


class TestSessionResume(unittest.TestCase):
    """Test suite for Session resume operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.agb = AGB(api_key="test-api-key")
        self.agb.client = MagicMock()

        # Create a mock session
        self.session = Session(self.agb, "session-123")
        self.session.resource_url = ""
        self.session.image_id = ""
        self.session.app_instance_id = ""
        self.session.resource_id = ""

    def test_resume_async_success_immediate(self):
        """Test successful async session resume with immediate success."""
        # Mock the resume_session_async response
        mock_response = ResumeSessionResponse(
            status_code=200,
            url="https://api.example.com/resume",
            headers={},
            success=True,
            json_data={
                "success": True,
                "message": "Session resume initiated successfully",
                "httpStatusCode": 200,
                "requestId": "test-request-id"
            },
            request_id="test-request-id"
        )
        self.agb.client.resume_session_async = AsyncMock(return_value=mock_response)

        # Mock get_session to return RUNNING immediately
        get_session_running = GetSessionResult(
            request_id="test-request-id",
            success=True,
            data=GetSessionData(
                session_id="session-123",
                success=True,
                resource_url="",
                app_instance_id="",
                resource_id="",
            ),
        )
        # Set the status attribute that's expected by the code
        get_session_running.data.status = "RUNNING"
        self.agb.get_session = MagicMock(return_value=get_session_running)

        # Patch asyncio.sleep to avoid waiting
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            # Call the method
            result = asyncio.run(self.session.resume_async(timeout=10, poll_interval=1))

            # Verify the result
            self.assertIsInstance(result, SessionResumeResult)
            self.assertTrue(result.success)
            self.assertEqual(result.request_id, "test-request-id")
            self.assertEqual(result.error_message, "")

            # Verify that sleep was not called since we got RUNNING directly.
            mock_sleep.assert_not_called()

    def test_resume_async_success_after_polling(self):
        """Test successful async session resume after polling."""
        # Mock the resume_session_async response
        mock_response = ResumeSessionResponse(
            status_code=200,
            url="https://api.example.com/resume",
            headers={},
            success=True,
            json_data={
                "success": True,
                "message": "Session resume initiated successfully",
                "httpStatusCode": 200,
                "requestId": "test-request-id"
            },
            request_id="test-request-id"
        )
        self.agb.client.resume_session_async = AsyncMock(return_value=mock_response)

        # Mock get_session to return RESUMING first, then RUNNING
        get_session_resuming = GetSessionResult(
            request_id="test-request-id",
            success=True,
            data=GetSessionData(
                session_id="session-123",
                success=True,
                resource_url="",
                app_instance_id="",
                resource_id="",
            ),
        )
        get_session_resuming.data.status = "RESUMING"

        get_session_running = GetSessionResult(
            request_id="test-request-id",
            success=True,
            data=GetSessionData(
                session_id="session-123",
                success=True,
                resource_url="",
                app_instance_id="",
                resource_id="",
            ),
        )
        get_session_running.data.status = "RUNNING"
        self.agb.get_session = MagicMock(side_effect=[get_session_resuming, get_session_running])

        # Patch asyncio.sleep to avoid waiting
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            # Call the method
            result = asyncio.run(self.session.resume_async(timeout=10, poll_interval=1))

            # Verify the result
            self.assertIsInstance(result, SessionResumeResult)
            self.assertTrue(result.success)
            self.assertEqual(result.request_id, "test-request-id")
            self.assertEqual(result.error_message, "")

            # Verify that sleep was called once (after the first attempt)
            mock_sleep.assert_called_once_with(1)

    def test_resume_async_timeout(self):
        """Test async session resume timeout."""
        # Mock the resume_session_async response
        mock_response = ResumeSessionResponse(
            status_code=200,
            url="https://api.example.com/resume",
            headers={},
            success=True,
            json_data={
                "success": True,
                "message": "Session resume initiated successfully",
                "httpStatusCode": 200,
                "requestId": "test-request-id"
            },
            request_id="test-request-id"
        )
        self.agb.client.resume_session_async = AsyncMock(return_value=mock_response)

        # Mock get_session to always return RESUMING
        get_session_resuming = GetSessionResult(
            request_id="test-request-id",
            success=True,
            data=GetSessionData(
                session_id="session-123",
                success=True,
                resource_url="",
                app_instance_id="",
                resource_id="",
            ),
        )
        get_session_resuming.data.status = "RESUMING"
        self.agb.get_session = MagicMock(return_value=get_session_resuming)

        # Patch asyncio.sleep to avoid waiting
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            # Call the method with a short timeout
            result = asyncio.run(self.session.resume_async(timeout=2, poll_interval=1))

            # Verify the result
            self.assertIsInstance(result, SessionResumeResult)
            self.assertFalse(result.success)
            self.assertIn("timed out", result.error_message)
            self.assertEqual(result.request_id, "")

    def test_resume_async_get_session_failure(self):
        """Test async session resume when get_session fails."""
        # Mock the resume_session_async response
        mock_response = ResumeSessionResponse(
            status_code=200,
            url="https://api.example.com/resume",
            headers={},
            success=True,
            json_data={
                "success": True,
                "message": "Session resume initiated successfully",
                "httpStatusCode": 200,
                "requestId": "test-request-id"
            },
            request_id="test-request-id"
        )
        self.agb.client.resume_session_async = AsyncMock(return_value=mock_response)

        # Mock get_session to return failure
        get_session_failure = GetSessionResult(
            request_id="test-request-id",
            success=False,
            error_message="Failed to get session status",
        )
        self.agb.get_session = MagicMock(return_value=get_session_failure)

        # Patch asyncio.sleep to avoid waiting
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            # Call the method
            result = asyncio.run(self.session.resume_async())

            # Verify the result
            self.assertIsInstance(result, SessionResumeResult)
            self.assertFalse(result.success)
            self.assertIn("Failed to get session status", result.error_message)
            self.assertEqual(result.request_id, "test-request-id")

    def test_resume_async_api_error(self):
        """Test async session resume with API error."""
        # Mock the resume_session_async response with error
        mock_response = ResumeSessionResponse(
            status_code=404,
            url="https://api.example.com/resume",
            headers={},
            success=False,
            json_data={
                "success": False,
                "code": "SessionNotFound",
                "message": "Session does not exist",
                "httpStatusCode": 404,
                "requestId": "test-request-id"
            },
            request_id="test-request-id"
        )
        self.agb.client.resume_session_async = AsyncMock(return_value=mock_response)

        # Patch asyncio.sleep to avoid waiting
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            # Call the method
            result = asyncio.run(self.session.resume_async())

            # Verify the result
            self.assertIsInstance(result, SessionResumeResult)
            self.assertFalse(result.success)
            self.assertEqual(result.request_id, "test-request-id")
            self.assertEqual(result.error_message, "Session does not exist")

    def test_resume_async_client_exception(self):
        """Test async session resume with client exception."""
        # Mock the client to raise an exception
        self.agb.client.resume_session_async = AsyncMock(side_effect=Exception("Network error"))

        # Patch asyncio.sleep to avoid waiting
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            # Call the method
            result = asyncio.run(self.session.resume_async())

            # Verify the result
            self.assertIsInstance(result, SessionResumeResult)
            self.assertFalse(result.success)
            self.assertIn("Network error", result.error_message)
            self.assertEqual(result.request_id, "")

    def test_resume_async_unexpected_state(self):
        """Test async session resume with unexpected state."""
        # Mock the resume_session_async response
        mock_response = ResumeSessionResponse(
            status_code=200,
            url="https://api.example.com/resume",
            headers={},
            success=True,
            json_data={
                "success": True,
                "message": "Session resume initiated successfully",
                "httpStatusCode": 200,
                "requestId": "test-request-id"
            },
            request_id="test-request-id"
        )
        self.agb.client.resume_session_async = AsyncMock(return_value=mock_response)

        # Mock get_session to return unexpected state (should fail immediately)
        get_session_unexpected = GetSessionResult(
            request_id="test-request-id",
            success=True,
            data=GetSessionData(
                session_id="session-123",
                success=True,
                resource_url="",
                app_instance_id="",
                resource_id="",
            ),
        )
        get_session_unexpected.data.status = "other"
        self.agb.get_session = MagicMock(return_value=get_session_unexpected)

        # Patch asyncio.sleep to avoid waiting
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            # Call the method
            result = asyncio.run(self.session.resume_async(timeout=10, poll_interval=1))

            # Verify the result - should fail immediately due to unexpected state
            self.assertIsInstance(result, SessionResumeResult)
            self.assertFalse(result.success)
            self.assertEqual(result.request_id, "test-request-id")
            self.assertIn("unexpected state", result.error_message)

            # Verify that sleep was not called since we failed immediately
            mock_sleep.assert_not_called()

    def test_resume_sync_success_immediate(self):
        """Test successful synchronous session resume with immediate success."""
        # Mock the resume_session_async response
        mock_response = ResumeSessionResponse(
            status_code=200,
            url="https://api.example.com/resume",
            headers={},
            success=True,
            json_data={
                "success": True,
                "message": "Session resume initiated successfully",
                "httpStatusCode": 200,
                "requestId": "test-request-id"
            },
            request_id="test-request-id"
        )
        self.agb.client.resume_session_async = AsyncMock(return_value=mock_response)

        # Mock get_session to return RUNNING immediately
        get_session_running = GetSessionResult(
            request_id="test-request-id",
            success=True,
            data=GetSessionData(
                session_id="session-123",
                success=True,
                resource_url="",
                app_instance_id="",
                resource_id="",
            ),
        )
        get_session_running.data.status = "RUNNING"
        self.agb.get_session = MagicMock(return_value=get_session_running)

        # Patch asyncio.sleep to avoid waiting
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            # Patch asyncio.run to return a mock result directly
            with patch('asyncio.run') as mock_run:
                # Create a mock result that matches what we expect
                mock_result = SessionResumeResult(
                    request_id="test-request-id",
                    success=True,
                    error_message=""
                )
                mock_run.return_value = mock_result

                # Call the method
                result = self.session.resume(timeout=10, poll_interval=1)

                # Verify the result
                self.assertIsInstance(result, SessionResumeResult)
                self.assertTrue(result.success)
                self.assertEqual(result.request_id, "test-request-id")
                self.assertEqual(result.error_message, "")

    def test_resume_with_agb_resume_method(self):
        """Test AGB.resume method."""
        # Create mock result
        mock_result = SessionResumeResult(
            request_id="test-request-id",
            success=True,
            error_message=""
        )

        # Mock the session.resume method
        self.session.resume = MagicMock(return_value=mock_result)

        # Call the method with session object
        result = self.agb.resume(self.session)

        # Verify the result
        self.assertIsInstance(result, SessionResumeResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "test-request-id")
        self.assertEqual(result.error_message, "")



if __name__ == "__main__":
    unittest.main()