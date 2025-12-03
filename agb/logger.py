"""
Unified logging configuration for AGB SDK using loguru.

This module provides a centralized logging configuration with beautiful formatting
and structured output for different log levels.
"""

import sys
from pathlib import Path
from typing import Optional, Union
from loguru import logger
import os


class AGBLogger:
    """AGB SDK Logger with beautiful formatting."""

    _initialized = False
    _log_level = "INFO"
    _log_file: Optional[Path] = None

    @classmethod
    def setup(
        cls,
        level: str = "INFO",
        log_file: Optional[Union[str, Path]] = None,
        enable_console: bool = True,
        enable_file: bool = True,
        rotation: str = "10 MB",
        retention: str = "30 days"
    ) -> None:
        """
        Setup the logger with custom configuration.

        Args:
            level (str): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to "INFO".
            log_file (Optional[Union[str, Path]]): Path to log file (optional). Defaults to None.
            enable_console (bool): Whether to enable console logging. Defaults to True.
            enable_file (bool): Whether to enable file logging. Defaults to True.
            rotation (str): Log file rotation size. Defaults to "10 MB".
            retention (str): Log file retention period. Defaults to "30 days".
        """
        if cls._initialized:
            return

        # Remove default handler
        logger.remove()

        cls._log_level = level.upper()

        # Console handler with beautiful formatting
        if enable_console:
            console_format = (
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<bold><blue>AGB</blue></bold> | "
                "<level>{level}</level> | "
                "<yellow>{process.id}:{thread.id}</yellow> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            )

            logger.add(
                sys.stderr,
                format=console_format,
                level=cls._log_level,
                colorize=True,
                backtrace=True,
                diagnose=True
            )

        # File handler with structured formatting
        if enable_file:
            if log_file:
                cls._log_file = Path(log_file) if isinstance(log_file, str) else log_file
            else:
                # Default log file path in python/ directory
                current_dir = Path(__file__).parent.parent  # Go up from AGB/ to python/
                cls._log_file = current_dir / "agb.log"

            cls._log_file.parent.mkdir(parents=True, exist_ok=True)

            file_format = (
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
                "AGB | "
                "{level: <8} | "
                "{process.id}:{thread.id} | "
                "{name}:{function}:{line} | "
                "{message}"
            )

            logger.add(
                str(cls._log_file),
                format=file_format,
                level=cls._log_level,
                rotation=rotation,
                retention=retention,
                backtrace=True,
                diagnose=True
            )

        cls._initialized = True

    @classmethod
    def get_logger(cls, name: Optional[str] = None):
        """
        Get a logger instance.

        Args:
            name (Optional[str]): Logger name (optional). Defaults to None.

        Returns:
            logger: Configured logger instance.
        """
        if not cls._initialized:
            cls.setup()

        if name:
            return logger.bind(name=name)
        return logger

    @classmethod
    def set_level(cls, level: str) -> None:
        """
        Set the logging level.

        Args:
            level (str): New log level.
        """
        cls._log_level = level.upper()
        if cls._initialized:
            # Re-initialize with new level
            cls._initialized = False
            cls.setup(level=cls._log_level)


# Initialize logger on import
AGBLogger.setup(
    level=os.getenv("AGB_LOG_LEVEL", "INFO"),
    enable_console=True,
    enable_file=True,  # Always enable file logging by default
    log_file=os.getenv("AGB_LOG_FILE")  # Use custom path if specified, otherwise use default
)

# Export the logger instance for easy import
log = AGBLogger.get_logger("agb")


def get_logger(name: str):
    """
    Convenience function to get a named logger.

    Args:
        name (str): Logger name.

    Returns:
        logger: Named logger instance.
    """
    return AGBLogger.get_logger(name)


# Compatibility functions for common logging patterns
def log_api_call(api_name: str, request_data: str = "") -> None:
    """
    Log API call with consistent formatting.

    Args:
        api_name (str): Name of the API being called.
        request_data (str): Data sent with the request. Defaults to "".
    """
    log.opt(depth=1).info(f"🔗 API Call: {api_name}")
    if request_data:
        log.opt(depth=1).debug(f"📤 Request: {request_data}")


def log_api_response(response_data: str, success: bool = True) -> None:
    """
    Log API response with consistent formatting.

    Args:
        response_data (str): Data received in the response.
        success (bool): Whether the API call was successful. Defaults to True.
    """
    if success:
        log.opt(depth=1).info("✅ API Response received")
        log.opt(depth=1).info(f"📥 Response: {response_data}")
    else:
        log.opt(depth=1).error("❌ API Response failed")
        log.opt(depth=1).error(f"📥 Response: {response_data}")


def log_operation_start(operation: str, details: str = "") -> None:
    """
    Log the start of an operation.

    Args:
        operation (str): Name of the operation.
        details (str): Additional details about the operation. Defaults to "".
    """
    log.opt(depth=1).info(f"🚀 Starting: {operation}")
    if details:
        log.opt(depth=1).debug(f"📋 Details: {details}")


def log_operation_success(operation: str, result: str = "") -> None:
    """
    Log successful operation completion.

    Args:
        operation (str): Name of the operation.
        result (str): Result details of the operation. Defaults to "".
    """
    log.opt(depth=1).info(f"✅ Completed: {operation}")
    if result:
        log.opt(depth=1).debug(f"📊 Result: {result}")


def log_operation_error(operation: str, error: str) -> None:
    """
    Log operation error.

    Args:
        operation (str): Name of the operation.
        error (str): Error message.
    """
    log.opt(depth=1).error(f"❌ Failed: {operation}")
    log.opt(depth=1).error(f"💥 Error: {error}")


def log_warning(message: str, details: str = "") -> None:
    """
    Log warning with consistent formatting.

    Args:
        message (str): Warning message.
        details (str): Additional details about the warning. Defaults to "".
    """
    log.opt(depth=1).warning(f"⚠️  {message}")
    if details:
        log.opt(depth=1).warning(f"📝 Details: {details}")
