#!/usr/bin/env python3
"""
Unit tests for FileSystem module in AGB SDK.
Tests all file system operations with success and failure scenarios.
"""

import unittest
from unittest.mock import MagicMock, patch

from agb.modules.file_system import (
    FileSystem,
    FileChangeEvent,
    FileInfoResult,
    DirectoryListResult,
    FileContentResult,
    MultipleFileContentResult,
    FileChangeResult,
)
from agb.model.response import OperationResult, BoolResult, BinaryFileContentResult


class DummySession:
    """Dummy session class for testing."""

    def __init__(self):
        self.session_id = "test_session_id"
        self.client = MagicMock()

    def get_api_key(self) -> str:
        return "test_api_key"

    def get_session_id(self) -> str:
        return self.session_id

    def get_client(self):
        return self.client


class TestFileChangeEvent(unittest.TestCase):
    """Test FileChangeEvent class."""

    def test_file_change_event_initialization(self):
        """Test FileChangeEvent initialization."""
        event = FileChangeEvent(
            event_type="modify",
            path="/tmp/test.txt",
            path_type="file",
        )

        self.assertEqual(event.event_type, "modify")
        self.assertEqual(event.path, "/tmp/test.txt")
        self.assertEqual(event.path_type, "file")

    def test_file_change_event_to_dict(self):
        """Test FileChangeEvent to_dict conversion."""
        event = FileChangeEvent(
            event_type="create",
            path="/tmp/new.txt",
            path_type="file",
        )

        result = event.to_dict()

        self.assertEqual(result["eventType"], "create")
        self.assertEqual(result["path"], "/tmp/new.txt")
        self.assertEqual(result["pathType"], "file")

    def test_file_change_event_from_dict(self):
        """Test FileChangeEvent from_dict creation."""
        data = {
            "eventType": "delete",
            "path": "/tmp/old.txt",
            "pathType": "file",
        }

        event = FileChangeEvent.from_dict(data)

        self.assertEqual(event.event_type, "delete")
        self.assertEqual(event.path, "/tmp/old.txt")
        self.assertEqual(event.path_type, "file")


