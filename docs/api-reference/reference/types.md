# Types & Schemas

This section details the response types and schemas used throughout the AGB SDK.

## SessionResult

`SessionResult` is the response type returned by session creation operations in the AGB SDK.

### Overview

The `SessionResult` class represents the outcome of operations that create or return a session object, such as `AGB.create()`.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `error_message` | `str` | Error message if the operation failed |
| `session` | `Optional[BaseSession]` | The session object (if successful) |

### Usage

```python
from agb import AGB
from agb.session_params import CreateSessionParams

# Initialize AGB client
agb = AGB()

# Create a session
params = CreateSessionParams(
    image_id="agb-code-space-1"
)
result = agb.create(params)

# Check if successful
if result.success:
    session = result.session
    print(f"Session created: {session.session_id}")
    print(f"Request ID: {result.request_id}")
else:
    print(f"Failed to create session: {result.error_message}")
```

### Success Response

When the operation is successful:

```python
result.success = True
result.session = <Session object>
result.error_message = ""
result.request_id = "req_123456789"
```

### Error Response

When the operation fails:

```python
result.success = False
result.session = None
result.error_message = "Invalid image_id provided"
result.request_id = "req_123456789"
```

---

## SessionListResult

`SessionListResult` is the response type returned by session listing operations in the AGB SDK.

### Overview

The `SessionListResult` class represents the outcome of operations that retrieve a paginated list of session IDs, such as `AGB.list()`.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `error_message` | `str` | Error message if the operation failed |
| `session_ids` | `List[str]` | List of session IDs matching the filter criteria |
| `next_token` | `str` | Token for retrieving the next page (empty if no more pages) |
| `max_results` | `int` | Maximum number of results per page |
| `total_count` | `int` | Total number of sessions matching the filter criteria |

### Usage

```python
from agb import AGB

# Initialize AGB client
agb = AGB()

# List all sessions
result = agb.list()

# Check if successful
if result.success:
    print(f"Found {result.total_count} total sessions")
    print(f"Showing {len(result.session_ids)} session IDs on this page")
    print(f"Request ID: {result.request_id}")

    for session_id in result.session_ids:
        print(f"Session ID: {session_id}")

    # Check if there are more pages
    if result.next_token:
        print("More pages available")
else:
    print(f"Failed to list sessions: {result.error_message}")
```

### Pagination

The `SessionListResult` supports pagination through the `next_token` mechanism.

---

## DeleteResult

`DeleteResult` is the response type returned by session deletion operations in the AGB SDK.

### Overview

The `DeleteResult` class represents the outcome of operations that delete resources, such as `AGB.delete()`.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `error_message` | `str` | Error message if the operation failed |

### Usage

```python
from agb import AGB

# Initialize AGB client
agb = AGB()

# ... (create session) ...

# Delete the session
delete_result = agb.delete(session)

# Check if deletion was successful
if delete_result.success:
    print("Session deleted successfully")
    print(f"Request ID: {delete_result.request_id}")
else:
    print(f"Failed to delete session: {delete_result.error_message}")
```

---

## Execution Results

This section covers the response types for code and command execution operations.

### Response Types

#### CodeExecutionResult

Returned by `session.code.run_code()` operations.

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `result` | `str` | The execution result |
| `error_message` | `str` | Error message if the operation failed |

#### CommandResult

Returned by `session.command.execute_command()` operations.

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `output` | `str` | The command output (stdout) |
| `error_message` | `str` | Error message if the operation failed |

---

## File System Results

This section covers the response types for file system operations.

### Response Types

#### FileInfoResult

Returned by `session.file_system.get_file_info()` operations.

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `file_info` | `dict` | File information (size, permissions, etc.) |
| `error_message` | `str` | Error message if the operation failed |

#### DirectoryListResult

Returned by `session.file_system.list_directory()` operations.

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `entries` | `list` | List of files and directories  |
| `error_message` | `str` | Error message if the operation failed |

#### FileContentResult

Returned by `session.file_system.read_file()` operations.

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `content` | `str` | File content |
| `error_message` | `str` | Error message if the operation failed |

#### MultipleFileContentResult

Returned by `session.file_system.read_multiple_files()` operations.

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `contents` | `dict` | Dictionary mapping file paths to content |
| `error_message` | `str` | Error message if the operation failed |

#### FileSearchResult

Returned by `session.file_system.search_files()` operations.

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `matches` | `list` | List of matching file paths |
| `error_message` | `str` | Error message if the operation failed |

