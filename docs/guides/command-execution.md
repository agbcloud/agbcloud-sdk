# Command Execution Guide

This guide explains how to execute shell commands in the AGB cloud environment.

## Overview

The `session.command` module provides a direct interface to the underlying Linux shell of your cloud session. It allows you to run system tools, manage processes, and perform operations that aren't covered by the specialized File or Code APIs.

## Quick Start

```python
# Execute a simple command
result = session.command.execute_command("ls -la /tmp")

if result.success:
    print("Output:", result.output)
else:
    print("Error:", result.error_message)
```

## Core Concepts

### Environment Persistence
- **Working Directory**: The shell environment persists the working directory (`pwd`) between commands if you use `cd`.
- **Environment Variables**: To set persistent env vars, export them in `.bashrc` or prepend them to your command (`VAR=val ./script.sh`).

### Output Handling
- **Stdout & Stderr**: Both streams are captured and returned in `result.output`.
- **Exit Codes**: A non-zero exit code typically results in `result.success = False`.

### Timeouts
- Commands have a default timeout.
- For long-running operations (like downloads), increase the `timeout_ms` parameter:
  ```python
  session.command.execute_command("wget large-file.zip", timeout_ms=60000)
  ```

## Common Use Cases

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
session.command.execute_command("apt-get update && apt-get install -y jq")
```

## Best Practices

1. **Avoid Interactive Commands**: Do not run commands that wait for user input (like `python` without `-c`, or interactive installers). They will hang until timeout.
2. **Check Exit Status**: Always check `result.success`.
3. **Use Absolute Paths**: To avoid ambiguity about the current working directory.

## Advanced Examples

For complete scripts demonstrating data processing pipelines, log analysis, and system monitoring scripts, please refer to the executable example:

- **[Complete Example Script](../examples/command_execution/main.py)**
