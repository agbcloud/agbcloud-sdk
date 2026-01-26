#!/usr/bin/env python3
"""
Unit tests for Code module in AGB SDK.
Tests code execution functionality with success and failure scenarios.
"""

import unittest
from unittest.mock import MagicMock

from agb.modules.code import Code
from agb.model.response import OperationResult, EnhancedCodeExecutionResult, ExecutionResult, ExecutionLogs


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
            execution_time=0.5
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
            execution_time=0.0
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
            "result": [{"text/plain": "Hello, World!","isMainResult": True}],
            "stdout": ["Hello, World!"],
            "stderr": [],
            "execution_count": 1,
            "execution_time": 0.5
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
            {"code": "print('Hello, World!')", "language": "python", "timeout_s": 60}
        )

    def test_run_success_javascript(self):
        """Test successful JavaScript code execution."""
        mock_api_response = {
            "result": [{"text/plain": "42"}],
            "stdout": ["42"],
            "stderr": [],
            "execution_count": 1,
            "execution_time": 0.3
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
            "execution_time": 1.2
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
            "execution_time": 0.8
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
            "execution_time": 0.4
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
            "execution_time": 0.2
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
            "execution_time": 0.3
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


if __name__ == "__main__":
    unittest.main()

