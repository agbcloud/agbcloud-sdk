# Session API Reference

## 🔧 Related Tutorial

- [Session Management Guide](../guides/session-management.md) - Detailed tutorial on session lifecycle and management

## Overview

The Session module provides methods for creating, managing, and terminating sessions
in the AGB cloud environment. Sessions are the foundation for all operations.




## Session

```python
class Session()
```

Session represents a session in the AGB cloud environment.

### set\_labels

```python
def set_labels(labels: Dict[str, str]) -> OperationResult
```

Sets the labels for this session.

**Arguments**:

- `labels` _Dict[str, str]_ - The labels to set for the session.


**Returns**:

    OperationResult: Result indicating success or failure with request ID.


**Raises**:

    SessionError: If the operation fails.

### get\_labels

```python
def get_labels() -> OperationResult
```

Gets the labels for this session.

**Returns**:

    OperationResult: Result containing the labels as data and request ID.


**Raises**:

    SessionError: If the operation fails.

### info

```python
def info() -> OperationResult
```

Get session information including resource details.

**Returns**:

    OperationResult: Result containing the session information as data and
  request ID.

### get\_link

```python
def get_link(protocol_type: Optional[str] = None,
             port: Optional[int] = None) -> OperationResult
```

Get a link associated with the current session.

**Arguments**:

- `protocol_type` _Optional[str]_ - The protocol type to use for the
  link. Defaults to None.
- `port` _Optional[int]_ - The port to use for the link.


**Returns**:

    OperationResult: Result containing the link as data and request ID.


**Raises**:

    SessionError: If the request fails or the response is invalid.

### delete

```python
def delete(sync_context: bool = False) -> DeleteResult
```

Delete a session by session object.

**Arguments**:

- `sync_context` _bool_ - Whether to sync context before deletion. Defaults to False.


**Returns**:

    DeleteResult: Result indicating success or failure and request ID.

### pause

```python
def pause(timeout: int = 600,
          poll_interval: float = 2.0) -> SessionPauseResult
```

Synchronously pause this session, putting it into a dormant state.

This method internally calls the pause_session_async API and then polls the get_session API
to check the session status until it becomes PAUSED or until timeout.

**Arguments**:

- `timeout` _int, optional_ - Timeout in seconds to wait for the session to pause.
  Defaults to 600 seconds.
- `poll_interval` _float, optional_ - Interval in seconds between status polls.
  Defaults to 2.0 seconds.


**Returns**:

    SessionPauseResult: Result containing the request ID, success status, and final session status.
  - success (bool): True if the session was successfully paused
  - request_id (str): Unique identifier for this API request
  - status (str): Final session status (should be "PAUSED" if successful)
  - error_message (str): Error description (if success is False)
  - code (str): API response code (if available)
  - message (str): API response message (if available)
  - http_status_code (int): HTTP status code (if available)

### pause\_async

```python
async def pause_async(timeout: int = 600,
                      poll_interval: float = 2.0) -> SessionPauseResult
```

Asynchronously pause this session, putting it into a dormant state.

This method directly calls the pause_session_async API and then polls the get_session API
asynchronously to check the session status until it becomes PAUSED or until timeout.

**Arguments**:

- `timeout` _int, optional_ - Timeout in seconds to wait for the session to pause.
  Defaults to 600 seconds.
- `poll_interval` _float, optional_ - Interval in seconds between status polls.
  Defaults to 2.0 seconds.


**Returns**:

    SessionPauseResult: Result containing the request ID, success status, and final session status.
  - success (bool): True if the session was successfully paused
  - request_id (str): Unique identifier for this API request
  - status (str): Final session status (should be "PAUSED" if successful)
  - error_message (str): Error description (if success is False)
  - code (str): API response code (if available)
  - message (str): API response message (if available)
  - http_status_code (int): HTTP status code (if available)

### resume

```python
def resume(timeout: int = 600,
           poll_interval: float = 2.0) -> SessionResumeResult
```

Synchronously resume this session from a paused state.

This method internally calls the resume_session_async API and then polls the get_session API
to check the session status until it becomes RUNNING or until timeout.

**Arguments**:

- `timeout` _int, optional_ - Timeout in seconds to wait for the session to resume.
  Defaults to 600 seconds.
- `poll_interval` _float, optional_ - Interval in seconds between status polls.
  Defaults to 2.0 seconds.


**Returns**:

    SessionResumeResult: Result containing the request ID, success status, and final session status.
  - success (bool): True if the session was successfully resumed
  - request_id (str): Unique identifier for this API request
  - status (str): Final session status (should be "RUNNING" if successful)
  - error_message (str): Error description (if success is False)
  - code (str): API response code (if available)
  - message (str): API response message (if available)
  - http_status_code (int): HTTP status code (if available)

### resume\_async

```python
async def resume_async(timeout: int = 600,
                       poll_interval: float = 2.0) -> SessionResumeResult
```

Asynchronously resume this session from a paused state.

This method directly calls the resume_session_async API and then polls the get_session API
asynchronously to check the session status until it becomes RUNNING or until timeout.

**Arguments**:

- `timeout` _int, optional_ - Timeout in seconds to wait for the session to resume.
  Defaults to 600 seconds.
- `poll_interval` _float, optional_ - Interval in seconds between status polls.
  Defaults to 2.0 seconds.


**Returns**:

    SessionResumeResult: Result containing the request ID, success status, and final session status.
  - success (bool): True if the session was successfully resumed
  - request_id (str): Unique identifier for this API request
  - status (str): Final session status (should be "RUNNING" if successful)
  - error_message (str): Error description (if success is False)
  - code (str): API response code (if available)
  - message (str): API response message (if available)
  - http_status_code (int): HTTP status code (if available)

## Related Resources

- [AGB API Reference](agb.md)
- [Context API Reference](data_context/context.md)
- [Context Manager API Reference](data_context/context_manager.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
