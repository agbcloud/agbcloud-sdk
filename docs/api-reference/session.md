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

Delete this session and release all associated resources.

**Arguments**:

- `sync_context` _bool, optional_ - Whether to sync context data (trigger file uploads)
  before deleting the session. Defaults to False.


**Returns**:

    DeleteResult: Result indicating success or failure with request ID.
  - success (bool): True if deletion succeeded
  - error_message (str): Error details if deletion failed
  - request_id (str): Unique identifier for this API request

## Related Resources

- [AGB API Reference](agb.md)
- [Context API Reference](data_context/context.md)
- [Context Manager API Reference](data_context/context_manager.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
