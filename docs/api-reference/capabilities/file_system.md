# File System API Reference

## 📁 Related Tutorial

- [File Operations Guide](../../guides/file-operations.md) - Complete guide to file system operations

## Overview

The File System module provides comprehensive file and directory operations
within the AGB cloud environment. It supports file upload, download, and manipulation.




## FileChangeEvent

```python
class FileChangeEvent()
```

Represents a single file change event.

## FileInfoResult

```python
class FileInfoResult(ApiResponse)
```

Result of file info operations.

## DirectoryListResult

```python
class DirectoryListResult(ApiResponse)
```

Result of directory listing operations.

## FileContentResult

```python
class FileContentResult(ApiResponse)
```

Result of file read operations.

## MultipleFileContentResult

```python
class MultipleFileContentResult(ApiResponse)
```

Result of multiple file read operations.

## FileSearchResult

```python
class FileSearchResult(ApiResponse)
```

Result of file search operations.

## FileChangeResult

```python
class FileChangeResult(ApiResponse)
```

Result of file change detection operations.

### has\_changes

```python
def has_changes() -> bool
```

Check if there are any file changes.

### get\_modified\_files

```python
def get_modified_files() -> List[str]
```

Get list of modified file paths.

### get\_created\_files

```python
def get_created_files() -> List[str]
```

Get list of created file paths.

### get\_deleted\_files

```python
def get_deleted_files() -> List[str]
```

Get list of deleted file paths.

## FileSystem

```python
class FileSystem(BaseService)
```

FileSystem provides file system operations for the session.

#### DEFAULT\_CHUNK\_SIZE

```python
DEFAULT_CHUNK_SIZE = 50 * 1024
```

### create\_directory

```python
def create_directory(path: str) -> BoolResult
```

Create a new directory at the specified path.

**Arguments**:

- `path` _str_ - The path of the directory to create.


**Returns**:

    BoolResult: Result object containing success status and error message if
  any.

### edit\_file

```python
def edit_file(path: str,
              edits: List[Dict[str, str]],
              dry_run: bool = False) -> BoolResult
```

Edit a file by replacing occurrences of oldText with newText.

**Arguments**:

- `path` _str_ - The path of the file to edit.
- `edits` _List[Dict[str, str]]_ - A list of dictionaries specifying oldText and newText.
- `dry_run` _bool_ - If True, preview changes without applying them. Defaults to False.


**Returns**:

    BoolResult: Result object containing success status and error message if
  any.

### get\_file\_info

```python
def get_file_info(path: str) -> FileInfoResult
```

Get information about a file or directory.

**Arguments**:

- `path` _str_ - The path of the file or directory to inspect.


**Returns**:

    FileInfoResult: Result object containing file info and error message if any.

### list\_directory

```python
def list_directory(path: str) -> DirectoryListResult
```

List the contents of a directory.

**Arguments**:

- `path` _str_ - The path of the directory to list.


**Returns**:

    DirectoryListResult: Result object containing directory entries and error
  message if any.

### move\_file

```python
def move_file(source: str, destination: str) -> BoolResult
```

Move a file or directory from source path to destination path.

**Arguments**:

- `source` _str_ - The source path of the file or directory.
- `destination` _str_ - The destination path.


**Returns**:

    BoolResult: Result object containing success status and error message if
  any.

### read\_file

```python
def read_file(path: str) -> FileContentResult
```

Read the contents of a file.

**Arguments**:

- `path` _str_ - The path of the file to read.


**Returns**:

    FileContentResult: Result object containing file content and error message
  if any.

### write\_file

```python
def write_file(path: str, content: str, mode: str = "overwrite") -> BoolResult
```

Write content to a file. Automatically handles large files by chunking.

**Arguments**:

- `path` _str_ - The path of the file to write.
- `content` _str_ - The content to write to the file.
- `mode` _str_ - The write mode ("overwrite" or "append"). Defaults to "overwrite".


**Returns**:

    BoolResult: Result object containing success status and error message if
  any.

### read\_multiple\_files

```python
def read_multiple_files(paths: List[str]) -> MultipleFileContentResult
```

Read the contents of multiple files at once.

**Arguments**:

- `paths` _List[str]_ - A list of file paths to read.


**Returns**:

    MultipleFileContentResult: Result object containing a dictionary mapping
  file paths to contents,
  and error message if any.

### search\_files

```python
def search_files(
        path: str,
        pattern: str,
        exclude_patterns: Optional[List[str]] = None) -> FileSearchResult
```

Search for files in the specified path using a pattern.

**Arguments**:

- `path` _str_ - The base directory path to search in.
- `pattern` _str_ - The glob pattern to search for.
- `exclude_patterns` _Optional[List[str]]_ - Optional list of patterns to exclude from the search.
  Defaults to None.


**Returns**:

    FileSearchResult: Result object containing matching file paths and error
  message if any.

### watch\_directory

```python
def watch_directory(
        path: str,
        callback: Callable[[List[FileChangeEvent]], None],
        interval: float = 1.0,
        stop_event: Optional[threading.Event] = None) -> threading.Thread
```

Watch a directory for file changes and call the callback function when changes occur.

**Arguments**:

- `path` _str_ - The directory path to monitor for file changes.
- `callback` _Callable[[List[FileChangeEvent]], None]_ - Callback function that will be called with a list of FileChangeEvent
  objects when changes are detected.
- `interval` _float_ - Polling interval in seconds. Defaults to 1.0.
- `stop_event` _Optional[threading.Event]_ - Optional threading.Event to stop the monitoring. If not provided,
  a new Event will be created and returned via the thread object. Defaults to None.


**Returns**:

    threading.Thread: The monitoring thread. Call thread.start() to begin monitoring.
  Use the thread's stop_event attribute to stop monitoring.

## Best Practices

1. Always check file permissions before operations
2. Use appropriate file paths and handle path separators correctly
3. Clean up temporary files after operations
4. Handle file operation errors gracefully
5. Use streaming for large file operations

## Related Resources

- [Session API Reference](../session.md)
- [Command API Reference](shell_commands.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
