# Context Manager API Reference

## 🗂️ Related Tutorial

- [Context Usage Guide](../../guides/context-usage-guide.md) - Advanced context management features

## Overview

The Context Manager module provides advanced context management capabilities
including context synchronization and lifecycle management.




## ContextStatusData

```python
class ContextStatusData()
```

## ContextInfoResult

```python
class ContextInfoResult(ApiResponse)
```

## ContextSyncResult

```python
class ContextSyncResult(ApiResponse)
```

## ContextManager

```python
class ContextManager()
```

Manages context operations within a session in the AGB cloud environment.

The ContextManager provides methods to get information about context synchronization
status and to synchronize contexts with the session.

### info

```python
def info(context_id: Optional[str] = None,
         path: Optional[str] = None,
         task_type: Optional[str] = None) -> ContextInfoResult
```

Get detailed information about context synchronization status.

**Arguments**:

- `context_id` _Optional[str]_ - The ID of the context to query.
- `path` _Optional[str]_ - Specific path within the context to query.
- `task_type` _Optional[str]_ - Filter by task type (e.g., "upload", "download").


**Returns**:

    ContextInfoResult: Result object containing status information.

### sync

```python
async def sync(context_id: Optional[str] = None,
               path: Optional[str] = None,
               mode: Optional[str] = None,
               callback: Optional[Callable[[bool], None]] = None,
               max_retries: int = 150,
               retry_interval: int = 1500) -> ContextSyncResult
```

Synchronizes context with support for both async and sync calling patterns.

Usage:
# Async call - wait for completion
result = await session.context.sync()

# Sync call - immediate return with callback
session.context.sync(callback=lambda success: logger.info(f"Done: {success}"))

**Arguments**:

- `context_id` _Optional[str]_ - Optional ID of the context to synchronize. If provided, `path` must also be provided.
- `path` _Optional[str]_ - Optional path where the context should be mounted. If provided, `context_id` must also be provided.
- `mode` _Optional[str]_ - Optional synchronization mode (e.g., "upload", "download")
- `callback` _Optional[Callable[[bool], None]]_ - Optional callback function that receives success status. If provided, the method runs in background and calls callback when complete
- `max_retries` _int_ - Maximum number of retries for polling. Defaults to 150.
- `retry_interval` _int_ - Milliseconds to wait between retries. Defaults to 1500.


**Returns**:

    ContextSyncResult: Result object containing success status and request ID

## Related Resources

- [Context API Reference](context.md)
- [Session API Reference](../session.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
