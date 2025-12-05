# Command Execution Guide

This guide explains how to execute shell commands in the AGB cloud environment.

## Overview

The `session.command` module provides a direct interface to the underlying Linux shell of your cloud session. It allows you to run system tools, manage processes, and perform operations that aren't covered by the specialized File or Code APIs.

## Quick Reference (1 minute)

```python
# Execute a simple command
result = session.command.execute_command("ls -la /tmp")

if result.success:
    print("Output:", result.output)
else:
    print("Error:", result.error_message)
```

## Core Concepts

### Command Execution Model
Each `execute_command` call runs in a **new, isolated shell session**. This means:
- **Working Directory**: The working directory does NOT persist between separate command calls. Each command starts from the default directory (usually the home directory).
- **Environment Variables**: Environment variables set with `export` do NOT persist to subsequent command calls.

**To work with multiple operations in the same context:**
- Use command chaining with `&&` or `;` to combine operations in a single command:
  ```python
  # Change directory and list files in one command
  session.command.execute_command("cd /tmp && ls -la")

  # Set environment variable and use it in the same command
  session.command.execute_command("export MY_VAR=value && echo $MY_VAR")
  ```
- Use environment variable prefix syntax for single commands:
  ```python
  # Set variable only for this command
  session.command.execute_command("MY_VAR=value ./script.sh")
  ```
- Use absolute paths instead of relying on working directory:
  ```python
  # Use absolute path instead of cd
  session.command.execute_command("ls -la /tmp/myproject")
  ```

### Output Handling
- **Stdout & Stderr**: Both streams are captured and returned in `result.output`.
- **Exit Codes**: A non-zero exit code typically results in `result.success = False`.

### Timeouts
- Commands have a default timeout.
- For long-running operations (like downloads), increase the `timeout_ms` parameter:
  ```python
  session.command.execute_command("wget large-file.zip", timeout_ms=60000)
  ```

## Basic Usage (5-10 minutes)

### 1. System Diagnostics
Check CPU, memory, and disk usage.
```python
session.command.execute_command("free -h")
session.command.execute_command("df -h")
```

### 2. Advanced File Operations
Use `tar`, `gzip`, `grep`, or `awk` for complex file tasks.
```python
# Compress logs
session.command.execute_command("tar -czf logs.tar.gz /var/log/*.log")
```

### 3. Installing Packages
If your session image permits (e.g., has `sudo` or is root), you can install tools.
```python
session.command.execute_command("apt-get update && apt-get install -y jq", timeout_ms=30000)
```

## Best Practices

1. **Avoid Interactive Commands**: Do not run commands that wait for user input (like `python` without `-c`, or interactive installers). They will hang until timeout.
2. **Check Exit Status**: Always check `result.success`.
3. **Use Absolute Paths**: Since each command runs in a new shell session, always use absolute paths instead of relying on working directory persistence.
4. **Chain Related Operations**: If you need to perform multiple operations that depend on each other (like `cd` followed by file operations), combine them in a single command using `&&` or `;`:
   ```python
   # Good: Combine operations in one command
   session.command.execute_command("cd /tmp && ls -la && cat file.txt")

   # Avoid: Separate commands (cd won't persist)
   session.command.execute_command("cd /tmp")  # This won't affect next command
   session.command.execute_command("ls -la")   # Runs from default directory
   ```
5. **Set Environment Variables Per Command**: If you need environment variables, set them in the same command where they're used:
   ```python
   # Good: Set and use in same command
   session.command.execute_command("export PATH=/custom/path:$PATH && my_command")

   # Avoid: Setting in one command and using in another
   session.command.execute_command("export MY_VAR=value")  # Won't persist
   session.command.execute_command("echo $MY_VAR")         # Variable not set
   ```

## Troubleshooting

### Command Not Found
- Use absolute paths (e.g. `/bin/ls` instead of `ls`) if PATH is issues.
- Verify the tool is installed in the image.

### Permission Denied
- Commands run as the default user.
- Use `sudo` if needed and permitted.

### Command Timeout
- Long running commands (like `apt-get install`) may hit default timeout.
- Increase `timeout_ms` parameter in `execute_command`.

### Working Directory or Environment Variables Not Persisting
- **Issue**: Changes made with `cd` or `export` don't persist to the next command.
- **Cause**: Each `execute_command` call runs in a new shell session.
- **Solution**:
  - Combine related operations in a single command using `&&` or `;`
  - Use absolute paths instead of relative paths
  - Set environment variables in the same command where they're used
  ```python
  # Instead of:
  session.command.execute_command("cd /tmp")
  session.command.execute_command("ls -la")

  # Do this:
  session.command.execute_command("cd /tmp && ls -la")
  ```

## Related Documentation

- **[Code Execution Guide](code-execution.md)** - Running Python/JS code
- **[Session Management Guide](session-management.md)** - Managing sessions
- **[API Reference](../api-reference/capabilities/shell_commands.md)** - Complete Command API
- **[Examples](../examples/command_execution/README.md)** - Advanced scripts
