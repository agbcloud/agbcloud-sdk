"""
Unit tests for AGB logger module.
"""

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from agb.logger import (
    AGBLogger,
    _colorize_log_message,
    _mask_sensitive_data,
    get_logger,
    log,
    log_api_call,
    log_api_response,
    log_api_response_with_details,
    log_code_execution_output,
    log_info_with_color,
    log_operation_error,
    log_operation_start,
    log_operation_success,
    log_warning,
    mask_sensitive_data,
)


class TestColorizeLogMessage:
    """Test log message colorization."""

    def test_colorize_api_call(self):
        """Test API call messages are colored blue."""
        record = {"message": "🔗 API Call: test_api"}
        result = _colorize_log_message(record)
        assert result is True
        assert "\033[34m" in record["message"]  # Blue color
        assert "\033[0m" in record["message"]  # Reset

    def test_colorize_api_response_success(self):
        """Test API response success messages are colored green."""
        record = {"message": "✅ API Response received"}
        result = _colorize_log_message(record)
        assert result is True
        assert "\033[32m" in record["message"]  # Green color

    def test_colorize_completed(self):
        """Test completed messages are colored green."""
        record = {"message": "✅ Completed: operation"}
        result = _colorize_log_message(record)
        assert result is True
        assert "\033[32m" in record["message"]  # Green color

    def test_colorize_starting(self):
        """Test starting messages are colored cyan."""
        record = {"message": "🚀 Starting: operation"}
        result = _colorize_log_message(record)
        assert result is True
        assert "\033[36m" in record["message"]  # Cyan color

    def test_colorize_regular_message(self):
        """Test regular messages are not colored."""
        original_message = "Regular log message"
        record = {"message": original_message}
        result = _colorize_log_message(record)
        assert result is True
        assert record["message"] == original_message


class TestAGBLoggerColorDetection:
    """Test color detection logic."""

    @patch("sys.stderr.isatty", return_value=False)
    @patch.dict(os.environ, {"DISABLE_COLORS": "1"}, clear=True)
    def test_should_use_colors_disabled(self, mock_isatty):
        """Test colors are disabled when DISABLE_COLORS=1."""
        assert AGBLogger._should_use_colors() is False

    @patch("sys.stderr.isatty", return_value=False)
    @patch.dict(os.environ, {"FORCE_COLOR": "1"}, clear=True)
    def test_should_use_colors_forced(self, mock_isatty):
        """Test colors are enabled when FORCE_COLOR=1."""
        assert AGBLogger._should_use_colors() is True

    @patch("sys.stderr.isatty", return_value=False)
    @patch.dict(os.environ, {"FORCE_COLOR": "0"}, clear=True)
    def test_should_use_colors_forced_disabled(self, mock_isatty):
        """Test colors are disabled when FORCE_COLOR=0."""
        assert AGBLogger._should_use_colors() is False

    @patch("sys.stderr.isatty", return_value=True)
    @patch.dict(os.environ, {}, clear=True)
    def test_should_use_colors_tty(self, mock_isatty):
        """Test colors are enabled for TTY output."""
        assert AGBLogger._should_use_colors() is True

    @patch("sys.stderr.isatty", return_value=False)
    @patch.dict(os.environ, {"TERM_PROGRAM": "vscode"}, clear=True)
    def test_should_use_colors_vscode(self, mock_isatty):
        """Test colors are enabled for VS Code."""
        assert AGBLogger._should_use_colors() is True

    @patch("sys.stderr.isatty", return_value=False)
    @patch.dict(os.environ, {"GOLAND": "true"}, clear=True)
    def test_should_use_colors_goland(self, mock_isatty):
        """Test colors are enabled for GoLand."""
        assert AGBLogger._should_use_colors() is True

    @patch("sys.stderr.isatty", return_value=False)
    @patch.dict(os.environ, {"IDEA_INITIAL_DIRECTORY": "/path"}, clear=True)
    def test_should_use_colors_intellij(self, mock_isatty):
        """Test colors are enabled for IntelliJ."""
        assert AGBLogger._should_use_colors() is True

    @patch("sys.stderr.isatty", return_value=False)
    @patch.dict(os.environ, {}, clear=True)
    def test_should_use_colors_default_false(self, mock_isatty):
        """Test colors are disabled by default."""
        assert AGBLogger._should_use_colors() is False


