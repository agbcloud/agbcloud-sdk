# ContextManager API Reference

The `ContextManager` class provides functionality for managing contexts within a session. It enables you to interact with the contexts that are synchronized to the session, including reading and writing data, and managing file operations.

## Properties

### session

```python
session: BaseSession  # The Session instance that this ContextManager belongs to
```

## Data Types

```python
class ContextStatusData:
    context_id: str     # The ID of the context
    path: str           # The path where the context is mounted
    error_message: str  # Error message if the operation failed
    status: str         # Status of the synchronization task
    start_time: int     # Start time of the task (Unix timestamp)
    finish_time: int    # Finish time of the task (Unix timestamp)
    task_type: str      # Type of the task (e.g., "upload", "download")
```

## Methods

### info

Gets information about context synchronization status.

```python
info(context_id: Optional[str] = None, path: Optional[str] = None, task_type: Optional[str] = None) -> ContextInfoResult
```

**Parameters:**
- `context_id` (str, optional): The ID of the context to get information for.
- `path` (str, optional): The path where the context is mounted.
- `task_type` (str, optional): The type of task to get information for.

**Returns:**
- `ContextInfoResult`: A result object containing the context status data, success status, and request ID. This class inherits from `ApiResponse`.
  - `context_status_data` (List[ContextStatusData]): A list of context status data objects.

**Example:**
```python
from agb import AGB

# Initialize the SDK
agb = AGB(api_key="your_api_key")

# Create a session
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
if result.success:
    session = result.session

    # Get context synchronization information
    info_result = session.context.info()
    if info_result.context_status_data:
        for item in info_result.context_status_data:
            print(f"Context {item.context_id} status: {item.status}")
    else:
        print("No context synchronization tasks found")
```

### sync

Synchronizes a context with the session.

```python
async def sync(
    context_id: Optional[str] = None,
    path: Optional[str] = None,
    mode: Optional[str] = None,
    callback: Optional[Callable[[bool], None]] = None,
    max_retries: int = 150,
    retry_interval: int = 1500
) -> ContextSyncResult
```

**Parameters:**
- `context_id` (str, optional): The ID of the context to synchronize.
- `path` (str, optional): The path where the context should be mounted.
- `mode` (str, optional): The synchronization mode.
- `callback` (Callable[[bool], None], optional): Callback function for synchronous usage.
- `max_retries` (int, optional): Maximum number of retries for polling (default: 150).
- `retry_interval` (int, optional): Milliseconds to wait between retries (default: 1500).

**Returns:**
- `ContextSyncResult`: A result object containing success status and request ID.
  - `success` (bool): Indicates whether the synchronization was successful.

**Example:**
```python
from agb import AGB
from agb.session_params import CreateSessionParams

# Initialize the SDK
agb = AGB(api_key="your_api_key")

# Create a session
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
if result.success:
    session = result.session

    # Trigger context synchronization
    sync_result = await session.context.sync()

    if sync_result.success:
        print(f"Context synchronization triggered successfully, request ID: {sync_result.request_id}")
    else:
        print(f"Failed to trigger context synchronization")
```

## Async Support

The `sync` method supports both synchronous and asynchronous calling patterns:

### Synchronous Usage with Callback

```python
def sync_callback(success: bool):
    if success:
        print("Context sync completed successfully")
    else:
        print("Context sync failed")

# This will return immediately and call the callback when done
session.context.sync(callback=sync_callback)
```

### Asynchronous Usage

```python
import asyncio

async def sync_context():
    # This will wait for completion
    result = await session.context.sync()
    if result.success:
        print("Context sync completed successfully")
    else:
        print("Context sync failed")

# Run the async function
asyncio.run(sync_context())
```

## Error Handling

The ContextManager provides comprehensive error handling and logging:

- All operations return result objects with success status and error messages
- Detailed logging is provided for debugging context synchronization issues
- Automatic retry mechanisms for polling context status
- Graceful handling of network errors and timeouts

## Related Resources

- [Context API Reference](context.md)
- [Session API Reference](../02_session.md)
