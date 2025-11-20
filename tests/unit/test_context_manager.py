#!/usr/bin/env python3
"""
Unit tests for ContextManager module in AGB SDK.
Tests context info and sync operations with success and failure scenarios.
"""

import unittest
from unittest.mock import MagicMock, patch
import json

from agb.context_manager import (
    ContextManager,
    ContextStatusData,
    ContextInfoResult,
    ContextSyncResult,
)
from agb.api.models.get_context_info_response import GetContextInfoResponse
from agb.api.models.sync_context_response import SyncContextResponse


class DummySession:
    """Dummy session class for testing."""

    def __init__(self):
        self.session_id = "test_session_id"
        self.client = MagicMock()

    def get_api_key(self) -> str:
        return "test_api_key"

    def get_session_id(self) -> str:
        return self.session_id

    def get_client(self):
        return self.client


class TestContextStatusData(unittest.TestCase):
    """Test ContextStatusData class."""

    def test_context_status_data_initialization(self):
        """Test ContextStatusData initialization."""
        status = ContextStatusData(
            context_id="ctx-123",
            path="/tmp/test",
            error_message="",
            status="Success",
            start_time=1000,
            finish_time=2000,
            task_type="upload",
        )

        self.assertEqual(status.context_id, "ctx-123")
        self.assertEqual(status.path, "/tmp/test")
        self.assertEqual(status.status, "Success")
        self.assertEqual(status.task_type, "upload")

    def test_context_status_data_from_dict(self):
        """Test ContextStatusData from_dict creation."""
        data = {
            "contextId": "ctx-456",
            "path": "/tmp/file.txt",
            "errorMessage": "",
            "status": "Failed",
            "startTime": 3000,
            "finishTime": 4000,
            "taskType": "download",
        }

        status = ContextStatusData.from_dict(data)

        self.assertEqual(status.context_id, "ctx-456")
        self.assertEqual(status.path, "/tmp/file.txt")
        self.assertEqual(status.status, "Failed")
        self.assertEqual(status.task_type, "download")

    def test_context_status_data_from_dict_with_missing_fields(self):
        """Test ContextStatusData from_dict with missing optional fields."""
        data = {
            "contextId": "ctx-789",
            "status": "Pending",
        }

        status = ContextStatusData.from_dict(data)

        self.assertEqual(status.context_id, "ctx-789")
        self.assertEqual(status.status, "Pending")
        self.assertEqual(status.path, "")
        self.assertEqual(status.error_message, "")
        self.assertEqual(status.start_time, 0)
        self.assertEqual(status.finish_time, 0)
        self.assertEqual(status.task_type, "")