class TestAGBLoggerSetup:
    """Test logger setup functionality."""

    def setup_method(self):
        """Reset logger state before each test."""
        AGBLogger._initialized = False

    def teardown_method(self):
        """Clean up after each test."""
        AGBLogger._initialized = False

    def test_setup_basic(self):
        """Test basic logger setup."""
        AGBLogger.setup(level="INFO", force_reinit=True)
        assert AGBLogger._initialized is True
        assert AGBLogger._log_level == "INFO"

    def test_setup_with_custom_level(self):
        """Test logger setup with custom level."""
        AGBLogger.setup(level="DEBUG", force_reinit=True)
        assert AGBLogger._log_level == "DEBUG"

    def test_setup_without_reinit(self):
        """Test setup without reinitialization."""
        AGBLogger.setup(level="INFO", force_reinit=True)
        AGBLogger._log_level = "DEBUG"
        AGBLogger.setup(level="WARNING", force_reinit=False)
        # Should not change because force_reinit=False
        assert AGBLogger._log_level == "DEBUG"

    def test_setup_console_only(self):
        """Test setup with console logging only."""
        AGBLogger.setup(
            level="INFO", enable_console=True, enable_file=False, force_reinit=True
        )
        assert AGBLogger._initialized is True

    def test_setup_file_only(self, tmp_path):
        """Test setup with file logging only."""
        temp_log = tmp_path / "test_agb.log"
        AGBLogger.setup(
            level="INFO",
            enable_console=False,
            enable_file=True,
            log_file=temp_log,
            force_reinit=True,
        )
        assert AGBLogger._initialized is True
        assert AGBLogger._log_file == temp_log

    def test_setup_with_custom_log_file(self, tmp_path):
        """Test setup with custom log file path."""
        temp_log = tmp_path / "custom_agb.log"
        AGBLogger.setup(
            level="INFO", log_file=temp_log, force_reinit=True
        )
        assert AGBLogger._log_file == temp_log

    def test_setup_with_rotation(self, tmp_path):
        """Test setup with log rotation."""
        temp_log = tmp_path / "rotated_agb.log"
        AGBLogger.setup(
            level="INFO",
            log_file=temp_log,
            max_file_size="5 MB",
            retention="7 days",
            force_reinit=True,
        )
        assert AGBLogger._initialized is True

    def test_setup_with_colorize(self):
        """Test setup with explicit colorize setting."""
        AGBLogger.setup(level="INFO", colorize=True, force_reinit=True)
        assert AGBLogger._initialized is True

        AGBLogger.setup(level="INFO", colorize=False, force_reinit=True)
        assert AGBLogger._initialized is True

    def test_get_logger(self):
        """Test getting a logger instance."""
        AGBLogger.setup(force_reinit=True)
        logger = AGBLogger.get_logger("test")
        assert logger is not None

    def test_get_logger_without_name(self):
        """Test getting logger without name."""
        AGBLogger.setup(force_reinit=True)
        logger = AGBLogger.get_logger()
        assert logger is not None

    def test_set_level(self):
        """Test setting log level."""
        AGBLogger.setup(level="INFO", force_reinit=True)
        AGBLogger.set_level("DEBUG")
        assert AGBLogger._log_level == "DEBUG"

    def test_set_level_runtime(self):
        """Test setting log level at runtime."""
        AGBLogger.setup(level="INFO", force_reinit=True)
        AGBLogger.set_level("WARNING")
        assert AGBLogger._log_level == "WARNING"


