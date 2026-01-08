# Context API Reference

## Related Tutorial

- [Context Usage Guide](/context/overview.md) - Learn about context management and data persistence

## Overview

The Context module provides methods for managing session context and data persistence.
It allows you to store and retrieve data across session operations.




## Context

```python
class Context()
```

Represents a persistent storage context in the AGB cloud environment.

**Attributes**:

- `id` _str_ - The unique identifier of the context.
- `name` _str_ - The name of the context.
- `created_at` _str_ - Date and time when the Context was created.
- `last_used_at` _str_ - Date and time when the Context was last used.

## ContextResult

```python
class ContextResult(ApiResponse)
```

Result of operations returning a Context.

## ContextListResult

```python
class ContextListResult(ApiResponse)
```

Result of operations returning a list of Contexts.

## ContextFileEntry

```python
class ContextFileEntry()
```

Represents a file item in a context.

## FileUrlResult

```python
class FileUrlResult(ApiResponse)
```

Result of a presigned URL request.

## ContextFileListResult

```python
class ContextFileListResult(ApiResponse)
```

Result of file listing operation.

## ContextListParams

```python
class ContextListParams()
```

Parameters for listing contexts with pagination support.

## ClearContextResult

```python
class ClearContextResult(OperationResult)
```

Result of context clear operations, including the real-time status.

**Attributes**:

- `request_id` _str_ - Unique identifier for the API request.
- `success` _bool_ - Whether the operation was successful.
- `error_message` _str_ - Error message if the operation failed.
- `status` _Optional[str]_ - Current status of the clearing task. This corresponds to the
  context's state field. Possible values:
  - "clearing": Context data is being cleared (in progress)
  - "available": Clearing completed successfully
- `context_id` _Optional[str]_ - The unique identifier of the context being cleared.

## ContextService

```python
class ContextService()
```

Provides methods to manage persistent contexts in the AGB cloud environment.

### list

```python
def list(params: Optional[ContextListParams] = None) -> ContextListResult
```

Lists all available contexts with pagination support.

**Arguments**:

- `params` _Optional[ContextListParams], optional_ - Parameters for listing contexts.
  If None, defaults will be used.


**Returns**:

    ContextListResult: A result object containing the list of Context objects,
  pagination information, and request ID.

### get

```python
def get(name: Optional[str] = None,
        create: bool = False,
        login_region_id: Optional[str] = None,
        context_id: Optional[str] = None) -> ContextResult
```

Gets a context by ID or name. Optionally creates it if it doesn't exist.

**Arguments**:

- `name` _Optional[str]_ - The name of the context to get. Either name or context_id must be provided.
- `create` _bool, optional_ - Whether to create the context if it doesn't exist.
  If True, context_id cannot be provided (only name is allowed). Defaults to False.
- `login_region_id` _Optional[str], optional_ - Login region ID for the request.
  If None or empty, defaults to Hangzhou region (cn-hangzhou).
- `context_id` _Optional[str]_ - The ID of the context to get. Either name or context_id must be provided.
  This parameter is placed last for backward compatibility.


**Returns**:

    ContextResult: The ContextResult object containing the Context and request ID.


**Raises**:

    ValueError: If validation fails (both name and context_id are None, or
  context_id is provided when create is True).

### create

```python
def create(name: str) -> ContextResult
```

Creates a new context with the given name.

**Arguments**:

- `name` _str_ - The name for the new context.


**Returns**:

    ContextResult: The created ContextResult object with request ID.

### update

```python
def update(context: Context) -> OperationResult
```

Updates the specified context.

**Arguments**:

- `context` _Context_ - The Context object to update.


**Returns**:

    OperationResult: Result object containing success status and request ID.

### delete

```python
def delete(context: Context) -> OperationResult
```

Deletes the specified context.

**Arguments**:

- `context` _Context_ - The Context object to delete.


**Returns**:

    OperationResult: Result object containing success status and request ID.

### get\_file\_download\_url

```python
def get_file_download_url(context_id: str, file_path: str) -> FileUrlResult
```

Get a presigned download URL for a file in a context.

**Arguments**:

- `context_id` _str_ - The ID of the context.
- `file_path` _str_ - The path of the file within the context.


**Returns**:

    FileUrlResult: Result object containing the download URL.

### get\_file\_upload\_url

```python
def get_file_upload_url(context_id: str, file_path: str) -> FileUrlResult
```

Get a presigned upload URL for a file in a context.

**Arguments**:

- `context_id` _str_ - The ID of the context.
- `file_path` _str_ - The path of the file within the context.


**Returns**:

    FileUrlResult: Result object containing the upload URL.

### delete\_file

```python
def delete_file(context_id: str, file_path: str) -> OperationResult
```

Delete a file in a context.

**Arguments**:

- `context_id` _str_ - The ID of the context.
- `file_path` _str_ - The path of the file within the context.


**Returns**:

    OperationResult: Result object containing success status.

### list\_files

```python
def list_files(context_id: str,
               parent_folder_path: Optional[str] = None,
               page_number: int = 1,
               page_size: int = 50) -> ContextFileListResult
```

List files under a specific folder path in a context.

**Arguments**:

- `context_id` _str_ - The ID of the context.
- `parent_folder_path` _Optional[str]_ - The parent folder path. Can be empty or None.
- `page_number` _int_ - Page number for pagination. Defaults to 1.
- `page_size` _int_ - Page size for pagination. Defaults to 50.


**Returns**:

    ContextFileListResult: Result object containing list of file entries.

### clear\_async

```python
def clear_async(context_id: str) -> ClearContextResult
```

Asynchronously initiate a task to clear the context's persistent data.

This is a non-blocking method that returns immediately after initiating the clearing task
on the backend. The context's state will transition to "clearing" while the operation
is in progress.

**Arguments**:

    context_id: Unique ID of the context to clear.


**Returns**:

  A ClearContextResult object indicating the task has been successfully started,
  with status field set to "clearing".


**Raises**:

    AGBError: If the backend API rejects the clearing request (e.g., invalid ID).

### get\_clear\_status

```python
def get_clear_status(context_id: str) -> ClearContextResult
```

Query the status of the clearing task.

This method calls GetContext API directly and parses the raw response to extract
the state field, which indicates the current clearing status.

**Arguments**:

    context_id: ID of the context.


**Returns**:

  ClearContextResult object containing the current task status.

### clear

```python
def clear(context_id: str,
          timeout: int = 60,
          poll_interval: float = 2.0) -> ClearContextResult
```

Synchronously clear the context's persistent data and wait for the final result.

This method wraps the `clear_async` and `_get_clear_status` polling logic,
providing the simplest and most direct way to handle clearing tasks.

The clearing process transitions through the following states:
- "clearing": Data clearing is in progress
- "available": Clearing completed successfully (final success state)

**Arguments**:

- `context_id` _str_ - Unique ID of the context to clear.
- `timeout` _int_ - Timeout in seconds to wait for task completion. Defaults to 60.
- `poll_interval` _float_ - Interval in seconds between status polls. Defaults to 2.0.


**Returns**:

    ClearContextResult: ClearContextResult object containing the final task result.
  The status field will be "available" on success.


**Raises**:

    ClearanceTimeoutError: If the task fails to complete within the timeout.
    AGBError: If an API or network error occurs during execution.

## Related Resources

- [Session API Reference](../session.md)
- [Context Manager API Reference](context_manager.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