class TestContextManager(unittest.TestCase):
    """Test ContextManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.session = DummySession()
        self.manager = ContextManager(self.session)

    def test_info_success(self):
        """Test successful context info retrieval."""
        # Mock response with context status data
        context_status_data = [
            {
                "type": "data",
                "data": json.dumps([
                    {
                        "contextId": "ctx-123",
                        "path": "/tmp/test",
                        "errorMessage": "",
                        "status": "Success",
                        "startTime": 1000,
                        "finishTime": 2000,
                        "taskType": "upload",
                    }
                ])
            }
        ]

        mock_response = GetContextInfoResponse(
            status_code=200,
            json_data={
                "success": True,
                "message": "Success",
                "data": {
                    "contextStatus": json.dumps(context_status_data)
                },
            },
            request_id="req-info-1",
        )
        mock_response.is_successful = MagicMock(return_value=True)
        mock_response.get_context_status = MagicMock(
            return_value=json.dumps(context_status_data)
        )
        self.session.client.get_context_info = MagicMock(return_value=mock_response)

        result = self.manager.info(context_id="ctx-123")

        self.assertTrue(result.success)
        self.assertEqual(len(result.context_status_data), 1)
        self.assertEqual(result.context_status_data[0].context_id, "ctx-123")
        self.assertEqual(result.context_status_data[0].status, "Success")

    def test_info_with_all_parameters(self):
        """Test info method with all parameters."""
        mock_response = GetContextInfoResponse(
            status_code=200,
            json_data={
                "success": True,
                "message": "Success",
                "data": {"contextStatus": "[]"},
            },
            request_id="req-info-2",
        )
        mock_response.is_successful = MagicMock(return_value=True)
        mock_response.get_context_status = MagicMock(return_value="[]")
        self.session.client.get_context_info = MagicMock(return_value=mock_response)

        result = self.manager.info(
            context_id="ctx-456",
            path="/tmp/test",
            task_type="upload",
        )

        self.assertTrue(result.success)
        # Verify request was made with correct parameters
        call_args = self.session.client.get_context_info.call_args[0][0]
        self.assertEqual(call_args.context_id, "ctx-456")
        self.assertEqual(call_args.path, "/tmp/test")
        self.assertEqual(call_args.task_type, "upload")

    def test_info_api_failure(self):
        """Test info method when API returns failure."""
        mock_response = GetContextInfoResponse(
            status_code=400,
            json_data={
                "success": False,
                "message": "Context not found",
            },
            request_id="req-info-3",
        )
        mock_response.is_successful = MagicMock(return_value=False)
        mock_response.get_error_message = MagicMock(return_value="Context not found")
        self.session.client.get_context_info = MagicMock(return_value=mock_response)

        result = self.manager.info(context_id="ctx-nonexistent")

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Context not found")
        self.assertEqual(len(result.context_status_data), 0)

    def test_info_parse_error(self):
        """Test info method with invalid JSON in response."""
        mock_response = GetContextInfoResponse(
            status_code=200,
            json_data={
                "success": True,
                "message": "Success",
                "data": {"contextStatus": "invalid json"},
            },
            request_id="req-info-4",
        )
        mock_response.is_successful = MagicMock(return_value=True)
        mock_response.get_context_status = MagicMock(return_value="invalid json")
        self.session.client.get_context_info = MagicMock(return_value=mock_response)

        result = self.manager.info()

        self.assertFalse(result.success)
        # Check for parse error indicators
        self.assertTrue(
            "parse" in result.error_message.lower() or
            "error" in result.error_message.lower()
        )

    def test_info_empty_status(self):
        """Test info method with empty context status."""
        mock_response = GetContextInfoResponse(
            status_code=200,
            json_data={
                "success": True,
                "message": "Success",
                "data": {"contextStatus": ""},
            },
            request_id="req-info-5",
        )
        mock_response.is_successful = MagicMock(return_value=True)
        mock_response.get_context_status = MagicMock(return_value="")
        self.session.client.get_context_info = MagicMock(return_value=mock_response)

        result = self.manager.info()

        self.assertTrue(result.success)
        self.assertEqual(len(result.context_status_data), 0)

    def test_info_with_multiple_tasks(self):
        """Test info method with multiple context status tasks."""
        context_status_data = [
            {
                "type": "data",
                "data": json.dumps([
                    {
                        "contextId": "ctx-1",
                        "path": "/tmp/file1",
                        "status": "Success",
                        "taskType": "upload",
                    },
                    {
                        "contextId": "ctx-2",
                        "path": "/tmp/file2",
                        "status": "Failed",
                        "taskType": "download",
                    },
                ])
            }
        ]

        mock_response = GetContextInfoResponse(
            status_code=200,
            json_data={
                "success": True,
                "message": "Success",
                "data": {
                    "contextStatus": json.dumps(context_status_data)
                },
            },
            request_id="req-info-6",
        )
        mock_response.is_successful = MagicMock(return_value=True)
        mock_response.get_context_status = MagicMock(
            return_value=json.dumps(context_status_data)
        )
        self.session.client.get_context_info = MagicMock(return_value=mock_response)

        result = self.manager.info()

        self.assertTrue(result.success)
        self.assertEqual(len(result.context_status_data), 2)
        self.assertEqual(result.context_status_data[0].status, "Success")
        self.assertEqual(result.context_status_data[1].status, "Failed")

    def test_info_with_non_data_type_item(self):
        """Test info method with items that are not type 'data'."""
        context_status_data = [
            {
                "type": "other",
                "data": "some data"
            },
            {
                "type": "data",
                "data": json.dumps([
                    {
                        "contextId": "ctx-1",
                        "path": "/tmp/file1",
                        "status": "Success",
                        "taskType": "upload",
                    }
                ])
            }
        ]

        mock_response = GetContextInfoResponse(
            status_code=200,
            json_data={
                "success": True,
                "message": "Success",
                "data": {
                    "contextStatus": json.dumps(context_status_data)
                },
            },
            request_id="req-info-7",
        )
        mock_response.is_successful = MagicMock(return_value=True)
        mock_response.get_context_status = MagicMock(
            return_value=json.dumps(context_status_data)
        )
        self.session.client.get_context_info = MagicMock(return_value=mock_response)

        result = self.manager.info()

        self.assertTrue(result.success)
        # Only items with type "data" should be parsed
        self.assertEqual(len(result.context_status_data), 1)
        self.assertEqual(result.context_status_data[0].context_id, "ctx-1")

    def test_sync_success_async(self):
        """Test successful context sync (async mode)."""
        import asyncio

        # Mock sync response
        mock_sync_response = SyncContextResponse(
            status_code=200,
            json_data={
                "success": True,
                "message": "Sync started",
            },
            request_id="req-sync-1",
        )
        mock_sync_response.is_successful = MagicMock(return_value=True)
        self.session.client.sync_context = MagicMock(return_value=mock_sync_response)

        # Mock _poll_for_completion_async to return immediately
        async def mock_poll(context_id, path, max_retries, retry_interval):
            return True
        self.manager._poll_for_completion_async = mock_poll

        async def run_test():
            result = await self.manager.sync(context_id="ctx-123")
            return result

        result = asyncio.run(run_test())

        self.assertTrue(result.success)
        # Verify error_message is empty string on success
        self.assertEqual(result.error_message, "")
        self.assertEqual(result.request_id, "req-sync-1")

    def test_sync_with_callback(self):
        """Test sync method with callback (sync mode)."""
        import asyncio

        # Mock sync response
        mock_sync_response = SyncContextResponse(
            status_code=200,
            json_data={
                "success": True,
                "message": "Sync started",
            },
            request_id="req-sync-2",
        )
        mock_sync_response.is_successful = MagicMock(return_value=True)
        self.session.client.sync_context = MagicMock(return_value=mock_sync_response)

        callback_called = []
        callback_value = []

        def test_callback(success: bool):
            callback_called.append(True)
            callback_value.append(success)

        # Mock _poll_for_completion to call callback immediately
        def mock_poll(callback, context_id, path, max_retries, retry_interval):
            callback(True)
        self.manager._poll_for_completion = mock_poll

        async def run_test():
            result = await self.manager.sync(context_id="ctx-123", callback=test_callback)
            return result

        result = asyncio.run(run_test())

        self.assertTrue(result.success)
        # Note: callback runs in background thread, so we can't reliably test it here
        # In real scenarios, would use threading synchronization primitives

    def test_sync_api_failure(self):
        """Test sync method when API returns failure."""
        import asyncio

        mock_sync_response = SyncContextResponse(
            status_code=400,
            json_data={
                "success": False,
                "message": "Sync failed",
            },
            request_id="req-sync-3",
        )
        mock_sync_response.is_successful = MagicMock(return_value=False)
        mock_sync_response.get_error_message = MagicMock(return_value="Sync failed")
        self.session.client.sync_context = MagicMock(return_value=mock_sync_response)

        async def run_test():
            result = await self.manager.sync(context_id="ctx-123")
            return result

        result = asyncio.run(run_test())

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Sync failed")
        self.assertEqual(result.request_id, "req-sync-3")

    def test_sync_with_parameters(self):
        """Test sync method with all parameters."""
        import asyncio

        mock_sync_response = SyncContextResponse(
            status_code=200,
            json_data={
                "success": True,
                "message": "Sync started",
            },
            request_id="req-sync-4",
        )
        mock_sync_response.is_successful = MagicMock(return_value=True)
        self.session.client.sync_context = MagicMock(return_value=mock_sync_response)

        async def mock_poll(context_id, path, max_retries, retry_interval):
            return True
        self.manager._poll_for_completion_async = mock_poll

        async def run_test():
            result = await self.manager.sync(
                context_id="ctx-123",
                path="/tmp/test",
                mode="sync",
                max_retries=10,
                retry_interval=500,
            )
            return result

        result = asyncio.run(run_test())

        self.assertTrue(result.success)
        # Verify error_message is empty string on success
        self.assertEqual(result.error_message, "")
        # Verify request was made with correct parameters
        call_args = self.session.client.sync_context.call_args[0][0]
        self.assertEqual(call_args.context_id, "ctx-123")
        self.assertEqual(call_args.path, "/tmp/test")
        self.assertEqual(call_args.mode, "sync")

    def test_sync_result_error_message_initialization(self):
        """Test ContextSyncResult error_message initialization."""
        # Test with error message
        result_with_error = ContextSyncResult(
            request_id="req-1",
            success=False,
            error_message="Test error message"
        )
        self.assertEqual(result_with_error.request_id, "req-1")
        self.assertFalse(result_with_error.success)
        self.assertEqual(result_with_error.error_message, "Test error message")

        # Test without error message (success case)
        result_success = ContextSyncResult(
            request_id="req-2",
            success=True,
            error_message=""
        )
        self.assertEqual(result_success.request_id, "req-2")
        self.assertTrue(result_success.success)
        self.assertEqual(result_success.error_message, "")

        # Test default initialization
        result_default = ContextSyncResult()
        self.assertEqual(result_default.request_id, "")
        self.assertFalse(result_default.success)
        self.assertEqual(result_default.error_message, "")

    def test_sync_api_failure_with_different_error_messages(self):
        """Test sync method with different error message scenarios."""
        import asyncio

        # Test case 1: Error message from API response
        mock_sync_response_1 = SyncContextResponse(
            status_code=400,
            json_data={
                "success": False,
                "message": "Invalid context ID",
            },
            request_id="req-sync-error-1",
        )
        mock_sync_response_1.is_successful = MagicMock(return_value=False)
        mock_sync_response_1.get_error_message = MagicMock(return_value="Invalid context ID")
        self.session.client.sync_context = MagicMock(return_value=mock_sync_response_1)

        async def run_test_1():
            result = await self.manager.sync(context_id="invalid-ctx")
            return result

        result_1 = asyncio.run(run_test_1())
        self.assertFalse(result_1.success)
        self.assertEqual(result_1.error_message, "Invalid context ID")
        self.assertEqual(result_1.request_id, "req-sync-error-1")

        # Test case 2: HTTP error without message
        mock_sync_response_2 = SyncContextResponse(
            status_code=500,
            json_data={
                "success": False,
            },
            request_id="req-sync-error-2",
        )
        mock_sync_response_2.is_successful = MagicMock(return_value=False)
        mock_sync_response_2.get_error_message = MagicMock(return_value="HTTP 500 error")
        self.session.client.sync_context = MagicMock(return_value=mock_sync_response_2)

        async def run_test_2():
            result = await self.manager.sync(context_id="ctx-123")
            return result

        result_2 = asyncio.run(run_test_2())
        self.assertFalse(result_2.success)
        self.assertEqual(result_2.error_message, "HTTP 500 error")
        self.assertEqual(result_2.request_id, "req-sync-error-2")

    def test_sync_with_callback_error_message(self):
        """Test sync method with callback when API fails - verify error_message."""
        import asyncio

        # Mock sync response with failure
        mock_sync_response = SyncContextResponse(
            status_code=400,
            json_data={
                "success": False,
                "message": "Session not found",
            },
            request_id="req-sync-callback-error",
        )
        mock_sync_response.is_successful = MagicMock(return_value=False)
        mock_sync_response.get_error_message = MagicMock(return_value="Session not found")
        self.session.client.sync_context = MagicMock(return_value=mock_sync_response)

        callback_called = []

        def test_callback(success: bool):
            callback_called.append(success)

        async def run_test():
            result = await self.manager.sync(context_id="ctx-123", callback=test_callback)
            return result

        result = asyncio.run(run_test())

        # When API fails, callback should not be called (only called when success=True)
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Session not found")
        self.assertEqual(result.request_id, "req-sync-callback-error")
        # Callback should not be called when API fails
        self.assertEqual(len(callback_called), 0)


if __name__ == "__main__":
    unittest.main()