class TestMaskSensitiveData:
    """Test sensitive data masking."""

    def test_mask_password(self):
        """Test password masking."""
        data = {"username": "test", "password": "secret123"}
        masked = mask_sensitive_data(data)
        assert masked["username"] == "test"
        # Passwords longer than 4 chars show first 2 and last 2 chars
        assert masked["password"] == "se****23"

    def test_mask_api_key(self):
        """Test API key masking."""
        data = {"api_key": "sk_live_1234567890abcdef"}
        masked = mask_sensitive_data(data)
        assert masked["api_key"] == "sk****ef"

    def test_mask_token(self):
        """Test token masking."""
        data = {"token": "Bearer xyz123abc456"}
        masked = mask_sensitive_data(data)
        assert masked["token"] == "Be****56"

    def test_mask_short_password(self):
        """Test short password masking."""
        data = {"password": "123"}
        masked = mask_sensitive_data(data)
        assert masked["password"] == "****"

    def test_mask_nested_dict(self):
        """Test masking in nested dictionaries."""
        data = {
            "user": {"name": "Alice", "password": "secret"},
            "config": {"api_key": "key123"},
        }
        masked = mask_sensitive_data(data)
        assert masked["user"]["name"] == "Alice"
        # Passwords longer than 4 chars show first 2 and last 2 chars
        assert masked["user"]["password"] == "se****et"
        assert masked["config"]["api_key"] == "ke****23"

    def test_mask_list(self):
        """Test masking in lists."""
        data = [
            {"name": "Alice", "api_key": "key_alice"},
            {"name": "Bob", "api_key": "key_bob"},
        ]
        masked = mask_sensitive_data(data)
        assert masked[0]["name"] == "Alice"
        assert masked[0]["api_key"] == "ke****ce"
        assert masked[1]["name"] == "Bob"
        assert masked[1]["api_key"] == "ke****ob"

    def test_mask_with_custom_fields(self):
        """Test masking with custom field names."""
        data = {"credit_card": "1234-5678-9012-3456", "ssn": "123-45-6789"}
        masked = mask_sensitive_data(data, fields=["credit_card", "ssn"])
        assert masked["credit_card"] == "12****56"
        assert masked["ssn"] == "12****89"

    def test_mask_string(self):
        """Test that plain strings are not masked."""
        data = "This is a plain string"
        masked = mask_sensitive_data(data)
        assert masked == "This is a plain string"

    def test_mask_number(self):
        """Test that numbers are not masked."""
        data = 12345
        masked = mask_sensitive_data(data)
        assert masked == 12345

    def test_mask_none(self):
        """Test that None is not masked."""
        data = None
        masked = mask_sensitive_data(data)
        assert masked is None

    def test_mask_empty_dict(self):
        """Test masking empty dictionary."""
        data = {}
        masked = mask_sensitive_data(data)
        assert masked == {}

    def test_mask_empty_list(self):
        """Test masking empty list."""
        data = []
        masked = mask_sensitive_data(data)
        assert masked == []

    def test_mask_case_insensitive(self):
        """Test that field matching is case insensitive."""
        data = {"PASSWORD": "secret", "Api_Key": "key123"}
        masked = mask_sensitive_data(data)
        # Passwords longer than 4 chars show first 2 and last 2 chars
        assert masked["PASSWORD"] == "se****et"
        assert masked["Api_Key"] == "ke****23"


class TestLoggingFunctions:
    """Test logging convenience functions."""

    def test_log_api_call(self):
        """Test API call logging."""
        # Just ensure it doesn't raise an exception
        log_api_call("test_api")
        log_api_call("test_api", "request data")

    def test_log_api_response_success(self):
        """Test successful API response logging."""
        log_api_response("response data", success=True)

    def test_log_api_response_failure(self):
        """Test failed API response logging."""
        log_api_response("error data", success=False)

    def test_log_api_response_with_details_success(self):
        """Test API response logging with details."""
        log_api_response_with_details(
            api_name="test_api",
            request_id="req123",
            success=True,
            key_fields={"status": "200", "count": 5},
            full_response='{"data": "test"}',
        )

    def test_log_api_response_with_details_failure(self):
        """Test failed API response logging with details."""
        log_api_response_with_details(
            api_name="test_api",
            request_id="req123",
            success=False,
            full_response='{"error": "test"}',
        )

    def test_log_code_execution_output_valid(self):
        """Test code execution output logging with valid JSON."""
        raw_output = json.dumps(
            {
                "content": [
                    {"type": "text", "text": "Line 1\nLine 2\nLine 3"},
                ]
            }
        )
        log_code_execution_output("req123", raw_output)

    def test_log_code_execution_output_empty(self):
        """Test code execution output logging with empty content."""
        raw_output = json.dumps({"content": []})
        log_code_execution_output("req123", raw_output)

    def test_log_code_execution_output_invalid_json(self):
        """Test code execution output logging with invalid JSON."""
        raw_output = "invalid json"
        log_code_execution_output("req123", raw_output)

    def test_log_code_execution_output_no_content(self):
        """Test code execution output logging without content field."""
        raw_output = json.dumps({"data": "test"})
        log_code_execution_output("req123", raw_output)

    def test_log_code_execution_output_non_text_content(self):
        """Test code execution output logging with non-text content."""
        raw_output = json.dumps(
            {"content": [{"type": "image", "data": "base64"}]}
        )
        log_code_execution_output("req123", raw_output)

    def test_log_operation_start(self):
        """Test operation start logging."""
        log_operation_start("test_operation")
        log_operation_start("test_operation", "details")

    def test_log_operation_success(self):
        """Test operation success logging."""
        log_operation_success("test_operation")
        log_operation_success("test_operation", "result")

    def test_log_operation_error(self):
        """Test operation error logging."""
        log_operation_error("test_operation", "error message")
        log_operation_error("test_operation", "error message", exc_info=False)

    def test_log_warning(self):
        """Test warning logging."""
        log_warning("warning message")
        log_warning("warning message", "details")

    def test_log_info_with_color(self):
        """Test info logging with custom color."""
        log_info_with_color("colored message")
        log_info_with_color("colored message", "\033[32m")


