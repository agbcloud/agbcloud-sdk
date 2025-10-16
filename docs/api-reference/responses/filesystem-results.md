# File System Results

This document covers the response types for file system operations in the AGB SDK.

## Overview

File system results are returned by operations that interact with files and directories in the AGB cloud environment.

## Response Types

### FileInfoResult

Returned by `session.file_system.get_file_info()` operations.

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `file_info` | `dict` | File information (size, permissions, etc.) |
| `error_message` | `str` | Error message if the operation failed |

**Example:**
```python
info_result = session.file_system.get_file_info("/tmp/test.txt")
if info_result.success:
    file_info = info_result.file_info
    print(f"File size: {file_info.get('size')}")
    print(f"Permissions: {file_info.get('permissions')}")
else:
    print(f"Error: {info_result.error_message}")
```

### DirectoryListResult

Returned by `session.file_system.list_directory()` operations.

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `entries` | `list` | List of files and directories |
| `error_message` | `str` | Error message if the operation failed |

**Example:**
```python
list_result = session.file_system.list_directory("/tmp")
if list_result.success:
    items = list_result.entries
    for item in items:
        print(f"{item['name']} ({'DIR' if item['isDirectory'] else 'FILE'})")
else:
    print(f"Error: {list_result.error_message}")
```

### FileContentResult

Returned by `session.file_system.read_file()` operations.

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `content` | `str` | File content |
| `error_message` | `str` | Error message if the operation failed |

**Example:**
```python
read_result = session.file_system.read_file("/tmp/test.txt")
if read_result.success:
    content = read_result.content
    print(f"File content: {content}")
else:
    print(f"Error: {read_result.error_message}")
```

### MultipleFileContentResult

Returned by `session.file_system.read_multiple_files()` operations.

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `contents` | `dict` | Dictionary mapping file paths to content |
| `error_message` | `str` | Error message if the operation failed |

**Example:**
```python
files_result = session.file_system.read_multiple_files(["/tmp/file1.txt", "/tmp/file2.txt"])
if files_result.success:
    files_data = files_result.contents
    for file_path, content in files_data.items():
        print(f"{file_path}: {content}")
else:
    print(f"Error: {files_result.error_message}")
```

### FileSearchResult

Returned by `session.file_system.search_files()` operations.

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `matches` | `list` | List of matching file paths |
| `error_message` | `str` | Error message if the operation failed |

**Example:**
```python
search_result = session.file_system.search_files("/tmp", "*.txt")
if search_result.success:
    files = search_result.matches
    print(f"Found {len(files)} files:")
    for file_path in files:
        print(f"  {file_path}")
else:
    print(f"Error: {search_result.error_message}")
```

## Common Operations

### File Operations
```python
# Write file
write_result = session.file_system.write_file("/tmp/test.txt", "Hello World!")

# Read file
read_result = session.file_system.read_file("/tmp/test.txt")

# Get file info
info_result = session.file_system.get_file_info("/tmp/test.txt")

# Move file (can be used for deletion by moving to trash or temp location)
move_result = session.file_system.move_file("/tmp/test.txt", "/tmp/trash/test.txt")
```

### Directory Operations
```python
# Create directory
create_result = session.file_system.create_directory("/tmp/my_project")

# List directory
list_result = session.file_system.list_directory("/tmp")

# Move directory (can be used for deletion by moving to trash location)
move_result = session.file_system.move_file("/tmp/my_project", "/tmp/trash/my_project")
```

### Search Operations
```python
# Search files by pattern
search_result = session.file_system.search_files("/tmp", "*.py")

# Search files by name
search_result = session.file_system.search_files("/tmp", "config")
```

## Best Practices

### Error Handling
```python
result = session.file_system.read_file("/tmp/test.txt")
if result.success:
    content = result.content
    print(f"File content: {content}")
else:
    print(f"Failed to read file: {result.error_message}")
    print(f"Request ID: {result.request_id}")
```

### Path Validation
```python
import os

def safe_file_operation(session, file_path, operation):
    # Normalize path
    normalized_path = os.path.normpath(file_path)

    # Check for path traversal
    if ".." in normalized_path:
        print("Error: Path traversal not allowed")
        return

    # Perform operation
    if operation == "read":
        result = session.file_system.read_file(normalized_path)
    elif operation == "write":
        result = session.file_system.write_file(normalized_path, "content")

    return result
```

### Batch Operations
```python
# Read multiple files efficiently
file_paths = ["/tmp/file1.txt", "/tmp/file2.txt", "/tmp/file3.txt"]
result = session.file_system.read_multiple_files(file_paths)

if result.success:
    for file_path, content in result.contents.items():
        print(f"{file_path}: {len(content)} characters")
else:
    print(f"Batch read failed: {result.error_message}")
```

## Related Documentation

- **[File System Module](../modules/filesystem.md)** - File system operations documentation
- **[Session Management](../core/session.md)** - Session object documentation
