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

Deletes a context.

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

Updates a context's properties.

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

- [Session API Reference](session.md)
- [ContextManager API Reference](context-manager.md)
