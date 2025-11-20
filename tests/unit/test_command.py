#!/usr/bin/env python3
"""
Unit tests for Command module in AGB SDK.
Tests command execution functionality with success and failure scenarios.
"""

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

    def find_server_for_tool(self, tool_name: str) -> str:
        return "default-server"


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


class TestCommand(unittest.TestCase):
    """Test Command class."""

    def setUp(self):
        """Set up test fixtures."""
        self.session = DummySession()
        self.command = Command(self.session)

    def test_execute_command_success(self):
        """Test successful command execution."""
        # Mock the _call_mcp_tool response
        mock_result = OperationResult(
            request_id="req-123",
            success=True,
            data="Command output line 1\nCommand output line 2",
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        # Execute command
        result = self.command.execute_command("ls -la", timeout_ms=5000)

        # Assertions
        self.assertTrue(result.success)
        self.assertEqual(result.output, "Command output line 1\nCommand output line 2")
        self.assertEqual(result.request_id, "req-123")
        self.assertEqual(result.error_message, "")
        self.command._call_mcp_tool.assert_called_once_with(
            "shell",
            {"command": "ls -la", "timeout_ms": 5000}
        )

    def test_execute_command_empty_output(self):
        """Test command execution with empty output."""
        mock_result = OperationResult(
            request_id="req-456",
            success=True,
            data="",
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.command.execute_command("echo", timeout_ms=1000)

        self.assertTrue(result.success)
        self.assertEqual(result.output, "")
        self.assertEqual(result.request_id, "req-456")

    def test_execute_command_default_timeout(self):
        """Test command execution with default timeout."""
        mock_result = OperationResult(
            request_id="req-timeout-1",
            success=True,
            data="output",
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.command.execute_command("ls")

        self.assertTrue(result.success)
        # Verify default timeout is 1000ms
        call_args = self.command._call_mcp_tool.call_args
        self.assertEqual(call_args[0][1]["timeout_ms"], 1000)

    def test_execute_command_custom_timeout(self):
        """Test command execution with custom timeout."""
        mock_result = OperationResult(
            request_id="req-timeout-2",
            success=True,
            data="output",
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.command.execute_command("sleep 5", timeout_ms=10000)

        self.assertTrue(result.success)
        call_args = self.command._call_mcp_tool.call_args
        self.assertEqual(call_args[0][1]["timeout_ms"], 10000)

    def test_execute_command_api_failure(self):
        """Test command execution when API returns failure."""
        mock_result = OperationResult(
            request_id="req-fail-1",
            success=False,
            data=None,
            error_message="Command execution timeout",
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.command.execute_command("sleep 60", timeout_ms=1000)

        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "req-fail-1")
        self.assertEqual(result.error_message, "Command execution timeout")

    def test_execute_command_api_failure_no_error_message(self):
        """Test command execution when API fails without error message."""
        mock_result = OperationResult(
            request_id="req-fail-2",
            success=False,
            data=None,
        )
        self.command._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.command.execute_command("invalid_command", timeout_ms=1000)

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Failed to execute command")

    def test_execute_command_exception_handling(self):
        """Test exception handling during command execution."""
        self.command._call_mcp_tool = MagicMock(side_effect=Exception("Network error"))

        result = self.command.execute_command("ls", timeout_ms=1000)

        self.assertFalse(result.success)
        self.assertIn("Failed to execute command", result.error_message)
        self.assertIn("Network error", result.error_message)

    def test_execute_command_various_commands(self):
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

                result = self.command.execute_command(cmd, timeout_ms=1000)

                self.assertTrue(result.success)
                self.assertEqual(result.output, "output")


if __name__ == "__main__":
    unittest.main()