class TestFileSystem(unittest.TestCase):
    """Test FileSystem class."""

    def setUp(self):
        """Set up test fixtures."""
        self.session = DummySession()
        self.file_system = FileSystem(self.session)

    def test_create_directory_success(self):
        """Test successful directory creation."""
        mock_result = OperationResult(
            request_id="req-123",
            success=True,
            data=True,
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.file_system.create_directory("/tmp/test_dir")

        self.assertTrue(result.success)
        self.assertTrue(result.data)
        self.file_system._call_mcp_tool.assert_called_once_with(
            "create_directory", {"path": "/tmp/test_dir"}
        )

    def test_create_directory_failure(self):
        """Test directory creation failure."""
        mock_result = OperationResult(
            request_id="req-456",
            success=False,
            error_message="Directory already exists",
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.file_system.create_directory("/tmp/existing_dir")

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Directory already exists")

    def test_create_directory_exception(self):
        """Test directory creation exception handling."""
        self.file_system._call_mcp_tool = MagicMock(side_effect=Exception("Network error"))

        result = self.file_system.create_directory("/tmp/test_dir")

        self.assertFalse(result.success)
        self.assertIn("Failed to create directory", result.error_message)

    def test_edit_file_success(self):
        """Test successful file editing."""
        mock_result = OperationResult(
            request_id="req-789",
            success=True,
            data=True,
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        edits = [{"oldText": "old", "newText": "new"}]
        result = self.file_system.edit_file("/tmp/test.txt", edits)

        self.assertTrue(result.success)
        self.file_system._call_mcp_tool.assert_called_once_with(
            "edit_file",
            {"path": "/tmp/test.txt", "edits": edits, "dryRun": False},
        )

    def test_edit_file_dry_run(self):
        """Test file editing with dry run."""
        mock_result = OperationResult(
            request_id="req-dry-1",
            success=True,
            data=True,
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        edits = [{"oldText": "old", "newText": "new"}]
        result = self.file_system.edit_file("/tmp/test.txt", edits, dry_run=True)

        self.assertTrue(result.success)
        call_args = self.file_system._call_mcp_tool.call_args
        self.assertTrue(call_args[0][1]["dryRun"])

    def test_edit_file_failure(self):
        """Test file editing failure."""
        mock_result = OperationResult(
            request_id="req-fail-1",
            success=False,
            error_message="File not found",
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        edits = [{"oldText": "old", "newText": "new"}]
        result = self.file_system.edit_file("/tmp/nonexistent.txt", edits)

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "File not found")

    def test_get_file_info_success(self):
        """Test successful file info retrieval."""
        mock_result = OperationResult(
            request_id="req-info-1",
            success=True,
            data="name: test.txt\nsize: 1024\nisDirectory: false",
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.file_system.get_file_info("/tmp/test.txt")

        self.assertTrue(result.success)
        self.assertEqual(result.file_info["name"], "test.txt")
        self.assertEqual(result.file_info["size"], 1024)
        self.assertFalse(result.file_info["isDirectory"])

    def test_get_file_info_failure(self):
        """Test file info retrieval failure."""
        mock_result = OperationResult(
            request_id="req-info-2",
            success=False,
            error_message="File not found",
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.file_system.get_file_info("/tmp/nonexistent.txt")

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "File not found")

    def test_list_directory_success(self):
        """Test successful directory listing."""
        mock_result = OperationResult(
            request_id="req-list-1",
            success=True,
            data="[DIR] folder1\n[FILE] file1.txt\n[DIR] folder2",
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.file_system.list_directory("/tmp")

        self.assertTrue(result.success)
        self.assertEqual(len(result.entries), 3)
        self.assertTrue(result.entries[0]["isDirectory"])
        self.assertEqual(result.entries[0]["name"], "folder1")
        self.assertFalse(result.entries[1]["isDirectory"])
        self.assertEqual(result.entries[1]["name"], "file1.txt")

    def test_list_directory_failure(self):
        """Test directory listing failure."""
        mock_result = OperationResult(
            request_id="req-list-2",
            success=False,
            error_message="Directory not found",
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.file_system.list_directory("/nonexistent")

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Directory not found")

    def test_move_file_success(self):
        """Test successful file move."""
        mock_result = OperationResult(
            request_id="req-move-1",
            success=True,
            data=True,
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.file_system.move_file("/tmp/src.txt", "/tmp/dst.txt")

        self.assertTrue(result.success)
        self.file_system._call_mcp_tool.assert_called_once_with(
            "move_file",
            {"source": "/tmp/src.txt", "destination": "/tmp/dst.txt"},
        )

    def test_move_file_failure(self):
        """Test file move failure."""
        mock_result = OperationResult(
            request_id="req-move-2",
            success=False,
            error_message="Source file not found",
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.file_system.move_file("/tmp/nonexistent.txt", "/tmp/dst.txt")

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Source file not found")

    def test_delete_file_success(self):
        """Test successful file deletion."""
        mock_result = OperationResult(
            request_id="req-delete-1",
            success=True,
            data=True,
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.file_system.delete_file("/tmp/test.txt")

        self.assertTrue(result.success)
        self.assertTrue(result.data)
        self.file_system._call_mcp_tool.assert_called_once_with(
            "delete_file", {"path": "/tmp/test.txt"}
        )

    def test_delete_file_failure(self):
        """Test file deletion failure."""
        mock_result = OperationResult(
            request_id="req-delete-2",
            success=False,
            error_message="File not found",
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.file_system.delete_file("/tmp/nonexistent.txt")

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "File not found")

    def test_delete_file_exception(self):
        """Test file deletion exception handling."""
        self.file_system._call_mcp_tool = MagicMock(side_effect=Exception("Network error"))

        result = self.file_system.delete_file("/tmp/test.txt")

        self.assertFalse(result.success)
        self.assertIn("Failed to delete file", result.error_message)

    def test_delete_file_permission_denied(self):
        """Test file deletion with permission denied."""
        mock_result = OperationResult(
            request_id="req-delete-3",
            success=False,
            error_message="Permission denied",
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.file_system.delete_file("/root/protected.txt")

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Permission denied")

    def test_delete_file_directory_error(self):
        """Test file deletion when path is a directory."""
        mock_result = OperationResult(
            request_id="req-delete-4",
            success=False,
            error_message="Cannot delete directory with delete_file",
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.file_system.delete_file("/tmp/directory")

        self.assertFalse(result.success)
        self.assertIn("directory", result.error_message.lower())

    @patch.object(FileSystem, "get_file_info")
    @patch.object(FileSystem, "_read_file_chunk")
    def test_read_file_success_text_format(self, mock_read_chunk, mock_get_info):
        """Test successful file read with text format (default)."""
        # Mock file info
        mock_info_result = FileInfoResult(
            request_id="req-info-read",
            success=True,
            file_info={"size": 100, "isDirectory": False},
        )
        mock_get_info.return_value = mock_info_result

        # Mock chunk read
        mock_chunk_result = FileContentResult(
            request_id="req-chunk-1",
            success=True,
            content="Hello, World!",
        )
        mock_read_chunk.return_value = mock_chunk_result

        result = self.file_system.read_file("/tmp/test.txt")

        self.assertTrue(result.success)
        self.assertEqual(result.content, "Hello, World!")
        self.assertIsInstance(result, FileContentResult)

    @patch.object(FileSystem, "get_file_info")
    @patch.object(FileSystem, "_read_file_chunk")
    def test_read_file_success_text_format_explicit(self, mock_read_chunk, mock_get_info):
        """Test successful file read with explicit text format."""
        # Mock file info
        mock_info_result = FileInfoResult(
            request_id="req-info-read-text",
            success=True,
            file_info={"size": 50, "isDirectory": False},
        )
        mock_get_info.return_value = mock_info_result

        # Mock chunk read
        mock_chunk_result = FileContentResult(
            request_id="req-chunk-text",
            success=True,
            content="Text file content",
        )
        mock_read_chunk.return_value = mock_chunk_result

        result = self.file_system.read_file("/tmp/test.txt", format="text")

        self.assertTrue(result.success)
        self.assertEqual(result.content, "Text file content")
        self.assertIsInstance(result, FileContentResult)
        self.assertIsInstance(result.content, str)

    @patch.object(FileSystem, "get_file_info")
    @patch.object(FileSystem, "_read_file_chunk")
    def test_read_file_success_bytes_format(self, mock_read_chunk, mock_get_info):
        """Test successful file read with bytes format."""
        # Mock file info
        mock_info_result = FileInfoResult(
            request_id="req-info-read-bytes",
            success=True,
            file_info={"size": 20, "isDirectory": False},
        )
        mock_get_info.return_value = mock_info_result

        # Mock chunk read - return binary content
        test_binary_content = b"Binary file content\x00\x01\x02"
        mock_chunk_result = BinaryFileContentResult(
            request_id="req-chunk-bytes",
            success=True,
            content=test_binary_content,
        )
        mock_read_chunk.return_value = mock_chunk_result

        result = self.file_system.read_file("/tmp/binary.dat", format="bytes")

        self.assertTrue(result.success)
        self.assertEqual(result.content, test_binary_content)
        self.assertIsInstance(result, BinaryFileContentResult)
        self.assertIsInstance(result.content, bytes)

    @patch.object(FileSystem, "get_file_info")
    @patch.object(FileSystem, "_read_file_chunk")
    def test_read_file_bytes_format_failure(self, mock_read_chunk, mock_get_info):
        """Test file read with bytes format failure."""
        # Mock file info
        mock_info_result = FileInfoResult(
            request_id="req-info-bytes-fail",
            success=True,
            file_info={"size": 100, "isDirectory": False},
        )
        mock_get_info.return_value = mock_info_result

        # Mock chunk read failure
        mock_chunk_result = BinaryFileContentResult(
            request_id="req-chunk-bytes-fail",
            success=False,
            content=b"",
            error_message="Failed to read binary file",
        )
        mock_read_chunk.return_value = mock_chunk_result

        result = self.file_system.read_file("/tmp/binary.dat", format="bytes")

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Failed to read binary file")
        self.assertIsInstance(result, BinaryFileContentResult)
        self.assertEqual(result.content, b"")

    @patch.object(FileSystem, "get_file_info")
    def test_read_file_bytes_format_file_not_found(self, mock_get_info):
        """Test file read with bytes format when file doesn't exist."""
        mock_info_result = FileInfoResult(
            request_id="req-info-bytes-404",
            success=False,
            error_message="File not found",
        )
        mock_get_info.return_value = mock_info_result

        result = self.file_system.read_file("/tmp/nonexistent.dat", format="bytes")

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "File not found")
        self.assertIsInstance(result, BinaryFileContentResult)
        self.assertEqual(result.content, b"")

    @patch.object(FileSystem, "get_file_info")
    def test_read_file_bytes_format_is_directory(self, mock_get_info):
        """Test file read with bytes format when path is a directory."""
        mock_info_result = FileInfoResult(
            request_id="req-info-bytes-dir",
            success=False,
            file_info={"isDirectory": True},
            error_message="Path does not exist or is a directory:/tmp/directory"
        )
        mock_get_info.return_value = mock_info_result

        result = self.file_system.read_file("/tmp/directory", format="bytes")

        self.assertFalse(result.success)
        self.assertIn("is a directory", result.error_message)
        self.assertIsInstance(result, BinaryFileContentResult)

    @patch.object(FileSystem, "get_file_info")
    def test_read_file_bytes_format_empty_file(self, mock_get_info):
        """Test reading an empty file with bytes format."""
        mock_info_result = FileInfoResult(
            request_id="req-info-bytes-empty",
            success=True,
            file_info={"size": 0, "isDirectory": False},
        )
        mock_get_info.return_value = mock_info_result

        result = self.file_system.read_file("/tmp/empty.dat", format="bytes")

        self.assertTrue(result.success)
        self.assertEqual(result.content, b"")
        self.assertIsInstance(result, BinaryFileContentResult)
    @patch.object(FileSystem, "read_file")
    def test_read_alias_method_default(self, mock_read_file):
        """Test that the read() alias method works correctly with default format."""
        mock_result = FileContentResult(
            request_id="req-read-alias",
            success=True,
            content="Test content",
        )
        mock_read_file.return_value = mock_result

        result = self.file_system.read("/tmp/test.txt")

        self.assertTrue(result.success)
        self.assertEqual(result.content, "Test content")
        mock_read_file.assert_called_once_with("/tmp/test.txt")
    @patch.object(FileSystem, "get_file_info")
    def test_read_file_not_found(self, mock_get_info):
        """Test file read when file doesn't exist."""
        mock_info_result = FileInfoResult(
            request_id="req-info-404",
            success=False,
            error_message="File not found",
        )
        mock_get_info.return_value = mock_info_result

        result = self.file_system.read_file("/tmp/nonexistent.txt")

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "File not found")

    @patch.object(FileSystem, "get_file_info")
    def test_read_file_is_directory(self, mock_get_info):
        """Test file read when path is a directory."""
        mock_info_result = FileInfoResult(
            request_id="req-info-dir",
            success=True,
            file_info={"isDirectory": True},
        )
        mock_get_info.return_value = mock_info_result

        result = self.file_system.read_file("/tmp/directory")

        self.assertFalse(result.success)
        self.assertIn("is a directory", result.error_message)

    @patch.object(FileSystem, "get_file_info")
    def test_read_file_empty(self, mock_get_info):
        """Test reading an empty file."""
        mock_info_result = FileInfoResult(
            request_id="req-info-empty",
            success=True,
            file_info={"size": 0, "isDirectory": False},
        )
        mock_get_info.return_value = mock_info_result

        result = self.file_system.read_file("/tmp/empty.txt")

        self.assertTrue(result.success)
        self.assertEqual(result.content, "")

    @patch.object(FileSystem, "_write_file_chunk")
    def test_write_file_success_small(self, mock_write_chunk):
        """Test successful write of small file."""
        mock_write_result = BoolResult(
            request_id="req-write-1",
            success=True,
            data=True,
        )
        mock_write_chunk.return_value = mock_write_result

        result = self.file_system.write_file("/tmp/test.txt", "Hello, World!")

        self.assertTrue(result.success)
        mock_write_chunk.assert_called_once()

    @patch.object(FileSystem, "_write_file_chunk")
    def test_write_file_success_large(self, mock_write_chunk):
        """Test successful write of large file (chunked)."""
        # Create content larger than DEFAULT_CHUNK_SIZE
        large_content = "x" * (FileSystem.DEFAULT_CHUNK_SIZE + 100)

        mock_write_result = BoolResult(
            request_id="req-write-2",
            success=True,
            data=True,
        )
        mock_write_chunk.return_value = mock_write_result

        result = self.file_system.write_file("/tmp/large.txt", large_content)

        self.assertTrue(result.success)
        # Should be called multiple times for chunked write
        self.assertGreater(mock_write_chunk.call_count, 1)

    def test_read_multiple_files_success(self):
        """Test successful reading of multiple files."""
        mock_result = OperationResult(
            request_id="req-multi-1",
            success=True,
            data="/tmp/file1.txt: Content 1\n\n---\n/tmp/file2.txt: Content 2",
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.file_system.read_multiple_files(["/tmp/file1.txt", "/tmp/file2.txt"])

        self.assertTrue(result.success)
        self.assertEqual(result.contents["/tmp/file1.txt"], "Content 1")
        self.assertEqual(result.contents["/tmp/file2.txt"], "Content 2")

    def test_read_multiple_files_failure(self):
        """Test reading multiple files failure."""
        mock_result = OperationResult(
            request_id="req-multi-2",
            success=False,
            error_message="Some files not found",
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.file_system.read_multiple_files(["/tmp/file1.txt", "/tmp/file2.txt"])

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Some files not found")

    def test_search_files_success(self):
        """Test successful file search."""
        mock_result = OperationResult(
            request_id="req-search-1",
            success=True,
            data="/tmp/file1.py\n/tmp/file2.py\n/tmp/subdir/file3.py",
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.file_system.search_files("/tmp", pattern="*.py")

        self.assertTrue(result.success)
        self.assertEqual(len(result.matches), 3)
        self.assertIn("/tmp/file1.py", result.matches)

    def test_search_files_failure(self):
        """Test file search failure."""
        mock_result = OperationResult(
            request_id="req-search-2",
            success=False,
            error_message="Search failed",
        )
        self.file_system._call_mcp_tool = MagicMock(return_value=mock_result)

        result = self.file_system.search_files("/tmp", pattern="*.py")

        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Search failed")


class TestFileChangeResult(unittest.TestCase):
    """Test FileChangeResult class."""

    def test_file_change_result_initialization(self):
        """Test FileChangeResult initialization."""
        events = [
            FileChangeEvent(event_type="modify", path="/tmp/file1.txt", path_type="file"),
            FileChangeEvent(event_type="create", path="/tmp/file2.txt", path_type="file"),
        ]
        result = FileChangeResult(
            request_id="req-change-1",
            success=True,
            events=events,
        )

        self.assertTrue(result.success)
        self.assertEqual(len(result.events), 2)

    def test_file_change_result_has_changes(self):
        """Test FileChangeResult has_changes method."""
        events = [
            FileChangeEvent(event_type="modify", path="/tmp/file1.txt", path_type="file"),
        ]
        result = FileChangeResult(
            request_id="req-change-2",
            success=True,
            events=events,
        )

        self.assertTrue(result.has_changes())

    def test_file_change_result_no_changes(self):
        """Test FileChangeResult with no changes."""
        result = FileChangeResult(
            request_id="req-change-3",
            success=True,
            events=[],
        )

        self.assertFalse(result.has_changes())

    def test_file_change_result_get_modified_files(self):
        """Test FileChangeResult get_modified_files method."""
        events = [
            FileChangeEvent(event_type="modify", path="/tmp/file1.txt", path_type="file"),
            FileChangeEvent(event_type="create", path="/tmp/file2.txt", path_type="file"),
            FileChangeEvent(event_type="delete", path="/tmp/file3.txt", path_type="file"),
        ]
        result = FileChangeResult(
            request_id="req-change-4",
            success=True,
            events=events,
        )

        modified = result.get_modified_files()
        self.assertEqual(len(modified), 1)
        self.assertEqual(modified[0], "/tmp/file1.txt")

    def test_file_change_result_get_created_files(self):
        """Test FileChangeResult get_created_files method."""
        events = [
            FileChangeEvent(event_type="create", path="/tmp/file1.txt", path_type="file"),
            FileChangeEvent(event_type="create", path="/tmp/dir1", path_type="directory"),
        ]
        result = FileChangeResult(
            request_id="req-change-5",
            success=True,
            events=events,
        )

        created = result.get_created_files()
        self.assertEqual(len(created), 1)
        self.assertEqual(created[0], "/tmp/file1.txt")

    def test_file_change_result_get_deleted_files(self):
        """Test FileChangeResult get_deleted_files method."""
        events = [
            FileChangeEvent(event_type="delete", path="/tmp/file1.txt", path_type="file"),
            FileChangeEvent(event_type="delete", path="/tmp/dir1", path_type="directory"),
        ]
        result = FileChangeResult(
            request_id="req-change-6",
            success=True,
            events=events,
        )

        deleted = result.get_deleted_files()
        self.assertEqual(len(deleted), 1)
        self.assertEqual(deleted[0], "/tmp/file1.txt")


if __name__ == "__main__":
    unittest.main()

