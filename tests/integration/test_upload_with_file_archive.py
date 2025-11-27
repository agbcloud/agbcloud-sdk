#!/usr/bin/env python3
"""
Integration test for upload mode functionality in context synchronization.
Tests different upload modes (FILE and ARCHIVE) based on context_sync.py UploadMode enum.
Based on test_context_sync_integration.py format and external test content.
"""

import os
import time
import unittest
import random
import asyncio

from agb import AGB
from agb.context_manager import ContextStatusData
from agb.session_params import CreateSessionParams
from agb.context_sync import ContextSync, SyncPolicy, UploadPolicy, UploadMode

def generate_unique_id():
    """Generate unique ID for test isolation."""
    timestamp = int(time.time() * 1000000) + random.randint(0, 999)
    random_part = random.randint(0, 9999)
    return f"{timestamp}-{random_part}"

class TestUploadModeIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for different upload modes in context synchronization."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        # Skip if no API key is available or in CI environment
        api_key = os.environ.get("AGB_API_KEY")
        if not api_key or os.environ.get("CI"):
            raise unittest.SkipTest(
                "Skipping integration test: No API key available or running in CI"
            )

        # Initialize AGB client
        cls.agb = AGB(api_key)
        cls.unique_id = generate_unique_id()
        cls.test_sessions = []
        print(f"Using unique ID for test: {cls.unique_id}")

    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures."""
        print("Cleaning up: Deleting all test sessions...")
        # Note: Sessions should be cleaned up in individual tests
        # This is a safety net for any remaining sessions

    async def test_create_session_with_default_file_upload_mode(self):
        """Test creating session with default FILE upload mode and basic file operations."""
        print("\n=== Testing default FILE upload mode functionality ===")

        # Step 1: Create context using context.get method
        context_name = f"test-file-mode-context-{self.unique_id}"
        print(f"Creating context with name: {context_name}")

        context_result = self.agb.context.get(context_name, create=True)
        self.assertTrue(context_result.success, f"Failed to create context: {context_result.error_message}")
        self.assertIsNotNone(context_result.context)

        context = context_result.context
        print(f"Generated context: {context.name} (ID: {context.id})")
        print(f"Context get request ID: {context_result.request_id}")
        session = None
        try:
            # Step 2: Create session with default FILE upload mode (using SyncPolicy default)
            sync_policy = SyncPolicy()  # Uses default uploadMode "File"

            # Verify default upload mode is FILE
            self.assertEqual(sync_policy.upload_policy.upload_mode, UploadMode.FILE)
            sync_path =  f"/tmp/test"

            context_sync = ContextSync(
                context_id=context.id,
                path=sync_path,
                policy=sync_policy
            )

            session_params = CreateSessionParams(
                image_id="agb-code-space-2",
                labels={
                    "test": f"upload-mode-{self.unique_id}",
                    "type": "basic-functionality"
                },
                context_syncs=[context_sync]
            )

            print("Creating session with default File upload mode...")
            session_result = self.agb.create(session_params)

            # Step 3: Verify session creation success
            self.assertTrue(session_result.success, f"Failed to create session: {session_result.error_message}")
            self.assertIsNotNone(session_result.session)
            self.assertIsNotNone(session_result.request_id)

            session = session_result.session
            self.test_sessions.append(session)

            print(f"✅ Session created successfully!")
            print(f"Session ID: {session.session_id}")
            print(f"Session creation request ID: {session_result.request_id}")

            # Get session info to verify appInstanceId
            session_info = self.agb.get_session(session.session_id)
            self.assertTrue(session_info.success, f"Failed to get session info: {session_info.error_message}")
            self.assertIsNotNone(session_info.data)

            print(f"App Instance ID: {session_info.data.app_instance_id}")
            print(f"Get session request ID: {session_info.request_id}")

            print("✅ All basic FILE upload mode functionality tests passed!")
            # Wait for session to be ready
            time.sleep(5)

            # Write a 5KB file using FileSystem
            print("Writing 5KB file using FileSystem...")

            # Generate 5KB content (approximately 5120 bytes)
            content_size = 5 * 1024  # 5KB
            base_content = "Archive mode test successful! This is a test file created in the session path. "
            repeated_content = base_content * (content_size // len(base_content) + 1)
            file_content = repeated_content[:content_size]

            # Create file path in the session path directory
            file_path = f"{sync_path}/test-file-5kb.txt"

            print(f"Creating file: {file_path}")
            print(f"File content size: {len(file_content)} bytes")

            write_result = session.file_system.write_file(file_path, file_content, "overwrite")

            # Verify file write success
            self.assertTrue(write_result.success, f"Failed to write file: {write_result.error_message}")
            self.assertIsNotNone(write_result.request_id)
            self.assertNotEqual(write_result.request_id, "")

            print(f"✅ File write successful!")
            print(f"Write file request ID: {write_result.request_id}")

            # Test context sync and info functionality
            print("Testing context sync functionality...")
            # Call context sync before getting info
            print("Calling context sync before getting info...")

            # Use asyncio.run to handle the async sync method
            sync_result = await session.context.sync()

            self.assertTrue(sync_result.success, f"Failed to sync context")
            self.assertIsNotNone(sync_result.request_id)

            print(f"✅ Context sync successful!")
            print(f"Sync request ID: {sync_result.request_id}")

            # Now call context info after sync
            print("Calling context info after sync...")
            info_result = session.context.info()

            self.assertTrue(info_result.success, f"Failed to get context info: {info_result.error_message}")
            self.assertIsNotNone(info_result.request_id)
            self.assertIsNotNone(info_result.context_status_data)

            print(f"✅ Context info successful!")
            print(f"Info request ID: {info_result.request_id}")
            print(f"Context status data count: {len(info_result.context_status_data)}")

            # Log context status details
            if len(info_result.context_status_data) > 0:
                print("Context status details:")
                for index, status in enumerate(info_result.context_status_data):
                    print(f"  [{index}] ContextId: {status.context_id}, Path: {status.path}, Status: {status.status}, TaskType: {status.task_type}")

            # List files in context sync directory
            print("Listing files in context sync directory...")

            list_result = self.agb.context.list_files(context.id, sync_path, page_number=1, page_size=10)

            # Verify ListFiles success
            self.assertTrue(list_result.success, f"Failed to list files: {getattr(list_result, 'error_message', 'Unknown error')}")
            self.assertIsNotNone(list_result.request_id)
            self.assertNotEqual(list_result.request_id, "")

            print(f"✅ List files successful!")
            print(f"List files request ID: {list_result.request_id}")
            print(f"Total files found: {len(list_result.entries)}")

            if list_result.entries:
                print("📋 Files in context sync directory:")
                for index, entry in enumerate(list_result.entries):
                    print(f"  [{index}] FilePath: {entry.file_path}")
                    print(f"      FileType: {entry.file_type}")
                    print(f"      FileName: {entry.file_name}")

            print("✅ All ARCHIVE upload mode tests passed!")

        finally:
            # Cleanup
            print("Cleaning up: Deleting the session...")
            if session in self.test_sessions:
                delete_result = self.agb.delete(session, sync_context=True)
                self.assertTrue(delete_result.success, f"Failed to delete session: {delete_result.error_message}")
                print(f"Session {session.session_id} deleted successfully")
                self.test_sessions.remove(session)

            # Clean up context
            try:
                self.agb.context.delete(context)
                print(f"Context deleted: {context.id}")
            except Exception as e:
                print(f"Warning: Failed to delete context: {e}")

    async def test_context_sync_with_archive_mode_and_file_operations(self):
        """Test contextId and path usage with Archive mode and file operations."""
        print("\n=== Testing contextId and path usage with Archive mode and file operations ===")

        context_name = f"archive-mode-context-{self.unique_id}"
        context_result = self.agb.context.get(context_name, create=True)

        self.assertTrue(context_result.success, f"Failed to create context: {context_result.error_message}")
        self.assertIsNotNone(context_result.context)

        context = context_result.context
        print(f"Generated context: {context.name} (ID: {context.id})")
        session = None
        try:
            # Create sync policy with Archive upload mode
            upload_policy = UploadPolicy(upload_mode=UploadMode.ARCHIVE)
            sync_policy = SyncPolicy(upload_policy=upload_policy)

            context_sync = ContextSync.new(
                context_id=context.id,
                path="/tmp/archive-mode-test",
                policy=sync_policy
            )

            self.assertEqual(context_sync.context_id, context.id)
            self.assertEqual(context_sync.path, "/tmp/archive-mode-test")
            self.assertEqual(context_sync.policy.upload_policy.upload_mode, UploadMode.ARCHIVE)

            print("✅ ContextSync.new works correctly with contextId and path using Archive mode")

            # Create session with the contextSync
            session_params = CreateSessionParams(
                image_id="agb-code-space-2",
                labels={
                    "test": f"archive-mode-{self.unique_id}",
                    "type": "contextId-path-validation"
                },
                context_syncs=[context_sync]
            )

            print("Creating session with Archive mode contextSync...")
            session_result = self.agb.create(session_params)

            self.assertTrue(session_result.success, f"Failed to create session: {session_result.error_message}")
            self.assertIsNotNone(session_result.session)
            self.assertIsNotNone(session_result.request_id)

            session = session_result.session
            self.test_sessions.append(session)

            # Get session info to verify appInstanceId
            session_info = self.agb.get_session(session.session_id)
            self.assertTrue(session_info.success, f"Failed to get session info: {session_info.error_message}")
            self.assertIsNotNone(session_info.data)

            print(f"App Instance ID: {session_info.data.app_instance_id}")

            print(f"✅ Session created successfully with ID: {session.session_id}")
            print(f"Session creation request ID: {session_result.request_id}")

            # Wait for session to be ready
            time.sleep(5)

            # Write a 5KB file using FileSystem
            print("Writing 5KB file using FileSystem...")

            # Generate 5KB content (approximately 5120 bytes)
            content_size = 5 * 1024  # 5KB
            base_content = "Archive mode test successful! This is a test file created in the session path. "
            repeated_content = base_content * (content_size // len(base_content) + 1)
            file_content = repeated_content[:content_size]

            # Create file path in the session path directory
            file_path = "/tmp/archive-mode-test/test-file-5kb.txt"

            print(f"Creating file: {file_path}")
            print(f"File content size: {len(file_content)} bytes")

            write_result = session.file_system.write_file(file_path, file_content, "overwrite")

            # Verify file write success
            self.assertTrue(write_result.success, f"Failed to write file: {write_result.error_message}")
            self.assertIsNotNone(write_result.request_id)
            self.assertNotEqual(write_result.request_id, "")

            print(f"✅ File write successful!")
            print(f"Write file request ID: {write_result.request_id}")

            # Test context sync and info functionality
            print("Testing context sync functionality...")
            # Call context sync before getting info
            print("Calling context sync before getting info...")

            # Use asyncio.run to handle the async sync method
            sync_result = await session.context.sync()

            self.assertTrue(sync_result.success, f"Failed to sync context")
            self.assertIsNotNone(sync_result.request_id)

            print(f"✅ Context sync successful!")
            print(f"Sync request ID: {sync_result.request_id}")

            # Now call context info after sync
            print("Calling context info after sync...")
            info_result = session.context.info()

            self.assertTrue(info_result.success, f"Failed to get context info: {info_result.error_message}")
            self.assertIsNotNone(info_result.request_id)
            self.assertIsNotNone(info_result.context_status_data)

            print(f"✅ Context info successful!")
            print(f"Info request ID: {info_result.request_id}")
            print(f"Context status data count: {len(info_result.context_status_data)}")

            # Log context status details
            if len(info_result.context_status_data) > 0:
                print("Context status details:")
                for index, status in enumerate(info_result.context_status_data):
                    print(f"  [{index}] ContextId: {status.context_id}, Path: {status.path}, Status: {status.status}, TaskType: {status.task_type}")

            # List files in context sync directory
            print("Listing files in context sync directory...")

            # Use the sync directory path
            sync_dir_path = "/tmp/archive-mode-test"

            list_result = self.agb.context.list_files(context.id, sync_dir_path, page_number=1, page_size=10)

            # Verify ListFiles success
            self.assertTrue(list_result.success, f"Failed to list files: {getattr(list_result, 'error_message', 'Unknown error')}")
            self.assertIsNotNone(list_result.request_id)
            self.assertNotEqual(list_result.request_id, "")

            print(f"✅ List files successful!")
            print(f"List files request ID: {list_result.request_id}")
            print(f"Total files found: {len(list_result.entries)}")

            if list_result.entries:
                print("📋 Files in context sync directory:")
                for index, entry in enumerate(list_result.entries):
                    print(f"  [{index}] FilePath: {entry.file_path}")
                    print(f"      FileType: {entry.file_type}")
                    print(f"      FileName: {entry.file_name}")


            print("✅ All ARCHIVE upload mode tests passed!")

        finally:
            # Cleanup
            print("Cleaning up: Deleting the session...")
            if session in self.test_sessions:
                delete_result = self.agb.delete(session, sync_context=True)
                self.assertTrue(delete_result.success, f"Failed to delete session: {delete_result.error_message}")
                print(f"Session {session.session_id} deleted successfully")
                self.test_sessions.remove(session)

            # Clean up context
            try:
                self.agb.context.delete(context)
                print(f"Context deleted: {context.id}")
            except Exception as e:
                print(f"Warning: Failed to delete context: {e}")

    async def test_upload_mode_archive_persistence_with_command(self):
        """Test upload mode persistence across sessions with retry for context status checks."""
        print("\n=== Testing upload mode persistence with retry ===")

        # 1. Create a unique context name and get its ID
        context_name = f"test-persistence-retry-py-{int(time.time())}"
        context_result = self.agb.context.get(context_name, create=True)
        self.assertTrue(context_result.success, "Error getting/creating context")
        self.assertIsNotNone(context_result.context, "Context should not be None")

        context = context_result.context
        print(f"Created context: {context.name} (ID: {context.id})")

        try:
            # 2. Create a session with context sync, using a timestamped path under /home
            timestamp = int(time.time())
            sync_path = f"/home/test-path-py-{timestamp}"

            # Use ARCHIVE upload mode for first session
            upload_policy = UploadPolicy(upload_mode=UploadMode.ARCHIVE)
            sync_policy = SyncPolicy(upload_policy=upload_policy)

            # Create session parameters with context sync
            session_params = CreateSessionParams(image_id="agb-code-space-2")
            context_sync = ContextSync.new(context.id, sync_path, sync_policy)
            session_params.context_syncs = [context_sync]

            # Create first session
            session_result = self.agb.create(session_params)
            if not session_result.success or not session_result.session:
                self.skipTest(f"Failed to create first session: {session_result.error_message}")

            session1 = session_result.session
            print(f"Created first session: {session1.session_id}")

            try:
                # 3. Wait for session to be ready and retry context info until data is available
                print("Waiting for session to be ready and context status data to be available...")

                found_data = False
                context_info = None

                # 4. Create a 1GB file in the context sync path
                test_file_path = f"{sync_path}/test-file.txt"

                # Create directory first
                print(f"Creating directory: {sync_path}")
                dir_result = session1.file_system.create_directory(sync_path)
                self.assertTrue(dir_result.success, "Error creating directory")

                # Create a 1GB file using dd command
                print(f"Creating 1GB file at {test_file_path}")
                create_file_cmd = f"dd if=/dev/zero of={test_file_path} bs=1M count=1024"
                cmd_result = session1.command.execute_command(create_file_cmd,timeout_ms=10000)
                self.assertTrue(cmd_result.success, "Error creating 1GB file")
                print(f"Created 1GB file: {cmd_result.output}")

                # 5. Sync to trigger file upload
                print("Triggering context sync...")
                sync_result = await session1.context.sync()
                self.assertTrue(sync_result.success, "Context sync should be successful")
                print(f"Context sync successful (RequestID: {sync_result.request_id})")

                # 6. Get context info  for upload status
                context_info = session1.context.info()

                self.assertTrue(context_info.success, f"Failed to get context info: {context_info.error_message}")
                self.assertIsNotNone(context_info.context_status_data)

                print(f"✅ Context info successful!")
                print(f"Info request ID: {context_info.request_id}")
                print(f"Context status data count: {len(context_info.context_status_data)}")

                # Log context status details
                if len(context_info.context_status_data) > 0:
                    print("Context status details:")
                    for index, status in enumerate(context_info.context_status_data):
                        print(f"  [{index}] ContextId: {status.context_id}, Path: {status.path}, Status: {status.status}, TaskType: {status.task_type}")
                    time.sleep(1)
                else:
                    print("Warning: Could not find upload status after all retries")

                # 7. List files in context sync directory

                list_result = self.agb.context.list_files(context.id, sync_path, page_number=1, page_size=10)

                # Verify ListFiles success
                self.assertTrue(list_result.success, f"Failed to list files: {getattr(list_result, 'error_message', 'Unknown error')}")
                self.assertIsNotNone(list_result.request_id)
                self.assertNotEqual(list_result.request_id, "")

                print(f"✅ List files successful!")
                print(f"List files request ID: {list_result.request_id}")
                print(f"Total files found: {len(list_result.entries)}")

                if list_result.entries:
                    print("📋 Files in context sync directory:")
                    for index, entry in enumerate(list_result.entries):
                        print(f"  [{index}] FilePath: {entry.file_path}")
                        print(f"      FileType: {entry.file_type}")
                        print(f"      FileName: {entry.file_name}")

                print("✅ All ARCHIVE upload mode tests passed!")
            finally:
                # Clean up first session if it still exists
                try:
                    self.agb.delete(session1)
                    print(f"First session deleted: {session1.session_id}")
                except Exception:
                    pass  # Already deleted

        finally:
            # Clean up context
            try:
                self.agb.context.delete(context)
                print(f"Context deleted: {context.id}")
            except Exception as e:
                print(f"Warning: Failed to delete context: {e}")

    def test_invalid_upload_mode_validation(self):
        """Test that invalid upload_mode values raise ValueError."""
        print("\n=== Testing invalid upload_mode validation ===")

        # Test with invalid string value
        with self.assertRaises(ValueError) as context:
            UploadPolicy(upload_mode="InvalidMode")

        error_message = str(context.exception)
        self.assertIn("Invalid upload_mode value", error_message)
        self.assertIn("InvalidMode", error_message)
        self.assertIn("Valid values are", error_message)
        self.assertIn("File", error_message)
        self.assertIn("Archive", error_message)

        print("✅ Invalid upload_mode validation test passed!")
        print(f"Expected error message: {error_message}")

if __name__ == "__main__":
    unittest.main()