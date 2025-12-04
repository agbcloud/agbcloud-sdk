# Command API Reference

## ⚡ Related Tutorial

- [Command Execution Guide](../../guides/command-execution.md) - Learn how to execute commands in sessions

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
def execute_command(command: str, timeout_ms: int = 1000) -> CommandResult
```

Execute a command in the cloud environment with a specified timeout.

**Arguments**:

- `command` _str_ - The command to execute.
- `timeout_ms` _int_ - The timeout for the command execution in milliseconds. Defaults to 1000.


**Returns**:

    CommandResult: Result object containing success status, command output,
  and error message if any.

## Best Practices

1. Always specify appropriate timeout values based on expected command duration
2. Handle command execution errors gracefully
3. Use absolute paths when referencing files in commands
4. Be aware that commands run with session user permissions
5. Clean up temporary files created by commands

## Related Resources

- [Session API Reference](../session.md)
- [File System API Reference](file_system.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
