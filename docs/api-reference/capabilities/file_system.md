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

### get\_file\_transfer\_context\_path

```python
def get_file_transfer_context_path() -> Optional[str]
```

Get the context path for file transfer operations.

This method ensures the context ID is loaded and returns the associated
context path that was retrieved from GetAndLoadInternalContext API.

**Returns**:

    Optional[str]: The context path if available, None otherwise.

### upload\_file

```python
def upload_file(
        local_path: str,
        remote_path: str,
        *,
        content_type: Optional[str] = None,
        wait: bool = True,
        wait_timeout: float = 30.0,
        poll_interval: float = 1.5,
        progress_cb: Optional[Callable[[int], None]] = None) -> UploadResult
```

Upload a file from local to remote path using pre-signed URLs.

**Arguments**:

    local_path: Local file path to upload
    remote_path: Remote file path to upload to
    content_type: Optional content type for the file
    wait: Whether to wait for the sync operation to complete
    wait_timeout: Timeout for waiting for sync completion
    poll_interval: Interval between polling for sync completion
    progress_cb: Callback for upload progress updates


**Returns**:

    UploadResult: Result of the upload operation


**Example**:

```python
remote_path = session.file_system.get_file_transfer_context_path() + "/file.txt"
upload_result = session.file_system.upload_file("/local/file.txt", remote_path)
```

### download\_file

```python
def download_file(
        remote_path: str,
        local_path: str,
        *,
        overwrite: bool = True,
        wait: bool = True,
        wait_timeout: float = 30.0,
        poll_interval: float = 1.5,
        progress_cb: Optional[Callable[[int], None]] = None) -> DownloadResult
```

Download a file from remote path to local path using pre-signed URLs.

**Arguments**:

    remote_path: Remote file path to download from
    local_path: Local file path to download to
    overwrite: Whether to overwrite existing local file
    wait: Whether to wait for the sync operation to complete
    wait_timeout: Timeout for waiting for sync completion
    poll_interval: Interval between polling for sync completion
    progress_cb: Callback for download progress updates


**Returns**:

    DownloadResult: Result of the download operation


**Example**:

```python
remote_path = session.file_system.get_file_transfer_context_path() + "/file.txt"
download_result = session.file_system.download_file(remote_path, "/local/file.txt")
```

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
