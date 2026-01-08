# Command API Reference

## Related Tutorial

- [Command Execution Guide](/command/overview.md) - Learn how to execute commands in sessions

## Overview

The Command module provides methods for executing shell commands within a session
in the AGB cloud environment. It supports command execution with configurable timeouts.




## CommandResult

```python
class CommandResult(ApiResponse)
```

Result of command execution operations.

## Command

```python
class Command(BaseService)
```

Handles command execution operations in the AGB cloud environment.

### execute\_command

```python
def execute_command(command: str,
                    timeout_ms: int = 1000,
                    cwd: Optional[str] = None,
                    envs: Optional[Dict[str, str]] = None) -> CommandResult
```

Execute a shell command with optional working directory and environment variables.

Executes a shell command in the session environment with configurable timeout,
working directory, and environment variables. The command runs with session
user permissions in a Linux shell environment.

**Arguments**:

- `command` _str_ - The shell command to execute.
- `timeout_ms` _int_ - Timeout in milliseconds (default: 1000ms).
- `cwd` _Optional[str]_ - The working directory for command execution. If not specified,
  the command runs in the default session directory.
- `envs` _Optional[Dict[str, str]]_ - Environment variables as a dictionary of key-value pairs.
  These variables are set for the command execution only.


**Returns**:

    CommandResult: Result object containing:
  - success: Whether the command executed successfully (exit_code == 0)
  - output: Command output for backward compatibility (stdout + stderr)
  - exit_code: The exit code of the command execution (0 for success)
  - stdout: Standard output from the command execution
  - stderr: Standard error from the command execution
  - trace_id: Trace ID for error tracking (only present when exit_code != 0)
  - request_id: Unique identifier for this API request
  - error_message: Error description if execution failed


**Example**:

session = agb.create().session
result = session.command.execute_command("echo 'Hello, World!'")
print(result.output)
print(result.exit_code)
session.delete()


**Example**:

result = session.command.execute_command(
"pwd",
timeout_ms=5000,
cwd="/tmp",
    envs={"TEST_VAR": "test_value"}
)
print(result.stdout)
session.delete()

## Best Practices

1. Always specify appropriate timeout values based on expected command duration
2. Handle command execution errors gracefully
3. Use absolute paths when referencing files in commands, or use the `cwd` parameter
4. Use the `cwd` parameter to set working directory instead of `cd` commands
5. Use the `envs` parameter to set environment variables instead of `export` commands
6. Check `exit_code` for more precise error handling (0 means success)
7. Use `stdout` and `stderr` separately for better output parsing
8. Be aware that commands run with session user permissions
9. Clean up temporary files created by commands

## Related Resources

- [Session API Reference](../session.md)
- [File System API Reference](file_system.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
