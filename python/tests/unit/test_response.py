#!/usr/bin/env python3
"""
Unit tests for response model classes in AGB SDK.
Tests all response types with success and failure scenarios.
"""

import unittest
from unittest.mock import MagicMock

from agb.model.response import (
    ApiResponse,
    SessionResult,
    DeleteResult,
    OperationResult,
    BoolResult,
    GetSessionData,
    GetSessionResult,
    SessionListResult,
)


class TestApiResponse(unittest.TestCase):
    """Test ApiResponse base class."""

    def test_api_response_initialization(self):
        """Test ApiResponse initialization."""
        response = ApiResponse(request_id="req-123")

        self.assertEqual(response.request_id, "req-123")

    def test_api_response_default_request_id(self):
        """Test ApiResponse with default empty request_id."""
        response = ApiResponse()

        self.assertEqual(response.request_id, "")

    def test_api_response_get_request_id(self):
        """Test ApiResponse get_request_id method."""
        response = ApiResponse(request_id="req-456")

        self.assertEqual(response.get_request_id(), "req-456")


class TestSessionResult(unittest.TestCase):
    """Test SessionResult class."""

    def test_session_result_success(self):
        """Test SessionResult with successful operation."""
        mock_session = MagicMock()
        result = SessionResult(
            request_id="req-session-1",
            success=True,
            session=mock_session,
            error_message="",
        )

        self.assertEqual(result.request_id, "req-session-1")
        self.assertTrue(result.success)
        self.assertEqual(result.session, mock_session)
        self.assertEqual(result.error_message, "")

    def test_session_result_failure(self):
        """Test SessionResult with failed operation."""
        result = SessionResult(
            request_id="req-session-2",
            success=False,
            session=None,
            error_message="Session creation failed",
        )

        self.assertEqual(result.request_id, "req-session-2")
        self.assertFalse(result.success)
        self.assertIsNone(result.session)
        self.assertEqual(result.error_message, "Session creation failed")

    def test_session_result_defaults(self):
        """Test SessionResult with default values."""
        result = SessionResult()

        self.assertEqual(result.request_id, "")
        self.assertFalse(result.success)
        self.assertIsNone(result.session)
        self.assertEqual(result.error_message, "")


class TestDeleteResult(unittest.TestCase):
    """Test DeleteResult class."""

    def test_delete_result_success(self):
        """Test DeleteResult with successful deletion."""
        result = DeleteResult(
            request_id="req-delete-1",
            success=True,
            error_message="",
        )

        self.assertEqual(result.request_id, "req-delete-1")
        self.assertTrue(result.success)
        self.assertEqual(result.error_message, "")

    def test_delete_result_failure(self):
        """Test DeleteResult with failed deletion."""
        result = DeleteResult(
            request_id="req-delete-2",
            success=False,
            error_message="Resource not found",
        )

        self.assertEqual(result.request_id, "req-delete-2")
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Resource not found")

    def test_delete_result_defaults(self):
        """Test DeleteResult with default values."""
        result = DeleteResult()

        self.assertEqual(result.request_id, "")
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "")


class TestOperationResult(unittest.TestCase):
    """Test OperationResult class."""

    def test_operation_result_success_with_data(self):
        """Test OperationResult with successful operation and data."""
        result = OperationResult(
            request_id="req-op-1",
            success=True,
            data={"key": "value"},
            error_message="",
        )

        self.assertEqual(result.request_id, "req-op-1")
        self.assertTrue(result.success)
        self.assertEqual(result.data, {"key": "value"})
        self.assertEqual(result.error_message, "")

    def test_operation_result_failure(self):
        """Test OperationResult with failed operation."""
        result = OperationResult(
            request_id="req-op-2",
            success=False,
            data=None,
            error_message="Operation failed",
        )

        self.assertEqual(result.request_id, "req-op-2")
        self.assertFalse(result.success)
        self.assertIsNone(result.data)
        self.assertEqual(result.error_message, "Operation failed")

    def test_operation_result_defaults(self):
        """Test OperationResult with default values."""
        result = OperationResult()

        self.assertEqual(result.request_id, "")
        self.assertFalse(result.success)
        self.assertIsNone(result.data)
        self.assertEqual(result.error_message, "")

    def test_operation_result_with_string_data(self):
        """Test OperationResult with string data."""
        result = OperationResult(
            request_id="req-op-3",
            success=True,
            data="output string",
        )

        self.assertEqual(result.data, "output string")

    def test_operation_result_with_list_data(self):
        """Test OperationResult with list data."""
        result = OperationResult(
            request_id="req-op-4",
            success=True,
            data=[1, 2, 3],
        )

        self.assertEqual(result.data, [1, 2, 3])


class TestBoolResult(unittest.TestCase):
    """Test BoolResult class."""

    def test_bool_result_success_true(self):
        """Test BoolResult with successful operation returning True."""
        result = BoolResult(
            request_id="req-bool-1",
            success=True,
            data=True,
            error_message="",
        )

        self.assertEqual(result.request_id, "req-bool-1")
        self.assertTrue(result.success)
        self.assertTrue(result.data)
        self.assertEqual(result.error_message, "")

    def test_bool_result_success_false(self):
        """Test BoolResult with successful operation returning False."""
        result = BoolResult(
            request_id="req-bool-2",
            success=True,
            data=False,
        )

        self.assertTrue(result.success)
        self.assertFalse(result.data)

    def test_bool_result_failure(self):
        """Test BoolResult with failed operation."""
        result = BoolResult(
            request_id="req-bool-3",
            success=False,
            data=None,
            error_message="Operation failed",
        )

        self.assertFalse(result.success)
        self.assertIsNone(result.data)
        self.assertEqual(result.error_message, "Operation failed")

    def test_bool_result_defaults(self):
        """Test BoolResult with default values."""
        result = BoolResult()

        self.assertEqual(result.request_id, "")
        self.assertFalse(result.success)
        self.assertIsNone(result.data)
        self.assertEqual(result.error_message, "")


