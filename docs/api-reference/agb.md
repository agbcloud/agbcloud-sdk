# AGB API Reference

## Related Tutorial

- [Quick Start Guide](../quickstart.md) - Get started with the AGB Python SDK

## Overview

The main AGB module provides the core functionality for creating and managing sessions
with the AGB cloud platform. It serves as the entry point for all SDK operations.




AGB represents the main client for interacting with the AGB cloud runtime
environment.

## AGB

```python
class AGB()
```

AGB represents the main client for interacting with the AGB cloud runtime
environment.

### create

```python
def create(params: Optional[CreateSessionParams] = None) -> SessionResult
```

Create a new session in the AGB cloud environment.

**Arguments**:

- `params` _Optional[CreateSessionParams]_ - Parameters for creating the session.
  Defaults to None.


**Returns**:

    SessionResult: Result containing the created session and request ID.

### list

```python
def list(labels: Optional[Dict[str, str]] = None,
         page: Optional[int] = None,
         limit: Optional[int] = None) -> SessionListResult
```

Returns paginated list of session IDs filtered by labels.

**Arguments**:

- `labels` _Optional[Dict[str, str]]_ - Labels to filter sessions.
  Defaults to None (empty dict).
- `page` _Optional[int]_ - Page number for pagination (starting from 1).
  Defaults to None (returns first page).
- `limit` _Optional[int]_ - Maximum number of items per page.
  Defaults to None (uses default of 10).


**Returns**:

    SessionListResult: Paginated list of session IDs that match the labels,
  including request_id, success status, and pagination information.

### delete

```python
def delete(session: Session, sync_context: bool = False) -> DeleteResult
```

Delete a session by session object.

**Arguments**:

- `session` _Session_ - The session to delete.
- `sync_context` _bool_ - Whether to sync context before deletion. Defaults to False.


**Returns**:

    DeleteResult: Result indicating success or failure and request ID.

### get\_session

```python
def get_session(session_id: str) -> GetSessionResult
```

Get session information by session ID.

**Arguments**:

- `session_id` _str_ - The ID of the session to retrieve.


**Returns**:

    GetSessionResult: Result containing session information.

### get

```python
def get(session_id: str) -> SessionResult
```

Get a session by its ID.

This method retrieves a session by calling the GetSession API
and returns a SessionResult containing the Session object and request ID.

**Arguments**:

- `session_id` _str_ - The ID of the session to retrieve.


**Returns**:

    SessionResult: Result containing the Session instance, request ID, and success status.

## Related Resources

- [Session API Reference](session.md)
- [Context API Reference](data_context/context.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
