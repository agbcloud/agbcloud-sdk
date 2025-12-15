#!/usr/bin/env python3
"""
Unit tests for GetAndLoadInternalContext request and response models in AGB SDK.
Tests request/response models and data parsing functionality.
"""

import unittest
from unittest.mock import MagicMock

from agb.api.models import (
    GetAndLoadInternalContextRequest,
    GetAndLoadInternalContextResponse,
)
from agb.api.models.get_and_load_internal_context_response import (
    GetAndLoadInternalContextResponseBodyData,
)


class TestGetAndLoadInternalContextRequest(unittest.TestCase):
    """Test GetAndLoadInternalContextRequest class."""

    def test_request_initialization(self):
        """Test request initialization with all parameters."""
        request = GetAndLoadInternalContextRequest(
            authorization="Bearer test-api-key",
            session_id="session-123",
            context_types=["file_transfer", "other_type"],
        )

        self.assertEqual(request.authorization, "Bearer test-api-key")
        self.assertEqual(request.session_id, "session-123")
        self.assertEqual(request.context_types, ["file_transfer", "other_type"])

    def test_request_defaults(self):
        """Test request with default values."""
        request = GetAndLoadInternalContextRequest()

        self.assertEqual(request.authorization, "")
        self.assertEqual(request.session_id, "")
        self.assertEqual(request.context_types, [])

    def test_request_get_params(self):
        """Test get_params method."""
        import json

        request = GetAndLoadInternalContextRequest(
            session_id="session-456",
            context_types=["file_transfer"],
        )

        params = request.get_params()

        self.assertEqual(params["sessionId"], "session-456")
        # contextTypes is serialized as JSON string for query parameters
        self.assertEqual(params["contextTypes"], '["file_transfer"]')
        # Verify it can be parsed back to original list
        parsed = json.loads(params["contextTypes"])
        self.assertEqual(parsed, ["file_transfer"])

    def test_request_get_params_empty(self):
        """Test get_params with empty values."""
        request = GetAndLoadInternalContextRequest()

        params = request.get_params()

        self.assertEqual(params, {})

    def test_request_get_body(self):
        """Test get_body method."""
        request = GetAndLoadInternalContextRequest(
            context_types=["file_transfer"],
        )

        body = request.get_body()

        # Body should be empty for this request type
        self.assertEqual(body, {})

    def test_request_context_types_none(self):
        """Test request with None context_types."""
        request = GetAndLoadInternalContextRequest(
            context_types=None,
        )

        self.assertEqual(request.context_types, [])


class TestGetAndLoadInternalContextResponseBodyData(unittest.TestCase):
    """Test GetAndLoadInternalContextResponseBodyData class."""

    def test_body_data_initialization(self):
        """Test body data initialization with all parameters."""
        data = GetAndLoadInternalContextResponseBodyData(
            context_id="ctx-123",
            context_type="file_transfer",
            context_path="/tmp/file_transfer",
        )

        self.assertEqual(data.context_id, "ctx-123")
        self.assertEqual(data.context_type, "file_transfer")
        self.assertEqual(data.context_path, "/tmp/file_transfer")

    def test_body_data_defaults(self):
        """Test body data with default values."""
        data = GetAndLoadInternalContextResponseBodyData()

        self.assertEqual(data.context_id, "")
        self.assertEqual(data.context_type, "")
        self.assertEqual(data.context_path, "")

    def test_body_data_from_dict(self):
        """Test from_dict class method."""
        dict_data = {
            "ContextId": "ctx-456",
            "ContextType": "file_transfer",
            "ContextPath": "/tmp/test",
        }

        data = GetAndLoadInternalContextResponseBodyData.from_dict(dict_data)

        self.assertEqual(data.context_id, "ctx-456")
        self.assertEqual(data.context_type, "file_transfer")
        self.assertEqual(data.context_path, "/tmp/test")

    def test_body_data_from_dict_partial(self):
        """Test from_dict with partial data."""
        dict_data = {
            "ContextId": "ctx-789",
            # Missing ContextType and ContextPath
        }

        data = GetAndLoadInternalContextResponseBodyData.from_dict(dict_data)

        self.assertEqual(data.context_id, "ctx-789")
        self.assertEqual(data.context_type, "")
        self.assertEqual(data.context_path, "")

    def test_body_data_from_dict_empty(self):
        """Test from_dict with empty dictionary."""
        dict_data = {}

        data = GetAndLoadInternalContextResponseBodyData.from_dict(dict_data)

        self.assertEqual(data.context_id, "")
        self.assertEqual(data.context_type, "")
        self.assertEqual(data.context_path, "")