class TestGetSessionData(unittest.TestCase):
    """Test GetSessionData class."""

    def test_get_session_data_initialization(self):
        """Test GetSessionData initialization."""
        data = GetSessionData(
            app_instance_id="app-1",
            resource_id="res-1",
            session_id="session-1",
            success=True,
            resource_url="http://10.0.0.1:8080",
        )

        self.assertEqual(data.app_instance_id, "app-1")
        self.assertEqual(data.resource_id, "res-1")
        self.assertEqual(data.session_id, "session-1")
        self.assertTrue(data.success)
        self.assertEqual(data.resource_url, "http://10.0.0.1:8080")

    def test_get_session_data_defaults(self):
        """Test GetSessionData with default values."""
        data = GetSessionData()

        self.assertEqual(data.app_instance_id, "")
        self.assertEqual(data.resource_id, "")
        self.assertEqual(data.session_id, "")
        self.assertFalse(data.success)
        self.assertEqual(data.resource_url, "")


class TestGetSessionResult(unittest.TestCase):
    """Test GetSessionResult class."""

    def test_get_session_result_success(self):
        """Test GetSessionResult with successful operation."""
        session_data = GetSessionData(
            session_id="session-1",
            success=True,
        )
        result = GetSessionResult(
            request_id="req-get-session-1",
            http_status_code=200,
            code="Success",
            success=True,
            data=session_data,
            error_message="",
        )

        self.assertEqual(result.request_id, "req-get-session-1")
        self.assertEqual(result.http_status_code, 200)
        self.assertEqual(result.code, "Success")
        self.assertTrue(result.success)
        self.assertEqual(result.data, session_data)
        self.assertEqual(result.error_message, "")

    def test_get_session_result_failure(self):
        """Test GetSessionResult with failed operation."""
        result = GetSessionResult(
            request_id="req-get-session-2",
            http_status_code=404,
            code="NotFound",
            success=False,
            data=None,
            error_message="Session not found",
        )

        self.assertFalse(result.success)
        self.assertEqual(result.http_status_code, 404)
        self.assertEqual(result.code, "NotFound")
        self.assertIsNone(result.data)
        self.assertEqual(result.error_message, "Session not found")

    def test_get_session_result_defaults(self):
        """Test GetSessionResult with default values."""
        result = GetSessionResult()

        self.assertEqual(result.request_id, "")
        self.assertEqual(result.http_status_code, 0)
        self.assertEqual(result.code, "")
        self.assertFalse(result.success)
        self.assertIsNone(result.data)
        self.assertEqual(result.error_message, "")


class TestSessionListResult(unittest.TestCase):
    """Test SessionListResult class."""

    def test_session_list_result_success(self):
        """Test SessionListResult with successful operation."""
        result = SessionListResult(
            request_id="req-list-1",
            success=True,
            error_message="",
            session_ids=["session-1", "session-2", "session-3"],
            next_token="token-123",
            max_results=10,
            total_count=3,
        )

        self.assertEqual(result.request_id, "req-list-1")
        self.assertTrue(result.success)
        self.assertEqual(len(result.session_ids), 3)
        self.assertEqual(result.next_token, "token-123")
        self.assertEqual(result.max_results, 10)
        self.assertEqual(result.total_count, 3)

    def test_session_list_result_with_pagination(self):
        """Test SessionListResult with pagination."""
        result = SessionListResult(
            request_id="req-list-2",
            success=True,
            session_ids=["session-1"],
            next_token="token-next",
            max_results=1,
            total_count=100,
        )

        self.assertEqual(len(result.session_ids), 1)
        self.assertEqual(result.next_token, "token-next")
        self.assertEqual(result.max_results, 1)
        self.assertEqual(result.total_count, 100)

    def test_session_list_result_empty(self):
        """Test SessionListResult with empty session list."""
        result = SessionListResult(
            request_id="req-list-3",
            success=True,
            session_ids=[],
            next_token="",
            max_results=10,
            total_count=0,
        )

        self.assertEqual(len(result.session_ids), 0)
        self.assertEqual(result.total_count, 0)

    def test_session_list_result_failure(self):
        """Test SessionListResult with failed operation."""
        result = SessionListResult(
            request_id="req-list-4",
            success=False,
            error_message="Failed to list sessions",
            session_ids=[],
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Failed to list sessions")
        self.assertEqual(len(result.session_ids), 0)

    def test_session_list_result_defaults(self):
        """Test SessionListResult with default values."""
        result = SessionListResult()

        self.assertEqual(result.request_id, "")
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "")
        self.assertEqual(len(result.session_ids), 0)
        self.assertEqual(result.next_token, "")
        self.assertEqual(result.max_results, 0)
        self.assertEqual(result.total_count, 0)


if __name__ == "__main__":
    unittest.main()

