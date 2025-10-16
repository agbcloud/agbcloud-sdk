#!/usr/bin/env python3
"""
Unit tests for context file operations in AGB SDK.
Tests file upload/download URLs, file listing, and file deletion functionality.
"""

import unittest
from unittest.mock import MagicMock

from agb.context import ContextService
from agb.api.models import (
    GetContextFileUploadUrlResponse,
    GetContextFileDownloadUrlResponse,
    DescribeContextFilesResponse,
    DeleteContextFileResponse,
)
from agb.api.models.get_context_file_upload_url_response import GetContextFileUploadUrlResponseBodyData
from agb.api.models.get_context_file_download_url_response import GetContextFileDownloadUrlResponseBodyData
from agb.api.models.describe_context_files_response import DescribeContextFilesResponseBodyData


class TestContextFileOperations(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.agb = MagicMock()
        self.agb.api_key = "test-api-key"
        self.agb.client = MagicMock()
        self.context_service = ContextService(self.agb)
        self.context_id = "ctx-123"
        self.test_path = "/tmp/integration_upload_test.txt"

    def test_get_file_upload_url_success(self):
        """Test successful file upload URL retrieval."""
        # Mock the response
        mock_response = GetContextFileUploadUrlResponse(
            status_code=200,
            json_data={
                "success": True,
                "message": "Success",
                "data": {
                    "url": "https://oss.example.com/upload-url",
                    "expireTime": 3600
                },
                "requestId": "req-upload-1"
            },
            request_id="req-upload-1"
        )

        # Mock the client method
        self.agb.client.get_context_file_upload_url.return_value = mock_response

        # Call the method
        result = self.context_service.get_file_upload_url(self.context_id, self.test_path)

        # Assertions
        self.assertTrue(result.success)
        self.assertEqual(result.url, "https://oss.example.com/upload-url")
        self.assertEqual(result.expire_time, 3600)
        self.assertEqual(result.request_id, "req-upload-1")
        self.assertEqual(result.error_message, "")

        # Verify the client was called with correct parameters
        self.agb.client.get_context_file_upload_url.assert_called_once()
        call_args = self.agb.client.get_context_file_upload_url.call_args[0][0]
        self.assertEqual(call_args.context_id, self.context_id)
        self.assertEqual(call_args.file_path, self.test_path)
        self.assertEqual(call_args.authorization, "Bearer test-api-key")

    def test_get_file_upload_url_failure(self):
        """Test file upload URL retrieval failure."""
        # Mock the response
        mock_response = GetContextFileUploadUrlResponse(
            status_code=400,
            json_data={
                "success": False,
                "message": "Invalid context ID",
                "data": {},
                "requestId": "req-upload-2"
            },
            request_id="req-upload-2"
        )

        # Mock the client method
        self.agb.client.get_context_file_upload_url.return_value = mock_response

        # Call the method
        result = self.context_service.get_file_upload_url(self.context_id, self.test_path)

        # Assertions
        self.assertFalse(result.success)
        self.assertEqual(result.url, "")
        self.assertIsNone(result.expire_time)
        self.assertEqual(result.request_id, "req-upload-2")
        self.assertEqual(result.error_message, "Invalid context ID")

    def test_get_file_download_url_success(self):
        """Test successful file download URL retrieval."""
        # Mock the response
        mock_response = GetContextFileDownloadUrlResponse(
            status_code=200,
            json_data={
                "success": True,
                "message": "Success",
                "data": {
                    "url": "https://oss.example.com/download-url",
                    "expireTime": 7200
                },
                "requestId": "req-download-1"
            },
            request_id="req-download-1"
        )

        # Mock the client method
        self.agb.client.get_context_file_download_url.return_value = mock_response

        # Call the method
        result = self.context_service.get_file_download_url(self.context_id, self.test_path)

        # Assertions
        self.assertTrue(result.success)
        self.assertEqual(result.url, "https://oss.example.com/download-url")
        self.assertEqual(result.expire_time, 7200)
        self.assertEqual(result.request_id, "req-download-1")
        self.assertEqual(result.error_message, "")

        # Verify the client was called with correct parameters
        self.agb.client.get_context_file_download_url.assert_called_once()
        call_args = self.agb.client.get_context_file_download_url.call_args[0][0]
        self.assertEqual(call_args.context_id, self.context_id)
        self.assertEqual(call_args.file_path, self.test_path)
        self.assertEqual(call_args.authorization, "Bearer test-api-key")

    def test_get_file_download_url_unavailable(self):
        """Test file download URL retrieval when file is unavailable."""
        # Mock the response
        mock_response = GetContextFileDownloadUrlResponse(
            status_code=404,
            json_data={
                "success": False,
                "message": "File not found",
                "data": {},
                "requestId": "req-download-2"
            },
            request_id="req-download-2"
        )

        # Mock the client method
        self.agb.client.get_context_file_download_url.return_value = mock_response

        # Call the method
        result = self.context_service.get_file_download_url(self.context_id, self.test_path)

        # Assertions
        self.assertFalse(result.success)
        self.assertEqual(result.url, "")
        self.assertIsNone(result.expire_time)
        self.assertEqual(result.request_id, "req-download-2")
        self.assertEqual(result.error_message, "File not found")

    def test_list_files_with_entries(self):
        """Test listing files with file entries."""
        # Mock the response
        mock_response = DescribeContextFilesResponse(
            status_code=200,
            json_data={
                "success": True,
                "message": "Success",
                "data": [
                    {
                        "fileId": "fid-1",
                        "fileName": "integration_upload_test.txt",
                        "filePath": "/tmp/integration_upload_test.txt",
                        "fileType": "txt",
                        "gmtCreate": "2024-01-01T00:00:00Z",
                        "gmtModified": "2024-01-01T00:00:00Z",
                        "size": 21,
                        "status": "ready"
                    }
                ],
                "count": 1,
                "requestId": "req-list-1"
            },
            request_id="req-list-1"
        )
        # Override the data property to return the list directly
        mock_response.data = [
            {
                "fileId": "fid-1",
                "fileName": "integration_upload_test.txt",
                "filePath": "/tmp/integration_upload_test.txt",
                "fileType": "txt",
                "gmtCreate": "2024-01-01T00:00:00Z",
                "gmtModified": "2024-01-01T00:00:00Z",
                "size": 21,
                "status": "ready"
            }
        ]

        # Mock the client method
        self.agb.client.describe_context_files.return_value = mock_response

        # Call the method
        result = self.context_service.list_files(self.context_id, "/tmp", page_number=1, page_size=50)

        # Assertions
        self.assertTrue(result.success)
        self.assertEqual(len(result.entries), 1)
        self.assertEqual(result.count, 1)
        self.assertEqual(result.request_id, "req-list-1")
        self.assertIsNone(result.error_message)

        # Check the file entry
        entry = result.entries[0]
        self.assertEqual(entry.file_id, "fid-1")
        self.assertEqual(entry.file_name, "integration_upload_test.txt")
        self.assertEqual(entry.file_path, "/tmp/integration_upload_test.txt")
        self.assertEqual(entry.file_type, "txt")
        self.assertEqual(entry.size, 21)
        self.assertEqual(entry.status, "ready")

        # Verify the client was called with correct parameters
        self.agb.client.describe_context_files.assert_called_once()
        call_args = self.agb.client.describe_context_files.call_args[0][0]
        self.assertEqual(call_args.context_id, self.context_id)
        self.assertEqual(call_args.parent_folder_path, "/tmp")
        self.assertEqual(call_args.page_number, 1)
        self.assertEqual(call_args.page_size, 50)
        self.assertEqual(call_args.authorization, "Bearer test-api-key")

    def test_list_files_empty(self):
        """Test listing files when no files exist."""
        # Mock the response
        mock_response = DescribeContextFilesResponse(
            status_code=200,
            json_data={
                "success": True,
                "message": "Success",
                "data": [],
                "count": 0,
                "requestId": "req-list-2"
            },
            request_id="req-list-2"
        )
        # Override the data property to return the list directly
        mock_response.data = []

        # Mock the client method
        self.agb.client.describe_context_files.return_value = mock_response

        # Call the method
        result = self.context_service.list_files(self.context_id, "/tmp", page_number=1, page_size=50)

        # Assertions
        self.assertTrue(result.success)
        self.assertEqual(len(result.entries), 0)
        self.assertEqual(result.count, 0)
        self.assertEqual(result.request_id, "req-list-2")
        self.assertIsNone(result.error_message)

    def test_list_files_failure(self):
        """Test listing files when API call fails."""
        # Mock the response
        mock_response = DescribeContextFilesResponse(
            status_code=400,
            json_data={
                "success": False,
                "message": "Invalid context ID",
                "data": {},
                "requestId": "req-list-3"
            },
            request_id="req-list-3"
        )
        # Override the data property to return empty list
        mock_response.data = []

        # Mock the client method
        self.agb.client.describe_context_files.return_value = mock_response

        # Call the method
        result = self.context_service.list_files(self.context_id, "/tmp", page_number=1, page_size=50)

        # Assertions
        self.assertFalse(result.success)  # ContextService returns success=False for API failures
        self.assertEqual(len(result.entries), 0)
        self.assertIsNone(result.count)
        self.assertEqual(result.request_id, "req-list-3")
        self.assertEqual(result.error_message, "Invalid context ID")

    def test_delete_file_success(self):
        """Test successful file deletion."""
        # Mock the response
        mock_response = DeleteContextFileResponse(
            status_code=200,
            json_data={
                "success": True,
                "message": "Success",
                "requestId": "req-del-1"
            },
            request_id="req-del-1"
        )

        # Mock the client method
        self.agb.client.delete_context_file.return_value = mock_response

        # Call the method
        result = self.context_service.delete_file(self.context_id, self.test_path)

        # Assertions
        self.assertTrue(result.success)
        self.assertEqual(result.request_id, "req-del-1")
        self.assertEqual(result.error_message, "")

        # Verify the client was called with correct parameters
        self.agb.client.delete_context_file.assert_called_once()
        call_args = self.agb.client.delete_context_file.call_args[0][0]
        self.assertEqual(call_args.context_id, self.context_id)
        self.assertEqual(call_args.file_path, self.test_path)
        self.assertEqual(call_args.authorization, "Bearer test-api-key")

    def test_delete_file_failure(self):
        """Test file deletion failure."""
        # Mock the response
        mock_response = DeleteContextFileResponse(
            status_code=404,
            json_data={
                "success": False,
                "message": "File not found",
                "requestId": "req-del-2"
            },
            request_id="req-del-2"
        )

        # Mock the client method
        self.agb.client.delete_context_file.return_value = mock_response

        # Call the method
        result = self.context_service.delete_file(self.context_id, self.test_path)

        # Assertions
        self.assertFalse(result.success)
        self.assertEqual(result.request_id, "req-del-2")
        self.assertEqual(result.error_message, "File not found")

    def test_list_files_with_multiple_entries(self):
        """Test listing files with multiple file entries."""
        # Mock the response
        mock_response = DescribeContextFilesResponse(
            status_code=200,
            json_data={
                "success": True,
                "message": "Success",
                "data": [
                    {
                        "fileId": "fid-1",
                        "fileName": "file1.txt",
                        "filePath": "/tmp/file1.txt",
                        "fileType": "txt",
                        "gmtCreate": "2024-01-01T00:00:00Z",
                        "gmtModified": "2024-01-01T00:00:00Z",
                        "size": 100,
                        "status": "ready"
                    },
                    {
                        "fileId": "fid-2",
                        "fileName": "file2.pdf",
                        "filePath": "/tmp/file2.pdf",
                        "fileType": "pdf",
                        "gmtCreate": "2024-01-01T01:00:00Z",
                        "gmtModified": "2024-01-01T01:00:00Z",
                        "size": 500,
                        "status": "ready"
                    }
                ],
                "count": 2,
                "requestId": "req-list-4"
            },
            request_id="req-list-4"
        )
        # Override the data property to return the list directly
        mock_response.data = [
            {
                "fileId": "fid-1",
                "fileName": "file1.txt",
                "filePath": "/tmp/file1.txt",
                "fileType": "txt",
                "gmtCreate": "2024-01-01T00:00:00Z",
                "gmtModified": "2024-01-01T00:00:00Z",
                "size": 100,
                "status": "ready"
            },
            {
                "fileId": "fid-2",
                "fileName": "file2.pdf",
                "filePath": "/tmp/file2.pdf",
                "fileType": "pdf",
                "gmtCreate": "2024-01-01T01:00:00Z",
                "gmtModified": "2024-01-01T01:00:00Z",
                "size": 500,
                "status": "ready"
            }
        ]

        # Mock the client method
        self.agb.client.describe_context_files.return_value = mock_response

        # Call the method
        result = self.context_service.list_files(self.context_id, "/tmp", page_number=1, page_size=50)

        # Assertions
        self.assertTrue(result.success)
        self.assertEqual(len(result.entries), 2)
        self.assertEqual(result.count, 2)
        self.assertEqual(result.request_id, "req-list-4")

        # Check the first file entry
        entry1 = result.entries[0]
        self.assertEqual(entry1.file_id, "fid-1")
        self.assertEqual(entry1.file_name, "file1.txt")
        self.assertEqual(entry1.file_path, "/tmp/file1.txt")
        self.assertEqual(entry1.file_type, "txt")
        self.assertEqual(entry1.size, 100)
        self.assertEqual(entry1.status, "ready")

        # Check the second file entry
        entry2 = result.entries[1]
        self.assertEqual(entry2.file_id, "fid-2")
        self.assertEqual(entry2.file_name, "file2.pdf")
        self.assertEqual(entry2.file_path, "/tmp/file2.pdf")
        self.assertEqual(entry2.file_type, "pdf")
        self.assertEqual(entry2.size, 500)
        self.assertEqual(entry2.status, "ready")

    def test_list_files_with_pagination(self):
        """Test listing files with pagination parameters."""
        # Mock the response
        mock_response = DescribeContextFilesResponse(
            status_code=200,
            json_data={
                "success": True,
                "message": "Success",
                "data": [],
                "count": 0,
                "requestId": "req-list-5"
            },
            request_id="req-list-5"
        )
        # Override the data property to return the list directly
        mock_response.data = []

        # Mock the client method
        self.agb.client.describe_context_files.return_value = mock_response

        # Call the method with custom pagination
        result = self.context_service.list_files(
            self.context_id,
            "/tmp",
            page_number=2,
            page_size=25
        )

        # Assertions
        self.assertTrue(result.success)
        self.assertEqual(len(result.entries), 0)
        self.assertEqual(result.count, 0)

        # Verify the client was called with correct pagination parameters
        self.agb.client.describe_context_files.assert_called_once()
        call_args = self.agb.client.describe_context_files.call_args[0][0]
        self.assertEqual(call_args.page_number, 2)
        self.assertEqual(call_args.page_size, 25)


if __name__ == "__main__":
    unittest.main()
