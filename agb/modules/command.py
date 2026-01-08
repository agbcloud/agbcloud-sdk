import json
from typing import Dict, Optional

from agb.api.base_service import BaseService
from agb.model.response import ApiResponse
from agb.logger import get_logger, log_operation_start, log_operation_success, log_operation_error

logger = get_logger(__name__)


class CommandResult(ApiResponse):
    """Result of command execution operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        output: str = "",
        error_message: str = "",
        exit_code: Optional[int] = None,
        stdout: str = "",
        stderr: str = "",
        trace_id: str = "",
    ):
        """
        Initialize a CommandResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
            success (bool, optional): Whether the operation was successful.
            output (str, optional): The command output (stdout + stderr for backward compatibility).
            error_message (str, optional): Error message if the operation failed.
            exit_code (Optional[int], optional): The exit code of the command execution (0 for success).
            stdout (str, optional): Standard output from the command execution.
            stderr (str, optional): Standard error from the command execution.
            trace_id (str, optional): Trace ID for error tracking (only present when exit_code != 0).
        """
        super().__init__(request_id)
        self.success = success
        self.output = output
        self.error_message = error_message
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.trace_id = trace_id


class Command(BaseService):
    """
    Handles command execution operations in the AGB cloud environment.
    """

    def execute_command(
        self,
        command: str,
        timeout_ms: int = 1000,
        cwd: Optional[str] = None,
        envs: Optional[Dict[str, str]] = None,
    ) -> CommandResult:
        """
        Execute a shell command with optional working directory and environment variables.

        Executes a shell command in the session environment with configurable timeout,
        working directory, and environment variables. The command runs with session
        user permissions in a Linux shell environment.

        Args:
            command (str): The shell command to execute.
            timeout_ms (int): Timeout in milliseconds (default: 1000ms).
            cwd (Optional[str]): The working directory for command execution. If not specified,
                the command runs in the default session directory.
            envs (Optional[Dict[str, str]]): Environment variables as a dictionary of key-value pairs.
                These variables are set for the command execution only.

        Returns:
            CommandResult: Result object containing:
                - success: Whether the command executed successfully (exit_code == 0)
                - output: Command output for backward compatibility (stdout + stderr)
                - exit_code: The exit code of the command execution (0 for success)
                - stdout: Standard output from the command execution
                - stderr: Standard error from the command execution
                - trace_id: Trace ID for error tracking (only present when exit_code != 0)
                - request_id: Unique identifier for this API request
                - error_message: Error description if execution failed

        Example:
            session = agb.create().session
            result = session.command.execute_command("echo 'Hello, World!'")
            print(result.output)
            print(result.exit_code)
            session.delete()

        Example:
            result = session.command.execute_command(
                "pwd",
                timeout_ms=5000,
                cwd="/tmp",
                envs={"TEST_VAR": "test_value"}
            )
            print(result.stdout)
            session.delete()
        """
        # Validate environment variables - strict type checking
        if envs is not None:
            invalid_vars = []
            for key, value in envs.items():
                if not isinstance(key, str):
                    invalid_vars.append(f"key '{key}' (type: {type(key).__name__})")
                if not isinstance(value, str):
                    invalid_vars.append(f"value for key '{key}' (type: {type(value).__name__})")
            
            if invalid_vars:
                raise ValueError(
                    f"Invalid environment variables: all keys and values must be strings. "
                    f"Found invalid entries: {', '.join(invalid_vars)}"
                )

        try:
            # Build request arguments
            args = {"command": command, "timeout_ms": timeout_ms}
            if cwd is not None:
                args["cwd"] = cwd
            if envs is not None:
                args["envs"] = envs

            log_operation_start("Command.execute_command", f"Command={command}, TimeoutMs={timeout_ms}, Cwd={cwd}, Envs={bool(envs)}")
            result = self._call_mcp_tool("shell", args)
            logger.debug(f"Command executed response: {result}")

            if result.success:
                # Try to parse the new JSON format response
                try:
                    # Parse JSON string from result.data
                    if isinstance(result.data, str):
                        data_json = json.loads(result.data)
                    else:
                        data_json = result.data

                    # Extract fields from new format
                    stdout = data_json.get("stdout", "")
                    stderr = data_json.get("stderr", "")
                    exit_code = data_json.get("exit_code", 0)
                    trace_id = data_json.get("traceId", "")

                    # Determine success based on exit_code (0 means success)
                    success = exit_code == 0

                    # For backward compatibility, output should be stdout + stderr
                    output = stdout + stderr

                    result_msg = f"RequestId={result.request_id}, ExitCode={exit_code}, OutputLength={len(output)}"
                    log_operation_success("Command.execute_command", result_msg)
                    return CommandResult(
                        request_id=result.request_id,
                        success=success,
                        output=output,
                        exit_code=exit_code,
                        stdout=stdout,
                        stderr=stderr,
                        trace_id=trace_id,
                    )
                except (json.JSONDecodeError, TypeError, AttributeError) as e:
                    # Fallback to old format if JSON parsing fails
                    logger.debug(f"Failed to parse JSON response, using old format: {e}")
                    result_msg = f"RequestId={result.request_id}, OutputLength={len(result.data) if result.data else 0}"
                    log_operation_success("Command.execute_command", result_msg)
                    return CommandResult(
                        request_id=result.request_id,
                        success=True,
                        output=result.data if isinstance(result.data, str) else str(result.data),
                    )
            else:
                # Try to parse error message as JSON (in case backend returns JSON in error_message)
                try:
                    if isinstance(result.error_message, str):
                        error_data = json.loads(result.error_message)
                    else:
                        error_data = result.error_message
                    
                    if isinstance(error_data, dict):
                        # Extract fields from error JSON
                        stdout = error_data.get("stdout", "")
                        stderr = error_data.get("stderr", "")
                        exit_code = error_data.get("exit_code")
                        if exit_code is None:
                            exit_code = error_data.get("errorCode", 0)
                        trace_id = error_data.get("traceId", "")
                        # For backward compatibility, output should be stdout + stderr
                        output = stdout + stderr
                        
                        error_msg = stderr or result.error_message or "Failed to execute command"
                        log_operation_error("Command.execute_command", error_msg)
                        return CommandResult(
                            request_id=result.request_id,
                            success=False,
                            output=output,
                            exit_code=exit_code,
                            stdout=stdout,
                            stderr=stderr,
                            trace_id=trace_id,
                            error_message=error_msg,
                        )
                except (json.JSONDecodeError, TypeError, AttributeError):
                    # If parsing fails, use original error message
                    pass
                
                error_msg = result.error_message or "Failed to execute command"
                log_operation_error("Command.execute_command", error_msg)
                return CommandResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("Command.execute_command", str(e), exc_info=True)
            return CommandResult(
                request_id="",
                success=False,
                error_message=f"Failed to execute command: {e}",
            )
