#!/usr/bin/env python3
"""
Unit tests for Code module in AGB SDK.
Tests code execution functionality with success and failure scenarios.
"""

import unittest
from unittest.mock import MagicMock

from agb.modules.code import Code
from agb.model.response import (
    OperationResult,
    EnhancedCodeExecutionResult,
    ExecutionResult,
    ExecutionLogs,
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
        self.assertEqual(result.error_message, "RuntimeError")

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


if __name__ == "__main__":
    unittest.main()
