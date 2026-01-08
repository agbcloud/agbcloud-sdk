import json
import threading
import time
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Union, overload, Literal

from agb.api.base_service import BaseService
from agb.model.response import ApiResponse, BoolResult, UploadResult, DownloadResult, BinaryFileContentResult
from agb.logger import get_logger, log_operation_start, log_operation_success, log_operation_error, log_warning
from agb.modules.file_transfer import FileTransfer
from agb.exceptions import FileError
logger = get_logger(__name__)


class FileChangeEvent:
    """Represents a single file change event."""

    def __init__(
        self,
        event_type: str = "",
        path: str = "",
        path_type: str = "",
    ):
        """
        Initialize a FileChangeEvent.

        Args:
            event_type (str): Type of the file change event (e.g., "modify", "create", "delete").
            path (str): Path of the file or directory that changed.
            path_type (str): Type of the path ("file" or "directory").
        """
        self.event_type = event_type
        self.path = path
        self.path_type = path_type

    def __repr__(self):
        return f"FileChangeEvent(event_type='{self.event_type}', path='{self.path}', path_type='{self.path_type}')"

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary representation."""
        return {
            "eventType": self.event_type,
            "path": self.path,
            "pathType": self.path_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "FileChangeEvent":
        """Create FileChangeEvent from dictionary."""
        return cls(
            event_type=data.get("eventType", ""),
            path=data.get("path", ""),
            path_type=data.get("pathType", ""),
        )


class FileInfoResult(ApiResponse):
    """Result of file info operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        file_info: Optional[Dict[str, Any]] = None,
        error_message: str = "",
    ):
        """
        Initialize a FileInfoResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            file_info (Dict[str, Any], optional): File information. Defaults to None.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.file_info = file_info or {}
        self.error_message = error_message


class DirectoryListResult(ApiResponse):
    """Result of directory listing operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        entries: Optional[List[Dict[str, Any]]] = None,
        error_message: str = "",
    ):
        """
        Initialize a DirectoryListResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            entries (List[Dict[str, Any]], optional): Directory entries. Defaults to
                None.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.entries = entries or []
        self.error_message = error_message


class FileContentResult(ApiResponse):
    """Result of file read operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        content: str = "",
        error_message: str = "",
    ):
        """
        Initialize a FileContentResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            content (str, optional): File content. Defaults to "".
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.content = content
        self.error_message = error_message


class MultipleFileContentResult(ApiResponse):
    """Result of multiple file read operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        contents: Optional[Dict[str, str]] = None,
        error_message: str = "",
    ):
        """
        Initialize a MultipleFileContentResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            contents (Dict[str, str], optional): Dictionary of file paths to file
                contents. Defaults to None.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.contents = contents or {}
        self.error_message = error_message


class FileSearchResult(ApiResponse):
    """Result of file search operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        matches: Optional[List[str]] = None,
        error_message: str = "",
    ):
        """
        Initialize a FileSearchResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            matches (List[str], optional): Matching file paths. Defaults to None.
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.matches = matches or []
        self.error_message = error_message


class FileChangeResult(ApiResponse):
    """Result of file change detection operations."""

    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        events: Optional[List[FileChangeEvent]] = None,
        raw_data: str = "",
        error_message: str = "",
    ):
        """
        Initialize a FileChangeResult.

        Args:
            request_id (str, optional): Unique identifier for the API request.
                Defaults to "".
            success (bool, optional): Whether the operation was successful.
                Defaults to False.
            events (List[FileChangeEvent], optional): List of file change events.
                Defaults to None.
            raw_data (str, optional): Raw response data for debugging. Defaults to "".
            error_message (str, optional): Error message if the operation failed.
                Defaults to "".
        """
        super().__init__(request_id)
        self.success = success
        self.events = events or []
        self.raw_data = raw_data
        self.error_message = error_message

    def has_changes(self) -> bool:
        """Check if there are any file changes."""
        return len(self.events) > 0

    def get_modified_files(self) -> List[str]:
        """Get list of modified file paths."""
        return [
            event.path
            for event in self.events
            if event.event_type == "modify" and event.path_type == "file"
        ]

    def get_created_files(self) -> List[str]:
        """Get list of created file paths."""
        return [
            event.path
            for event in self.events
            if event.event_type == "create" and event.path_type == "file"
        ]

    def get_deleted_files(self) -> List[str]:
        """Get list of deleted file paths."""
        return [
            event.path
            for event in self.events
            if event.event_type == "delete" and event.path_type == "file"
        ]

    def __repr__(self):
        return (
            f"FileChangeResult(success={self.success}, events_count={len(self.events)})"
        )


class FileSystem(BaseService):
    """
    FileSystem provides file system operations for the session.
    """


    def __init__(self, *args, **kwargs):
        """
        Initialize FileSystem with FileTransfer capability.

        Args:
            *args: Arguments to pass to BaseService
            **kwargs: Keyword arguments to pass to BaseService
        """
        super().__init__(*args, **kwargs)
        # Initialize _file_transfer as None - will be lazily initialized when needed
        self._file_transfer: Optional[FileTransfer] = None

    def _ensure_file_transfer(self) -> FileTransfer:
        """
        Ensure FileTransfer is initialized with the current session.
        This is a lazy initialization - FileTransfer is only created when actually needed.

        Returns:
            FileTransfer: The FileTransfer instance

        Raises:
            FileError: If FileTransfer cannot be initialized (e.g., missing AGB context)
        """
        if self._file_transfer is None:
            # Get the agb instance from the session
            agb = getattr(self.session, "agb", None)
            if agb is None:
                raise FileError("FileTransfer requires an AGB instance")

            # Get the session from the service
            session = self.session
            if session is None:
                raise FileError("FileTransfer requires a session")

            self._file_transfer = FileTransfer(agb, self.session)

        # Type assertion: _file_transfer is guaranteed to be non-None here
        assert self._file_transfer is not None, "FileTransfer should be initialized"
        return self._file_transfer


    def get_file_transfer_context_path(self) -> Optional[str]:
        """
        Get the context path for file transfer operations.

        This method ensures the context ID is loaded and returns the associated
        context path that was retrieved from GetAndLoadInternalContext API.

        Returns:
            Optional[str]: The context path if available, None otherwise.
        """
        # Ensure FileTransfer is initialized
        file_transfer = self._ensure_file_transfer()
        # Ensure context_id is loaded (this will also load context_path)
        if file_transfer.context_id is None:
            file_transfer.ensure_context_id()
        return file_transfer.context_path

    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        *,
        content_type: Optional[str] = None,
        wait: bool = True,
        wait_timeout: float = 30.0,
        poll_interval: float = 1.5,
        progress_cb: Optional[Callable[[int], None]] = None,
    ) -> UploadResult:
        """
        Upload a file from local to remote path using pre-signed URLs.

        Args:
            local_path: Local file path to upload
            remote_path: Remote file path to upload to
            content_type: Optional content type for the file
            wait: Whether to wait for the sync operation to complete
            wait_timeout: Timeout for waiting for sync completion
            poll_interval: Interval between polling for sync completion
            progress_cb: Callback for upload progress updates

        Returns:
            UploadResult: Result of the upload operation

        Example:
            ```python
            remote_path = session.file_system.get_file_transfer_context_path() + "/file.txt"
            upload_result = session.file_system.upload_file("/local/file.txt", remote_path)
            ```
        """
        log_operation_start("FileSystem.upload_file", f"LocalPath={local_path}, RemotePath={remote_path}, Wait={wait}")
        try:
            # Ensure FileTransfer is initialized
            file_transfer = self._ensure_file_transfer()
            result = file_transfer.upload(
                local_path=local_path,
                remote_path=remote_path,
                content_type=content_type,
                wait=wait,
                wait_timeout=wait_timeout,
                poll_interval=poll_interval,
                progress_cb=progress_cb,
            )
            # Upload completed successfully
            if result.success:
                result_msg = f"RemotePath={remote_path}, BytesSent={result.bytes_sent}, RequestIdUpload={result.request_id_upload_url}, RequestIdSync={result.request_id_sync}"
                log_operation_success("FileSystem.upload_file", result_msg)
            else:
                log_operation_error("FileSystem.upload_file", result.error_message or "Upload failed")
            return result
        except Exception as e:
            log_operation_error("FileSystem.upload_file", str(e), exc_info=True)
            return UploadResult(
                success=False,
                request_id_upload_url=None,
                request_id_sync=None,
                http_status=None,
                etag=None,
                bytes_sent=0,
                path=remote_path,
                error_message=f"Upload failed: {str(e)}",
            )

    def download_file(
        self,
        remote_path: str,
        local_path: str,
        *,
        overwrite: bool = True,
        wait: bool = True,
        wait_timeout: float = 30.0,
        poll_interval: float = 1.5,
        progress_cb: Optional[Callable[[int], None]] = None,
    ) -> DownloadResult:
        """
        Download a file from remote path to local path using pre-signed URLs.

        Args:
            remote_path: Remote file path to download from
            local_path: Local file path to download to
            overwrite: Whether to overwrite existing local file
            wait: Whether to wait for the sync operation to complete
            wait_timeout: Timeout for waiting for sync completion
            poll_interval: Interval between polling for sync completion
            progress_cb: Callback for download progress updates

        Returns:
            DownloadResult: Result of the download operation

        Example:
            ```python
            remote_path = session.file_system.get_file_transfer_context_path() + "/file.txt"
            download_result = session.file_system.download_file(remote_path, "/local/file.txt")
            ```
        """
        log_operation_start("FileSystem.download_file", f"RemotePath={remote_path}, LocalPath={local_path}, Wait={wait}, Overwrite={overwrite}")
        try:
            # Ensure FileTransfer is initialized
            file_transfer = self._ensure_file_transfer()
            result = file_transfer.download(
                remote_path=remote_path,
                local_path=local_path,
                overwrite=overwrite,
                wait=wait,
                wait_timeout=wait_timeout,
                poll_interval=poll_interval,
                progress_cb=progress_cb,
            )
            # Download completed successfully
            if result.success:
                result_msg = f"RemotePath={remote_path}, LocalPath={local_path}, BytesReceived={result.bytes_received}, RequestIdDownload={result.request_id_download_url}, RequestIdSync={result.request_id_sync}"
                log_operation_success("FileSystem.download_file", result_msg)
            else:
                log_operation_error("FileSystem.download_file", result.error_message or "Download failed")
            return result
        except Exception as e:
            log_operation_error("FileSystem.download_file", str(e), exc_info=True)
            return DownloadResult(
                success=False,
                request_id_download_url=None,
                request_id_sync=None,
                http_status=None,
                bytes_received=0,
                path=remote_path,
                local_path=local_path,
                error_message=f"Download exception: {str(e)}",
            )


    # Default chunk size is 50KB
    DEFAULT_CHUNK_SIZE = 50 * 1024

    def create_directory(self, path: str) -> BoolResult:
        """
        Create a new directory at the specified path.

        Args:
            path (str): The path of the directory to create.

        Returns:
            BoolResult: Result object containing success status and error message if
                any.
        """
        log_operation_start("FileSystem.create_directory", f"Path={path}")
        args = {"path": path}
        try:
            result = self._call_mcp_tool("create_directory", args)
            logger.debug(f"Response from CallMcpTool - create_directory: {result}")
            if result.success:
                result_msg = f"Path={path}, RequestId={result.request_id}"
                log_operation_success("FileSystem.create_directory", result_msg)
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                error_msg = result.error_message or "Unknown error"
                log_operation_error("FileSystem.create_directory", error_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("FileSystem.create_directory", str(e), exc_info=True)
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to create directory: {e}",
            )

    def edit_file(
        self, path: str, edits: List[Dict[str, str]], dry_run: bool = False
    ) -> BoolResult:
        """
        Edit a file by replacing occurrences of oldText with newText.

        Args:
            path (str): The path of the file to edit.
            edits (List[Dict[str, str]]): A list of dictionaries specifying oldText and newText.
            dry_run (bool): If True, preview changes without applying them. Defaults to False.

        Returns:
            BoolResult: Result object containing success status and error message if
                any.
        """
        log_operation_start("FileSystem.edit_file", f"Path={path}, EditsCount={len(edits)}, DryRun={dry_run}")
        args = {"path": path, "edits": edits, "dryRun": dry_run}
        try:
            result = self._call_mcp_tool("edit_file", args)
            logger.debug(f"Response from CallMcpTool - edit_file: {result}")
            if result.success:
                result_msg = f"Path={path}, RequestId={result.request_id}"
                log_operation_success("FileSystem.edit_file", result_msg)
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                error_msg = result.error_message or "Unknown error"
                log_operation_error("FileSystem.edit_file", error_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("FileSystem.edit_file", str(e), exc_info=True)
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to edit file: {e}",
            )

    def get_file_info(self, path: str) -> FileInfoResult:
        """
        Get information about a file or directory.

        Args:
            path (str): The path of the file or directory to inspect.

        Returns:
            FileInfoResult: Result object containing file info and error message if any.
        """

        def parse_file_info(file_info_str: str) -> Dict[str, Any]:
            """
            Parse file info string into a dictionary.

            Args:
                file_info_str (str): File info string in format:
                    "key1: value1\nkey2: value2\n..."

            Returns:
                Dict[str, Any]: Dictionary containing parsed file information.
            """
            result: Dict[str, Any] = {}
            lines = file_info_str.split("\n")
            for line in lines:
                if ":" in line:
                    key, value_str = line.split(":", 1)
                    key = key.strip()
                    value_str = value_str.strip()

                    # Convert boolean values
                    value: Any = value_str
                    if value_str.lower() == "true":
                        value = True
                    elif value_str.lower() == "false":
                        value = False

                    # Convert numeric values
                    try:
                        if isinstance(value, str):
                            value = float(value) if "." in value else int(value)
                    except ValueError:
                        pass

                    result[key] = value
            return result

        log_operation_start("FileSystem.get_file_info", f"Path={path}")
        args = {"path": path}
        try:
            result = self._call_mcp_tool("get_file_info", args)
            if result.success:
                file_info = parse_file_info(result.data)
                result_msg = f"Path={path}, RequestId={result.request_id}, IsDirectory={file_info.get('isDirectory', False)}"
                log_operation_success("FileSystem.get_file_info", result_msg)
                return FileInfoResult(
                    request_id=result.request_id,
                    success=True,
                    file_info=file_info,
                )
            else:
                error_msg = result.error_message or "Failed to get file info"
                log_operation_error("FileSystem.get_file_info", error_msg)
                return FileInfoResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("FileSystem.get_file_info", str(e), exc_info=True)
            return FileInfoResult(
                request_id="",
                success=False,
                error_message=f"Failed to get file info: {e}",
            )

    def list_directory(self, path: str) -> DirectoryListResult:
        """
        List the contents of a directory.

        Args:
            path (str): The path of the directory to list.

        Returns:
            DirectoryListResult: Result object containing directory entries and error
                message if any.
        """

        def parse_directory_listing(text) -> List[Dict[str, Union[str, bool]]]:
            """
            Parse a directory listing text into a list of file/directory entries.

            Args:
                text (str): Directory listing text in format:
                    [DIR] directory_name
                    [FILE] file_name
                    Each entry should be on a new line with [DIR] or [FILE] prefix

            Returns:
                list: List of dictionaries, each containing:
                    - name (str): Name of the file or directory
                    - isDirectory (bool): True if entry is a directory, False if file

            Example:
                Input text:
                    [DIR] folder1
                    [FILE] test.txt

                Returns:
                    [
                        {"name": "folder1", "isDirectory": True},
                        {"name": "test.txt", "isDirectory": False}
                    ]
            """
            result: List[Dict[str, Union[str, bool]]] = []
            lines = text.split("\n")

            for line in lines:
                line = line.strip()
                if line == "":
                    continue

                entry_map: Dict[str, Union[str, bool]] = {}
                if line.startswith("[DIR]"):
                    entry_map["isDirectory"] = True
                    entry_map["name"] = line.replace("[DIR]", "").strip()
                elif line.startswith("[FILE]"):
                    entry_map["isDirectory"] = False
                    entry_map["name"] = line.replace("[FILE]", "").strip()
                else:
                    # Skip lines that don't match the expected format
                    continue

                result.append(entry_map)

            return result

        log_operation_start("FileSystem.list_directory", f"Path={path}")
        args = {"path": path}
        try:
            result = self._call_mcp_tool("list_directory", args)
            try:
                logger.debug("Response body:")
                logger.debug(
                    json.dumps(
                        getattr(result, "body", result), ensure_ascii=False, indent=2
                    )
                )
            except Exception:
                logger.debug(f"Response: {result}")
            if result.success:
                entries = parse_directory_listing(result.data)
                result_msg = f"Path={path}, EntriesCount={len(entries)}, RequestId={result.request_id}"
                log_operation_success("FileSystem.list_directory", result_msg)
                return DirectoryListResult(
                    request_id=result.request_id, success=True, entries=entries
                )
            else:
                error_msg = result.error_message or "Failed to list directory"
                log_operation_error("FileSystem.list_directory", error_msg)
                return DirectoryListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("FileSystem.list_directory", str(e), exc_info=True)
            return DirectoryListResult(
                request_id="",
                success=False,
                error_message=f"Failed to list directory: {e}",
            )

    def move_file(self, source: str, destination: str) -> BoolResult:
        """
        Move a file or directory from source path to destination path.

        Args:
            source (str): The source path of the file or directory.
            destination (str): The destination path.

        Returns:
            BoolResult: Result object containing success status and error message if
                any.
        """
        log_operation_start("FileSystem.move_file", f"Source={source}, Destination={destination}")
        args = {"source": source, "destination": destination}
        try:
            result = self._call_mcp_tool("move_file", args)
            logger.debug(f"Response from CallMcpTool - move_file: {result}")
            if result.success:
                result_msg = f"Source={source}, Destination={destination}, RequestId={result.request_id}"
                log_operation_success("FileSystem.move_file", result_msg)
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                error_msg = result.error_message or "Failed to move file"
                log_operation_error("FileSystem.move_file", error_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("FileSystem.move_file", str(e), exc_info=True)
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to move file: {e}",
            )

    def delete_file(self, path: str) -> BoolResult:
        """
        Delete a file at the specified path.

        Args:
            path (str): The path of the file to delete.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Example:
            ```python
            session = (agb.create()).session
            session.file_system.write_file("/tmp/to_delete.txt", "hello")
            delete_result = session.file_system.delete_file("/tmp/to_delete.txt")
            session.delete()
            ```
        """
        log_operation_start("FileSystem.delete_file", f"Path={path}")
        args = {"path": path}
        try:
            result = self._call_mcp_tool("delete_file", args)
            if result.success:
                result_msg = f"Path={path}, RequestId={result.request_id}"
                log_operation_success("FileSystem.delete_file", result_msg)
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                error_msg = result.error_message or "Failed to delete file"
                log_operation_error("FileSystem.delete_file", error_msg)
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=error_msg,
                )
        except Exception as e:
            log_operation_error("FileSystem.delete_file", str(e), exc_info=True)
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to delete file: {e}",
            )

    def _read_file_chunk(
        self, path: str, offset: int = 0, length: int = 0, format_type: str = "text"
    ) -> Union[FileContentResult, BinaryFileContentResult]:
        """
        Internal method to read a file chunk. Used for chunked file operations.

        Args:
            path: The path of the file to read.
            offset: Byte offset to start reading from (0-based).
            length: Number of bytes to read. If 0, reads the entire file from offset.
            format_type: Format to read the file in. "text" (default) or "binary".

        Returns:
            FileContentResult: For text format, contains file content as string.
            BinaryFileContentResult: For binary format, contains file content as bytes.
        """
        args = {"path": path}
        if offset >= 0:
            args["offset"] = offset
        if length >= 0:
            args["length"] = length

        # Only pass format parameter for binary files
        if format_type == "binary":
            args["format"] = "binary"

        try:
            log_operation_start("FileSystem.read_file", f"Path={path}, Offset={offset}, Length={length}, Format={format_type}")
            result = self._call_mcp_tool("read_file", args)
            if result.success:
                if format_type == "binary":
                    # Backend returns base64-encoded string, decode to bytes
                    try:
                        log_operation_success("FileSystem.read_file.binary", f"result={str(result.data)}, RequestId={result.request_id}")
                        import base64
                        binary_content = base64.b64decode(result.data)
                        return BinaryFileContentResult(
                            request_id=result.request_id,
                            success=True,
                            content=binary_content,
                        )
                    except Exception as e:
                        log_operation_error("FileSystem.read_file.binary", str(e), exc_info=True)
                        return BinaryFileContentResult(
                            request_id=result.request_id,
                            success=False,
                            content=b"",
                            error_message=f"Failed to decode base64: {e}",
                        )
                else:
                    log_operation_success("FileSystem.read_file.text", f"result={str(result.data)}, RequestId={result.request_id}")
                    # Text format, return as string
                    return FileContentResult(
                        request_id=result.request_id,
                        success=True,
                        content=result.data,
                    )
            else:
                # Error case - return appropriate result type
                if format_type == "binary":
                    log_operation_error("FileSystem.read_file.binary", result.error_message or "Failed to read file")
                    return BinaryFileContentResult(
                        request_id=result.request_id,
                        success=False,
                        content=b"",
                        error_message=result.error_message or "Failed to read file",
                    )
                else:
                    log_operation_error("FileSystem.read_file.text", result.error_message or "Failed to read file")
                    return FileContentResult(
                        request_id=result.request_id,
                        success=False,
                        error_message=result.error_message or "Failed to read file",
                    )
        except FileError as e:
            if format_type == "binary":
                log_operation_error("FileSystem.read_file.binary", str(e), exc_info=True)
                return BinaryFileContentResult(request_id="", success=False, content=b"", error_message=str(e))
            else:
                log_operation_error("FileSystem.read_file.text", str(e), exc_info=True)
                return FileContentResult(request_id="", success=False, error_message=str(e))
        except Exception as e:
            if format_type == "binary":
                log_operation_error("FileSystem.read_file.binary", str(e), exc_info=True)
                return BinaryFileContentResult(request_id="", success=False, content=b"", error_message=str(e))
            else:
                log_operation_error("FileSystem.read_file.text", str(e), exc_info=True)
                return FileContentResult(request_id="", success=False, error_message=str(e))

    def _write_file_chunk(
        self, path: str, content: str, mode: str = "overwrite"
    ) -> BoolResult:
        """
        Write content to a file (internal function for chunked writing).

        Args:
            path: The path of the file to write.
            content: The content to write to the file.
            mode: The write mode ("overwrite" or "append").

        Returns:
            BoolResult: Result object containing success status and error message if
                any.
        """
        if mode not in ["overwrite", "append"]:
            return BoolResult(
                request_id="",
                success=False,
                error_message=(
                    f"Invalid write mode: {mode}. Must be 'overwrite' or " "'append'."
                ),
            )

        args = {"path": path, "content": content, "mode": mode}
        try:
            result = self._call_mcp_tool("write_file", args)
            logger.debug(f"Response from CallMcpTool - write_file: {result}")
            if result.success:
                return BoolResult(request_id=result.request_id, success=True, data=True)
            else:
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to write file",
                )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to write file: {e}",
            )

    @overload
    def read_file(self, path: str) -> FileContentResult: ...

    @overload
    def read_file(self, path: str, *, format: Literal["text"]) -> FileContentResult: ...

    @overload
    def read_file(self, path: str, *, format: Literal["bytes"]) -> BinaryFileContentResult: ...

    def read_file(
        self, path: str, *, format: str = "text"
    ) -> Union[FileContentResult, BinaryFileContentResult]:
        """
        Read the contents of a file. Automatically handles large files by chunking.

        Args:
            path (str): The path of the file to read.
            format (str): Format to read the file in. "text" (default) or "bytes".
                - "text": Returns FileContentResult with content as string (UTF-8)
                - "bytes": Returns BinaryFileContentResult with content as bytes

        Returns:
            FileContentResult: For text format, contains file content as string.
            BinaryFileContentResult: For bytes format, contains file content as bytes.

        Raises:
            FileError: If the file does not exist or is a directory.

        Example:
            ```python
            session = (agb.create()).session
            
            # Read text file (default)
            text_result = session.file_system.read_file("/tmp/test.txt")
            print(text_result.content)  # str
            
            # Read binary file
            binary_result = session.file_system.read_file("/tmp/image.png", format="bytes")
            print(binary_result.content)  # bytes
            
            session.delete()
            ```

        Note:
            - Automatically handles large files by reading in chunks (default 50KB per chunk)
            - Returns empty string/bytes for empty files
            - Returns error if path is a directory
            - Binary files are returned as bytes (backend uses base64 encoding internally)

        See Also:
            FileSystem.write_file, FileSystem.list_directory, FileSystem.get_file_info
        """
        chunk_size = self.DEFAULT_CHUNK_SIZE

        log_operation_start("FileSystem.read_file", f"Path={path}, Format={format}")
        try:
            # Get file info to check size
            file_info_result = self.get_file_info(path)
            if not file_info_result.success:
                if format == "bytes":
                    return BinaryFileContentResult(
                        request_id=file_info_result.request_id,
                        success=False,
                        content=b"",
                        error_message=file_info_result.error_message,
                    )
                else:
                    return FileContentResult(
                        request_id=file_info_result.request_id,
                        success=False,
                        error_message=file_info_result.error_message,
                    )

            # Check if file exists and is a file (not a directory)
            if not file_info_result.file_info or file_info_result.file_info.get(
                "isDirectory", False
            ):
                error_msg = f"Path does not exist or is a directory: {path}"
                log_operation_error("FileSystem.read_file", error_msg)
                if format == "bytes":
                    return BinaryFileContentResult(
                        request_id=file_info_result.request_id,
                        success=False,
                        content=b"",
                        error_message=error_msg,
                    )
                else:
                    return FileContentResult(
                        request_id=file_info_result.request_id,
                        success=False,
                        error_message=error_msg,
                    )

            # If the file is empty, return empty content
            file_size = file_info_result.file_info.get("size", 0)
            if file_size == 0:
                log_operation_error("FileSystem.read_file", "File is empty")
                if format == "bytes":
                    return BinaryFileContentResult(
                        request_id=file_info_result.request_id,
                        success=True,
                        content=b"",
                        size=0,
                    )
                else:
                    return FileContentResult(
                        request_id=file_info_result.request_id,
                        success=True,
                        content="",
                    )

            # Read the file in chunks
            if format == "bytes":
                # Binary format
                content_chunks = []
                offset = 0
                chunk_count = 0
                while offset < file_size:
                    length = min(chunk_size, file_size - offset)
                    chunk_result = self._read_file_chunk(path, offset, length, format_type="binary")

                    if not chunk_result.success:
                        return chunk_result  # Return the error

                    # chunk_result is BinaryFileContentResult for binary format
                    if isinstance(chunk_result, BinaryFileContentResult):
                        content_chunks.append(chunk_result.content)
                    else:
                        # Should not happen, but handle gracefully
                        return BinaryFileContentResult(
                            request_id=chunk_result.request_id,
                            success=False,
                            content=b"",
                            error_message="Unexpected result type for binary format",
                        )

                    offset += length
                    chunk_count += 1

                # Combine all binary chunks
                final_content = b"".join(content_chunks)
                result_msg = f"Path={path}, Format={format}, ContentLength={len(final_content)}, RequestId={file_info_result.request_id}"
                log_operation_success("FileSystem.read_file", result_msg)
                return BinaryFileContentResult(
                    request_id=file_info_result.request_id,
                    success=True,
                    content=final_content,
                    size=len(final_content),
                )
            else:
                # Text format (default)
                content = []
                offset = 0
                chunk_count = 0
                while offset < file_size:
                    length = min(chunk_size, file_size - offset)
                    chunk_result = self._read_file_chunk(path, offset, length, format_type="text")
                    if not chunk_result.success:
                        return chunk_result  # Return the error

                    content.append(chunk_result.content)
                    offset += length
                    chunk_count += 1

                content_str = "".join(content)
                result_msg = f"Path={path}, Format={format}, ContentLength={len(content_str)}, RequestId={file_info_result.request_id}"
                log_operation_success("FileSystem.read_file", result_msg)
                return FileContentResult(
                    request_id=file_info_result.request_id,
                    success=True,
                    content=content_str,
                )

        except Exception as e:
            log_operation_error("FileSystem.read_file", str(e), exc_info=True)
            if format == "bytes":
                return BinaryFileContentResult(request_id="", success=False, content=b"", error_message=str(e))
            else:
                return FileContentResult(request_id="", success=False, error_message=str(e))

    def read(self, path: str) -> FileContentResult:
        """
        Alias of read_file().
        """
        return self.read_file(path)

    def write_file(
        self, path: str, content: str, mode: str = "overwrite"
    ) -> BoolResult:
        """
        Write content to a file. Automatically handles large files by chunking.

        Args:
            path (str): The path of the file to write.
            content (str): The content to write to the file.
            mode (str): The write mode ("overwrite" or "append"). Defaults to "overwrite".

        Returns:
            BoolResult: Result object containing success status and error message if
                any.
        """
        content_len = len(content)
        log_operation_start("FileSystem.write_file", f"Path={path}, Mode={mode}, ContentLength={content_len}")

        # If the content length is less than the chunk size, write it directly
        if content_len <= self.DEFAULT_CHUNK_SIZE:
            return self._write_file_chunk(path, content, mode)

        try:
            # Write the first chunk (creates or overwrites the file)
            first_chunk = content[: self.DEFAULT_CHUNK_SIZE]
            result = self._write_file_chunk(path, first_chunk, mode)
            if not result.success:
                return result

            # Write the rest in chunks (appending)
            offset = self.DEFAULT_CHUNK_SIZE
            while offset < content_len:
                end = min(offset + self.DEFAULT_CHUNK_SIZE, content_len)
                current_chunk = content[offset:end]
                result = self._write_file_chunk(path, current_chunk, "append")
                if not result.success:
                    error_msg = result.error_message or "Failed to write file chunk"
                    log_operation_error("FileSystem.write_file", error_msg)
                    return result
                offset = end

            result_msg = f"Path={path}, ContentLength={content_len}, RequestId={result.request_id}"
            log_operation_success("FileSystem.write_file", result_msg)
            return BoolResult(request_id=result.request_id, success=True, data=True)

        except Exception as e:
            log_operation_error("FileSystem.write_file", str(e), exc_info=True)
            return BoolResult(
                request_id="",
                success=False,
                error_message=f"Failed to write file: {e}",
            )

    def read_multiple_files(self, paths: List[str]) -> MultipleFileContentResult:
        """
        Read the contents of multiple files at once.

        Args:
            paths (List[str]): A list of file paths to read.

        Returns:
            MultipleFileContentResult: Result object containing a dictionary mapping
                file paths to contents,
            and error message if any.
        """

        def parse_multiple_files_response(text: str) -> Dict[str, str]:
            """
            Parse the response from reading multiple files.

            Args:
                text (str): The response string containing file contents.
                Format: "/path/to/file1.txt: Content of file1\n\n---\n
                    /path/to/file2.txt: \nContent of file2\n"

            Returns:
                Dict[str, str]: A dictionary mapping file paths to their content.
            """
            result: Dict[str, str] = {}
            if not text:
                return result

            lines = text.split("\n")
            current_path = None
            current_content = []

            for i, line in enumerate(lines):
                # Check if this line contains a file path (ends with a colon)
                if ":" in line and not current_path:
                    # Extract path (everything before the first colon)
                    path_end = line.find(":")
                    path = line[:path_end].strip()

                    # Start collecting content (everything after the colon)
                    current_path = path

                    # If there's content on the same line after the colon, add it
                    if len(line) > path_end + 1:
                        content_start = line[path_end + 1 :].strip()
                        if content_start:
                            current_content.append(content_start)

                # Check if this is a separator line
                elif line.strip() == "---":
                    # Save the current file content
                    if current_path:
                        result[current_path] = "\n".join(current_content).strip()
                        current_path = None
                        current_content = []

                # If we're collecting content for a path, add this line
                elif current_path is not None:
                    current_content.append(line)

            # Save the last file content if exists
            if current_path:
                result[current_path] = "\n".join(current_content).strip()

            return result

        args = {"paths": paths}
        try:
            result = self._call_mcp_tool("read_multiple_files", args)
            try:
                logger.debug("Response body:")
                logger.debug(
                    json.dumps(
                        getattr(result, "body", result), ensure_ascii=False, indent=2
                    )
                )
            except Exception:
                logger.debug(f"Response: {result}")

            if result.success:
                files_content = parse_multiple_files_response(result.data)
                return MultipleFileContentResult(
                    request_id=result.request_id,
                    success=True,
                    contents=files_content,
                )
            else:
                return MultipleFileContentResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message
                    or "Failed to read multiple files",
                )
        except Exception as e:
            return MultipleFileContentResult(
                request_id="",
                success=False,
                error_message=f"Failed to read multiple files: {e}",
            )

    def search_files(
        self,
        path: str,
        pattern: str,
        exclude_patterns: Optional[List[str]] = None,
    ) -> FileSearchResult:
        """
        Search for files in the specified path using a pattern.

        Args:
            path (str): The base directory path to search in.
            pattern (str): The glob pattern to search for.
            exclude_patterns (Optional[List[str]]): Optional list of patterns to exclude from the search.
                Defaults to None.

        Returns:
            FileSearchResult: Result object containing matching file paths and error
                message if any.
        """

        args: Dict[str, Any] = {"path": path, "pattern": pattern}
        if exclude_patterns:
            args["excludePatterns"] = exclude_patterns

        try:
            result = self._call_mcp_tool("search_files", args)
            logger.debug(f"Response from CallMcpTool - search_files: {result}")

            if result.success:
                # Handle "No matches found" case
                if (
                    result.data
                    and result.data.strip()
                    and result.data.strip() != "No matches found"
                ):
                    matching_files = result.data.strip().split("\n")
                else:
                    matching_files = []
                return FileSearchResult(
                    request_id=result.request_id,
                    success=True,
                    matches=matching_files,
                )
            else:
                return FileSearchResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message or "Failed to search files",
                )
        except Exception as e:
            return FileSearchResult(
                request_id="",
                success=False,
                error_message=f"Failed to search files: {e}",
            )

    def _get_file_change(self, path: str) -> FileChangeResult:
        """
        Get file change information for the specified directory path.

        Args:
            path: The directory path to monitor for file changes.

        Returns:
            FileChangeResult: Result object containing parsed file change events and
                error message if any.
        """

        def parse_file_change_data(raw_data: str) -> List[FileChangeEvent]:
            """
            Parse the raw file change data into FileChangeEvent objects.

            Args:
                raw_data (str): Raw JSON string containing file change events.

            Returns:
                List[FileChangeEvent]: List of parsed file change events.
            """
            events = []
            try:
                # Parse the JSON array
                change_data = json.loads(raw_data)
                if isinstance(change_data, list):
                    for event_dict in change_data:
                        if isinstance(event_dict, dict):
                            event = FileChangeEvent.from_dict(event_dict)
                            events.append(event)
                else:
                    logger.warning(f"Expected list but got {type(change_data)}")
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON data: {e}")
                logger.warning(f"Raw data: {raw_data}")
            except Exception as e:
                logger.warning(f"Unexpected error parsing file change data: {e}")

            return events

        args = {"path": path}
        try:
            result = self._call_mcp_tool("get_file_change", args)
            try:
                logger.debug("Response body:")
                logger.debug(
                    json.dumps(
                        getattr(result, "body", result), ensure_ascii=False, indent=2
                    )
                )
            except Exception:
                logger.debug(f"Response: {result}")

            if result.success:
                # Parse the file change events
                events = parse_file_change_data(result.data)
                return FileChangeResult(
                    request_id=result.request_id,
                    success=True,
                    events=events,
                    raw_data=result.data,
                )
            else:
                return FileChangeResult(
                    request_id=result.request_id,
                    success=False,
                    raw_data=getattr(result, "data", ""),
                    error_message=result.error_message or "Failed to get file change",
                )
        except Exception as e:
            return FileChangeResult(
                request_id="",
                success=False,
                error_message=f"Failed to get file change: {e}",
            )

    def watch_directory(
        self,
        path: str,
        callback: Callable[[List[FileChangeEvent]], None],
        interval: float = 1.0,
        stop_event: Optional[threading.Event] = None,
    ) -> threading.Thread:
        """
        Watch a directory for file changes and call the callback function when changes occur.

        Args:
            path (str): The directory path to monitor for file changes.
            callback (Callable[[List[FileChangeEvent]], None]): Callback function that will be called with a list of FileChangeEvent
                objects when changes are detected.
            interval (float): Polling interval in seconds. Defaults to 1.0.
            stop_event (Optional[threading.Event]): Optional threading.Event to stop the monitoring. If not provided,
                a new Event will be created and returned via the thread object. Defaults to None.

        Returns:
            threading.Thread: The monitoring thread. Call thread.start() to begin monitoring.
                Use the thread's stop_event attribute to stop monitoring.
        """

        def _monitor_directory():
            """Internal function to monitor directory changes."""
            logger.info(f"Starting directory monitoring for: {path}")
            logger.info(f"Polling interval: {interval} seconds")

            while not stop_event.is_set():
                try:
                    # Get current file changes
                    result = self._get_file_change(path)

                    if result.success:
                        current_events = result.events

                        # Always call callback with current events (no deduplication)
                        logger.debug(f"Detected {len(current_events)} file changes:")
                        for event in current_events:
                            logger.debug(f"  - {event}")

                        try:
                            callback(current_events)
                        except Exception as e:
                            logger.error(f"Error in callback function: {e}")

                    else:
                        logger.error(f"Error monitoring directory: {result.error_message}")

                    # Wait for the next poll
                    stop_event.wait(interval)

                except Exception as e:
                    logger.error(f"Unexpected error in directory monitoring: {e}")
                    stop_event.wait(interval)

            logger.info(f"Stopped monitoring directory: {path}")

        # Create stop event if not provided
        if stop_event is None:
            stop_event = threading.Event()

        # Create and configure the monitoring thread
        monitor_thread = threading.Thread(
            target=_monitor_directory,
            name=f"DirectoryWatcher-{path.replace('/', '_')}",
            daemon=True,
        )

        # Add stop_event as an attribute to the thread for easy access
        setattr(monitor_thread, "stop_event", stop_event)
        return monitor_thread
