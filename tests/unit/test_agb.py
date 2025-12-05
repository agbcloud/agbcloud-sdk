import os
import unittest
from unittest.mock import MagicMock, patch

from agb import AGB
from agb.session_params import CreateSessionParams
from agb.api.models import CreateSessionResponse
from agb.api.models.create_session_response import SessionData

class TestAGB(unittest.TestCase):
    """Test the functionality of the main AGB class"""

    @patch.dict(os.environ, {"AGB_API_KEY": "test-api-key"})
    @patch("agb.agb.load_config")
    @patch("agb.agb.mcp_client")
    def test_initialization_with_env_var(self, mock_mcp_client, mock_load_config):
        """Test initializing AGB with an API key from environment variable"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.endpoint = "test.endpoint.com"
        mock_config.timeout_ms = 30000
        mock_load_config.return_value = mock_config

        # Mock client
        mock_client = MagicMock()
        mock_mcp_client.return_value = mock_client

        # Create AGB instance
        agb = AGB()

        # Verify results
        self.assertEqual(agb.api_key, "test-api-key")
        self.assertEqual(agb.client, mock_client)
        self.assertDictEqual(agb._sessions, {})
        self.assertIsNotNone(agb._lock)
        self.assertIsNotNone(agb.context)

    @patch("agb.agb.load_config")
    @patch("agb.agb.mcp_client")
    def test_initialization_with_provided_key(self, mock_mcp_client, mock_load_config):
        """Test initializing AGB with a provided API key"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.endpoint = "another.endpoint.com"
        mock_config.timeout_ms = 60000
        mock_load_config.return_value = mock_config

        # Mock client
        mock_client = MagicMock()
        mock_mcp_client.return_value = mock_client

        # Create AGB instance
        agb = AGB(api_key="provided-api-key")

        # Verify results
        self.assertEqual(agb.api_key, "provided-api-key")

    @patch.dict(os.environ, {}, clear=True)
    @patch("agb.agb.load_config")
    def test_initialization_without_api_key(self, mock_load_config):
        """Test initialization failure when no API key is available"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.endpoint = "test.endpoint.com"
        mock_config.timeout_ms = 30000
        mock_load_config.return_value = mock_config

        # Test initialization failure
        with self.assertRaises(ValueError) as context:
            AGB()

        self.assertIn("API key is required", str(context.exception))

    @patch("agb.agb.load_config")
    @patch("agb.agb.mcp_client")
    def test_create_session_success(self, mock_mcp_client, mock_load_config):
        """Test successfully creating a session"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.endpoint = "test.endpoint.com"
        mock_config.timeout_ms = 30000
        mock_load_config.return_value = mock_config

        # Mock client and response
        mock_client = MagicMock()
        mock_response = MagicMock(spec=CreateSessionResponse)

        # Mock response data
        mock_data = MagicMock(spec=SessionData)
        mock_data.success = True
        mock_data.session_id = "new-session-id"
        mock_data.resource_url = "http://resource.url"
        mock_data.app_instance_id = "app-instance-id"
        mock_data.resource_id = "resource-id"
        mock_response.data = mock_data
        mock_response.request_id = "create-request-id"

        # Mock response methods
        mock_response.get_session_id.return_value = "new-session-id"
        mock_response.get_resource_url.return_value = "http://resource.url"
        mock_response.get_error_message.return_value = None
        mock_response.to_dict.return_value = {
            "data": {
                "sessionId": "new-session-id",
                "resourceUrl": "http://resource.url",
                "success": True
            },
            "requestId": "create-request-id"
        }

        mock_client.create_mcp_session.return_value = mock_response
        mock_mcp_client.return_value = mock_client

        # Create AGB instance and session parameters
        agb = AGB(api_key="test-key")
        params = CreateSessionParams(
            image_id="agb-code-space-1",
            labels={"env": "test"},
        )

        # Test creating a session
        result = agb.create(params)

        # Verify results
        self.assertEqual(result.request_id, "create-request-id")
        self.assertTrue(result.success)
        self.assertIsNotNone(result.session)
        self.assertEqual(result.session.session_id, "new-session-id")

        # Verify session was added to the internal dictionary
        self.assertIn("new-session-id", agb._sessions)
        self.assertEqual(agb._sessions["new-session-id"], result.session)

    @patch("agb.agb.load_config")
    @patch("agb.agb.mcp_client")
    def test_create_session_invalid_response(self, mock_mcp_client, mock_load_config):
        """Test handling invalid response when creating a session"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.endpoint = "test.endpoint.com"
        mock_config.timeout_ms = 30000
        mock_load_config.return_value = mock_config

        # Mock client and invalid response
        mock_client = MagicMock()
        mock_response = MagicMock(spec=CreateSessionResponse)
        mock_response.data = None  # Invalid Data field
        mock_response.request_id = "error-request-id"
        mock_response.get_session_id.return_value = None
        mock_response.get_error_message.return_value = "Invalid response format"

        mock_client.create_mcp_session.return_value = mock_response
        mock_mcp_client.return_value = mock_client

        # Create AGB instance
        agb = AGB(api_key="test-key")

        # Test session creation with invalid response
        params = CreateSessionParams(image_id="agb-code-space-1")
        result = agb.create(params)

        # Verify the result indicates failure
        self.assertFalse(result.success)
        self.assertIsNone(result.session)
        self.assertIn("Invalid response format", result.error_message)

    @patch("agb.agb.load_config")
    @patch("agb.agb.mcp_client")
    def test_create_session_with_failure_response(self, mock_mcp_client, mock_load_config):
        """Test handling failure response when creating a session"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.endpoint = "test.endpoint.com"
        mock_config.timeout_ms = 30000
        mock_load_config.return_value = mock_config

        # Mock client and failure response
        mock_client = MagicMock()
        mock_response = MagicMock(spec=CreateSessionResponse)

        # Mock response data with failure
        mock_data = MagicMock(spec=SessionData)
        mock_data.success = False
        mock_data.err_msg = "Session creation failed"
        mock_response.data = mock_data
        mock_response.request_id = "failure-request-id"

        mock_client.create_mcp_session.return_value = mock_response
        mock_mcp_client.return_value = mock_client

        # Create AGB instance
        agb = AGB(api_key="test-key")

        # Test session creation with failure response
        params = CreateSessionParams(image_id="agb-code-space-1")
        result = agb.create(params)

        # Verify the result indicates failure
        self.assertFalse(result.success)
        self.assertIsNone(result.session)
        self.assertEqual(result.error_message, "Session creation failed")
        self.assertEqual(result.request_id, "failure-request-id")

    @patch("agb.agb.load_config")
    @patch("agb.agb.mcp_client")
    def test_create_session_with_exception(self, mock_mcp_client, mock_load_config):
        """Test handling exception when creating a session"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.endpoint = "test.endpoint.com"
        mock_config.timeout_ms = 30000
        mock_load_config.return_value = mock_config

        # Mock client to raise exception
        mock_client = MagicMock()
        mock_client.create_mcp_session.side_effect = Exception("Network error")
        mock_mcp_client.return_value = mock_client

        # Create AGB instance
        agb = AGB(api_key="test-key")

        # Test session creation with exception
        params = CreateSessionParams(image_id="agb-code-space-1")
        result = agb.create(params)

        # Verify the result indicates failure
        self.assertFalse(result.success)
        self.assertIsNone(result.session)
        self.assertIn("Failed to create session: Network error", result.error_message)

    @patch("agb.agb.load_config")
    @patch("agb.agb.mcp_client")
    def test_list(self, mock_mcp_client, mock_load_config):
        """Test listing sessions using the new list API"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.endpoint = "test.endpoint.com"
        mock_config.timeout_ms = 30000
        mock_load_config.return_value = mock_config

        # Mock client and response
        mock_client = MagicMock()
        from agb.api.models.list_session_response import ListSessionResponse

        # Create mock response
        mock_response = MagicMock(spec=ListSessionResponse)
        mock_response.is_successful.return_value = True
        mock_response.get_session_data.return_value = [
            MagicMock(session_id="session-1", session_status="RUNNING"),
            MagicMock(session_id="session-2", session_status="RUNNING"),
            MagicMock(session_id="session-3", session_status="RUNNING"),
        ]
        mock_response.get_count.return_value = 3
        mock_response.get_max_results.return_value = 10
        mock_response.get_next_token.return_value = None
        mock_response.request_id = "list-request-id"

        mock_client.list_sessions.return_value = mock_response
        mock_mcp_client.return_value = mock_client

        # Create AGB instance
        agb = AGB(api_key="test-key")

        # Test listing all sessions (no labels)
        result = agb.list()
        self.assertEqual(result.request_id, "list-request-id")
        self.assertEqual(len(result.session_ids), 3)
        self.assertEqual(result.total_count, 3)
        self.assertTrue(result.success)

        # Test listing sessions with labels
        result = agb.list(labels={"env": "prod"})
        self.assertEqual(result.request_id, "list-request-id")
        self.assertEqual(len(result.session_ids), 3)

        # Test listing sessions with pagination
        result = agb.list(labels={"env": "prod"}, page=1, limit=2)
        self.assertEqual(result.request_id, "list-request-id")
        self.assertEqual(len(result.session_ids), 3)

    @patch("agb.agb.load_config")
    @patch("agb.agb.mcp_client")
    def test_list_pagination(self, mock_mcp_client, mock_load_config):
        """Test listing sessions with pagination"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.endpoint = "test.endpoint.com"
        mock_config.timeout_ms = 30000
        mock_load_config.return_value = mock_config

        # Mock client and response for pagination
        mock_client = MagicMock()
        from agb.api.models.list_session_response import ListSessionResponse

        # Create mock response for first page (page=1, direct call)
        mock_response_page1 = MagicMock(spec=ListSessionResponse)
        mock_response_page1.is_successful.return_value = True
        mock_response_page1.get_session_data.return_value = [
            MagicMock(session_id="session-1", session_status="RUNNING"),
            MagicMock(session_id="session-2", session_status="RUNNING"),
        ]
        mock_response_page1.get_count.return_value = 5
        mock_response_page1.get_max_results.return_value = 2
        mock_response_page1.get_next_token.return_value = "next-token-123"
        mock_response_page1.request_id = "list-page1-request-id"

        # For page=2, agb.list() will make 2 API calls:
        # 1. First call to get next_token from page 1
        # 2. Second call to get actual page 2 data

        # Mock response for getting next_token (internal call)
        mock_response_get_token = MagicMock(spec=ListSessionResponse)
        mock_response_get_token.is_successful.return_value = True
        mock_response_get_token.get_next_token.return_value = "next-token-123"
        mock_response_get_token.get_count.return_value = 5
        mock_response_get_token.request_id = "internal-request-id"

        # Mock response for actual page 2 data
        mock_response_page2 = MagicMock(spec=ListSessionResponse)
        mock_response_page2.is_successful.return_value = True
        mock_response_page2.get_session_data.return_value = [
            MagicMock(session_id="session-3", session_status="RUNNING"),
            MagicMock(session_id="session-4", session_status="RUNNING"),
        ]
        mock_response_page2.get_count.return_value = 5
        mock_response_page2.get_max_results.return_value = 2
        mock_response_page2.get_next_token.return_value = "next-token-456"
        mock_response_page2.request_id = "list-page2-request-id"

        # Configure mock client to return responses in order:
        # 1. First call: page 1 direct
        # 2. Second call: get token for page 2
        # 3. Third call: actual page 2 data
        mock_client.list_sessions.side_effect = [
            mock_response_page1,      # page=1 call
            mock_response_get_token,  # page=2 internal call to get token
            mock_response_page2       # page=2 final call
        ]
        mock_mcp_client.return_value = mock_client

        # Create AGB instance
        agb = AGB(api_key="test-key")

        # Test first page (single API call)
        result_page1 = agb.list(labels={"env": "test"}, page=1, limit=2)
        self.assertEqual(result_page1.request_id, "list-page1-request-id")
        self.assertEqual(len(result_page1.session_ids), 2)
        self.assertEqual(result_page1.total_count, 5)
        self.assertEqual(result_page1.max_results, 2)
        self.assertEqual(result_page1.next_token, "next-token-123")
        self.assertTrue(result_page1.success)

        # Test second page (two API calls: get token + get data)
        result_page2 = agb.list(labels={"env": "test"}, page=2, limit=2)
        self.assertEqual(result_page2.request_id, "list-page2-request-id")
        self.assertEqual(len(result_page2.session_ids), 2)
        self.assertEqual(result_page2.total_count, 5)
        self.assertEqual(result_page2.max_results, 2)
        self.assertEqual(result_page2.next_token, "next-token-456")
        self.assertTrue(result_page2.success)

    @patch("agb.agb.load_config")
    @patch("agb.agb.mcp_client")
    def test_delete_session_success(self, mock_mcp_client, mock_load_config):
        """Test successfully deleting a session"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.endpoint = "test.endpoint.com"
        mock_config.timeout_ms = 30000
        mock_load_config.return_value = mock_config

        # Mock client
        mock_client = MagicMock()
        mock_mcp_client.return_value = mock_client

        # Create AGB instance
        agb = AGB(api_key="test-key")

        # Create a mock session
        from agb.session import Session
        from agb.model.response import DeleteResult

        session = Session(agb, "session-to-delete")
        agb._sessions["session-to-delete"] = session

        # Mock session delete method
        mock_delete_result = DeleteResult(
            request_id="delete-request-id",
            success=True
        )
        session.delete = MagicMock(return_value=mock_delete_result)

        # Test deleting the session
        result = agb.delete(session)

        # Verify results
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "delete-request-id")

        # Verify session was removed from internal dictionary
        self.assertNotIn("session-to-delete", agb._sessions)

    @patch("agb.agb.load_config")
    @patch("agb.agb.mcp_client")
    def test_delete_session_with_sync_context(self, mock_mcp_client, mock_load_config):
        """Test deleting a session with context synchronization"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.endpoint = "test.endpoint.com"
        mock_config.timeout_ms = 30000
        mock_load_config.return_value = mock_config

        # Mock client
        mock_client = MagicMock()
        mock_mcp_client.return_value = mock_client

        # Create AGB instance
        agb = AGB(api_key="test-key")

        # Create a mock session
        from agb.session import Session
        from agb.model.response import DeleteResult

        session = Session(agb, "session-with-sync")
        agb._sessions["session-with-sync"] = session

        # Mock session delete method
        mock_delete_result = DeleteResult(
            request_id="sync-delete-request-id",
            success=True
        )
        session.delete = MagicMock(return_value=mock_delete_result)

        # Test deleting the session with sync_context=True
        result = agb.delete(session, sync_context=True)

        # Verify results
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "sync-delete-request-id")

        # Verify session.delete was called with sync_context=True
        session.delete.assert_called_once_with(sync_context=True)

        # Verify session was removed from internal dictionary
        self.assertNotIn("session-with-sync", agb._sessions)

    @patch("agb.agb.load_config")
    @patch("agb.agb.mcp_client")
    def test_delete_session_failure(self, mock_mcp_client, mock_load_config):
        """Test handling failure when deleting a session"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.endpoint = "test.endpoint.com"
        mock_config.timeout_ms = 30000
        mock_load_config.return_value = mock_config

        # Mock client
        mock_client = MagicMock()
        mock_mcp_client.return_value = mock_client

        # Create AGB instance
        agb = AGB(api_key="test-key")

        # Create a mock session
        from agb.session import Session

        session = Session(agb, "session-delete-fail")
        agb._sessions["session-delete-fail"] = session

        # Mock session delete method to raise exception
        session.delete = MagicMock(side_effect=Exception("Delete failed"))

        # Test deleting the session
        result = agb.delete(session)

        # Verify results
        self.assertFalse(result.success)
        self.assertIn("Failed to delete session: Delete failed", result.error_message)

        # Verify session was NOT removed from internal dictionary on failure
        self.assertIn("session-delete-fail", agb._sessions)

if __name__ == "__main__":
    unittest.main()