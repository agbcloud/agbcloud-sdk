import unittest
from unittest.mock import MagicMock, patch
from agb.session import Session, DeleteResult

class DummyAGB:
    def __init__(self):
        self.client = MagicMock()
        self.api_key = "test_api_key"

    def get_api_key(self):
        return self.api_key

    def get_client(self):
        return self.client

class TestSession(unittest.TestCase):
    def setUp(self):
        self.agb = DummyAGB()
        self.session_id = "test_session_id"
        self.session = Session(self.agb, self.session_id)

    def test_validate_labels_success(self):
        # Test successful validation with valid labels
        labels = {"key1": "value1", "key2": "value2"}
        result = self.session._validate_labels(labels)
        self.assertIsNone(result)

    def test_validate_labels_none(self):
        # Test validation with None labels
        labels = None
        result = self.session._validate_labels(labels)
        self.assertIsNotNone(result)
        self.assertFalse(result.success)
        self.assertIn("Labels cannot be null", result.error_message)

    def test_validate_labels_list(self):
        # Test validation with list instead of dict
        labels = ["key1", "value1"]
        result = self.session._validate_labels(labels)
        self.assertIsNotNone(result)
        self.assertFalse(result.success)
        self.assertIn("Labels cannot be an array", result.error_message)

    def test_validate_labels_empty_dict(self):
        # Test validation with empty dict
        labels = {}
        result = self.session._validate_labels(labels)
        self.assertIsNotNone(result)
        self.assertFalse(result.success)
        self.assertIn("Labels cannot be empty", result.error_message)

    def test_validate_labels_empty_key(self):
        # Test validation with empty key
        labels = {"": "value1"}
        result = self.session._validate_labels(labels)
        self.assertIsNotNone(result)
        self.assertFalse(result.success)
        self.assertIn("Label keys cannot be empty", result.error_message)

    def test_validate_labels_empty_value(self):
        # Test validation with empty value
        labels = {"key1": ""}
        result = self.session._validate_labels(labels)
        self.assertIsNotNone(result)
        self.assertFalse(result.success)
        self.assertIn("Label values cannot be empty", result.error_message)

    def test_validate_labels_none_value(self):
        # Test validation with None value
        labels = {"key1": None}
        result = self.session._validate_labels(labels)
        self.assertIsNotNone(result)
        self.assertFalse(result.success)
        self.assertIn("Label values cannot be empty", result.error_message)

    def test_initialization(self):
        self.assertEqual(self.session.session_id, self.session_id)
        self.assertEqual(self.session.agb, self.agb)
        self.assertIsNotNone(self.session.file_system)
        self.assertIsNotNone(self.session.command)
        self.assertEqual(self.session.file_system.session, self.session)
        self.assertEqual(self.session.command.session, self.session)

    def test_get_api_key(self):
        self.assertEqual(self.session.get_api_key(), "test_api_key")

    def test_get_client(self):
        self.assertEqual(self.session.get_client(), self.agb.client)

    def test_get_session_id(self):
        self.assertEqual(self.session.get_session_id(), "test_session_id")

    @patch("agb.session.ReleaseSessionRequest")
    def test_delete_success(self, MockReleaseSessionRequest):
        mock_request = MagicMock()
        mock_response = MagicMock()
        MockReleaseSessionRequest.return_value = mock_request
        self.agb.client.release_mcp_session.return_value = mock_response

        # Mock the response methods
        mock_response.is_successful.return_value = True
        mock_response.request_id = "request-123"

        result = self.session.delete()
        self.assertIsInstance(result, DeleteResult)
        self.assertEqual(result.request_id, "request-123")
        self.assertTrue(result.success)

        MockReleaseSessionRequest.assert_called_once_with(
            authorization="Bearer test_api_key", session_id="test_session_id"
        )
        self.agb.client.release_mcp_session.assert_called_once_with(mock_request)

    @patch("agb.session.ReleaseSessionRequest")
    def test_delete_without_params(self, MockReleaseSessionRequest):
        # Test default behavior when no parameters are provided
        mock_request = MagicMock()
        mock_response = MagicMock()
        MockReleaseSessionRequest.return_value = mock_request
        self.agb.client.release_mcp_session.return_value = mock_response

        # Mock the response methods
        mock_response.is_successful.return_value = True
        mock_response.request_id = "request-123"

        # Set up context mock object
        self.session.context = MagicMock()

        # Call delete method without parameters
        result = self.session.delete()
        self.assertIsInstance(result, DeleteResult)
        self.assertTrue(result.success)

        # Verify sync was not called
        self.session.context.sync.assert_not_called()

        # Verify API call is correct
        MockReleaseSessionRequest.assert_called_once_with(
            authorization="Bearer test_api_key", session_id="test_session_id"
        )
        self.agb.client.release_mcp_session.assert_called_once_with(mock_request)

    @patch("agb.session.ReleaseSessionRequest")
    def test_delete_with_sync_context(self, MockReleaseSessionRequest):
        # Test behavior when sync_context=True
        mock_request = MagicMock()
        mock_response = MagicMock()
        MockReleaseSessionRequest.return_value = mock_request
        self.agb.client.release_mcp_session.return_value = mock_response

        # Mock the response methods
        mock_response.is_successful.return_value = True
        mock_response.request_id = "request-123"

        # Set up context mock object
        self.session.context = MagicMock()

        # Mock context.sync return value (now returns a coroutine)
        sync_result = MagicMock()
        sync_result.success = True
        # Since context.sync is now async, we need to mock it as a coroutine
        import asyncio
        async def mock_sync():
            return sync_result
        self.session.context.sync.return_value = mock_sync()

        # Call delete method with sync_context=True
        result = self.session.delete(sync_context=True)
        self.assertIsInstance(result, DeleteResult)
        self.assertTrue(result.success)

        # Verify sync was called (but not info since we're not using callback mode)
        self.session.context.sync.assert_called_once()

        # Verify API call is correct
        MockReleaseSessionRequest.assert_called_once_with(
            authorization="Bearer test_api_key", session_id="test_session_id"
        )
        self.agb.client.release_mcp_session.assert_called_once_with(mock_request)

    @patch("agb.session.ReleaseSessionRequest")
    def test_delete_failure(self, MockReleaseSessionRequest):
        mock_request = MagicMock()
        MockReleaseSessionRequest.return_value = mock_request
        self.agb.client.release_mcp_session.side_effect = Exception("Test error")

        result = self.session.delete()
        self.assertIsInstance(result, DeleteResult)
        self.assertFalse(result.success)
        self.assertEqual(
            result.error_message,
            f"Failed to delete session {self.session_id}: Test error",
        )

        MockReleaseSessionRequest.assert_called_once_with(
            authorization="Bearer test_api_key", session_id="test_session_id"
        )
        self.agb.client.release_mcp_session.assert_called_once_with(mock_request)

    @patch("agb.session.ReleaseSessionRequest")
    def test_delete_api_failure_response(self, MockReleaseSessionRequest):
        mock_request = MagicMock()
        mock_response = MagicMock()
        MockReleaseSessionRequest.return_value = mock_request
        self.agb.client.release_mcp_session.return_value = mock_response

        # Mock the response methods to return a failure response
        mock_response.is_successful.return_value = False
        mock_response.get_error_message.return_value = "API Error"
        mock_response.request_id = "request-123"

        result = self.session.delete()
        self.assertIsInstance(result, DeleteResult)
        self.assertEqual(result.request_id, "request-123")
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "API Error")

        MockReleaseSessionRequest.assert_called_once_with(
            authorization="Bearer test_api_key", session_id="test_session_id"
        )
        self.agb.client.release_mcp_session.assert_called_once_with(mock_request)

    @patch("agb.session.SetLabelRequest")
    def test_set_labels_success(self, MockSetLabelRequest):
        from agb.model.response import OperationResult

        mock_request = MagicMock()
        mock_response = MagicMock()
        MockSetLabelRequest.return_value = mock_request
        self.agb.client.set_label.return_value = mock_response

        # Mock the response methods
        mock_response.is_successful.return_value = True
        mock_response.request_id = "request-123"

        labels = {"key1": "value1", "key2": "value2"}
        result = self.session.set_labels(labels)

        self.assertIsInstance(result, OperationResult)
        self.assertEqual(result.request_id, "request-123")
        self.assertTrue(result.success)

        MockSetLabelRequest.assert_called_once()
        self.agb.client.set_label.assert_called_once_with(mock_request)

    @patch("agb.session.SetLabelRequest")
    def test_set_labels_validation_failure(self, MockSetLabelRequest):
        from agb.model.response import OperationResult

        # Test with empty labels (should fail validation)
        labels = {}
        result = self.session.set_labels(labels)

        self.assertIsInstance(result, OperationResult)
        self.assertFalse(result.success)
        self.assertIn("Labels cannot be empty", result.error_message)

        # Verify API was not called due to validation failure
        MockSetLabelRequest.assert_not_called()
        self.agb.client.set_label.assert_not_called()

    @patch("agb.session.GetLabelRequest")
    def test_get_labels_success(self, MockGetLabelRequest):
        from agb.model.response import OperationResult

        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_labels_data = MagicMock()
        MockGetLabelRequest.return_value = mock_request
        self.agb.client.get_label.return_value = mock_response

        # Mock the response methods
        mock_response.is_successful.return_value = True
        mock_response.request_id = "request-123"
        mock_response.get_labels_data.return_value = mock_labels_data
        mock_labels_data.labels = '{"key1": "value1", "key2": "value2"}'

        result = self.session.get_labels()

        self.assertIsInstance(result, OperationResult)
        self.assertEqual(result.request_id, "request-123")
        self.assertTrue(result.success)
        self.assertEqual(result.data, {"key1": "value1", "key2": "value2"})

        MockGetLabelRequest.assert_called_once_with(
            authorization="Bearer test_api_key", session_id="test_session_id"
        )
        self.agb.client.get_label.assert_called_once_with(mock_request)

    @patch("agb.session.GetLabelRequest")
    def test_get_labels_empty_response(self, MockGetLabelRequest):
        from agb.model.response import OperationResult

        mock_request = MagicMock()
        mock_response = MagicMock()
        MockGetLabelRequest.return_value = mock_request
        self.agb.client.get_label.return_value = mock_response

        # Mock the response methods for empty labels
        mock_response.is_successful.return_value = True
        mock_response.request_id = "request-123"
        mock_response.get_labels_data.return_value = None

        result = self.session.get_labels()

        self.assertIsInstance(result, OperationResult)
        self.assertEqual(result.request_id, "request-123")
        self.assertTrue(result.success)
        self.assertEqual(result.data, {})

        MockGetLabelRequest.assert_called_once_with(
            authorization="Bearer test_api_key", session_id="test_session_id"
        )
        self.agb.client.get_label.assert_called_once_with(mock_request)

    @patch("agb.session.GetMcpResourceRequest")
    def test_info_success(self, MockGetMcpResourceRequest):
        from agb.model.response import OperationResult

        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_resource_data = MagicMock()
        MockGetMcpResourceRequest.return_value = mock_request
        self.agb.client.get_mcp_resource.return_value = mock_response

        # Mock the response methods
        mock_response.is_successful.return_value = True
        mock_response.request_id = "request-123"
        mock_response.get_resource_data.return_value = mock_resource_data
        mock_resource_data.session_id = "test_session_id"
        mock_resource_data.resource_url = "https://example.com/resource"
        mock_resource_data.desktop_info = None

        result = self.session.info()

        self.assertIsInstance(result, OperationResult)
        self.assertEqual(result.request_id, "request-123")
        self.assertTrue(result.success)
        self.assertEqual(result.data["session_id"], "test_session_id")
        self.assertEqual(result.data["resource_url"], "https://example.com/resource")

        MockGetMcpResourceRequest.assert_called_once_with(
            authorization="Bearer test_api_key", session_id="test_session_id"
        )
        self.agb.client.get_mcp_resource.assert_called_once_with(mock_request)

if __name__ == "__main__":
    unittest.main()