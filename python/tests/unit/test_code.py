#!/usr/bin/env python3
"""
Unit tests for Code module in AGB SDK.
Tests code execution functionality with success and failure scenarios.
"""

import unittest
from unittest.mock import MagicMock, patch

from agb.modules.code import Code
from agb.model.response import (
    OperationResult,
    EnhancedCodeExecutionResult,
    ExecutionResult,
    ExecutionLogs,
    ExecutionError,
)


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


class TestEnhancedCodeExecutionResult(unittest.TestCase):
    """Test EnhancedCodeExecutionResult class."""

    def test_enhanced_code_execution_result_initialization(self):
        """Test EnhancedCodeExecutionResult initialization."""
        logs = ExecutionLogs(stdout=["output"], stderr=[])
        results = [ExecutionResult(text="Hello, World!", is_main_result=True)]

        result = EnhancedCodeExecutionResult(
            request_id="req-123",
            success=True,
            logs=logs,
            results=results,
            error_message="",
            execution_count=1,
            execution_time=0.5,
        )

        self.assertEqual(result.request_id, "req-123")
        self.assertTrue(result.success)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].text, "Hello, World!")
        self.assertTrue(result.results[0].is_main_result)
        self.assertEqual(result.logs.stdout, ["output"])
        self.assertEqual(result.logs.stderr, [])
        self.assertEqual(result.error_message, "")
        self.assertEqual(result.execution_count, 1)
        self.assertEqual(result.execution_time, 0.5)

    def test_enhanced_code_execution_result_failure(self):
        """Test EnhancedCodeExecutionResult with failure."""
        logs = ExecutionLogs(stdout=[], stderr=["Error occurred"])

        result = EnhancedCodeExecutionResult(
            request_id="req-456",
            success=False,
            logs=logs,
            results=[],
            error_message="RuntimeError: Execution failed",
            execution_count=None,
            execution_time=0.0,
        )

        self.assertEqual(result.request_id, "req-456")
        self.assertFalse(result.success)
        self.assertEqual(len(result.results), 0)
        self.assertEqual(result.logs.stderr, ["Error occurred"])
        self.assertIsNotNone(result.error_message)
        self.assertEqual(result.error_message, "RuntimeError: Execution failed")


