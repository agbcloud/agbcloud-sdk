# CommandResult

`CommandResult` is the response type returned by command execution operations in the AGB SDK.

## Overview

The `CommandResult` class represents the outcome of shell command execution operations, such as `session.command.execute_command()`.

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `output` | `str` | The command output (stdout) |
| `error_message` | `str` | Error message if the operation failed |

## Usage

```python
from agb import AGB
from agb.session_params import CreateSessionParams

# Initialize AGB client
agb = AGB()

# Create a session
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
if result.success:
    session = result.session

    # Execute a shell command
    cmd_result = session.command.execute_command("ls -la")

    # Check if execution was successful
    if cmd_result.success:
        print("Command executed successfully")
        print(f"Output: {cmd_result.output}")
        print(f"Request ID: {cmd_result.request_id}")
    else:
        print(f"Command execution failed: {cmd_result.error_message}")
```

## Success Response

When the operation is successful:

```python
cmd_result.success = True
cmd_result.output = """total 8
drwxr-xr-x  2 user user 4096 Jan 15 10:30 .
drwxr-xr-x  3 user user 4096 Jan 15 10:30 ..
-rw-r--r--  1 user user   12 Jan 15 10:30 test.txt"""
cmd_result.error_message = ""
cmd_result.request_id = "req_123456789"
```

## Error Response

When the operation fails:

```python
cmd_result.success = False
cmd_result.output = ""
cmd_result.error_message = "Command not found: invalid_command"
cmd_result.request_id = "req_123456789"
```

## Common Commands

### File Operations
```python
# List files
cmd_result = session.command.execute_command("ls -la")

# Create directory
cmd_result = session.command.execute_command("mkdir -p /tmp/my_project")

# Copy files
cmd_result = session.command.execute_command("cp source.txt destination.txt")

# Remove files
cmd_result = session.command.execute_command("rm -f temp_file.txt")
```

### System Information
```python
# Get system info
cmd_result = session.command.execute_command("uname -a")

# Check disk usage
cmd_result = session.command.execute_command("df -h")

# Check memory usage
cmd_result = session.command.execute_command("free -m")

# Get current user
cmd_result = session.command.execute_command("whoami")
```

### Package Management
```python
# Install packages (if available)
cmd_result = session.command.execute_command("pip install requests")
# Check Python version
cmd_result = session.command.execute_command("python3 --version")
# Check Node.js version
cmd_result = session.command.execute_command("node --version")
```
### Text Processing
```python
# Search in files
cmd_result = session.command.execute_command("grep -r 'pattern' /path/to/search")

# Count lines
cmd_result = session.command.execute_command("wc -l file.txt")

# Sort lines
cmd_result = session.command.execute_command("sort file.txt")
```

## Methods

All response objects inherit from `ApiResponse` and have access to the `request_id` property for tracking API requests.

## Advanced Usage

### Chaining Commands
```python
# Chain commands with &&
cmd_result = session.command.execute_command("cd /tmp && ls -la")

# Use pipes
cmd_result = session.command.execute_command("ps aux | grep python")

# Complex command
cmd_result = session.command.execute_command("find /tmp -name '*.txt' -exec wc -l {} +")
```

### Environment Variables
```python
# Set environment variable
cmd_result = session.command.execute_command("export MY_VAR=hello && echo $MY_VAR")

# Use environment variables
cmd_result = session.command.execute_command("echo $HOME")
```

### Working Directory
```python
# Change directory and execute
cmd_result = session.command.execute_command("cd /tmp && pwd")

# Execute in specific directory
cmd_result = session.command.execute_command("ls -la /home")
```

## Related Types

- **[BaseSession](../core/session.md)** - The session object for command execution
- **[SessionResult](session-result.md)** - Result type for session creation

## Best Practices

### Always Check Success
```python
cmd_result = session.command.execute_command(command)

if cmd_result.success:
    # Process the output
    output = cmd_result.output
    print(f"Command output: {output}")
else:
    # Handle errors
    print(f"Command failed: {cmd_result.error_message}")
```

### Handle Long Output
```python
cmd_result = session.command.execute_command("find / -name '*.txt' 2>/dev/null")

if cmd_result.success:
    output = cmd_result.output
    if len(output) > 1000:
        print(f"Output truncated (first 1000 chars): {output[:1000]}...")
    else:
        print(f"Full output: {output}")
```

### Use Appropriate Commands
```python
# Good: Use built-in commands
cmd_result = session.command.execute_command("ls -la")

# Avoid: Potentially dangerous commands
# cmd_result = session.command.execute_command("rm -rf /")
# cmd_result = session.command.execute_command("sudo su")
```
