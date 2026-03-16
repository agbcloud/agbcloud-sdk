#!/usr/bin/env python3
"""
Unit tests for Command module in AGB SDK.
Tests command execution functionality with success and failure scenarios.
"""

import json
import unittest
from unittest.mock import MagicMock

from agb.modules.command import Command, CommandResult
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


class TestCommandResult(unittest.TestCase):
    """Test CommandResult class."""

    def test_command_result_initialization(self):
        """Test CommandResult initialization."""
        result = CommandResult(
            request_id="req-123",
            success=True,
            output="command output",
            error_message="",
        )

        self.assertEqual(result.request_id, "req-123")
        self.assertTrue(result.success)
        self.assertEqual(result.output, "command output")
        self.assertEqual(result.error_message, "")

    def test_command_result_failure(self):
        """Test CommandResult with failure."""
        result = CommandResult(
            request_id="req-456",
            success=False,
            output="",
            error_message="Command failed",
        )

        self.assertEqual(result.request_id, "req-456")
        self.assertFalse(result.success)
        self.assertEqual(result.output, "")
        self.assertEqual(result.error_message, "Command failed")

    def test_command_result_with_new_fields(self):
        """Test CommandResult with new fields (exit_code, stdout, stderr, trace_id)."""
        result = CommandResult(
            request_id="req-789",
            success=True,
            output="stdout output",
            error_message="",
            exit_code=0,
            stdout="stdout output",
            stderr="",
            trace_id="trace-123",
        )

        self.assertEqual(result.request_id, "req-789")
        self.assertTrue(result.success)
        self.assertEqual(result.output, "stdout output")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "stdout output")
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.trace_id, "trace-123")

    def test_command_result_with_error_fields(self):
        """Test CommandResult with error fields."""
        result = CommandResult(
            request_id="req-error",
            success=False,
            output="error output",
            error_message="Command failed",
            exit_code=1,
            stdout="",
            stderr="error output",
            trace_id="trace-error-456",
        )

        self.assertEqual(result.request_id, "req-error")
        self.assertFalse(result.success)
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "error output")
        self.assertEqual(result.trace_id, "trace-error-456")


