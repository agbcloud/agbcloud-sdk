#!/usr/bin/env python3
"""
Unit tests for CreateSessionRequest model in AGB SDK.
Tests CreateSessionRequest with various parameter combinations including new mcp_policy_id parameter.
"""

import unittest
from agb.api.models import CreateSessionRequest, CreateMcpSessionRequestPersistenceDataList


class TestCreateSessionRequest(unittest.TestCase):
    """Test CreateSessionRequest class."""

    def test_create_session_request_minimal(self):
        """Test CreateSessionRequest with minimal parameters."""
        request = CreateSessionRequest()

        self.assertEqual(request.authorization, "")
        self.assertIsNone(request.context_id)
        self.assertEqual(request.image_id, "")
        self.assertIsNone(request.labels)
        self.assertIsNone(request.persistence_data_list)
        self.assertEqual(request.session_id, "")
        self.assertIsNone(request.sdk_stats)
        self.assertIsNone(request.mcp_policy_id)

    def test_create_session_request_with_mcp_policy_id(self):
        """Test CreateSessionRequest with mcp_policy_id."""
        request = CreateSessionRequest(mcp_policy_id="policy-123")

        self.assertEqual(request.mcp_policy_id, "policy-123")
        self.assertEqual(request.authorization, "")
        self.assertIsNone(request.context_id)

    def test_create_session_request_get_body_with_mcp_policy_id(self):
        """Test get_body method with mcp_policy_id."""
        request = CreateSessionRequest(
            session_id="session-123",
            mcp_policy_id="policy-456",
            labels='{"env": "test"}'
        )

        body = request.get_body()

        self.assertEqual(body["sessionId"], "session-123")
        self.assertEqual(body["labels"], '{"env": "test"}')
        self.assertEqual(body["mcpPolicyId"], "policy-456")
        self.assertNotIn("contextId", body)

    def test_create_session_request_get_body_without_mcp_policy_id(self):
        """Test get_body method without mcp_policy_id."""
        request = CreateSessionRequest(
            session_id="session-123",
            labels='{"env": "test"}'
        )

        body = request.get_body()

        self.assertEqual(body["sessionId"], "session-123")
        self.assertEqual(body["labels"], '{"env": "test"}')
        self.assertNotIn("mcpPolicyId", body)

    def test_create_session_request_get_params(self):
        """Test get_params method."""
        request = CreateSessionRequest(
            image_id="image-123",
            sdk_stats={"version": "1.0", "source": "sdk"}
        )

        params = request.get_params()

        self.assertEqual(params["imageId"], "image-123")
        self.assertEqual(params["sdkStats"], '{"version":"1.0","source":"sdk"}')

    def test_create_session_request_with_persistence_data_list(self):
        """Test CreateSessionRequest with persistence_data_list."""
        persistence_data = CreateMcpSessionRequestPersistenceDataList(
            context_id="ctx-123",
            path="/tmp/test",
            policy="policy-abc"
        )

        request = CreateSessionRequest(
            mcp_policy_id="policy-789",
            persistence_data_list=[persistence_data]
        )

        body = request.get_body()

        self.assertEqual(body["mcpPolicyId"], "policy-789")
        self.assertIn("persistenceDataList", body)
        self.assertEqual(len(body["persistenceDataList"]), 1)
        self.assertEqual(body["persistenceDataList"][0]["contextId"], "ctx-123")


if __name__ == "__main__":
    unittest.main()