# Context API Reference

The Context API provides functionality for managing persistent storage contexts in the AGB cloud environment. Contexts allow you to persist data across sessions and reuse it in future sessions.

## Context Class

The `Context` class represents a persistent storage context in the AGB cloud environment.

### Properties

```python
id: str                    # The unique identifier of the context
name: str                  # The name of the context
created_at: Optional[str]  # Date and time when the Context was created
last_used_at: Optional[str] # Date and time when the Context was last used
```

## ContextService Class

The `ContextService` class provides methods for managing persistent contexts in the AGB cloud environment.

### list

Lists all available contexts.

```python
list(params: Optional[ContextListParams] = None) -> ContextListResult
```

**Parameters:**
- `params` (ContextListParams, optional): Parameters for listing contexts. If None, defaults will be used.

**Returns:**
- `ContextListResult`: A result object containing the list of Context objects, pagination information, and request ID.

**Example:**
```python
from agb import AGB

# Initialize the SDK
agb = AGB(api_key="your_api_key")

# List all contexts
result = agb.context.list()
if result.success:
    print(f"Found {len(result.contexts)} contexts:")
    for context in result.contexts:
        print(f"Context ID: {context.id}, Name: {context.name}, Created: {context.created_at}")
else:
    print("Failed to list contexts")

# List contexts with pagination using next_token
from agb.context import ContextListParams

# Get first page with limited results
params = ContextListParams(max_results=5)
result = agb.context.list(params)
if result.success:
    print(f"First page: Found {len(result.contexts)} contexts")
    for context in result.contexts:
        print(f"Context ID: {context.id}, Name: {context.name}")

    # Check if there are more pages and get next page using next_token
    if result.next_token:
        print(f"Total contexts: {result.total_count}")
        print("Getting next page...")

        # Use next_token to get the next page
        next_params = ContextListParams(
            max_results=5,
            next_token=result.next_token
        )
        next_result = agb.context.list(next_params)

        if next_result.success:
            print(f"Next page: Found {len(next_result.contexts)} contexts")
            for context in next_result.contexts:
                print(f"Context ID: {context.id}, Name: {context.name}")
        else:
            print(f"Failed to get next page: {next_result.error_message}")
    else:
        print("No more pages available")
else:
    print("Failed to list contexts")
```

### get

Gets a context by name. Optionally creates it if it doesn't exist.

```python
get(name: str, create: bool = False, login_region_id: Optional[str] = None) -> ContextResult
```

**Parameters:**
- `name` (str): The name of the context to get.
- `create` (bool, optional): Whether to create the context if it doesn't exist. Defaults to False.
- `login_region_id` (Optional[str], optional): Login region ID for the request.
  If None or empty, defaults to Hangzhou region (cn-hangzhou). Defaults to None.

**Returns:**
- `ContextResult`: A result object containing the Context object and request ID.

**Example:**
```python
from agb import AGB

# Initialize the SDK
agb = AGB(api_key="your_api_key")

# Get a context, creating it if it doesn't exist
result = agb.context.get("my-persistent-context", create=True)
if result.success:
    context = result.context
    print(f"Context ID: {context.id}, Name: {context.name}, Created: {context.created_at}")
else:
    print(f"Failed to get context: {result.error_message}")

# Get a context with specific login region ID
result = agb.context.get("my-context", login_region_id="us-west-1")
if result.success:
    context = result.context
    print(f"Context ID: {context.id}, Name: {context.name}")
else:
    print(f"Failed to get context: {result.error_message}")

# Get a context using default region (Hangzhou)
result = agb.context.get("my-context")  # Will use cn-hangzhou as default
if result.success:
    context = result.context
    print(f"Context ID: {context.id}, Name: {context.name}")
else:
    print(f"Failed to get context: {result.error_message}")
```

### create

Creates a new context.

```python
create(name: str) -> ContextResult
```

**Parameters:**
- `name` (str): The name of the context to create.

**Returns:**
- `ContextResult`: A result object containing the created Context object and request ID.

**Example:**
```python
from agb import AGB

# Initialize the SDK
agb = AGB(api_key="your_api_key")

# Create a new context
result = agb.context.create("my-new-context")
if result.success:
    context = result.context
    print(f"Created context with ID: {context.id}, Name: {context.name}")
else:
    print(f"Failed to create context: {result.error_message}")
```

### delete

Deletes the specified context.

```python
delete(context: Context) -> OperationResult
```

**Parameters:**
- `context` (Context): The Context object to delete.

**Returns:**
- `OperationResult`: A result object containing success status and request ID.

**Example:**
```python
from agb import AGB

# Initialize the SDK
agb = AGB(api_key="your_api_key")

# Get a context first
result = agb.context.get("my-context")
if result.success and result.context:
    # Delete the context
    delete_result = agb.context.delete(result.context)
    if delete_result.success:
        print("Context deleted successfully")
    else:
        print(f"Failed to delete context: {delete_result.error_message}")
else:
    print(f"Failed to get context: {result.error_message}")
```

### update

Updates the specified context.

```python
update(context: Context) -> OperationResult
```

**Parameters:**
- `context` (Context): The Context object with updated properties.

**Returns:**
- `OperationResult`: A result object containing success status and request ID.