class TestCommand(unittest.TestCase):
    """Test Command class."""

    def setUp(self):
        """Set up test fixtures."""
        self.session = DummySession()
        self.command = Command(self.session)

    def test_execute_success(self):
        """Test successful command execution."""
        # Mock the _call_mcp_tool response
        mock_result = OperationResult(
            request_id="req-123",
            success=True,
            data="Command output line 1\nCommand output line 2",
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        # Execute command
        result = self.command.execute("ls -la", timeout_ms=5000)

        # Assertions
        self.assertTrue(result.success)
        self.assertEqual(result.output, "Command output line 1\nCommand output line 2")
        self.assertEqual(result.request_id, "req-123")
        self.assertEqual(result.error_message, "")
        self.command._call_mcp_tool.assert_called_once_with(
            "shell",
            {"command": "ls -la", "timeout_ms": 5000}
        )

    def test_execute_empty_output(self):
        """Test command execution with empty output."""
        mock_result = OperationResult(
            request_id="req-456",
            success=True,
            data="",
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.command.execute("echo", timeout_ms=1000)

        self.assertTrue(result.success)
        self.assertEqual(result.output, "")
        self.assertEqual(result.request_id, "req-456")

    def test_execute_default_timeout(self):
        """Test command execution with default timeout."""
        mock_result = OperationResult(
            request_id="req-timeout-1",
            success=True,
            data="output",
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.command.execute("ls")

        self.assertTrue(result.success)
        # Verify default timeout is 1000ms
        call_args = self.command._call_mcp_tool.call_args
        self.assertEqual(call_args[0][1]["timeout_ms"], 1000)

    def test_execute_custom_timeout(self):
        """Test command execution with custom timeout."""
        mock_result = OperationResult(
            request_id="req-timeout-2",
            success=True,
            data="output",
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.command.execute("sleep 5", timeout_ms=10000)

        self.assertTrue(result.success)
        call_args = self.command._call_mcp_tool.call_args
        self.assertEqual(call_args[0][1]["timeout_ms"], 10000)

    def test_execute_api_failure(self):
        """Test command execution when API returns failure."""
        mock_result = OperationResult(
            request_id="req-fail-1",
            success=False,
            data=None,
            error_message="Command execution timeout",
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.command.execute("sleep 60", timeout_ms=1000)

        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "req-fail-1")
        self.assertEqual(result.error_message, "Command execution timeout")

    def test_execute_api_failure_no_error_message(self):
        """Test command execution when API fails without error message."""
        mock_result = OperationResult(
            request_id="req-fail-2",
            success=False,
            data=None,
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.command.execute("invalid_command", timeout_ms=1000)

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Failed to execute command")

    def test_execute_exception_handling(self):
        """Test exception handling during command execution."""
        self.command._call_mcp_tool = MagicMock(side_effect=Exception("Network error"))

        result = self.command.execute("ls", timeout_ms=1000)

        self.assertFalse(result.success)
        self.assertIn("Failed to execute command", result.error_message)
        self.assertIn("Network error", result.error_message)

    def test_execute_various_commands(self):
        """Test various command types."""
        commands = [
            "pwd",
            "whoami",
            "echo 'Hello World'",
            "cat /etc/passwd | head -5",
            "python3 --version",
        ]

        for cmd in commands:
            with self.subTest(command=cmd):
                mock_result = OperationResult(
                    request_id=f"req-{cmd}",
                    success=True,
                    data="output",
                )
                self.command._call_mcp_tool = MagicMock(return_value=mock_result)

                result = self.command.execute(cmd, timeout_ms=1000)

                self.assertTrue(result.success)
                self.assertEqual(result.output, "output")

    def test_execute_json_format_response(self):
        """Test command execution with new JSON format response."""
        json_data = {
            "stdout": "Hello World",
            "stderr": "",
            "exit_code": 0,
            "traceId": "trace-json-123",
        }
        mock_result = OperationResult(
            request_id="req-json-1",
            success=True,
            data=json.dumps(json_data),
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.command.execute("echo 'Hello World'", timeout_ms=1000)

        self.assertTrue(result.success)
        self.assertEqual(result.output, "Hello World")
        self.assertEqual(result.stdout, "Hello World")
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.trace_id, "trace-json-123")

    def test_execute_json_format_with_stderr(self):
        """Test command execution with JSON format containing stderr."""
        json_data = {
            "stdout": "",
            "stderr": "cat: file.txt: No such file or directory",
            "exit_code": 2,
            "traceId": "trace-json-456",
        }
        mock_result = OperationResult(
            request_id="req-json-2",
            success=True,
            data=json.dumps(json_data),
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.command.execute("cat file.txt", timeout_ms=1000)

        # exit_code != 0, so success should be False
        self.assertFalse(result.success)
        self.assertEqual(result.output, "cat: file.txt: No such file or directory")
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "cat: file.txt: No such file or directory")
        self.assertEqual(result.exit_code, 2)
        self.assertEqual(result.trace_id, "trace-json-456")

    def test_execute_json_format_dict_response(self):
        """Test command execution with JSON format as dict (not string)."""
        json_data = {
            "stdout": "output text",
            "stderr": "",
            "exit_code": 0,
        }
        mock_result = OperationResult(
            request_id="req-json-3",
            success=True,
            data=json_data,  # Already a dict, not a string
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.command.execute("echo test", timeout_ms=1000)

        self.assertTrue(result.success)
        self.assertEqual(result.stdout, "output text")
        self.assertEqual(result.exit_code, 0)

    def test_execute_backward_compatibility(self):
        """Test backward compatibility with old format (plain text)."""
        mock_result = OperationResult(
            request_id="req-old-format",
            success=True,
            data="Plain text output without JSON",
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.command.execute("ls", timeout_ms=1000)

        self.assertTrue(result.success)
        self.assertEqual(result.output, "Plain text output without JSON")
        # New fields should be None or empty for old format
        self.assertIsNone(result.exit_code)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_execute_with_cwd(self):
        """Test command execution with working directory parameter."""
        mock_result = OperationResult(
            request_id="req-cwd",
            success=True,
            data="output",
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.command.execute("pwd", timeout_ms=1000, cwd="/tmp")

        self.assertTrue(result.success)
        call_args = self.command._call_mcp_tool.call_args
        self.assertEqual(call_args[0][1]["cwd"], "/tmp")

    def test_execute_with_envs(self):
        """Test command execution with environment variables."""
        mock_result = OperationResult(
            request_id="req-envs",
            success=True,
            data="output",
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        envs = {"TEST_VAR": "test_value", "ANOTHER_VAR": "another_value"}
        result = self.command.execute("echo $TEST_VAR", timeout_ms=1000, envs=envs)

        self.assertTrue(result.success)
        call_args = self.command._call_mcp_tool.call_args
        self.assertEqual(call_args[0][1]["envs"], envs)

    def test_execute_with_cwd_and_envs(self):
        """Test command execution with both cwd and envs."""
        mock_result = OperationResult(
            request_id="req-both",
            success=True,
            data="output",
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        envs = {"VAR": "value"}
        result = self.command.execute(
            "pwd", timeout_ms=1000, cwd="/home", envs=envs
        )

        self.assertTrue(result.success)
        call_args = self.command._call_mcp_tool.call_args
        self.assertEqual(call_args[0][1]["cwd"], "/home")
        self.assertEqual(call_args[0][1]["envs"], envs)

    def test_execute_envs_validation_invalid_key_type(self):
        """Test environment variable validation with invalid key type."""
        envs = {123: "value"}  # Invalid: key is not a string

        with self.assertRaises(ValueError) as context:
            self.command.execute("echo test", envs=envs)

        self.assertIn("Invalid environment variables", str(context.exception))
        self.assertIn("all keys and values must be strings", str(context.exception))

    def test_execute_envs_validation_invalid_value_type(self):
        """Test environment variable validation with invalid value type."""
        envs = {"KEY": 123}  # Invalid: value is not a string

        with self.assertRaises(ValueError) as context:
            self.command.execute("echo test", envs=envs)

        self.assertIn("Invalid environment variables", str(context.exception))
        self.assertIn("all keys and values must be strings", str(context.exception))

    def test_execute_envs_validation_multiple_invalid(self):
        """Test environment variable validation with multiple invalid entries."""
        envs = {123: "value", "KEY": 456, "ANOTHER": "valid"}  # Multiple invalid

        with self.assertRaises(ValueError) as context:
            self.command.execute("echo test", envs=envs)

        self.assertIn("Invalid environment variables", str(context.exception))

    def test_execute_error_json_format(self):
        """Test error response with JSON format in error_message."""
        error_json = {
            "stdout": "",
            "stderr": "Command not found",
            "exit_code": 127,
            "traceId": "trace-error-789",
        }
        mock_result = OperationResult(
            request_id="req-error-json",
            success=False,
            error_message=json.dumps(error_json),
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.command.execute("nonexistent_command", timeout_ms=1000)

        self.assertFalse(result.success)
        self.assertEqual(result.output, "Command not found")
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "Command not found")
        self.assertEqual(result.exit_code, 127)
        self.assertEqual(result.trace_id, "trace-error-789")

    def test_execute_error_json_format_with_errorCode(self):
        """Test error response with errorCode field (alternative to exit_code)."""
        error_json = {
            "stdout": "",
            "stderr": "Permission denied",
            "errorCode": 13,  # Alternative field name
            "traceId": "trace-error-alt",
        }
        mock_result = OperationResult(
            request_id="req-error-alt",
            success=False,
            error_message=json.dumps(error_json),
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.command.execute("cat /etc/shadow", timeout_ms=1000)

        self.assertFalse(result.success)
        self.assertEqual(result.exit_code, 13)  # Should use errorCode
        self.assertEqual(result.stderr, "Permission denied")

    def test_execute_error_json_format_exit_code_zero_with_errorCode(self):
        """Test error response with exit_code=0 and errorCode both present.
        
        This tests the fix for the bug where exit_code=0 (falsy) would incorrectly
        fall back to errorCode. Should use exit_code=0, not errorCode.
        """
        error_json = {
            "stdout": "Some output",
            "stderr": "",
            "exit_code": 0,  # Valid exit code, but falsy value
            "errorCode": 13,  # Should NOT be used when exit_code exists
            "traceId": "trace-zero-test",
        }
        mock_result = OperationResult(
            request_id="req-zero-test",
            success=False,
            error_message=json.dumps(error_json),
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.command.execute("test_command", timeout_ms=1000)

        self.assertFalse(result.success)
        # Should use exit_code=0, NOT errorCode=13
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "Some output")
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.trace_id, "trace-zero-test")


if __name__ == "__main__":
    unittest.main()

