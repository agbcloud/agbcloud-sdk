# CodeExecutionResult

`CodeExecutionResult` is the response type returned by code execution operations in the AGB SDK.

## Overview

The `CodeExecutionResult` class represents the outcome of code execution operations, such as `session.code.run_code()`.

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `result` | `str` | The execution output/result |
| `error_message` | `str` | Error message if the operation failed |

## Usage

```python
from agb import AGB

# Initialize AGB client
agb = AGB()

# Create a session
result = agb.create()
if result.success:
    session = result.session

    # Execute Python code
    code_result = session.code.run_code("""
import datetime
print(f"Current time: {datetime.datetime.now()}")
print("Hello from AGB!")
""", "python")

    # Check if execution was successful
    if code_result.success:
        print("Code executed successfully")
        print(f"Output: {code_result.result}")
        print(f"Request ID: {code_result.request_id}")
    else:
        print(f"Code execution failed: {code_result.error_message}")
```

## Supported Languages

The AGB SDK supports multiple programming languages:

### Python
```python
code_result = session.code.run_code("""
import sys
print(f"Python version: {sys.version}")
print("Hello from Python!")
""", "python")
```

### JavaScript
```python
code_result = session.code.run_code("""
console.log("Hello from JavaScript!");
console.log("Current time:", new Date().toISOString());
""", "javascript")
```

### Java
```python
code_result = session.code.run_code("""
System.out.println("Hello from Java!");
System.out.println("Java version: " + System.getProperty("java.version"));
""", "java")
```

### R
```python
code_result = session.code.run_code("""
cat("Hello from R!\\n")
cat("R version:", R.version.string, "\\n")
""", "r")
```

## Methods

All response objects inherit from `ApiResponse` and have access to the `request_id` property for tracking API requests.

## Common Error Scenarios

### Syntax Errors
```python
# Python syntax error
code_result = session.code.run_code("print('Hello world'", "python")
# code_result.error_message = "SyntaxError: unexpected EOF while parsing"
```

### Runtime Errors
```python
# Division by zero
code_result = session.code.run_code("1/0", "python")
# code_result.error_message = "ZeroDivisionError: division by zero"
```

### Unsupported Language
```python
# Unsupported language
code_result = session.code.run_code("print('Hello')", "unsupported")
# code_result.error_message = "Unsupported language: unsupported"
```

### Timeout
```python
# Code execution timeout
code_result = session.code.run_code("""
import time
time.sleep(300)  # 5 minutes
""", "python", timeout_s=30)
# code_result.error_message = "Code execution timeout"
```

## Best Practices

### Always Check Success
```python
code_result = session.code.run_code(code, language)

if code_result.success:
    # Process the result
    output = code_result.result
    print(f"Code output: {output}")
else:
    # Handle errors
    print(f"Execution failed: {code_result.error_message}")
```

### Set Appropriate Timeouts
```python
# For quick operations
code_result = session.code.run_code("print('Hello')", "python", timeout_s=10)

# For longer operations
code_result = session.code.run_code("""
import time
# Long running computation
for i in range(1000000):
    pass
print("Done!")
""", "python", timeout_s=60)
```

### Handle Different Languages
```python
languages = ["python", "javascript", "java", "r"]
for lang in languages:
    code_result = session.code.run_code(f"print('Hello from {lang}')", lang)
    if code_result.success:
        print(f"{lang}: {code_result.result}")
    else:
        print(f"{lang} failed: {code_result.error_message}")
```
