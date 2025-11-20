import unittest
from unittest.mock import MagicMock, patch

from agb.context import ContextService
from agb.api.models.get_context_response import GetContextResponseBodyData, GetContextResponse
from agb.api.models.clear_context_response import ClearContextResponse
from agb.exceptions import ClearanceTimeoutError, AGBError


class TestContextServiceClear(unittest.TestCase):
    """Test cases for context clearing operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.agb = MagicMock()
        self.agb.api_key = "test-api-key"
        self.agb.client = MagicMock()
        self.context_service = ContextService(self.agb)

    def test_clear_async_success(self):
        """Test successfully starting a context clearing task."""
        # Mock the response from the API
        mock_response = MagicMock(spec=ClearContextResponse)
        mock_response.is_successful.return_value = True
        mock_response.request_id = "req-clear-123"
        mock_response.json_data = {"success": True}
        self.agb.client.clear_context.return_value = mock_response

        # Call the method
        result = self.context_service.clear_async("context-123")

        # Verify the results
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-clear-123")
        self.assertEqual(result.context_id, "context-123")
        self.assertEqual(result.status, "clearing")
        self.assertEqual(result.error_message, "")

        # Verify the API was called correctly
        self.agb.client.clear_context.assert_called_once()
        call_args = self.agb.client.clear_context.call_args[0][0]
        self.assertEqual(call_args.id, "context-123")
        self.assertEqual(call_args.authorization, "Bearer test-api-key")

    def test_clear_async_api_failure(self):
        """Test clear_async when API call fails."""
        # Mock the response from the API
        mock_response = MagicMock(spec=ClearContextResponse)
        mock_response.is_successful.return_value = False
        mock_response.get_error_message.return_value = "Context not found"
        mock_response.request_id = "req-error-123"
        mock_response.json_data = {"success": False, "message": "Context not found"}
        self.agb.client.clear_context.return_value = mock_response

        # Call the method
        result = self.context_service.clear_async("context-123")

        # Verify the results
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "req-error-123")
        self.assertEqual(result.error_message, "Context not found")

    def test_clear_async_exception(self):
        """Test clear_async when an exception occurs."""
        # Mock the client to raise an exception
        self.agb.client.clear_context.side_effect = Exception("Network error")

        # Call the method and expect it to raise AGBError
        with self.assertRaises(AGBError) as context:
            self.context_service.clear_async("context-123")

        # Verify the error message
        self.assertIn("Failed to start context clearing", str(context.exception))
        self.assertIn("context-123", str(context.exception))

    def test_get_clear_status_success_clearing(self):
        """Test getting clear status when status is 'clearing'."""
        # Mock the response from the API
        mock_response = MagicMock(spec=GetContextResponse)
        mock_response.is_successful.return_value = True
        mock_response.request_id = "req-status-123"
        mock_response.json_data = {"success": True}
        mock_response.get_context_data.return_value = GetContextResponseBodyData(
            id="context-123",
            name="test-context",
            state="clearing"
        )
        self.agb.client.get_context.return_value = mock_response

        # Call the method
        result = self.context_service.get_clear_status("context-123")

        # Verify the results
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-status-123")
        self.assertEqual(result.context_id, "context-123")
        self.assertEqual(result.status, "clearing")

        # Verify the API was called correctly
        self.agb.client.get_context.assert_called_once()
        call_args = self.agb.client.get_context.call_args[0][0]
        self.assertEqual(call_args.id, "context-123")
        self.assertEqual(call_args.allow_create, False)

    def test_get_clear_status_success_available(self):
        """Test getting clear status when status is 'available'."""
        # Mock the response from the API
        mock_response = MagicMock(spec=GetContextResponse)
        mock_response.is_successful.return_value = True
        mock_response.request_id = "req-status-456"
        mock_response.json_data = {"success": True}
        mock_response.get_context_data.return_value = GetContextResponseBodyData(
            id="context-123",
            name="test-context",
            state="available"
        )
        self.agb.client.get_context.return_value = mock_response

        # Call the method
        result = self.context_service.get_clear_status("context-123")

        # Verify the results
        self.assertTrue(result.success)
        self.assertEqual(result.status, "available")

    def test_get_clear_status_success_no_state(self):
        """Test getting clear status when state is not provided (defaults to 'clearing')."""
        # Mock the response from the API
        mock_response = MagicMock(spec=GetContextResponse)
        mock_response.is_successful.return_value = True
        mock_response.request_id = "req-status-default"
        mock_response.json_data = {"success": True}
        mock_response.get_context_data.return_value = GetContextResponseBodyData(
            id="context-123",
            name="test-context",
            state=None
        )
        self.agb.client.get_context.return_value = mock_response

        # Call the method
        result = self.context_service.get_clear_status("context-123")

        # Verify the results - should default to "clearing"
        self.assertTrue(result.success)
        self.assertEqual(result.status, "clearing")

    def test_get_clear_status_api_failure(self):
        """Test get_clear_status when API call fails."""
        # Mock the response from the API
        mock_response = MagicMock(spec=GetContextResponse)
        mock_response.is_successful.return_value = False
        mock_response.get_error_message.return_value = "Context not found"
        mock_response.request_id = "req-error-status"
        mock_response.json_data = {"success": False, "message": "Context not found"}
        self.agb.client.get_context.return_value = mock_response

        # Call the method
        result = self.context_service.get_clear_status("context-123")

        # Verify the results
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "req-error-status")
        self.assertEqual(result.error_message, "Context not found")

    def test_get_clear_status_exception(self):
        """Test get_clear_status when an exception occurs."""
        # Mock the client to raise an exception
        self.agb.client.get_context.side_effect = Exception("Network error")

        # Call the method
        result = self.context_service.get_clear_status("context-123")

        # Verify the results - should return error result instead of raising
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "")
        self.assertIn("Failed to get clear status", result.error_message)
        self.assertIn("Network error", result.error_message)

    @patch('agb.context.time.sleep')
    @patch('agb.context.time.time')
    def test_clear_success(self, mock_time, mock_sleep):
        """Test successfully clearing a context with polling."""
        # Mock time.time to return increasing values
        mock_time.side_effect = [0.0, 2.0, 4.0]  # start, first poll, second poll

        # Mock clear_async to return success
        mock_clear_response = MagicMock(spec=ClearContextResponse)
        mock_clear_response.is_successful.return_value = True
        mock_clear_response.request_id = "req-clear-start"
        mock_clear_response.json_data = {"success": True}
        self.agb.client.clear_context.return_value = mock_clear_response

        # Mock get_context to return different states over time
        # First call: clearing, Second call: available
        mock_get_responses = [
            MagicMock(spec=GetContextResponse),
            MagicMock(spec=GetContextResponse),
        ]
        mock_get_responses[0].is_successful.return_value = True
        mock_get_responses[0].request_id = "req-status-1"
        mock_get_responses[0].json_data = {"success": True}
        mock_get_responses[0].get_context_data.return_value = GetContextResponseBodyData(
            id="context-123",
            state="clearing"
        )
        mock_get_responses[1].is_successful.return_value = True
        mock_get_responses[1].request_id = "req-status-2"
        mock_get_responses[1].json_data = {"success": True}
        mock_get_responses[1].get_context_data.return_value = GetContextResponseBodyData(
            id="context-123",
            state="available"
        )
        self.agb.client.get_context.side_effect = mock_get_responses

        # Call the method
        result = self.context_service.clear("context-123", timeout=60, poll_interval=2.0)

        # Verify the results
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-clear-start")
        self.assertEqual(result.context_id, "context-123")
        self.assertEqual(result.status, "available")

        # Verify polling occurred (sleep should be called)
        self.assertEqual(mock_sleep.call_count, 2)  # Called twice before completion

    @patch('agb.context.time.sleep')
    @patch('agb.context.time.time')
    def test_clear_start_failure(self, mock_time, mock_sleep):
        """Test clear when starting the task fails."""
        # Mock clear_async to return failure
        mock_clear_response = MagicMock(spec=ClearContextResponse)
        mock_clear_response.is_successful.return_value = False
        mock_clear_response.get_error_message.return_value = "Failed to start"
        mock_clear_response.request_id = "req-clear-fail"
        mock_clear_response.json_data = {"success": False}
        self.agb.client.clear_context.return_value = mock_clear_response

        # Call the method
        result = self.context_service.clear("context-123")

        # Verify the results
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "req-clear-fail")
        self.assertEqual(result.error_message, "Failed to start")

        # Verify polling did not occur
        mock_sleep.assert_not_called()
        self.agb.client.get_context.assert_not_called()

    @patch('agb.context.time.sleep')
    @patch('agb.context.time.time')
    def test_clear_status_query_failure(self, mock_time, mock_sleep):
        """Test clear when status query fails during polling."""
        # Mock time.time
        mock_time.side_effect = [0.0, 2.0]

        # Mock clear_async to return success
        mock_clear_response = MagicMock(spec=ClearContextResponse)
        mock_clear_response.is_successful.return_value = True
        mock_clear_response.request_id = "req-clear-start"
        mock_clear_response.json_data = {"success": True}
        self.agb.client.clear_context.return_value = mock_clear_response

        # Mock get_context to return failure
        mock_get_response = MagicMock(spec=GetContextResponse)
        mock_get_response.is_successful.return_value = False
        mock_get_response.get_error_message.return_value = "Status query failed"
        mock_get_response.request_id = "req-status-fail"
        mock_get_response.json_data = {"success": False}
        self.agb.client.get_context.return_value = mock_get_response

        # Call the method
        result = self.context_service.clear("context-123", timeout=60, poll_interval=2.0)

        # Verify the results
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Status query failed")

        # Verify polling occurred once
        self.assertEqual(mock_sleep.call_count, 1)

    @patch('agb.context.time.sleep')
    @patch('agb.context.time.time')
    def test_clear_timeout(self, mock_time, mock_sleep):
        """Test clear when the task times out."""
        # Mock time.time to simulate timeout
        # The code calls time.time() at:
        # 1. start_time = time.time() (at the beginning)
        # 2. time.time() in the loop (for elapsed calculation in warning, but only if status is unexpected)
        # 3. time.time() at the end (for final elapsed calculation)
        # Since status is "clearing" (expected), the elapsed calculation in the loop won't happen
        # So we need: start_time=0, then after 30 attempts, final check should be >= 60

        # Create a call counter to track time.time() calls
        call_count = [0]
        def time_side_effect():
            call_count[0] += 1
            if call_count[0] == 1:
                return 0.0  # start_time
            else:
                # After 30 attempts (each with 2.0 interval), we're at 60 seconds
                return 60.0 + (call_count[0] - 2) * 0.1  # Add small increments for subsequent calls

        mock_time.side_effect = time_side_effect

        # Mock clear_async to return success
        mock_clear_response = MagicMock(spec=ClearContextResponse)
        mock_clear_response.is_successful.return_value = True
        mock_clear_response.request_id = "req-clear-start"
        mock_clear_response.json_data = {"success": True}
        self.agb.client.clear_context.return_value = mock_clear_response

        # Mock get_context to always return "clearing" (never completes)
        mock_get_response = MagicMock(spec=GetContextResponse)
        mock_get_response.is_successful.return_value = True
        mock_get_response.request_id = "req-status-timeout"
        mock_get_response.json_data = {"success": True}
        mock_get_response.get_context_data.return_value = GetContextResponseBodyData(
            id="context-123",
            state="clearing"
        )
        self.agb.client.get_context.return_value = mock_get_response

        # Call the method and expect timeout exception
        with self.assertRaises(ClearanceTimeoutError) as context:
            self.context_service.clear("context-123", timeout=60, poll_interval=2.0)

        # Verify the error message
        self.assertIn("timed out", str(context.exception))
        # The elapsed time should be around 60 seconds (after 30 attempts)
        # Since we're using 60.0 as the final time, elapsed should be 60.0
        self.assertIn("60", str(context.exception))

        # Verify polling occurred multiple times (should be 30 attempts)
        self.assertEqual(mock_sleep.call_count, 30)

    @patch('agb.context.time.sleep')
    @patch('agb.context.time.time')
    def test_clear_unexpected_state(self, mock_time, mock_sleep):
        """Test clear when context is in an unexpected state (but continues polling)."""
        # Mock time.time
        mock_time.side_effect = [0.0, 2.0, 4.0, 6.0]

        # Mock clear_async to return success
        mock_clear_response = MagicMock(spec=ClearContextResponse)
        mock_clear_response.is_successful.return_value = True
        mock_clear_response.request_id = "req-clear-start"
        mock_clear_response.json_data = {"success": True}
        self.agb.client.clear_context.return_value = mock_clear_response

        # Mock get_context to return unexpected state, then available
        mock_get_responses = [
            MagicMock(spec=GetContextResponse),
            MagicMock(spec=GetContextResponse),
        ]
        mock_get_responses[0].is_successful.return_value = True
        mock_get_responses[0].request_id = "req-status-1"
        mock_get_responses[0].json_data = {"success": True}
        mock_get_responses[0].get_context_data.return_value = GetContextResponseBodyData(
            id="context-123",
            state="unexpected-state"
        )
        mock_get_responses[1].is_successful.return_value = True
        mock_get_responses[1].request_id = "req-status-2"
        mock_get_responses[1].json_data = {"success": True}
        mock_get_responses[1].get_context_data.return_value = GetContextResponseBodyData(
            id="context-123",
            state="available"
        )
        self.agb.client.get_context.side_effect = mock_get_responses

        # Call the method
        result = self.context_service.clear("context-123", timeout=60, poll_interval=2.0)

        # Verify the results - should eventually succeed
        self.assertTrue(result.success)
        self.assertEqual(result.status, "available")

        # Verify polling continued despite unexpected state
        self.assertEqual(mock_sleep.call_count, 2)


if __name__ == "__main__":
    unittest.main()

