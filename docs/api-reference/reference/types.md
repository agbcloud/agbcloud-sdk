# Response Types & Schemas

This section details the response types and schemas used throughout the AGB SDK.

## SessionResult

Result of operations returning a single Session

### API Methods Using This Response Type

- `AGB.create()`
- `AGB.get()`

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `Any` | Unique identifier for the API request. Defaults to "". |
| `session` | `Any` | The session object. Defaults to None. |
| `success` | `Any` | Whether the operation was successful. Defaults to False. |
| `error_message` | `Any` | Error message if the operation failed. Defaults to "". |

### Related Guide

📖 **[Session Management APIs](../../guides/session-management.md)**

Get a session by its ID or create a new session in the AGB cloud environment


---

## DeleteResult

Result of delete operations

### API Methods Using This Response Type

- `session.delete()`
- `AGB.delete()`

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `Any` | Unique identifier for the API request. Defaults to "". |
| `success` | `Any` | Whether the delete operation was successful. Defaults to False. |
| `error_message` | `Any` | Error message if the operation failed. Defaults to "". |

### Related Guide

📖 **[Session and Resource Deletion APIs](../../guides/session-management.md)**

Delete sessions and manage resource cleanup operations


---

## OperationResult

Result of general operations

### API Methods Using This Response Type

- `session.set_labels()`
- `session.get_labels()`
- `session.info()`
- `session.get_link()`
- `agb.context.update()`
- `agb.context.delete()`
- `agb.context.delete_file()`
- `session.computer.get_cursor_position()`
- `session.computer.get_screen_size()`
- `session.computer.screenshot()`

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `Any` | Unique identifier for the API request. Defaults to "". |
| `success` | `Any` | Whether the operation was successful. Defaults to False. |
| `data` | `Any` | Data returned by the operation. Defaults to None. |
| `error_message` | `Any` | Error message if the operation failed. Defaults to "". |

### Related Guide

📖 **[Context and Session Management APIs](../../guides/context-usage-guide.md)**

Update context data, delete files, and manage session operations


---

## BoolResult

Result of operations returning a boolean value

### API Methods Using This Response Type

- `session.file_system.create_directory()`
- `session.file_system.edit_file()`
- `session.file_system.move_file()`
- `session.file_system.write_file()`
- `session.computer.click_mouse()`
- `session.computer.move_mouse()`
- `session.computer.drag_mouse()`
- `session.computer.scroll()`
- `session.computer.input_text()`
- `session.computer.press_keys()`
- `session.computer.release_keys()`
- `session.computer.activate_window()`
- `session.computer.close_window()`
- `session.computer.maximize_window()`
- `session.computer.minimize_window()`
- `session.computer.restore_window()`
- `session.computer.resize_window()`
- `session.computer.fullscreen_window()`
- `session.computer.focus_mode()`

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `Any` | Unique identifier for the API request. Defaults to "". |
| `success` | `Any` | Whether the operation was successful. Defaults to False. |
| `data` | `Any` | The boolean result. Defaults to None. |
| `error_message` | `Any` | Error message if the operation failed. Defaults to "". |

### Related Guide

📖 **[File System Validation APIs](../../guides/file-operations.md)**

File existence checks and validation operations


---

## SessionListResult

Result of operations returning a list of Sessions

### API Methods Using This Response Type

- `AGB.list()`

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `Any` | The request ID. |
| `success` | `Any` | Whether the operation was successful. |
| `error_message` | `Any` | Error message if the operation failed. |
| `session_ids` | `Any` | List of session IDs. |
| `next_token` | `Any` | Token for the next page of results. |
| `max_results` | `Any` | Number of results per page. |
| `total_count` | `Any` | Total number of results available. |

### Related Guide

📖 **[Session Listing APIs](../../guides/session-management.md)**

Returns paginated list of session IDs filtered by labels


---

## FileInfoResult

Result of file info operations

### API Methods Using This Response Type

- `session.file_system.get_file_info()`

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `Any` | Unique identifier for the API request. Defaults to "". |
| `success` | `Any` | Whether the operation was successful. Defaults to False. |
| `file_info` | `Any` | File information. Defaults to None. |
| `error_message` | `Any` | Error message if the operation failed. Defaults to "". |

### Related Guide

📖 **[File Information and Metadata APIs](../../guides/file-operations.md)**

Get file properties, permissions, and metadata information


---

## FileContentResult

Result of file read operations

### API Methods Using This Response Type

- `session.file_system.read_file()`

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `Any` | Unique identifier for the API request. Defaults to "". |
| `success` | `Any` | Whether the operation was successful. Defaults to False. |
| `content` | `Any` | File content. Defaults to "". |
| `error_message` | `Any` | Error message if the operation failed. Defaults to "". |

### Related Guide

📖 **[File Content Access APIs](../../guides/file-operations.md)**

Read file content and retrieve file data


---

## MultipleFileContentResult

Result of multiple file read operations

### API Methods Using This Response Type

- `session.file_system.read_multiple_files()`

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `Any` | Unique identifier for the API request. Defaults to "". |
| `success` | `Any` | Whether the operation was successful. Defaults to False. |
| `contents` | `Any` | Dictionary of file paths to file contents. Defaults to None. |
| `error_message` | `Any` | Error message if the operation failed. Defaults to "". |

### Related Guide

📖 **[File Content Management APIs](../../guides/file-operations.md)**

Read multiple files and batch file content operations


---

## DirectoryListResult

Result of directory listing operations

### API Methods Using This Response Type

- `session.file_system.list_directory()`

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `Any` | Unique identifier for the API request. Defaults to "". |
| `success` | `Any` | Whether the operation was successful. Defaults to False. |
| `entries` | `Any` | Directory entries. Defaults to None. |
| `error_message` | `Any` | Error message if the operation failed. Defaults to "". |

### Related Guide

📖 **[Directory Management APIs](../../guides/file-operations.md)**

List directory contents and navigate file system structure


---

## FileSearchResult

Result of file search operations

### API Methods Using This Response Type

- `session.file_system.search_files()`

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `Any` | Unique identifier for the API request. Defaults to "". |
| `success` | `Any` | Whether the operation was successful. Defaults to False. |
| `matches` | `Any` | Matching file paths. Defaults to None. |
| `error_message` | `Any` | Error message if the operation failed. Defaults to "". |

### Related Guide

📖 **[File Search and Discovery APIs](../../guides/file-operations.md)**

Search files by patterns and locate specific file content


---


## Base Response Type

All response types inherit from `ApiResponse`, which provides the basic `request_id` property for tracking API requests.

---

*Documentation generated automatically from source code.*
