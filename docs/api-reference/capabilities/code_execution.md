# Code API Reference

## Related Tutorial

- [Code Execution Guide](/code-interpreting/overview.md) - Execute code in isolated environments

## Overview

The Code module provides secure code execution capabilities in isolated environments.
It supports multiple programming languages including Python, JavaScript, and more.


## Requirements

- Requires `agb-code-space-1` image for code execution features



## Code

```python
class Code(BaseService)
```

Handles code execution operations in the AGB cloud environment.

### run

```python
def run(code: str,
        language: str,
        timeout_s: int = 60) -> EnhancedCodeExecutionResult
```

Execute code in the specified language with a timeout.

**Arguments**:

- `code` _str_ - The code to execute.
- `language` _str_ - The programming language of the code. Supported languages are:
  'python', 'javascript', 'java', 'r'.
- `timeout_s` _int_ - The timeout for the code execution in seconds. Default is 60s.


**Returns**:

    EnhancedCodeExecutionResult: Enhanced result object containing success status,
  execution results with rich format support (HTML, images, charts, etc.),
  logs, and error information if any.


**Raises**:

    CommandError: If the code execution fails or if an unsupported language is
  specified.

## Best Practices

1. Validate code syntax before execution
2. Set appropriate execution timeouts
3. Handle execution errors and exceptions
4. Use proper resource limits to prevent resource exhaustion
5. Clean up temporary files after code execution

## Related Resources

- [Session API Reference](../session.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
