from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch
from typing import Any, cast
from agb.session import Session, DeleteResult
from agb.model.response import SessionStatusResult, SessionMetricsResult, SessionMetrics

class DummyAGB:
    def __init__(self):
        self.client = MagicMock()
        self.api_key = "test_api_key"

    def get_api_key(self):
        return self.api_key

    def get_client(self):
        return self.client

    def get_session(self, session_id):
        # Default implementation - can be overridden in tests
        result = MagicMock()
        result.success = False
        result.code = "InvalidMcpSession.NotFound"
        result.error_message = "Session not found"
        result.http_status_code = 400
        return result

class TestSession(unittest.TestCase):
    def setUp(self):
        self.agb = DummyAGB()
        self.session_id = "test_session_id"
        self.session = Session(cast(Any, self.agb), self.session_id)

    def test_validate_labels_success(self):
        # Test successful validation with valid labels
        labels = {"key1": "value1", "key2": "value2"}
        result = self.session._validate_labels(labels)
        self.assertIsNone(result)

    def test_validate_labels_none(self):
        # Test validation with None labels
        labels = None
        result = self.session._validate_labels(cast(Any, labels))
        self.assertIsNotNone(result)
        assert result is not None
        self.assertFalse(result.success)
        self.assertIn("Labels cannot be null", result.error_message)

    def test_validate_labels_list(self):
        # Test validation with list instead of dict
        labels = ["key1", "value1"]
        result = self.session._validate_labels(cast(Any, labels))
        self.assertIsNotNone(result)
        assert result is not None
        self.assertFalse(result.success)
        self.assertIn("Labels cannot be an array", result.error_message)

    def test_validate_labels_empty_dict(self):
        # Test validation with empty dict
        labels = {}
        result = self.session._validate_labels(labels)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertFalse(result.success)
        self.assertIn("Labels cannot be empty", result.error_message)

    def test_validate_labels_empty_key(self):
        # Test validation with empty key
        labels = {"": "value1"}
        result = self.session._validate_labels(labels)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertFalse(result.success)
        self.assertIn("Label keys cannot be empty", result.error_message)

    def test_validate_labels_empty_value(self):
        # Test validation with empty value
        labels = {"key1": ""}
        result = self.session._validate_labels(labels)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertFalse(result.success)
        self.assertIn("Label values cannot be empty", result.error_message)

    def test_validate_labels_none_value(self):
        # Test validation with None value
        labels = {"key1": None}
        result = self.session._validate_labels(cast(Any, labels))
        self.assertIsNotNone(result)
        assert result is not None
        self.assertFalse(result.success)
        self.assertIn("Label values cannot be empty", result.error_message)

    def test_initialization(self):
        self.assertEqual(self.session.session_id, self.session_id)
        self.assertEqual(self.session.agb, self.agb)
        self.assertIsNotNone(self.session.file)
        self.assertIsNotNone(self.session.command)
        self.assertEqual(self.session.file.session, self.session)
        self.assertEqual(self.session.command.session, self.session)

    def test_get_api_key(self):
        self.assertEqual(self.session.get_api_key(), "test_api_key")

    def test_get_client(self):
        self.assertEqual(self.session.get_client(), self.agb.client)

    def test_get_session_id(self):
        self.assertEqual(self.session.get_session_id(), "test_session_id")

    @patch("agb.session.DeleteSessionAsyncRequest")
    def test_delete_success(self, MockDeleteSessionAsyncRequest):
        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response_body = MagicMock()
        MockDeleteSessionAsyncRequest.return_value = mock_request
        self.agb.client.delete_session_async.return_value = mock_response

        # Mock the response methods
        mock_response.is_successful.return_value = True
        mock_response.body = mock_response_body
        mock_response_body.request_id = "request-123"
        mock_response.request_id = "request-123"

        # Mock get_status to return a normal flow: DELETING -> FINISH
        self.session.get_status = MagicMock(
            side_effect=[
                SessionStatusResult(
                    request_id="rid-1",
                    http_status_code=200,
                    code="",
                    success=True,
                    status="DELETING",
                    error_message="",
                ),
                SessionStatusResult(
                    request_id="rid-2",
                    http_status_code=200,
                    code="",
                    success=True,
                    status="FINISH",
                    error_message="",
                ),
            ]
        )

        with patch("time.sleep", return_value=None):
            result = self.session.delete()
        self.assertIsInstance(result, DeleteResult)
        self.assertEqual(result.request_id, "request-123")
        self.assertTrue(result.success)
        self.assertGreaterEqual(self.session.get_status.call_count, 2)

        MockDeleteSessionAsyncRequest.assert_called_once_with(
            authorization="Bearer test_api_key", session_id="test_session_id"
        )
        self.agb.client.delete_session_async.assert_called_once_with(mock_request)

    @patch("agb.session.DeleteSessionAsyncRequest")
    def test_delete_without_params(self, MockDeleteSessionAsyncRequest):
        # Test default behavior when no parameters are provided
        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response_body = MagicMock()
        MockDeleteSessionAsyncRequest.return_value = mock_request
        self.agb.client.delete_session_async.return_value = mock_response

        # Mock the response methods
        mock_response.is_successful.return_value = True
        mock_response.body = mock_response_body
        mock_response_body.request_id = "request-123"
        mock_response.request_id = "request-123"

        # Set up context mock object
        self.session.context = MagicMock()

        # Mock get_status to return NotFound error (session deleted)
        self.session.get_status = MagicMock(
            return_value=SessionStatusResult(
                request_id="",
                http_status_code=400,
                code="InvalidMcpSession.NotFound",
                success=False,
                status="",
                error_message="Session not found",
            )
        )

        # Call delete method without parameters
        result = self.session.delete()
        self.assertIsInstance(result, DeleteResult)
        self.assertTrue(result.success)

        # Verify sync was not called
        self.session.context.sync.assert_not_called()

        # Verify API call is correct
        MockDeleteSessionAsyncRequest.assert_called_once_with(
            authorization="Bearer test_api_key", session_id="test_session_id"
        )
        self.agb.client.delete_session_async.assert_called_once_with(mock_request)

    @patch("agb.session.DeleteSessionAsyncRequest")
    def test_delete_with_sync_context(self, MockDeleteSessionAsyncRequest):
        # Test behavior when sync_context=True
        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response_body = MagicMock()
        MockDeleteSessionAsyncRequest.return_value = mock_request
        self.agb.client.delete_session_async.return_value = mock_response

        # Mock the response methods
        mock_response.is_successful.return_value = True
        mock_response.body = mock_response_body
        mock_response_body.request_id = "request-123"
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

        # Mock get_status to return NotFound error (session deleted)
        self.session.get_status = MagicMock(
            return_value=SessionStatusResult(
                request_id="",
                http_status_code=400,
                code="InvalidMcpSession.NotFound",
                success=False,
                status="",
                error_message="Session not found",
            )
        )

        # Call delete method with sync_context=True
        result = self.session.delete(sync_context=True)
        self.assertIsInstance(result, DeleteResult)
        self.assertTrue(result.success)

        # Verify sync was called (but not info since we're not using callback mode)
        self.session.context.sync.assert_called_once()

        # Verify API call is correct
        MockDeleteSessionAsyncRequest.assert_called_once_with(
            authorization="Bearer test_api_key", session_id="test_session_id"
        )
        self.agb.client.delete_session_async.assert_called_once_with(mock_request)

    @patch("agb.session.DeleteSessionAsyncRequest")
    def test_delete_failure(self, MockDeleteSessionAsyncRequest):
        mock_request = MagicMock()
        MockDeleteSessionAsyncRequest.return_value = mock_request
        self.agb.client.delete_session_async.side_effect = Exception("Test error")

        result = self.session.delete()
        self.assertIsInstance(result, DeleteResult)
        self.assertFalse(result.success)
        self.assertEqual(
            result.error_message,
            f"Failed to delete session {self.session_id}: Test error",
        )

        MockDeleteSessionAsyncRequest.assert_called_once_with(
            authorization="Bearer test_api_key", session_id="test_session_id"
        )
        self.agb.client.delete_session_async.assert_called_once_with(mock_request)

    @patch("agb.session.DeleteSessionAsyncRequest")
    def test_delete_api_failure_response(self, MockDeleteSessionAsyncRequest):
        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response_body = MagicMock()
        MockDeleteSessionAsyncRequest.return_value = mock_request
        self.agb.client.delete_session_async.return_value = mock_response

        # Mock the response methods to return a failure response
        mock_response.is_successful.return_value = False
        mock_response.body = mock_response_body
        mock_response_body.code = "ErrorCode"
        mock_response_body.message = "API Error"
        mock_response_body.request_id = "request-123"
        mock_response.request_id = "request-123"

        # Mock to_map to return proper structure
        mock_response.to_map.return_value = {
            "json": {},
            "request_id": "request-123"
        }

        result = self.session.delete()
        self.assertIsInstance(result, DeleteResult)
        self.assertEqual(result.request_id, "request-123")
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "[ErrorCode] API Error")

        MockDeleteSessionAsyncRequest.assert_called_once_with(
            authorization="Bearer test_api_key", session_id="test_session_id"
        )
        self.agb.client.delete_session_async.assert_called_once_with(mock_request)

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

    @patch.object(Session, 'call_mcp_tool')
    def test_get_metrics_success(self, mock_call_mcp_tool):
        """Test successful get_metrics operation"""
        from agb.model.response import McpToolResult
        
        # Mock successful tool result with metrics data
        mock_tool_result = McpToolResult(
            request_id="request-123",
            success=True,
            data='{"cpu_count": 4, "cpu_used_pct": 25.5, "disk_total": 1000000, "disk_used": 500000, "mem_total": 8192, "mem_used": 4096, "rx_rate_kbyte_per_s": 100.5, "tx_rate_kbyte_per_s": 50.2, "rx_used_kbyte": 1024.0, "tx_used_kbyte": 512.0, "timestamp": "2024-01-01T12:00:00Z"}',
            error_message=""
        )
        mock_call_mcp_tool.return_value = mock_tool_result

        result = self.session.get_metrics()

        self.assertIsInstance(result, SessionMetricsResult)
        self.assertEqual(result.request_id, "request-123")
        self.assertTrue(result.success)
        self.assertIsNotNone(result.metrics)
        
        # Verify metrics data
        metrics = result.metrics
        self.assertEqual(metrics.cpu_count, 4)
        self.assertEqual(metrics.cpu_used_pct, 25.5)
        self.assertEqual(metrics.disk_total, 1000000)
        self.assertEqual(metrics.disk_used, 500000)
        self.assertEqual(metrics.mem_total, 8192)
        self.assertEqual(metrics.mem_used, 4096)
        self.assertEqual(metrics.rx_rate_kbyte_per_s, 100.5)
        self.assertEqual(metrics.tx_rate_kbyte_per_s, 50.2)
        self.assertEqual(metrics.rx_used_kbyte, 1024.0)
        self.assertEqual(metrics.tx_used_kbyte, 512.0)
        self.assertEqual(metrics.timestamp, "2024-01-01T12:00:00Z")

        # Verify tool was called correctly
        mock_call_mcp_tool.assert_called_once_with(
            tool_name="get_metrics",
            args={},
            read_timeout=None,
            connect_timeout=None
        )

    @patch.object(Session, 'call_mcp_tool')
    def test_get_metrics_with_timeouts(self, mock_call_mcp_tool):
        """Test get_metrics with custom timeouts"""
        from agb.model.response import McpToolResult
        
        # Mock successful tool result
        mock_tool_result = McpToolResult(
            request_id="request-456",
            success=True,
            data='{"cpu_count": 2, "cpu_used_pct": 10.0, "timestamp": "2024-01-01T12:00:00Z"}',
            error_message=""
        )
        mock_call_mcp_tool.return_value = mock_tool_result

        result = self.session.get_metrics(read_timeout=5000, connect_timeout=3000)

        self.assertIsInstance(result, SessionMetricsResult)
        self.assertTrue(result.success)
        
        # Verify tool was called with correct timeouts
        mock_call_mcp_tool.assert_called_once_with(
            tool_name="get_metrics",
            args={},
            read_timeout=5000,
            connect_timeout=3000
        )

    @patch.object(Session, 'call_mcp_tool')
    def test_get_metrics_tool_failure(self, mock_call_mcp_tool):
        """Test get_metrics when underlying tool call fails"""
        from agb.model.response import McpToolResult
        
        # Mock failed tool result
        mock_tool_result = McpToolResult(
            request_id="request-789",
            success=False,
            data="",
            error_message="Tool execution failed"
        )
        mock_call_mcp_tool.return_value = mock_tool_result

        result = self.session.get_metrics()

        self.assertIsInstance(result, SessionMetricsResult)
        self.assertEqual(result.request_id, "request-789")
        self.assertFalse(result.success)
        self.assertIsNone(result.metrics)
        self.assertEqual(result.error_message, "Tool execution failed")
        self.assertEqual(result.raw, {})

    @patch.object(Session, 'call_mcp_tool')
    def test_get_metrics_invalid_json(self, mock_call_mcp_tool):
        """Test get_metrics with invalid JSON response"""
        from agb.model.response import McpToolResult
        
        # Mock tool result with invalid JSON
        mock_tool_result = McpToolResult(
            request_id="request-invalid",
            success=True,
            data='invalid json data',
            error_message=""
        )
        mock_call_mcp_tool.return_value = mock_tool_result

        result = self.session.get_metrics()

        self.assertIsInstance(result, SessionMetricsResult)
        self.assertEqual(result.request_id, "request-invalid")
        self.assertFalse(result.success)
        self.assertIsNone(result.metrics)
        self.assertIn("Failed to parse get_metrics response", result.error_message)
        self.assertEqual(result.raw, {})

    @patch.object(Session, 'call_mcp_tool')
    def test_get_metrics_non_dict_response(self, mock_call_mcp_tool):
        """Test get_metrics with non-dict JSON response"""
        from agb.model.response import McpToolResult
        
        # Mock tool result with array instead of object
        mock_tool_result = McpToolResult(
            request_id="request-array",
            success=True,
            data='["not", "an", "object"]',
            error_message=""
        )
        mock_call_mcp_tool.return_value = mock_tool_result

        result = self.session.get_metrics()

        self.assertIsInstance(result, SessionMetricsResult)
        self.assertEqual(result.request_id, "request-array")
        self.assertFalse(result.success)
        self.assertIsNone(result.metrics)
        self.assertIn("get_metrics returned non-object JSON", result.error_message)
        self.assertEqual(result.raw, {})

    @patch.object(Session, 'call_mcp_tool')
    def test_get_metrics_alternative_field_names(self, mock_call_mcp_tool):
        """Test get_metrics with alternative field names for backward compatibility"""
        from agb.model.response import McpToolResult
        
        # Mock tool result with alternative field names
        mock_tool_result = McpToolResult(
            request_id="request-alt",
            success=True,
            data='{"cpu_count": 8, "rx_rate_kbps": 200.5, "tx_rate_KBps": 100.2, "rx_used_KB": 2048.0, "tx_used_kb": 1024.0, "timestamp": "2024-01-01T12:00:00Z"}',
            error_message=""
        )
        mock_call_mcp_tool.return_value = mock_tool_result

        result = self.session.get_metrics()

        self.assertIsInstance(result, SessionMetricsResult)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.metrics)
        
        # Verify alternative field names are correctly parsed
        metrics = result.metrics
        self.assertEqual(metrics.cpu_count, 8)
        self.assertEqual(metrics.rx_rate_kbyte_per_s, 200.5)  # from rx_rate_kbps
        self.assertEqual(metrics.tx_rate_kbyte_per_s, 100.2)  # from tx_rate_KBps
        self.assertEqual(metrics.rx_used_kbyte, 2048.0)       # from rx_used_KB
        self.assertEqual(metrics.tx_used_kbyte, 1024.0)       # from tx_used_kb

    @patch.object(Session, 'call_mcp_tool')
    def test_get_metrics_missing_fields(self, mock_call_mcp_tool):
        """Test get_metrics with missing fields (should use defaults)"""
        from agb.model.response import McpToolResult
        
        # Mock tool result with minimal data
        mock_tool_result = McpToolResult(
            request_id="request-minimal",
            success=True,
            data='{"cpu_count": 2}',  # Only cpu_count provided
            error_message=""
        )
        mock_call_mcp_tool.return_value = mock_tool_result

        result = self.session.get_metrics()

        self.assertIsInstance(result, SessionMetricsResult)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.metrics)
        
        # Verify defaults are used for missing fields
        metrics = result.metrics
        self.assertEqual(metrics.cpu_count, 2)
        self.assertEqual(metrics.cpu_used_pct, 0.0)
        self.assertEqual(metrics.disk_total, 0)
        self.assertEqual(metrics.disk_used, 0)
        self.assertEqual(metrics.mem_total, 0)
        self.assertEqual(metrics.mem_used, 0)
        self.assertEqual(metrics.rx_rate_kbyte_per_s, 0.0)
        self.assertEqual(metrics.tx_rate_kbyte_per_s, 0.0)
        self.assertEqual(metrics.rx_used_kbyte, 0.0)
        self.assertEqual(metrics.tx_used_kbyte, 0.0)
        self.assertEqual(metrics.timestamp, "")

if __name__ == "__main__":
    unittest.main()