class TestGetAndLoadInternalContextResponse(unittest.TestCase):
    """Test GetAndLoadInternalContextResponse class."""

    def test_response_initialization_success(self):
        """Test response initialization with successful response."""
        json_data = {
            "success": True,
            "message": "Success",
            "data": [
                {
                    "ContextId": "ctx-123",
                    "ContextType": "file_transfer",
                    "ContextPath": "/tmp/file_transfer",
                }
            ],
            "requestId": "req-1",
        }

        response = GetAndLoadInternalContextResponse(
            status_code=200,
            json_data=json_data,
            request_id="req-1",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.api_success)
        self.assertEqual(response.message, "Success")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.request_id, "req-1")

    def test_response_initialization_failure(self):
        """Test response initialization with failed response."""
        json_data = {
            "success": False,
            "message": "Context not found",
            "data": [],
            "requestId": "req-2",
        }

        response = GetAndLoadInternalContextResponse(
            status_code=404,
            json_data=json_data,
            request_id="req-2",
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.api_success)
        self.assertEqual(response.message, "Context not found")
        self.assertEqual(response.data, [])

    def test_response_defaults(self):
        """Test response with default values."""
        response = GetAndLoadInternalContextResponse()

        self.assertEqual(response.status_code, 0)
        self.assertFalse(response.api_success)
        self.assertEqual(response.message, "")
        self.assertEqual(response.data, [])
        self.assertIsNone(response.request_id)

    def test_response_from_http_response(self):
        """Test from_http_response class method."""
        response_dict = {
            "status_code": 200,
            "url": "https://api.example.com/sdk/context/GetAndLoadInternalContext",
            "headers": {"Content-Type": "application/json"},
            "json": {
                "success": True,
                "message": "Success",
                "data": [
                    {
                        "ContextId": "ctx-123",
                        "ContextType": "file_transfer",
                        "ContextPath": "/tmp/file_transfer",
                    }
                ],
                "requestId": "req-3",
            },
            "request_id": "req-3",
        }

        response = GetAndLoadInternalContextResponse.from_http_response(response_dict)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.api_success)
        self.assertEqual(response.request_id, "req-3")
        self.assertEqual(len(response.data), 1)

    def test_response_from_http_response_no_json(self):
        """Test from_http_response with no JSON data."""
        response_dict = {
            "status_code": 200,
            "url": "https://api.example.com/sdk/context/GetAndLoadInternalContext",
            "headers": {},
            "json": None,
            "request_id": None,
        }

        response = GetAndLoadInternalContextResponse.from_http_response(response_dict)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.api_success)
        self.assertEqual(response.data, [])

    def test_response_is_successful(self):
        """Test is_successful method."""
        # Successful response
        json_data = {
            "success": True,
            "message": "Success",
            "data": [],
        }
        response = GetAndLoadInternalContextResponse(
            status_code=200, json_data=json_data
        )
        self.assertTrue(response.is_successful())

        # Failed response - wrong status code
        response = GetAndLoadInternalContextResponse(
            status_code=404, json_data=json_data
        )
        self.assertFalse(response.is_successful())

        # Failed response - success=False
        json_data_fail = {
            "success": False,
            "message": "Error",
            "data": [],
        }
        response = GetAndLoadInternalContextResponse(
            status_code=200, json_data=json_data_fail
        )
        self.assertFalse(response.is_successful())

    def test_response_get_error_message(self):
        """Test get_error_message method."""
        # Successful response
        json_data = {
            "success": True,
            "message": "Success",
            "data": [],
        }
        response = GetAndLoadInternalContextResponse(
            status_code=200, json_data=json_data
        )
        self.assertEqual(response.get_error_message(), "")

        # Failed response
        json_data_fail = {
            "success": False,
            "message": "Context not found",
            "data": [],
        }
        response = GetAndLoadInternalContextResponse(
            status_code=404, json_data=json_data_fail
        )
        self.assertEqual(response.get_error_message(), "Context not found")

        # Failed response without message
        json_data_no_msg = {
            "success": False,
            "data": [],
        }
        response = GetAndLoadInternalContextResponse(
            status_code=500, json_data=json_data_no_msg
        )
        self.assertEqual(response.get_error_message(), "HTTP 500 error")

    def test_response_get_context_list(self):
        """Test get_context_list method."""
        json_data = {
            "success": True,
            "message": "Success",
            "data": [
                {
                    "ContextId": "ctx-1",
                    "ContextType": "file_transfer",
                    "ContextPath": "/tmp/file_transfer",
                },
                {
                    "ContextId": "ctx-2",
                    "ContextType": "other",
                    "ContextPath": "/tmp/other",
                },
            ],
        }

        response = GetAndLoadInternalContextResponse(
            status_code=200, json_data=json_data
        )

        context_list = response.get_context_list()

        self.assertEqual(len(context_list), 2)
        self.assertEqual(context_list[0]["ContextId"], "ctx-1")
        self.assertEqual(context_list[1]["ContextId"], "ctx-2")

    def test_response_get_context_list_empty(self):
        """Test get_context_list with empty data."""
        json_data = {
            "success": True,
            "message": "Success",
            "data": [],
        }

        response = GetAndLoadInternalContextResponse(
            status_code=200, json_data=json_data
        )

        context_list = response.get_context_list()

        self.assertEqual(len(context_list), 0)

    def test_response_get_context_list_failed(self):
        """Test get_context_list with failed response."""
        json_data = {
            "success": False,
            "message": "Error",
            "data": [],
        }

        response = GetAndLoadInternalContextResponse(
            status_code=400, json_data=json_data
        )

        context_list = response.get_context_list()

        self.assertEqual(len(context_list), 0)

    def test_response_get_context_list_data(self):
        """Test get_context_list_data method."""
        json_data = {
            "success": True,
            "message": "Success",
            "data": [
                {
                    "ContextId": "ctx-1",
                    "ContextType": "file_transfer",
                    "ContextPath": "/tmp/file_transfer",
                },
                {
                    "ContextId": "ctx-2",
                    "ContextType": "other",
                    "ContextPath": "/tmp/other",
                },
            ],
        }

        response = GetAndLoadInternalContextResponse(
            status_code=200, json_data=json_data
        )

        context_list = response.get_context_list_data()

        self.assertEqual(len(context_list), 2)
        self.assertIsInstance(context_list[0], GetAndLoadInternalContextResponseBodyData)
        self.assertEqual(context_list[0].context_id, "ctx-1")
        self.assertEqual(context_list[0].context_type, "file_transfer")
        self.assertEqual(context_list[0].context_path, "/tmp/file_transfer")
        self.assertEqual(context_list[1].context_id, "ctx-2")
        self.assertEqual(context_list[1].context_type, "other")
        self.assertEqual(context_list[1].context_path, "/tmp/other")

    def test_response_get_context_list_data_empty(self):
        """Test get_context_list_data with empty data."""
        json_data = {
            "success": True,
            "message": "Success",
            "data": [],
        }

        response = GetAndLoadInternalContextResponse(
            status_code=200, json_data=json_data
        )

        context_list = response.get_context_list_data()

        self.assertEqual(len(context_list), 0)

    def test_response_get_context_list_data_failed(self):
        """Test get_context_list_data with failed response."""
        json_data = {
            "success": False,
            "message": "Error",
            "data": [],
        }

        response = GetAndLoadInternalContextResponse(
            status_code=400, json_data=json_data
        )

        context_list = response.get_context_list_data()

        self.assertEqual(len(context_list), 0)

    def test_response_to_map(self):
        """Test to_map method for compatibility."""
        json_data = {
            "success": True,
            "message": "Success",
            "data": [
                {
                    "ContextId": "ctx-1",
                    "ContextType": "file_transfer",
                    "ContextPath": "/tmp/file_transfer",
                }
            ],
        }

        response = GetAndLoadInternalContextResponse(
            status_code=200, json_data=json_data, request_id="req-4"
        )

        response_map = response.to_map()

        self.assertIn("body", response_map)
        self.assertIn("request_id", response_map)
        self.assertEqual(response_map["request_id"], "req-4")
        self.assertEqual(response_map["body"]["Success"], True)
        self.assertEqual(response_map["body"]["Message"], "Success")
        self.assertEqual(len(response_map["body"]["Data"]), 1)

    def test_response_to_map_failed(self):
        """Test to_map with failed response."""
        json_data = {
            "success": False,
            "message": "Error occurred",
            "data": [],
        }

        response = GetAndLoadInternalContextResponse(
            status_code=400, json_data=json_data, request_id="req-5"
        )

        response_map = response.to_map()

        self.assertEqual(response_map["body"]["Success"], False)
        self.assertEqual(response_map["body"]["Code"], "Error occurred")
        self.assertEqual(response_map["body"]["Message"], "Error occurred")


if __name__ == "__main__":
    unittest.main()