**Example:**
```python
from agb import AGB

# Initialize the SDK
agb = AGB(api_key="your_api_key")

# Get a context first
result = agb.context.get("my-context")
if result.success and result.context:
    # Update the context name
    context = result.context
    context.name = "my-renamed-context"

    # Save the changes
    update_result = agb.context.update(context)
    if update_result.success:
        print("Context updated successfully")
    else:
        print(f"Failed to update context: {update_result.error_message}")
else:
    print(f"Failed to get context: {result.error_message}")
```

### clear
Clears the context's persistent data.
```python
clear(context_id: str, timeout: int = 60, poll_interval: float = 2.0) -> ClearContextResult
```
**Parameters:**
- `context_id` (str): The unique identifier of the context to clear.
- `timeout` (int, optional): Timeout in seconds to wait for task completion. Default is 60 seconds.
- `poll_interval` (float, optional): Interval in seconds between status polls. Default is 2.0 seconds.
**Returns:**
- `ClearContextResult`: A result object containing the final task result. The status field will be "available" on success.
**State Transitions:**
- "clearing": Data clearing is in progress
- "available": Clearing completed successfully (final success state)
**Example:**
```python
from agb import AGB
# Initialize the SDK
agb = AGB(api_key="your_api_key")
# Get a context first
result = agb.context.get("my-context")
if result.success and result.context:
    context = result.context
    # Clear context data synchronously (wait for completion)
    clear_result = agb.context.clear(context.id)
    if clear_result.success:
        print(f"Context data cleared successfully")
        print(f"Final Status: {clear_result.status}")
        # Expected output: Final Status: available
        print(f"Request ID: {clear_result.request_id}")
        # Expected: A valid UUID-format request ID
    else:
        print(f"Failed to clear context: {clear_result.error_message}")
else:
    print(f"Failed to get context: {result.error_message}")
```
### clear_async
Asynchronously initiates a task to clear the context's persistent data.
```python
clear_async(context_id: str) -> ClearContextResult
```
**Parameters:**
- `context_id` (str): The unique identifier of the context to clear.
**Returns:**
- `ClearContextResult`: A result object indicating the task has been successfully started, with status field set to "clearing".
**Example:**
```python
from agb import AGB
# Initialize the SDK
agb = AGB(api_key="your_api_key")
# Get a context first
result = agb.context.get("my-context")
if result.success and result.context:
    context = result.context
    # Start clearing context data asynchronously (non-blocking)
    clear_result = agb.context.clear_async(context.id)
    if clear_result.success:
        print(f"Clear task started: Success={clear_result.success}, Status={clear_result.status}")
        # Expected output: Clear task started: Success=True, Status=clearing
        print(f"Request ID: {clear_result.request_id}")
        # Expected: A valid UUID-format request ID
    else:
        print(f"Failed to start clear: {clear_result.error_message}")
else:
    print(f"Failed to get context: {result.error_message}")
```
### get_clear_status
Queries the status of the clearing task.
```python
get_clear_status(context_id: str) -> ClearContextResult
```
**Parameters:**
- `context_id` (str): The unique identifier of the context to check.
**Returns:**
- `ClearContextResult`: A result object containing the current task status.
**State Transitions:**
- "clearing": Data clearing is in progress
- "available": Clearing completed successfully (final success state)
**Example:**
```python
from agb import AGB
# Initialize the SDK
agb = AGB(api_key="your_api_key")
# Get a context first
result = agb.context.get("my-context")
if result.success and result.context:
    context = result.context
    # Check clearing status
    status_result = agb.context.get_clear_status(context.id)
    if status_result.success:
        print(f"Current status: {status_result.status}")
        print(f"Request ID: {status_result.request_id}")
        # Expected: Current status: clearing/available
    else:
        print(f"Failed to get status: {status_result.error_message}")
else:
    print(f"Failed to get context: {result.error_message}")

## File Operations

### get_file_download_url

Gets a presigned download URL for a file in a context.

```python
get_file_download_url(context_id: str, file_path: str) -> FileUrlResult
```

**Parameters:**
- `context_id` (str): The ID of the context.
- `file_path` (str): The path of the file to download.

**Returns:**
- `FileUrlResult`: A result object containing the download URL and expiration time.

### get_file_upload_url

Gets a presigned upload URL for a file in a context.

```python
get_file_upload_url(context_id: str, file_path: str) -> FileUrlResult
```

**Parameters:**
- `context_id` (str): The ID of the context.
- `file_path` (str): The path of the file to upload.

**Returns:**
- `FileUrlResult`: A result object containing the upload URL and expiration time.

### delete_file

Deletes a file in a context.

```python
delete_file(context_id: str, file_path: str) -> OperationResult
```

**Parameters:**
- `context_id` (str): The ID of the context.
- `file_path` (str): The path of the file to delete.

**Returns:**
- `OperationResult`: A result object containing success status and request ID.

### list_files

Lists files under a specific folder path in a context.

```python
list_files(
    context_id: str,
    parent_folder_path: str,
    page_number: int = 1,
    page_size: int = 50,
) -> ContextFileListResult
```

**Parameters:**
- `context_id` (str): The ID of the context.
- `parent_folder_path` (str): The path of the parent folder.
- `page_number` (int): Page number for pagination.
- `page_size` (int): Number of items per page.

**Returns:**
- `ContextFileListResult`: A result object containing the list of files and pagination information.

## Related Resources

- [Session API Reference](../02_session.md)
- [ContextManager API Reference](context-manager.md)
