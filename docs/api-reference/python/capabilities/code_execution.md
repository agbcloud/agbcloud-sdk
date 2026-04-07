# Code API Reference

## Related Tutorial

- [Code Execution Guide](../../../code-interpreting/overview.md) - Execute code in isolated environments

## Overview

The Code module provides secure code execution capabilities in isolated environments.
It supports multiple programming languages including Python, JavaScript, and more.


## Requirements

- Requires `agb-code-space-1` image for code execution features



#### LANGUAGE\_ALIASES

```python
LANGUAGE_ALIASES = {
    "py": "python",
    "python3": "python",
    "js": "javascript",
    "node" ...
```

#### SUPPORTED\_LANGUAGES

```python
SUPPORTED_LANGUAGES = {"python", "javascript", "java", "r"}
```

## Code

```python
class Code(BaseService)
```

Handles code execution operations in the AGB cloud environment.

### run

```python
def run(
    code: str,
    language: str,
    timeout_s: int = 60,
    stream_beta: bool = False,
    on_stdout: Optional[Callable[[str], None]] = None,
    on_stderr: Optional[Callable[[str], None]] = None,
    on_error: Optional[Callable[[Any], None]] = None
) -> EnhancedCodeExecutionResult
```

Execute code in the specified language with a timeout.

This is the primary public method for code execution. For real-time
streaming output, set stream_beta=True and provide callback functions.

**Arguments**:

    code: The code to execute.
    language: The programming language of the code. Case-insensitive.
  Supported values: 'python', 'javascript', 'r', 'java'.
    Aliases: 'py' -> 'python', 'js'/'node' -> 'javascript'.
    timeout_s: The timeout for the code execution in seconds. Default is 60s.
    stream_beta: If True, use WebSocket streaming for real-time stdout/stderr
  output. Requires the session to have a valid ws_url. Default is False.
    on_stdout: Callback invoked with each stdout chunk during streaming.
  Only used when stream_beta=True.
    on_stderr: Callback invoked with each stderr chunk during streaming.
  Only used when stream_beta=True.
    on_error: Callback invoked when an error occurs during streaming.
  Only used when stream_beta=True.


**Returns**:

    EnhancedCodeExecutionResult: Result object containing success status,
  execution results with rich format support (HTML, images, charts, etc.),
  logs, and error information if any.

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