class TestCode(unittest.TestCase):
    """Test Code class."""

    def setUp(self):
        """Set up test fixtures."""
        self.session = DummySession()
        self.code = Code(self.session)

    def test_run_success_python(self):
        """Test successful Python code execution."""
        # Mock the _call_mcp_tool response with raw API data
        mock_api_response = {
            "result": [{"text/plain": "Hello, World!", "isMainResult": True}],
            "stdout": ["Hello, World!"],
            "stderr": [],
            "execution_count": 1,
            "execution_time": 0.5,
        }
        mock_result = OperationResult(
            request_id="req-123",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        # Execute code
        result = self.code.run("print('Hello, World!')", "python", timeout_s=60)

        # Assertions
        self.assertIsInstance(result, EnhancedCodeExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-123")
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].text, "Hello, World!")
        self.assertTrue(result.results[0].is_main_result)
        self.assertEqual(result.logs.stdout, ["Hello, World!"])
        self.assertEqual(result.logs.stderr, [])
        self.assertEqual(result.error_message, "")
        self.code._call_mcp_tool.assert_called_once_with(
            "run_code",
            {"code": "print('Hello, World!')", "language": "python", "timeout_s": 60},
        )

    def test_run_success_javascript(self):
        """Test successful JavaScript code execution."""
        mock_api_response = {
            "result": [{"text/plain": "42"}],
            "stdout": ["42"],
            "stderr": [],
            "execution_count": 1,
            "execution_time": 0.3,
        }
        mock_result = OperationResult(
            request_id="req-456",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("console.log(42)", "javascript", timeout_s=30)

        self.assertIsInstance(result, EnhancedCodeExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-456")
        self.assertEqual(result.results[0].text, "42")

    def test_run_success_java(self):
        """Test successful Java code execution."""
        mock_api_response = {
            "result": [{"text/plain": "Java output"}],
            "stdout": ["Java output"],
            "stderr": [],
            "execution_count": 1,
            "execution_time": 1.2,
        }
        mock_result = OperationResult(
            request_id="req-789",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("System.out.println('test')", "java", timeout_s=120)

        self.assertIsInstance(result, EnhancedCodeExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.results[0].text, "Java output")

    def test_run_success_r(self):
        """Test successful R code execution."""
        mock_api_response = {
            "result": [{"text/plain": "[1] 1 2 3"}],
            "stdout": ["[1] 1 2 3"],
            "stderr": [],
            "execution_count": 1,
            "execution_time": 0.8,
        }
        mock_result = OperationResult(
            request_id="req-r-1",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("c(1, 2, 3)", "r", timeout_s=90)

        self.assertIsInstance(result, EnhancedCodeExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.results[0].text, "[1] 1 2 3")

    def test_run_case_insensitive_language(self):
        """Test that language parameter is case-insensitive."""
        mock_api_response = {
            "result": [{"text/plain": "output"}],
            "stdout": ["output"],
            "stderr": [],
            "execution_count": 1,
            "execution_time": 0.4,
        }
        mock_result = OperationResult(
            request_id="req-case-1",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print('test')", "PYTHON", timeout_s=60)

        self.assertIsInstance(result, EnhancedCodeExecutionResult)
        self.assertTrue(result.success)
        # Verify that language was converted to lowercase
        call_args = self.code._call_mcp_tool.call_args
        self.assertEqual(call_args[0][1]["language"], "python")

    def test_run_unsupported_language(self):
        """Test execution with unsupported language."""
        result = self.code.run("print('test')", "ruby", timeout_s=60)

        self.assertIsInstance(result, EnhancedCodeExecutionResult)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
        self.assertIn("Unsupported language", result.error_message)
        self.assertIn("ruby", result.error_message)

    def test_run_api_failure(self):
        """Test code execution when API returns failure."""
        mock_result = OperationResult(
            request_id="req-fail-1",
            success=False,
            data=None,
            error_message="API error occurred",
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print('test')", "python", timeout_s=60)

        self.assertIsInstance(result, EnhancedCodeExecutionResult)
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "req-fail-1")
        self.assertIsNotNone(result.error_message)
        self.assertEqual(result.error_message, "API error occurred")

    def test_run_api_failure_no_error_message(self):
        """Test code execution when API fails without error message."""
        mock_result = OperationResult(
            request_id="req-fail-2",
            success=False,
            data=None,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print('test')", "python", timeout_s=60)

        self.assertIsInstance(result, EnhancedCodeExecutionResult)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
        self.assertEqual(result.error_message, "Failed to run code")

    def test_run_exception_handling(self):
        """Test exception handling during code execution."""
        self.code._call_mcp_tool = MagicMock(side_effect=Exception("Network error"))

        result = self.code.run("print('test')", "python", timeout_s=60)

        self.assertIsInstance(result, EnhancedCodeExecutionResult)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
        self.assertIn("Failed to run code", result.error_message)
        self.assertIn("Network error", result.error_message)

    def test_run_default_timeout(self):
        """Test code execution with default timeout."""
        mock_api_response = {
            "result": [{"text/plain": "output"}],
            "stdout": ["output"],
            "stderr": [],
            "execution_count": 1,
            "execution_time": 0.2,
        }
        mock_result = OperationResult(
            request_id="req-timeout-1",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print('test')", "python")

        self.assertIsInstance(result, EnhancedCodeExecutionResult)
        self.assertTrue(result.success)
        # Verify default timeout is 60
        call_args = self.code._call_mcp_tool.call_args
        self.assertEqual(call_args[0][1]["timeout_s"], 60)

    def test_run_language_aliases(self):
        """Test language aliases support."""
        mock_api_response = {
            "result": [{"text/plain": "output"}],
            "stdout": ["output"],
            "stderr": [],
            "execution_count": 1,
            "execution_time": 0.3,
        }
        mock_result = OperationResult(
            request_id="req-alias-1",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        # Test python3 -> python
        result = self.code.run("print('test')", "python3", timeout_s=60)
        call_args = self.code._call_mcp_tool.call_args
        self.assertEqual(call_args[0][1]["language"], "python")

        # Test js -> javascript
        self.code._call_mcp_tool.reset_mock()
        result = self.code.run("console.log('test')", "js", timeout_s=60)
        call_args = self.code._call_mcp_tool.call_args
        self.assertEqual(call_args[0][1]["language"], "javascript")

    def test_run_success_no_data(self):
        """Test run when API success but data is None."""
        mock_result = OperationResult(
            request_id="req-nodata",
            success=True,
            data=None,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print(1)", "python")

        self.assertFalse(result.success)
        self.assertIn("No data", result.error_message)

    def test_run_success_legacy_format(self):
        """Test run with legacy content format response."""
        mock_api_response = {
            "content": [{"text": "legacy output"}],
        }
        mock_result = OperationResult(
            request_id="req-legacy",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print('legacy')", "python")

        self.assertTrue(result.success)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].text, "legacy output")

    def test_run_success_fallback_format(self):
        """Test run with dict data that triggers default fallback (no result/logs/content)."""
        mock_api_response = {"customKey": "customValue"}
        mock_result = OperationResult(
            request_id="req-fallback",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("1+1", "python")

        self.assertTrue(result.success)
        self.assertEqual(len(result.results), 1)
        self.assertIn("customKey", result.results[0].text)

    def test_run_with_non_dict_data(self):
        """Test run when API returns non-dict data (string)."""
        mock_result = OperationResult(
            request_id="req-string",
            success=True,
            data="simple string result",
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print('test')", "python")

        self.assertTrue(result.success)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].text, "simple string result")

    def test_run_with_number_data(self):
        """Test run when API returns number data."""
        mock_result = OperationResult(
            request_id="req-number",
            success=True,
            data=42,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("1+1", "python")

        self.assertTrue(result.success)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].text, "42")

    def test_run_with_execution_error(self):
        """Test run when response contains execution error."""
        mock_api_response = {
            "result": [],
            "stdout": [],
            "stderr": ["Error: Division by zero"],
            "executionError": "DivisionByZeroError",
            "execution_count": 1,
            "execution_time": 0.1,
        }
        mock_result = OperationResult(
            request_id="req-error",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("1/0", "python")

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "DivisionByZeroError")

    def test_run_with_rich_format(self):
        """Test run with rich format response (logs and results)."""
        mock_api_response = {
            "logs": {
                "stdout": ["output line 1", "output line 2"],
                "stderr": [],
            },
            "results": [
                {
                    "text": "text result",
                    "html": "<p>html result</p>",
                    "markdown": "**markdown**",
                    "is_main_result": True,
                }
            ],
            "execution_count": 1,
            "execution_time": 0.5,
            "isError": False,
        }
        mock_result = OperationResult(
            request_id="req-rich",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print('test')", "python")

        self.assertTrue(result.success)
        self.assertEqual(len(result.logs.stdout), 2)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].text, "text result")
        self.assertEqual(result.results[0].html, "<p>html result</p>")
        self.assertEqual(result.results[0].markdown, "**markdown**")

    def test_run_with_rich_format_error(self):
        """Test run with rich format response containing error."""
        mock_api_response = {
            "logs": {
                "stdout": [],
                "stderr": ["error message"],
            },
            "content": [{"text": "error output"}],
            "results": [],
            "error": {
                "value": "RuntimeError",
                "name": "RuntimeError",
            },
            "isError": True,
        }
        mock_result = OperationResult(
            request_id="req-rich-error",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("raise Error()", "python")

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Error in response: error output")

    def test_run_with_string_result_item(self):
        """Test run when result items are strings."""
        mock_api_response = {
            "result": ["string result 1", "string result 2"],
            "stdout": [],
            "stderr": [],
            "execution_count": 1,
            "execution_time": 0.1,
        }
        mock_result = OperationResult(
            request_id="req-string-item",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print('test')", "python")

        self.assertTrue(result.success)
        self.assertEqual(len(result.results), 2)
        self.assertEqual(result.results[0].text, "string result 1")
        self.assertEqual(result.results[1].text, "string result 2")

    def test_run_with_json_string_result_item(self):
        """Test run when result items are JSON strings."""
        mock_api_response = {
            "result": ['{"text/plain": "parsed result"}'],
            "stdout": [],
            "stderr": [],
            "execution_count": 1,
            "execution_time": 0.1,
        }
        mock_result = OperationResult(
            request_id="req-json-item",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print('test')", "python")

        self.assertTrue(result.success)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].text, "parsed result")

    def test_run_with_double_encoded_json(self):
        """Test run when result items are double-encoded JSON strings."""
        mock_api_response = {
            "result": ['"{\\"text/plain\\": \\"double encoded\\"}"'],
            "stdout": [],
            "stderr": [],
            "execution_count": 1,
            "execution_time": 0.1,
        }
        mock_result = OperationResult(
            request_id="req-double-json",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print('test')", "python")

        self.assertTrue(result.success)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].text, "double encoded")

    def test_run_with_invalid_json_string(self):
        """Test run when result items are invalid JSON strings."""
        mock_api_response = {
            "result": ["not a json string"],
            "stdout": [],
            "stderr": [],
            "execution_count": 1,
            "execution_time": 0.1,
        }
        mock_result = OperationResult(
            request_id="req-invalid-json",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print('test')", "python")

        self.assertTrue(result.success)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].text, "not a json string")

    def test_run_with_rich_format_all_fields(self):
        """Test run with rich format containing all possible fields."""
        mock_api_response = {
            "logs": {
                "stdout": ["output"],
                "stderr": [],
            },
            "results": [
                {
                    "text": "text",
                    "html": "<html>",
                    "markdown": "**md**",
                    "png": "base64png",
                    "jpeg": "base64jpeg",
                    "svg": "<svg>",
                    "json": '{"key": "value"}',
                    "latex": "x^2",
                    "chart": '{"mark": "bar"}',
                    "is_main_result": True,
                }
            ],
            "execution_count": 1,
            "execution_time": 0.5,
            "isError": False,
        }
        mock_result = OperationResult(
            request_id="req-all-fields",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print('test')", "python")

        self.assertTrue(result.success)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].text, "text")
        self.assertEqual(result.results[0].html, "<html>")
        self.assertEqual(result.results[0].markdown, "**md**")
        self.assertEqual(result.results[0].png, "base64png")
        self.assertEqual(result.results[0].jpeg, "base64jpeg")
        self.assertEqual(result.results[0].svg, "<svg>")
        self.assertEqual(result.results[0].json, '{"key": "value"}')
        self.assertEqual(result.results[0].latex, "x^2")
        self.assertEqual(result.results[0].chart, '{"mark": "bar"}')

    def test_run_with_legacy_format_no_content(self):
        """Test run with legacy format but no content."""
        mock_api_response = {
            "content": [],
        }
        mock_result = OperationResult(
            request_id="req-legacy-no-content",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print('test')", "python")

        self.assertFalse(result.success)
        self.assertIn("No content found", result.error_message)

    def test_run_with_legacy_format_no_text(self):
        """Test run with legacy format but content has no text field."""
        mock_api_response = {
            "content": [{"other_field": "value"}],
        }
        mock_result = OperationResult(
            request_id="req-legacy-no-text",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print('test')", "python")

        self.assertFalse(result.success)
        self.assertIn("No content found", result.error_message)

    def test_run_with_new_format_all_result_fields(self):
        """Test run with new format containing all result fields."""
        mock_api_response = {
            "result": [
                {
                    "text/plain": "plain text",
                    "text/html": "<html>",
                    "text/markdown": "**md**",
                    "image/png": "pngdata",
                    "image/jpeg": "jpegdata",
                    "image/svg+xml": "<svg>",
                    "application/json": '{"key": "value"}',
                    "text/latex": "x^2",
                    "application/vnd.vegalite.v4+json": '{"mark": "bar"}',
                    "isMainResult": True,
                }
            ],
            "stdout": ["output"],
            "stderr": [],
            "execution_count": 1,
            "execution_time": 0.5,
        }
        mock_result = OperationResult(
            request_id="req-new-all-fields",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print('test')", "python")

        self.assertTrue(result.success)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].text, "plain text")
        self.assertEqual(result.results[0].html, "<html>")
        self.assertEqual(result.results[0].markdown, "**md**")
        self.assertEqual(result.results[0].png, "pngdata")
        self.assertEqual(result.results[0].jpeg, "jpegdata")
        self.assertEqual(result.results[0].svg, "<svg>")
        self.assertEqual(result.results[0].json, '{"key": "value"}')
        self.assertEqual(result.results[0].latex, "x^2")
        self.assertEqual(result.results[0].chart, '{"mark": "bar"}')

    def test_run_with_object_data(self):
        """Test run when API returns a generic object (not dict/string)."""
        # Create a mock that returns a generic object
        mock_api_response = object()  # Generic object
        mock_result = OperationResult(
            request_id="req-object",
            success=True,
            data=mock_api_response,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print('test')", "python")

        # The code should handle this gracefully by converting to string
        self.assertTrue(result.success)
        self.assertEqual(len(result.results), 1)
        # The object should be converted to its string representation
        self.assertIn("object", result.results[0].text)

    def test_run_with_json_string_data(self):
        """Test run when API returns JSON string instead of dict."""
        json_str = '{"result": [{"text/plain": "parsed"}], "stdout": [], "stderr": []}'
        mock_result = OperationResult(
            request_id="req-json-string",
            success=True,
            data=json_str,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print('test')", "python")

        self.assertTrue(result.success)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].text, "parsed")

    def test_run_with_invalid_json_string_data(self):
        """Test run when API returns invalid JSON string."""
        invalid_json = "{not valid json"
        mock_result = OperationResult(
            request_id="req-invalid-json-string",
            success=True,
            data=invalid_json,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run("print('test')", "python")

        self.assertTrue(result.success)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].text, invalid_json)


class TestCodeStreamBeta(unittest.TestCase):
    """Test stream_beta WebSocket streaming code execution."""

    def setUp(self):
        """Set up test fixtures with WS-capable dummy session."""
        self.session = DummySession()
        # Add WS-related attributes
        self.mock_ws_client = MagicMock()
        self.session._get_ws_client = MagicMock(return_value=self.mock_ws_client)
        self.session.tool_list = []
        self.code = Code(self.session)

    def _setup_stream_handle(self, end_data=None, events=None):
        """Helper to set up a mock stream handle with event simulation.

        Args:
            end_data: Dict returned by handle.wait_end()
            events: List of (invocationId, eventData) tuples to replay via on_event
        """
        if end_data is None:
            end_data = {"executionCount": 1, "executionTime": 0.5}

        mock_handle = MagicMock()
        mock_handle.invocation_id = "inv-123"
        mock_handle.wait_end.return_value = end_data

        def fake_call_stream(*, target, data, on_event, on_end, on_error):
            # Replay events synchronously before returning the handle
            for inv_id, evt_data in (events or []):
                on_event(inv_id, evt_data)
            return mock_handle

        self.mock_ws_client.call_stream.side_effect = fake_call_stream
        return mock_handle

    # ── basic success ──────────────────────────────────────────────

    def test_stream_beta_success_with_stdout(self):
        """Test stream_beta=True collects stdout chunks and invokes callback."""
        self._setup_stream_handle(
            end_data={"executionCount": 1, "executionTime": 0.3},
            events=[
                ("inv-123", {"eventType": "stdout", "chunk": "hello\n"}),
                ("inv-123", {"eventType": "stdout", "chunk": "world\n"}),
            ],
        )

        captured = []
        result = self.code.run(
            "print('hello'); print('world')", "python",
            stream_beta=True,
            on_stdout=lambda c: captured.append(c),
        )

        self.assertIsInstance(result, EnhancedCodeExecutionResult)
        self.assertTrue(result.success)
        self.assertEqual(result.logs.stdout, ["hello\n", "world\n"])
        self.assertEqual(captured, ["hello\n", "world\n"])
        self.assertEqual(result.request_id, "inv-123")
        self.assertEqual(result.execution_count, 1)
        self.assertAlmostEqual(result.execution_time, 0.3)

    def test_stream_beta_success_with_stderr(self):
        """Test stream_beta=True collects stderr chunks."""
        self._setup_stream_handle(
            events=[
                ("inv-123", {"eventType": "stderr", "chunk": "warning\n"}),
            ],
        )

        captured_err = []
        result = self.code.run(
            "import sys; sys.stderr.write('warning')", "python",
            stream_beta=True,
            on_stderr=lambda c: captured_err.append(c),
        )

        self.assertTrue(result.success)
        self.assertEqual(result.logs.stderr, ["warning\n"])
        self.assertEqual(captured_err, ["warning\n"])

    def test_stream_beta_success_with_result_event(self):
        """Test stream_beta=True parses result events with mime types."""
        self._setup_stream_handle(
            events=[
                ("inv-123", {
                    "eventType": "result",
                    "result": {
                        "isMainResult": True,
                        "mime": {
                            "text/plain": "42",
                            "text/html": "<b>42</b>",
                        },
                    },
                }),
            ],
        )

        result = self.code.run("1+1", "python", stream_beta=True)

        self.assertTrue(result.success)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].text, "42")
        self.assertEqual(result.results[0].html, "<b>42</b>")
        self.assertTrue(result.results[0].is_main_result)

    def test_stream_beta_result_event_non_dict(self):
        """Test result event with a non-dict payload becomes text."""
        self._setup_stream_handle(
            events=[
                ("inv-123", {"eventType": "result", "result": "plain text"}),
            ],
        )

        result = self.code.run("x", "python", stream_beta=True)

        self.assertTrue(result.success)
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].text, "plain text")

    # ── error events ───────────────────────────────────────────────

    def test_stream_beta_error_event_dict(self):
        """Test stream_beta handles dict error event."""
        self._setup_stream_handle(
            events=[
                ("inv-123", {
                    "eventType": "error",
                    "error": {
                        "code": "RuntimeError",
                        "message": "division by zero",
                        "traceId": "trace-abc",
                    },
                }),
            ],
        )

        errors = []
        result = self.code.run(
            "1/0", "python",
            stream_beta=True,
            on_error=lambda e: errors.append(e),
        )

        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error.name, "RuntimeError")
        self.assertEqual(result.error.value, "division by zero")
        self.assertIn("trace-abc", result.error.traceback)
        self.assertEqual(result.error_message, "division by zero")
        self.assertEqual(len(errors), 1)

    def test_stream_beta_error_event_non_dict(self):
        """Test stream_beta handles non-dict error event."""
        self._setup_stream_handle(
            events=[
                ("inv-123", {"eventType": "error", "error": None}),
            ],
        )

        result = self.code.run("x", "python", stream_beta=True)

        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error.name, "ExecutionError")

    def test_stream_beta_execution_error_in_end_data(self):
        """Test executionError in wait_end data creates error when no prior error event."""
        self._setup_stream_handle(
            end_data={
                "executionCount": 1,
                "executionTime": 0.1,
                "executionError": "TimeoutError",
            },
        )

        result = self.code.run("time.sleep(999)", "python", stream_beta=True)

        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error.name, "ExecutionError")
        self.assertEqual(result.error.value, "TimeoutError")
        self.assertEqual(result.error_message, "TimeoutError")

    def test_stream_beta_status_failed(self):
        """Test status='failed' in end_data marks result as failure."""
        self._setup_stream_handle(
            end_data={"executionCount": 1, "executionTime": 0.1, "status": "failed"},
        )

        result = self.code.run("x", "python", stream_beta=True)

        self.assertFalse(result.success)

    # ── exception handling ─────────────────────────────────────────

    def test_stream_beta_ws_exception(self):
        """Test stream_beta handles WS call_stream exception."""
        self.mock_ws_client.call_stream.side_effect = Exception("WS connection failed")

        errors = []
        result = self.code.run(
            "x", "python",
            stream_beta=True,
            on_error=lambda e: errors.append(e),
        )

        self.assertFalse(result.success)
        self.assertIn("WS connection failed", result.error_message)
        self.assertEqual(len(errors), 1)

    def test_stream_beta_wait_end_exception(self):
        """Test stream_beta handles wait_end exception."""
        mock_handle = MagicMock()
        mock_handle.invocation_id = "inv-123"
        mock_handle.wait_end.side_effect = Exception("Stream interrupted")
        self.mock_ws_client.call_stream.return_value = mock_handle

        errors = []
        result = self.code.run(
            "x", "python",
            stream_beta=True,
            on_error=lambda e: errors.append(e),
        )

        self.assertFalse(result.success)
        self.assertIn("Stream interrupted", result.error_message)
        self.assertEqual(len(errors), 1)

    def test_stream_beta_exception_no_duplicate_on_error(self):
        """Test on_error is not called twice if error event was already reported."""
        def fake_call_stream(*, target, data, on_event, on_end, on_error):
            # First fire an error event
            on_event("inv-123", {"eventType": "error", "error": {"code": "E1", "message": "m1"}})
            # Then the on_error callback from WS also fires
            on_error("inv-123", Exception("WS error"))
            mock_handle = MagicMock()
            mock_handle.invocation_id = "inv-123"
            mock_handle.wait_end.side_effect = Exception("boom")
            return mock_handle

        self.mock_ws_client.call_stream.side_effect = fake_call_stream

        errors = []
        result = self.code.run(
            "x", "python",
            stream_beta=True,
            on_error=lambda e: errors.append(e),
        )

        self.assertFalse(result.success)
        # on_error should have been called by _handle_error_payload (from event + from ws on_error)
        # but NOT again in the except block because error_reported is already True
        self.assertEqual(len(errors), 2)  # event error + ws on_error, not 3

    # ── callbacks are optional ─────────────────────────────────────

    def test_stream_beta_no_callbacks(self):
        """Test stream_beta works without any callbacks."""
        self._setup_stream_handle(
            events=[
                ("inv-123", {"eventType": "stdout", "chunk": "out\n"}),
                ("inv-123", {"eventType": "stderr", "chunk": "err\n"}),
            ],
        )

        result = self.code.run("x", "python", stream_beta=True)

        self.assertTrue(result.success)
        self.assertEqual(result.logs.stdout, ["out\n"])
        self.assertEqual(result.logs.stderr, ["err\n"])

    # ── ignores non-string chunks ──────────────────────────────────

    def test_stream_beta_ignores_non_string_chunk(self):
        """Test stream_beta ignores non-string stdout/stderr chunks."""
        self._setup_stream_handle(
            events=[
                ("inv-123", {"eventType": "stdout", "chunk": 123}),
                ("inv-123", {"eventType": "stderr", "chunk": None}),
                ("inv-123", {"eventType": "stdout", "chunk": "valid\n"}),
            ],
        )

        result = self.code.run("x", "python", stream_beta=True)

        self.assertTrue(result.success)
        self.assertEqual(result.logs.stdout, ["valid\n"])
        self.assertEqual(result.logs.stderr, [])

    # ── target resolution ──────────────────────────────────────────

    def test_stream_beta_resolves_target_from_tool_list(self):
        """Test _resolve_stream_target picks server from tool_list."""
        mock_tool = MagicMock()
        mock_tool.name = "run_code"
        mock_tool.server = "custom_server"
        self.session.tool_list = [mock_tool]

        self._setup_stream_handle()
        self.code.run("x", "python", stream_beta=True)

        call_kwargs = self.mock_ws_client.call_stream.call_args[1]
        self.assertEqual(call_kwargs["target"], "custom_server")

    def test_stream_beta_default_target(self):
        """Test _resolve_stream_target falls back to wuying_codespace."""
        self.session.tool_list = []

        self._setup_stream_handle()
        self.code.run("x", "python", stream_beta=True)

        call_kwargs = self.mock_ws_client.call_stream.call_args[1]
        self.assertEqual(call_kwargs["target"], "wuying_codespace")

    # ── language validation still works in stream path ─────────────

    def test_stream_beta_unsupported_language(self):
        """Test stream_beta path still rejects unsupported languages."""
        result = self.code.run("x", "ruby", stream_beta=True)

        self.assertFalse(result.success)
        self.assertIn("Unsupported language", result.error_message)
        # WS client should not be called
        self.mock_ws_client.call_stream.assert_not_called()

    def test_stream_beta_language_alias(self):
        """Test stream_beta path resolves language aliases."""
        self._setup_stream_handle()
        self.code.run("x", "py", stream_beta=True)

        call_kwargs = self.mock_ws_client.call_stream.call_args[1]
        params = call_kwargs["data"]["params"]
        self.assertEqual(params["language"], "python")

    # ── mixed events ───────────────────────────────────────────────

    def test_stream_beta_mixed_events(self):
        """Test stream_beta with interleaved stdout, stderr, and result events."""
        self._setup_stream_handle(
            end_data={"executionCount": 2, "executionTime": 1.5},
            events=[
                ("inv-123", {"eventType": "stdout", "chunk": "line1\n"}),
                ("inv-123", {"eventType": "stderr", "chunk": "warn\n"}),
                ("inv-123", {"eventType": "stdout", "chunk": "line2\n"}),
                ("inv-123", {
                    "eventType": "result",
                    "result": {"mime": {"text/plain": "42"}, "isMainResult": True},
                }),
            ],
        )

        stdout, stderr = [], []
        result = self.code.run(
            "code", "python",
            stream_beta=True,
            on_stdout=lambda c: stdout.append(c),
            on_stderr=lambda c: stderr.append(c),
        )

        self.assertTrue(result.success)
        self.assertEqual(result.logs.stdout, ["line1\n", "line2\n"])
        self.assertEqual(result.logs.stderr, ["warn\n"])
        self.assertEqual(stdout, ["line1\n", "line2\n"])
        self.assertEqual(stderr, ["warn\n"])
        self.assertEqual(len(result.results), 1)
        self.assertEqual(result.results[0].text, "42")
        self.assertEqual(result.execution_count, 2)
        self.assertAlmostEqual(result.execution_time, 1.5)


if __name__ == "__main__":
    unittest.main()
