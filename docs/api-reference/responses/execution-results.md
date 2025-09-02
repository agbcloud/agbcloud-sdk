# Execution Results

This document covers the response types for code and command execution operations in the AGB SDK.

## Overview

Execution results are returned by operations that run code or execute shell commands in the AGB cloud environment.

## Response Types

### CodeExecutionResult

Returned by `session.code.run_code()` operations.

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `result` | `str` | The execution output/result |
| `error_message` | `str` | Error message if the operation failed |

**Example:**
```python
code_result = session.code.run_code("print('Hello World')", "python")
if code_result.success:
    print(f"Output: {code_result.result}")
else:
    print(f"Error: {code_result.error_message}")
```

### CommandResult

Returned by `session.command.execute_command()` operations.

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `output` | `str` | The command output (stdout) |
| `error_message` | `str` | Error message if the operation failed |

**Example:**
```python
cmd_result = session.command.execute_command("ls -la")
if cmd_result.success:
    print(f"Output: {cmd_result.output}")
else:
    print(f"Error: {cmd_result.error_message}")
```

## Supported Languages

### Python
```python
code_result = session.code.run_code("""
import sys
print(f"Python version: {sys.version}")
""", "python")
```

### JavaScript
```python
code_result = session.code.run_code("""
console.log("Hello from JavaScript!");
""", "javascript")
```

### Java
```python
code_result = session.code.run_code("""
System.out.println("Hello from Java!");
""", "java")
```

### R
```python
code_result = session.code.run_code("""
cat("Hello from R!\\n")
""", "r")
```

## Common Error Scenarios

### Code Execution Errors
- **Syntax Errors**: Invalid syntax in the provided code
- **Runtime Errors**: Errors that occur during code execution
- **Timeout Errors**: Code execution exceeds the timeout limit
- **Unsupported Language**: Language not supported by the system

### Command Execution Errors
- **Command Not Found**: The specified command doesn't exist
- **Permission Denied**: Insufficient permissions to execute the command
- **Invalid Arguments**: Command arguments are invalid
- **File Not Found**: Referenced files don't exist

## Best Practices

### Error Handling
```python
# Always check success before accessing results
result = session.code.run_code(code, language)
if result.success:
    # Process successful result
    output = result.result
else:
    # Handle error
    print(f"Execution failed: {result.error_message}")
    print(f"Request ID: {result.request_id}")
```

### Timeout Management
```python
# Set appropriate timeouts for different operations
quick_result = session.code.run_code("print('Hello')", "python", timeout_s=10)
long_result = session.code.run_code("""
import time
time.sleep(30)
print("Done!")
""", "python", timeout_s=60)
```

### Input Validation
```python
# Validate input before execution
if not code.strip():
    print("Error: Empty code provided")
    return

if language not in ["python", "javascript", "java", "r"]:
    print(f"Error: Unsupported language: {language}")
    return

result = session.code.run_code(code, language)
```

## Related Documentation

- **[CodeExecutionResult](code-result.md)** - Detailed code execution response documentation
- **[CommandResult](command-result.md)** - Detailed command execution response documentation
- **[Code Module](../modules/code.md)** - Code execution module documentation
- **[Command Module](../modules/command.md)** - Command execution module documentation
