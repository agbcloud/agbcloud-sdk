#!/usr/bin/env python3
"""
Unit tests for Code module in AGB SDK.
Tests code execution functionality with success and failure scenarios.
"""

import unittest
from unittest.mock import MagicMock

from agb.modules.code import Code, CodeExecutionResult
from agb.model.response import OperationResult


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


class TestCodeExecutionResult(unittest.TestCase):
    """Test CodeExecutionResult class."""

    def test_code_execution_result_initialization(self):
        """Test CodeExecutionResult initialization."""
        result = CodeExecutionResult(
            request_id="req-123",
            success=True,
            result="output",
            error_message="",
        )

        self.assertEqual(result.request_id, "req-123")
        self.assertTrue(result.success)
        self.assertEqual(result.result, "output")
        self.assertEqual(result.error_message, "")

    def test_code_execution_result_failure(self):
        """Test CodeExecutionResult with failure."""
        result = CodeExecutionResult(
            request_id="req-456",
            success=False,
            result="",
            error_message="Execution failed",
        )

        self.assertEqual(result.request_id, "req-456")
        self.assertFalse(result.success)
        self.assertEqual(result.result, "")
        self.assertEqual(result.error_message, "Execution failed")


class TestCode(unittest.TestCase):
    """Test Code class."""

    def setUp(self):
        """Set up test fixtures."""
        self.session = DummySession()
        self.code = Code(self.session)

    def test_run_code_success_python(self):
        """Test successful Python code execution."""
        # Mock the _call_mcp_tool response
        mock_result = OperationResult(
            request_id="req-123",
            success=True,
            data="Hello, World!",
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        # Execute code
        result = self.code.run_code("print('Hello, World!')", "python", timeout_s=60)

        # Assertions
        self.assertTrue(result.success)
        self.assertEqual(result.result, "Hello, World!")
        self.assertEqual(result.request_id, "req-123")
        self.assertEqual(result.error_message, "")
        self.code._call_mcp_tool.assert_called_once_with(
            "run_code",
            {"code": "print('Hello, World!')", "language": "python", "timeout_s": 60}
        )

    def test_run_code_success_javascript(self):
        """Test successful JavaScript code execution."""
        mock_result = OperationResult(
            request_id="req-456",
            success=True,
            data="42",
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run_code("console.log(42)", "javascript", timeout_s=30)

        self.assertTrue(result.success)
        self.assertEqual(result.result, "42")
        self.assertEqual(result.request_id, "req-456")

    def test_run_code_success_java(self):
        """Test successful Java code execution."""
        mock_result = OperationResult(
            request_id="req-789",
            success=True,
            data="Java output",
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run_code("System.out.println('test')", "java", timeout_s=120)

        self.assertTrue(result.success)
        self.assertEqual(result.result, "Java output")

    def test_run_code_success_r(self):
        """Test successful R code execution."""
        mock_result = OperationResult(
            request_id="req-r-1",
            success=True,
            data="[1] 1 2 3",
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run_code("c(1, 2, 3)", "r", timeout_s=90)

        self.assertTrue(result.success)
        self.assertEqual(result.result, "[1] 1 2 3")

    def test_run_code_case_insensitive_language(self):
        """Test that language parameter is case-insensitive."""
        mock_result = OperationResult(
            request_id="req-case-1",
            success=True,
            data="output",
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run_code("print('test')", "PYTHON", timeout_s=60)

        self.assertTrue(result.success)
        # Verify that language was converted to lowercase
        call_args = self.code._call_mcp_tool.call_args
        self.assertEqual(call_args[0][1]["language"], "python")

    def test_run_code_unsupported_language(self):
        """Test execution with unsupported language."""
        result = self.code.run_code("print('test')", "ruby", timeout_s=60)

        self.assertFalse(result.success)
        self.assertIn("Unsupported language", result.error_message)
        self.assertIn("ruby", result.error_message)

    def test_run_code_api_failure(self):
        """Test code execution when API returns failure."""
        mock_result = OperationResult(
            request_id="req-fail-1",
            success=False,
            data=None,
            error_message="API error occurred",
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run_code("print('test')", "python", timeout_s=60)

        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "req-fail-1")
        self.assertEqual(result.error_message, "API error occurred")

    def test_run_code_api_failure_no_error_message(self):
        """Test code execution when API fails without error message."""
        mock_result = OperationResult(
            request_id="req-fail-2",
            success=False,
            data=None,
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run_code("print('test')", "python", timeout_s=60)

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Failed to run code")

    def test_run_code_exception_handling(self):
        """Test exception handling during code execution."""
        self.code._call_mcp_tool = MagicMock(side_effect=Exception("Network error"))

        result = self.code.run_code("print('test')", "python", timeout_s=60)

        self.assertFalse(result.success)
        self.assertIn("Failed to run code", result.error_message)
        self.assertIn("Network error", result.error_message)

    def test_run_code_default_timeout(self):
        """Test code execution with default timeout."""
        mock_result = OperationResult(
            request_id="req-timeout-1",
            success=True,
            data="output",
        )
        self.code._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.code.run_code("print('test')", "python")

        self.assertTrue(result.success)
        # Verify default timeout is 60
        call_args = self.code._call_mcp_tool.call_args
        self.assertEqual(call_args[0][1]["timeout_s"], 60)


if __name__ == "__main__":
    unittest.main()

