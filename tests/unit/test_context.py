import unittest
from unittest.mock import MagicMock

from agb.context import Context, ContextService
from agb.context_manager import ContextManager, ContextInfoResult, ContextStatusData
from agb.api.models.list_contexts_response import ListContextsResponseBodyData
from agb.api.models.get_context_response import GetContextResponseBodyData
from agb.api.models.get_context_info_response import GetContextInfoResponse


class TestContext(unittest.TestCase):
    def test_context_initialization(self):
        """Test that Context initializes with the correct attributes."""
        context = Context(
            id="test-id",
            name="test-context",
            created_at="2025-05-29T12:00:00Z",
            last_used_at="2025-05-29T12:30:00Z",
        )

        self.assertEqual(context.id, "test-id")
        self.assertEqual(context.name, "test-context")
        self.assertEqual(context.created_at, "2025-05-29T12:00:00Z")
        self.assertEqual(context.last_used_at, "2025-05-29T12:30:00Z")


class TestContextService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.agb = MagicMock()
        self.agb.api_key = "test-api-key"
        self.agb.client = MagicMock()
        self.context_service = ContextService(self.agb)

    def test_list_contexts(self):
        """Test listing contexts."""
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.get_contexts_data.return_value = [
            ListContextsResponseBodyData(
                id="context-1",
                name="context-1-name",
                create_time="2025-05-29T12:00:00Z",
                last_used_time="2025-05-29T12:30:00Z",
            ),
            ListContextsResponseBodyData(
                id="context-2",
                name="context-2-name",
                create_time="2025-05-29T13:00:00Z",
                last_used_time="2025-05-29T13:30:00Z",
            ),
        ]
        mock_response.is_successful.return_value = True
        self.agb.client.list_contexts.return_value = mock_response

        # Call the method
        result = self.context_service.list()

        # Verify the results
        self.assertEqual(len(result.contexts), 2)
        self.assertEqual(result.contexts[0].id, "context-1")
        self.assertEqual(result.contexts[0].name, "context-1-name")
        self.assertEqual(result.contexts[1].id, "context-2")
        self.assertEqual(result.contexts[1].name, "context-2-name")

    def test_get_context(self):
        """Test getting a context."""
        # Mock the response from the API
        mock_get_response = MagicMock()
        mock_get_response.get_context_data.return_value = GetContextResponseBodyData(
            id="context-1",
            name="test-context",
            create_time="2025-05-29T12:00:00Z",
            last_used_time="2025-05-29T12:30:00Z",
        )
        mock_get_response.is_successful.return_value = True
        self.agb.client.get_context.return_value = mock_get_response

        # Call the method
        result = self.context_service.get("test-context")

        # Verify the results
        self.assertTrue(result.success)
        self.assertEqual(result.context_id, "context-1")
        if result.context:
            self.assertEqual(result.context.id, "context-1")
            self.assertEqual(result.context.name, "test-context")

    def test_get_context_with_login_region_id(self):
        """Test getting a context with login_region_id parameter."""
        # Mock the response from the API
        mock_get_response = MagicMock()
        mock_get_response.get_context_data.return_value = GetContextResponseBodyData(
            id="context-1",
            name="test-context",
            create_time="2025-05-29T12:00:00Z",
            last_used_time="2025-05-29T12:30:00Z",
        )
        mock_get_response.is_successful.return_value = True
        self.agb.client.get_context.return_value = mock_get_response

        # Call the method with login_region_id
        result = self.context_service.get("test-context", login_region_id="us-west-1")

        # Verify the results
        self.assertTrue(result.success)
        self.assertEqual(result.context_id, "context-1")
        if result.context:
            self.assertEqual(result.context.id, "context-1")
            self.assertEqual(result.context.name, "test-context")

        # Verify the client was called with correct parameters
        self.agb.client.get_context.assert_called_once()
        call_args = self.agb.client.get_context.call_args[0][0]
        self.assertEqual(call_args.name, "test-context")
        self.assertEqual(call_args.allow_create, False)
        self.assertEqual(call_args.login_region_id, "us-west-1")

    def test_create_context(self):
        """Test creating a context."""
        # Mock the response from the API
        mock_get_response = MagicMock()
        mock_get_response.get_context_data.return_value = GetContextResponseBodyData(
            id="new-context-id",
            name="new-context",
            create_time="2025-05-29T12:00:00Z",
            last_used_time="2025-05-29T12:30:00Z",
        )
        mock_get_response.is_successful.return_value = True
        self.agb.client.get_context.return_value = mock_get_response

        # Call the method
        result = self.context_service.create("new-context")

        # Verify the results
        self.assertTrue(result.success)
        self.assertEqual(result.context_id, "new-context-id")
        if result.context:
            self.assertEqual(result.context.id, "new-context-id")
            self.assertEqual(result.context.name, "new-context")

    def test_update_context(self):
        """Test updating a context."""
        # Create a context to update
        context = Context(
            id="context-to-update", name="updated-name"
        )

        # Mock the API response
        mock_response = MagicMock()
        mock_response.is_successful.return_value = True
        self.agb.client.modify_context.return_value = mock_response

        # Call the method
        result = self.context_service.update(context)

        # Verify the API was called correctly
        self.agb.client.modify_context.assert_called_once()

        # Verify the results - should return the original context if update successful
        self.assertTrue(result.success)

    def test_delete_context(self):
        """Test deleting a context."""
        # Create a context to delete
        context = Context(
            id="context-to-delete", name="context-name"
        )

        # Mock the API response
        mock_response = MagicMock()
        mock_response.is_successful.return_value = True
        self.agb.client.delete_context.return_value = mock_response

        # Call the method
        result = self.context_service.delete(context)

        # Verify the API was called correctly
        self.agb.client.delete_context.assert_called_once()

        # Verify the results
        self.assertTrue(result.success)


class TestContextManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.session = MagicMock()
        self.session.get_api_key.return_value = "test-api-key"
        self.session.get_session_id.return_value = "test-session-id"
        self.session.get_client.return_value = MagicMock()
        self.context_manager = ContextManager(self.session)

    def test_info_success(self):
        """Test getting context info successfully."""
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.is_successful.return_value = True
        mock_response.get_context_status.return_value = '[{"type": "data", "data": "[{\\"contextId\\": \\"ctx-123\\", \\"path\\": \\"/home/wuying\\", \\"status\\": \\"completed\\", \\"taskType\\": \\"upload\\", \\"startTime\\": 1640995200, \\"finishTime\\": 1640995260, \\"errorMessage\\": \\"\\"}]"}]'
        mock_response.request_id = "req-123"
        self.session.get_client().get_context_info.return_value = mock_response

        # Call the method
        result = self.context_manager.info()

        # Verify the results
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-123")
        self.assertEqual(len(result.context_status_data), 1)

        status_data = result.context_status_data[0]
        self.assertEqual(status_data.context_id, "ctx-123")
        self.assertEqual(status_data.path, "/home/wuying")
        self.assertEqual(status_data.status, "completed")
        self.assertEqual(status_data.task_type, "upload")
        self.assertEqual(status_data.start_time, 1640995200)
        self.assertEqual(status_data.finish_time, 1640995260)
        self.assertEqual(status_data.error_message, "")

    def test_info_with_parameters(self):
        """Test getting context info with specific parameters."""
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.is_successful.return_value = True
        mock_response.get_context_status.return_value = '[{"type": "data", "data": "[{\\"contextId\\": \\"ctx-456\\", \\"path\\": \\"/home/test\\", \\"status\\": \\"in_progress\\", \\"taskType\\": \\"download\\", \\"startTime\\": 1640995300, \\"finishTime\\": 0, \\"errorMessage\\": \\"\\"}]"}]'
        mock_response.request_id = "req-456"
        self.session.get_client().get_context_info.return_value = mock_response

        # Call the method with parameters
        result = self.context_manager.info(
            context_id="ctx-456",
            path="/home/test",
            task_type="download"
        )

        # Verify the results
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-456")
        self.assertEqual(len(result.context_status_data), 1)

        status_data = result.context_status_data[0]
        self.assertEqual(status_data.context_id, "ctx-456")
        self.assertEqual(status_data.path, "/home/test")
        self.assertEqual(status_data.status, "in_progress")
        self.assertEqual(status_data.task_type, "download")
        self.assertEqual(status_data.start_time, 1640995300)
        self.assertEqual(status_data.finish_time, 0)

    def test_info_with_error(self):
        """Test getting context info with error status."""
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.is_successful.return_value = True
        mock_response.get_context_status.return_value = '[{"type": "data", "data": "[{\\"contextId\\": \\"ctx-789\\", \\"path\\": \\"/home/error\\", \\"status\\": \\"failed\\", \\"taskType\\": \\"upload\\", \\"startTime\\": 1640995400, \\"finishTime\\": 1640995460, \\"errorMessage\\": \\"Network timeout\\"}]"}]'
        mock_response.request_id = "req-789"
        self.session.get_client().get_context_info.return_value = mock_response

        # Call the method
        result = self.context_manager.info()

        # Verify the results
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-789")
        self.assertEqual(len(result.context_status_data), 1)

        status_data = result.context_status_data[0]
        self.assertEqual(status_data.context_id, "ctx-789")
        self.assertEqual(status_data.path, "/home/error")
        self.assertEqual(status_data.status, "failed")
        self.assertEqual(status_data.task_type, "upload")
        self.assertEqual(status_data.error_message, "Network timeout")

    def test_info_api_failure(self):
        """Test getting context info when API call fails."""
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.is_successful.return_value = False
        mock_response.get_error_message.return_value = "API error"
        mock_response.request_id = "req-error"
        self.session.get_client().get_context_info.return_value = mock_response

        # Call the method
        result = self.context_manager.info()

        # Verify the results
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "req-error")
        self.assertEqual(result.error_message, "API error")
        self.assertEqual(len(result.context_status_data), 0)

    def test_info_empty_response(self):
        """Test getting context info with empty response."""
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.is_successful.return_value = True
        mock_response.get_context_status.return_value = None
        mock_response.request_id = "req-empty"
        self.session.get_client().get_context_info.return_value = mock_response

        # Call the method
        result = self.context_manager.info()

        # Verify the results
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-empty")
        self.assertEqual(len(result.context_status_data), 0)

    def test_info_invalid_json(self):
        """Test getting context info with invalid JSON response."""
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.is_successful.return_value = True
        mock_response.get_context_status.return_value = "invalid json"
        mock_response.request_id = "req-invalid"
        self.session.get_client().get_context_info.return_value = mock_response

        # Call the method
        result = self.context_manager.info()

        # Verify the results - should fail due to invalid JSON
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "req-invalid")
        self.assertEqual(len(result.context_status_data), 0)
        self.assertIn("Unexpected error parsing context status", result.error_message)

    def test_info_multiple_status_items(self):
        """Test getting context info with multiple status items."""
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.is_successful.return_value = True
        mock_response.get_context_status.return_value = '''[{"type": "data", "data": "[{\\"contextId\\": \\"ctx-1\\", \\"path\\": \\"/home/path1\\", \\"status\\": \\"completed\\", \\"taskType\\": \\"upload\\", \\"startTime\\": 1640995200, \\"finishTime\\": 1640995260, \\"errorMessage\\": \\"\\"}, {\\"contextId\\": \\"ctx-2\\", \\"path\\": \\"/home/path2\\", \\"status\\": \\"in_progress\\", \\"taskType\\": \\"download\\", \\"startTime\\": 1640995300, \\"finishTime\\": 0, \\"errorMessage\\": \\"\\"}]"}]'''
        mock_response.request_id = "req-multiple"
        self.session.get_client().get_context_info.return_value = mock_response

        # Call the method
        result = self.context_manager.info()

        # Verify the results
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-multiple")
        self.assertEqual(len(result.context_status_data), 2)

        # Check first item
        status_data_1 = result.context_status_data[0]
        self.assertEqual(status_data_1.context_id, "ctx-1")
        self.assertEqual(status_data_1.path, "/home/path1")
        self.assertEqual(status_data_1.status, "completed")
        self.assertEqual(status_data_1.task_type, "upload")

        # Check second item
        status_data_2 = result.context_status_data[1]
        self.assertEqual(status_data_2.context_id, "ctx-2")
        self.assertEqual(status_data_2.path, "/home/path2")
        self.assertEqual(status_data_2.status, "in_progress")
        self.assertEqual(status_data_2.task_type, "download")

    def test_info_with_none_parameters(self):
        """Test getting context info with None parameters."""
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.is_successful.return_value = True
        mock_response.get_context_status.return_value = '[]'
        mock_response.request_id = "req-none"
        self.session.get_client().get_context_info.return_value = mock_response

        # Call the method with None parameters
        result = self.context_manager.info(
            context_id=None,
            path=None,
            task_type=None
        )

        # Verify the results
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-none")
        self.assertEqual(len(result.context_status_data), 0)

        # Verify the request was created with default values
        self.session.get_client().get_context_info.assert_called_once()
        call_args = self.session.get_client().get_context_info.call_args[0][0]
        self.assertEqual(call_args.authorization, "Bearer test-api-key")
        self.assertEqual(call_args.session_id, "test-session-id")
        self.assertIsNone(call_args.context_id)
        self.assertIsNone(call_args.path)
        self.assertIsNone(call_args.task_type)


if __name__ == "__main__":
    unittest.main()
