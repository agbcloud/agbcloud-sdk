# Logging API Reference

Unified logging configuration for AGB SDK using loguru.

This module provides a centralized logging configuration with beautiful formatting
and structured output for different log levels.

## AGBLogger

```python
class AGBLogger()
```

AGB SDK Logger with beautiful formatting.

### setup

```python
@classmethod
def setup(cls,
          level: str = "INFO",
          log_file: Optional[Union[str, Path]] = None,
          enable_console: bool = True,
          enable_file: bool = True,
          rotation: str = "10 MB",
          retention: str = "30 days") -> None
```

Setup the logger with custom configuration.

**Arguments**:

- `level` _str_ - Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to "INFO".
- `log_file` _Optional[Union[str, Path]]_ - Path to log file (optional). Defaults to None.
- `enable_console` _bool_ - Whether to enable console logging. Defaults to True.
- `enable_file` _bool_ - Whether to enable file logging. Defaults to True.
- `rotation` _str_ - Log file rotation size. Defaults to "10 MB".
- `retention` _str_ - Log file retention period. Defaults to "30 days".

### get\_logger

```python
@classmethod
def get_logger(cls, name: Optional[str] = None)
```

Get a logger instance.

**Arguments**:

- `name` _Optional[str]_ - Logger name (optional). Defaults to None.


**Returns**:

    logger: Configured logger instance.

### set\_level

```python
@classmethod
def set_level(cls, level: str) -> None
```

Set the logging level.

**Arguments**:

- `level` _str_ - New log level.

#### log

```python
log = AGBLogger.get_logger("agb")
```

### get\_logger

```python
def get_logger(name: str)
```

Convenience function to get a named logger.

**Arguments**:

- `name` _str_ - Logger name.


**Returns**:

    logger: Named logger instance.

### log\_api\_call

```python
def log_api_call(api_name: str, request_data: str = "") -> None
```

Log API call with consistent formatting.

**Arguments**:

- `api_name` _str_ - Name of the API being called.
- `request_data` _str_ - Data sent with the request. Defaults to "".

### log\_api\_response

```python
def log_api_response(response_data: str, success: bool = True) -> None
```

Log API response with consistent formatting.

**Arguments**:

- `response_data` _str_ - Data received in the response.
- `success` _bool_ - Whether the API call was successful. Defaults to True.

### log\_operation\_start

```python
def log_operation_start(operation: str, details: str = "") -> None
```

Log the start of an operation.

**Arguments**:

- `operation` _str_ - Name of the operation.
- `details` _str_ - Additional details about the operation. Defaults to "".

### log\_operation\_success

```python
def log_operation_success(operation: str, result: str = "") -> None
```

Log successful operation completion.

**Arguments**:

- `operation` _str_ - Name of the operation.
- `result` _str_ - Result details of the operation. Defaults to "".

### log\_operation\_error

```python
def log_operation_error(operation: str, error: str) -> None
```

Log operation error.

**Arguments**:

- `operation` _str_ - Name of the operation.
- `error` _str_ - Error message.

### log\_warning

```python
def log_warning(message: str, details: str = "") -> None
```

Log warning with consistent formatting.

**Arguments**:

- `message` _str_ - Warning message.
- `details` _str_ - Additional details about the warning. Defaults to "".

---

*Documentation generated automatically from source code using pydoc-markdown.*
