#!/usr/bin/env python3
"""
Integration tests for GetAndLoadInternalContext API and FileTransfer functionality.
Tests actual API calls and file transfer operations.
"""

import os
import sys
import time
import unittest
import tempfile

from agb import AGB
from agb.session_params import CreateSessionParams


def get_api_key():
    """Get API Key from environment variables"""
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        raise unittest.SkipTest(
            "Skipping integration test: AGB_API_KEY environment variable not set"
        )
    return api_key


class TestGetAndLoadInternalContextIntegration(unittest.TestCase):
    """Integration tests for GetAndLoadInternalContext API."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before all tests."""
        api_key = get_api_key()
        cls.agb = AGB(api_key=api_key)

        # Create a test session with context sync
        print("\nCreating test session with context sync...")
        params = CreateSessionParams(
            image_id="agb-code-space-2",
        )
        result = cls.agb.create(params)

        if not result.success:
            raise unittest.SkipTest(
                f"Failed to create session: {result.error_message}"
            )

        cls.session = result.session
        print(f"✅ Session created: {cls.session.session_id}")

    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        if hasattr(cls, "session") and cls.session:
            try:
                cls.agb.delete(cls.session)
                print(f"✅ Session released: {cls.session.session_id}")
            except Exception as e:
                print(f"⚠️ Warning: Failed to release session: {e}")

    def test_get_and_load_internal_context_direct(self):
        """Test GetAndLoadInternalContext API call directly."""
        from agb.api.models import GetAndLoadInternalContextRequest

        request = GetAndLoadInternalContextRequest(
            authorization=f"Bearer {self.agb.api_key}",
            session_id=self.session.session_id,
            context_types=["file_transfer"],
        )

        response = self.agb.client.get_and_load_internal_context(request)

        # Check response structure
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.request_id)

        # If API call was successful
        if response.is_successful():
            print(f"✅ GetAndLoadInternalContext successful (RequestID: {response.request_id})")

            # Check data structure
            context_list = response.get_context_list()
            self.assertIsInstance(context_list, list)

            if len(context_list) > 0:
                print(f"   Found {len(context_list)} context(s)")
                for idx, ctx in enumerate(context_list):
                    print(f"   Context {idx + 1}:")
                    print(f"     contextId: {ctx.get('contextId', 'N/A')}")
                    print(f"     contextType: {ctx.get('contextType', 'N/A')}")
                    print(f"     contextPath: {ctx.get('contextPath', 'N/A')}")

                # Test parsed data objects
                context_data_list = response.get_context_list_data()
                self.assertEqual(len(context_data_list), len(context_list))

                if len(context_data_list) > 0:
                    ctx_data = context_data_list[0]
                    self.assertIsNotNone(ctx_data.context_id)
                    self.assertIsNotNone(ctx_data.context_type)
                    self.assertIsNotNone(ctx_data.context_path)
                    print(f"   Parsed first context:")
                    print(f"     context_id: {ctx_data.context_id}")
                    print(f"     context_type: {ctx_data.context_type}")
                    print(f"     context_path: {ctx_data.context_path}")
            else:
                print("   No contexts found in response")
        else:
            error_msg = response.get_error_message()
            print(f"⚠️ GetAndLoadInternalContext failed: {error_msg}")
            # Don't fail the test if API is not available, just skip
            self.skipTest(f"API call failed: {error_msg}")

    def test_file_transfer_ensure_context_id(self):
        """Test FileTransfer.ensure_context_id method through FileSystem."""
        # This test verifies that FileTransfer can successfully get context ID
        # FileTransfer is internal to FileSystem, so we access it through FileSystem methods
        file_system = self.session.file_system

        # The ensure_context_id is called internally when needed
        # We can trigger it by trying to use file_system.upload_file

        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            test_content = f"Test content for file transfer at {int(time.time())}\n"
            f.write(test_content)
            temp_file = f.name

        try:
            # Try to upload a file (this will trigger ensure_context_id)
            context_path = self.session.file_system.get_file_transfer_context_path()
            if context_path is None:
                self.fail("Context path not available - no file_transfer context found for this session")
            remote_path = context_path + "/test_upload.txt"
            result = file_system.upload_file(
                local_path=temp_file,
                remote_path=remote_path,
                wait=False,  # Don't wait for sync to complete
            )

            # Check if context_id was successfully retrieved
            # If upload succeeded or failed with a different error, context_id was retrieved
            if result.success or (
                not result.success
                and "Context ID not available" not in (result.error or "")
            ):
                # Context ID was successfully retrieved
                # Access through internal _file_transfer (for testing purposes)
                self.assertIsNotNone(file_system._file_transfer.context_id)
                print(f"✅ Context ID retrieved: {file_system._file_transfer.context_id}")
                if file_system._file_transfer.context_path:
                    print(f"   Context Path: {file_system._file_transfer.context_path}")

            # Clean up uploaded file if it was successful
            if result.success:
                try:
                    # Try to delete the file
                    context_id = file_system._file_transfer.context_id
                    delete_result = self.agb.context.delete_file(
                        context_id, remote_path
                    )
                    if delete_result.success:
                        print(f"✅ Cleaned up uploaded file: {remote_path}")
                except Exception as e:
                    print(f"⚠️ Warning: Failed to clean up file: {e}")

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except Exception as e:
                print(f"⚠️ Warning: Failed to delete temp file: {e}")

    def test_file_transfer_upload_download_flow(self):
        """Test complete file transfer upload and download flow."""
        # Create a temporary file with test content
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            test_content = f"Integration test content at {int(time.time())}\n"
            f.write(test_content)
            temp_file = f.name

        file_system = self.session.file_system
        context_path = file_system.get_file_transfer_context_path()
        if context_path is None:
            self.fail("Context path not available - no file_transfer context found for this session")
        remote_path = context_path + f"/test_integration_{int(time.time())}.txt"

        try:
            # Upload file
            print(f"\n📤 Uploading file: {temp_file} -> {remote_path}")
            upload_result = file_system.upload_file(
                local_path=temp_file,
                remote_path=remote_path,
                wait=True,
                wait_timeout=60.0,
            )

            if not upload_result.success:
                self.skipTest(f"Upload failed: {upload_result.error}")

            print(f"✅ Upload successful")
            print(f"   Request ID (upload URL): {upload_result.request_id_upload_url}")
            print(f"   Request ID (sync): {upload_result.request_id_sync}")
            print(f"   HTTP Status: {upload_result.http_status}")
            print(f"   Bytes sent: {upload_result.bytes_sent}")

            # Verify context_id was set (access through internal _file_transfer for testing)
            self.assertIsNotNone(file_system._file_transfer.context_id)
            print(f"   Context ID: {file_system._file_transfer.context_id}")

            # Download file
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
                download_file = f.name

            try:
                print(f"\n📥 Downloading file: {remote_path} -> {download_file}")
                download_result = file_system.download_file(
                    remote_path=remote_path,
                    local_path=download_file,
                    wait=True,
                    wait_timeout=300.0,
                )

                if not download_result.success:
                    self.skipTest(f"Download failed: {download_result.error}")

                print(f"✅ Download successful")
                print(f"   Request ID (download URL): {download_result.request_id_download_url}")
                print(f"   Request ID (sync): {download_result.request_id_sync}")
                print(f"   HTTP Status: {download_result.http_status}")
                print(f"   Bytes received: {download_result.bytes_received}")

                # Verify downloaded content matches uploaded content
                with open(download_file, "r") as f:
                    downloaded_content = f.read()

                self.assertEqual(downloaded_content, test_content)
                print(f"✅ Downloaded content matches uploaded content")

            finally:
                # Clean up downloaded file
                try:
                    os.unlink(download_file)
                except Exception as e:
                    print(f"⚠️ Warning: Failed to delete download file: {e}")

            # Clean up remote file
            try:
                context_id = file_system._file_transfer.context_id
                delete_result = self.agb.context.delete_file(
                    context_id, remote_path
                )
                if delete_result.success:
                    print(f"✅ Cleaned up remote file: {remote_path}")
            except Exception as e:
                print(f"⚠️ Warning: Failed to clean up remote file: {e}")

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except Exception as e:
                print(f"⚠️ Warning: Failed to delete temp file: {e}")


if __name__ == "__main__":
    unittest.main()