class TestGetLogger:
    """Test get_logger convenience function."""

    def test_get_logger_default(self):
        """Test get_logger with default name."""
        logger = get_logger()
        assert logger is not None

    def test_get_logger_custom_name(self):
        """Test get_logger with custom name."""
        logger = get_logger("custom")
        assert logger is not None


class TestModuleLog:
    """Test module-level log instance."""

    def test_module_log_exists(self):
        """Test that module-level log instance exists."""
        assert log is not None


class TestLoggerEnvironmentVariable:
    """Test logger initialization from environment variable."""

    @patch.dict(os.environ, {"AGB_LOG_LEVEL": "DEBUG"}, clear=True)
    def test_logger_init_from_env(self):
        """Test logger initialization from AGB_LOG_LEVEL env var."""
        # Reset and reinitialize
        AGBLogger._initialized = False
        # Manually set the env var and call setup
        AGBLogger.setup(level="DEBUG", force_reinit=True)
        assert AGBLogger._log_level == "DEBUG"

    @patch.dict(os.environ, {"AGB_LOG_LEVEL": "WARNING"}, clear=True)
    def test_logger_init_from_env_warning(self):
        """Test logger initialization with WARNING level."""
        AGBLogger._initialized = False
        # Manually set the env var and call setup
        AGBLogger.setup(level="WARNING", force_reinit=True)
        assert AGBLogger._log_level == "WARNING"


class TestLoggerFileHandling:
    """Test logger file handling."""

    def setup_method(self):
        """Reset logger state before each test."""
        AGBLogger._initialized = False

    def teardown_method(self):
        """Clean up after each test."""
        AGBLogger._initialized = False

    def test_log_file_creation(self, tmp_path):
        """Test that log file is created."""
        temp_log = tmp_path / "test_agb_creation.log"
        AGBLogger.setup(
            level="INFO",
            log_file=temp_log,
            enable_console=False,
            enable_file=True,
            force_reinit=True,
        )
        # Write a log message
        logger = AGBLogger.get_logger("test")
        logger.info("Test message")
        # Check file exists
        assert temp_log.exists()

    def test_log_file_directory_creation(self, tmp_path):
        """Test that log file directory is created if it doesn't exist."""
        temp_log = tmp_path / "test_agb_dir" / "subdir" / "test.log"
        AGBLogger.setup(
            level="INFO",
            log_file=temp_log,
            enable_console=False,
            enable_file=True,
            force_reinit=True,
        )
        # Check directory exists
        assert temp_log.parent.exists()

    def test_default_log_file_path(self):
        """Test default log file path."""
        AGBLogger.setup(
            level="INFO",
            enable_console=False,
            enable_file=True,
            force_reinit=True,
        )
        # Default log file should be in python/ directory
        assert AGBLogger._log_file is not None
        assert "agb.log" in str(AGBLogger._log_file)
