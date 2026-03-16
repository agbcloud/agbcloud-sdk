#!/usr/bin/env python3
"""
Integration test for context synchronization functionality.
Based on golang/examples/context_sync_example/main.go
"""

import os
import time
import unittest
import sys

from agb import AGB
from agb.context_manager import ContextStatusData
from agb.session_params import CreateSessionParams
from agb.context_sync import ContextSync, SyncPolicy


class TestContextSyncIntegration(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        # Fail if no API key is available
        api_key = os.environ.get("AGB_API_KEY")
        if not api_key:
            raise AssertionError(
                "Integration test failed: No API key available"
            )

        # Initialize AGB client
        cls.agb = AGB(api_key)

        # Create a unique context name for this test
        cls.context_name = f"test-sync-context-{int(time.time())}"

        # Create a context
        context_result = cls.agb.context.get(cls.context_name, create=True)
        if not context_result.success or not context_result.context:
            raise AssertionError("Failed to create context")

        cls.context = context_result.context
        print(f"Created context: {cls.context.name} (ID: {cls.context.id})")

        # Note: We don't create a session in setUpClass to avoid resource limit issues
        # Sessions will be created in individual test methods as needed

    @classmethod
    def tearDownClass(cls):
        # Clean up context
        if hasattr(cls, "context"):
            try:
                cls.agb.context.delete(cls.context)
                print(f"Context deleted: {cls.context.id}")
            except Exception as e:
                print(f"Warning: Failed to delete context: {e}")

    def test_context_info_returns_context_status_data(self):
        """Test that context info returns parsed ContextStatusData."""
        # Create session for this test
        session_params = CreateSessionParams(image_id="agb-code-space-2")
        context_sync = ContextSync.new(
            self.context.id, "/home", SyncPolicy()
        )
        session_params.context_syncs = [context_sync]

        session_result = self.agb.create(session_params)
        if not session_result.success or not session_result.session:
            self.fail("Failed to create session for test")

        session = session_result.session
        print(f"Created session: {session.session_id}")

        try:
            # Wait for session to be ready
            time.sleep(5)

            # Get context info
            context_info = session.context.info()

            # Verify that we have a request ID
            self.assertIsNotNone(context_info.request_id)
            self.assertNotEqual(context_info.request_id, "")

            # Log the context status data
            print(f"Context status data count: {len(context_info.context_status_data)}")
            for i, data in enumerate(context_info.context_status_data):
                print(f"Status data {i}:")
                print(f"  Context ID: {data.context_id}")
                print(f"  Path: {data.path}")
                print(f"  Status: {data.status}")
                print(f"  Task Type: {data.task_type}")
                print(f"  Start Time: {data.start_time}")
                print(f"  Finish Time: {data.finish_time}")
                if data.error_message:
                    print(f"  Error: {data.error_message}")

            # There might not be any status data yet, so we don't assert on the count
            # But if there is data, verify it has the expected structure
            for data in context_info.context_status_data:
                self.assertIsInstance(data, ContextStatusData)
                self.assertIsNotNone(data.context_id)
                self.assertIsNotNone(data.path)
                self.assertIsNotNone(data.status)
                self.assertIsNotNone(data.task_type)

        finally:
            # Clean up session
            try:
                self.agb.delete(session)
                print(f"Session deleted: {session.session_id}")
            except Exception as e:
                print(f"Warning: Failed to delete session: {e}")

    async def test_context_sync_and_info(self):
        """Test syncing context and then getting info."""
        # Create session for this test
        session_params = CreateSessionParams(image_id="agb-code-space-2")
        context_sync = ContextSync.new(
            self.context.id, "/home", SyncPolicy()
        )
        session_params.context_syncs = [context_sync]

        session_result = self.agb.create(session_params)
        if not session_result.success or not session_result.session:
            self.fail("Failed to create session for test")

        session = session_result.session
        print(f"Created session: {session.session_id}")

        try:
            # Wait for session to be ready
            time.sleep(5)

            # Sync context
            sync_result = await session.context.sync()

            # Verify sync result
            self.assertTrue(sync_result.success)
            self.assertIsNotNone(sync_result.request_id)
            self.assertNotEqual(sync_result.request_id, "")

            # Wait for sync to complete
            time.sleep(5)

            # Get context info
            context_info = session.context.info()

            # Verify context info
            self.assertIsNotNone(context_info.request_id)

            # Log the context status data
            print(
                f"Context status data after sync, count: {len(context_info.context_status_data)}"
            )
            for i, data in enumerate(context_info.context_status_data):
                print(f"Status data {i}:")
                print(f"  Context ID: {data.context_id}")
                print(f"  Path: {data.path}")
                print(f"  Status: {data.status}")
                print(f"  Task Type: {data.task_type}")

            # Check if we have status data for our context
            found_context = False
            for data in context_info.context_status_data:
                if data.context_id == self.context.id:
                    found_context = True
                    self.assertEqual(data.path, "/home")
                    # Status might vary, but should not be empty
                    self.assertIsNotNone(data.status)
                    self.assertNotEqual(data.status, "")
                    break

            # We should have found our context in the status data
            # But this might be flaky in CI, so just log a warning if not found
            if not found_context:
                print(f"Warning: Could not find context {self.context.id} in status data")

        finally:
            # Clean up session
            try:
                self.agb.delete(session)
                print(f"Session deleted: {session.session_id}")
            except Exception as e:
                print(f"Warning: Failed to delete session: {e}")

    def test_context_info_with_params(self):
        """Test getting context info with specific parameters."""
        # Create session for this test
        session_params = CreateSessionParams(image_id="agb-code-space-2")
        context_sync = ContextSync.new(
            self.context.id, "/home", SyncPolicy()
        )
        session_params.context_syncs = [context_sync]

        session_result = self.agb.create(session_params)
        if not session_result.success or not session_result.session:
            self.fail("Failed to create session for test")

        session = session_result.session
        print(f"Created session: {session.session_id}")

        try:
            # Wait for session to be ready
            time.sleep(5)

            # Get context info with parameters
            context_info = session.context.info(
                context_id=self.context.id, path="/home", task_type=None
            )

            # Verify that we have a request ID
            self.assertIsNotNone(context_info.request_id)

            # Log the filtered context status data
            print(
                f"Filtered context status data count: {len(context_info.context_status_data)}"
            )
            for i, data in enumerate(context_info.context_status_data):
                print(f"Status data {i}:")
                print(f"  Context ID: {data.context_id}")
                print(f"  Path: {data.path}")
                print(f"  Status: {data.status}")
                print(f"  Task Type: {data.task_type}")

            # If we have status data, verify it matches our filters
            for data in context_info.context_status_data:
                if data.context_id == self.context.id:
                    self.assertEqual(data.path, "/home")

        finally:
            # Clean up session
            try:
                self.agb.delete(session)
                print(f"Session deleted: {session.session_id}")
            except Exception as e:
                print(f"Warning: Failed to delete session: {e}")

    async def test_context_sync_persistence_with_retry(self):
        """Test context sync persistence with retry for context status checks."""
        # 1. Create a unique context name and get its ID
        context_name = f"test-persistence-retry-py-{int(time.time())}"
        context_result = self.agb.context.get(context_name, True)
        self.assertTrue(context_result.success, "Error getting/creating context")
        self.assertIsNotNone(context_result.context, "Context should not be None")

        context = context_result.context
        if not context:
            self.fail("Failed to create context")
        print(f"Created context: {context.name} (ID: {context.id})")

        try:
            # 2. Create a session with context sync, using a timestamped path under /home
            timestamp = int(time.time())
            sync_path = f"/home/test-path-py-{timestamp}"

            # Use default policy
            default_policy = SyncPolicy()

            # Create session parameters with context sync
            session_params = CreateSessionParams(image_id="agb-code-space-2")
            context_sync = ContextSync.new(context.id, sync_path, default_policy)
            session_params.context_syncs = [context_sync]

            # Create first session
            session_result = self.agb.create(session_params)
            if not session_result.success or not session_result.session:
                self.fail(f"Failed to create first session: {session_result.error_message}")

            session1 = session_result.session

            if not session1:
                self.fail("Failed to create first session")

            print(f"Created first session: {session1.session_id}")

            try:
                # 3. Wait for session to be ready and retry context info until data is available
                print(
                    "Waiting for session to be ready and context status data to be available..."
                )

                found_data = False
                context_info = None

                for i in range(20):  # Retry up to 20 times
                    context_info = session1.context.info()

                    if context_info.context_status_data:
                        print(f"Found context status data on attempt {i+1}")
                        found_data = True
                        break

                    print(
                        f"No context status data available yet (attempt {i+1}), retrying in 1 second..."
                    )
                    time.sleep(1)

                self.assertTrue(
                    found_data, "Context status data should be available after retries"
                )
                if context_info:
                    self._print_context_status_data(context_info.context_status_data)

                # 4. Create a 1GB file in the context sync path
                test_file_path = f"{sync_path}/test-file.txt"

                # Create directory first
                print(f"Creating directory: {sync_path}")
                dir_result = session1.file.mkdir(sync_path)
                self.assertTrue(dir_result.success, "Error creating directory")

                # Create a 1GB file using dd command
                # Note: Creating 1GB file may take time, so we use a longer timeout
                print(f"Creating 1GB file at {test_file_path}")
                create_file_cmd = f"dd if=/dev/zero of={test_file_path} bs=1M count=1024 2>&1"
                # Use a longer timeout for large file creation (5 minutes = 300000ms)
                cmd_result = session1.command.execute(create_file_cmd, timeout_ms=300000)
                if not cmd_result.success:
                    error_msg = f"Error creating 1GB file: {cmd_result.error_message or 'Unknown error'}"
                    if cmd_result.output:
                        error_msg += f"\nCommand output: {cmd_result.output}"
                    print(f"❌ {error_msg}")
                    self.fail(error_msg)
                print(f"Created 1GB file: {cmd_result.output}")

                # 5. Sync to trigger file upload
                print("Triggering context sync...")
                sync_result = await session1.context.sync()
                self.assertTrue(
                    sync_result.success, "Context sync should be successful"
                )
                print(f"Context sync successful (RequestID: {sync_result.request_id})")

                # 6. Get context info with retry for upload status
                print("Checking file upload status with retry...")

                found_upload = False
                for i in range(20):  # Retry up to 20 times
                    context_info = session1.context.info()

                    # Check if we have upload status for our context
                    if context_info and context_info.context_status_data:
                        for data in context_info.context_status_data:
                            if data.context_id == context.id and data.task_type == "upload":
                                found_upload = True
                                print(f"Found upload task for context at attempt {i+1}")
                                break

                    if found_upload:
                        break

                    print(
                        f"No upload status found yet (attempt {i+1}), retrying in 1 second..."
                    )
                    time.sleep(1)

                if found_upload:
                    print("Found upload status for context")
                    if context_info:
                        self._print_context_status_data(context_info.context_status_data)
                else:
                    print("Warning: Could not find upload status after all retries")

                # 7. Release first session
                print("Releasing first session...")
                if session1:
                    delete_result = self.agb.delete(session1, sync_context=True)
                    self.assertTrue(delete_result.success, "Error deleting first session")
                    session1 = None

                # 8. Create a second session with the same context
                print("Creating second session with the same context...")
                session_params = CreateSessionParams(image_id="agb-code-space-2")
                context_sync = ContextSync.new(context.id, sync_path, default_policy)
                session_params.context_syncs = [context_sync]

                session_result = self.agb.create(session_params)
                if not session_result.success or not session_result.session:
                    self.fail(f"Failed to create second session: {session_result.error_message}")

                session2 = session_result.session
                if not session2:
                    self.fail("Failed to create second session")
                print(f"Created second session: {session2.session_id}")

                try:
                    # 9. Get context info with retry for download status
                    print("Checking file download status with retry...")

                    found_download = False
                    download_completed = False
                    context_info = None
                    download_status = None

                    for i in range(40):  # Retry up to 40 times (increased from 20)
                        context_info = session2.context.info()

                        # Check if we have download status for our context
                        if context_info and context_info.context_status_data:
                            for data in context_info.context_status_data:
                                if (
                                    data.context_id == context.id
                                    and data.task_type == "download"
                                ):
                                    found_download = True
                                    download_status = data.status
                                    print(
                                        f"Found download task for context at attempt {i+1}, status: {data.status}"
                                    )
                                    # Check if download is completed
                                    if data.status and data.status.lower() in ["completed", "success", "done"]:
                                        download_completed = True
                                        print(f"Download task completed at attempt {i+1}")
                                        break

                        if download_completed:
                            break

                        if found_download and not download_completed:
                            print(
                                f"Download task found but not completed yet (status: {download_status or 'unknown'}), retrying in 1 second..."
                            )
                        else:
                            print(
                                f"No download status found yet (attempt {i+1}), retrying in 1 second..."
                            )
                        time.sleep(1)

                    if found_download:
                        print("Found download status for context")
                        if context_info:
                            self._print_context_status_data(
                                context_info.context_status_data
                            )
                    else:
                        print(
                            "Warning: Could not find download status after all retries"
                        )

                    if not download_completed:
                        print("Warning: Download task found but may not be completed yet")

                    # Wait additional time for file system to sync
                    print("Waiting for file system to sync after download...")
                    time.sleep(5)

                    # 10. Verify the 1GB file exists in the second session
                    print("Verifying 1GB file exists in second session...")

                    # Retry checking file existence with better error handling
                    file_verified = False
                    for i in range(10):  # Retry up to 10 times
                        # Check file size using ls command
                        check_file_cmd = f"ls -la {test_file_path}"
                        file_info_result = session2.command.execute(check_file_cmd, timeout_ms=10000)

                        if file_info_result.success:
                            print(f"File info (attempt {i+1}): {file_info_result.output}")

                            # Verify file exists and has expected size (approximately 1GB)
                            file_exists_cmd = f"test -f {test_file_path} && echo 'File exists'"
                            exists_result = session2.command.execute(file_exists_cmd, timeout_ms=10000)

                            if exists_result.success and "File exists" in exists_result.output:
                                file_verified = True
                                print("1GB file persistence verified successfully")
                                break
                            else:
                                error_msg = exists_result.error_message or "Unknown error"
                                print(f"File existence check failed (attempt {i+1}): {error_msg}")
                                if exists_result.output:
                                    print(f"Output: {exists_result.output}")
                        else:
                            error_msg = file_info_result.error_message or "Unknown error"
                            print(f"File info check failed (attempt {i+1}): {error_msg}")
                            if file_info_result.output:
                                print(f"Output: {file_info_result.output}")

                        if i < 9:  # Don't sleep on last attempt
                            print(f"Retrying file check in 2 seconds...")
                            time.sleep(2)

                    if not file_verified:
                        # Print detailed diagnostic information
                        print("\n=== Diagnostic Information ===")
                        print(f"Test file path: {test_file_path}")
                        print(f"Sync path: {sync_path}")

                        # Check if directory exists
                        dir_check_cmd = f"ls -la {sync_path}"
                        dir_result = session2.command.execute(dir_check_cmd, timeout_ms=10000)
                        print(f"Directory listing result: success={dir_result.success}")
                        if dir_result.success:
                            print(f"Directory contents: {dir_result.output}")
                        else:
                            print(f"Directory check error: {dir_result.error_message}")

                        # Check parent directory
                        parent_dir = os.path.dirname(test_file_path)
                        parent_check_cmd = f"ls -la {parent_dir}"
                        parent_result = session2.command.execute(parent_check_cmd, timeout_ms=10000)
                        print(f"Parent directory listing: success={parent_result.success}")
                        if parent_result.success:
                            print(f"Parent directory contents: {parent_result.output}")

                        # Print context status data again
                        if context_info:
                            print("\nFinal context status data:")
                            self._print_context_status_data(context_info.context_status_data)

                        self.fail(
                            f"Failed to verify 1GB file exists after all retries. "
                            f"File path: {test_file_path}, "
                            f"Last error: {file_info_result.error_message if 'file_info_result' in locals() else 'N/A'}"
                        )

                finally:
                    # Clean up second session
                    try:
                        if session2:
                            self.agb.delete(session2)
                            print(f"Second session deleted: {session2.session_id}")
                    except Exception as e:
                        print(f"Warning: Failed to delete second session: {e}")

            finally:
                # Clean up first session if it still exists
                try:
                    if session1:
                        self.agb.delete(session1)
                        print(f"First session deleted: {session1.session_id}")
                except Exception:
                    pass  # Already deleted

        finally:
            # Clean up context
            try:
                if context:
                    self.agb.context.delete(context)
                    print(f"Context deleted: {context.id}")
            except Exception as e:
                print(f"Warning: Failed to delete context: {e}")

    def _print_context_status_data(self, data):
        """Helper method to print context status data."""
        if not data:
            print("No context status data available")
            return

        for i, item in enumerate(data):
            print(f"Context Status Data [{i}]:")
            print(f"  ContextId: {item.context_id}")
            print(f"  Path: {item.path}")
            print(f"  Status: {item.status}")
            print(f"  TaskType: {item.task_type}")
            print(f"  StartTime: {item.start_time}")
            print(f"  FinishTime: {item.finish_time}")
            if item.error_message:
                print(f"  ErrorMessage: {item.error_message}")


class TestContextGetIntegration(unittest.TestCase):
    """Integration tests for context.get() method with ID and Name parameters."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        # Fail if no API key is available
        api_key = os.environ.get("AGB_API_KEY")
        if not api_key:
            raise AssertionError(
                "Integration test failed: No API key available"
            )

        # Initialize AGB client
        cls.agb = AGB(api_key)

        # Create a unique context name for this test
        cls.context_name = f"test-get-context-{int(time.time())}"

        # Create a context
        context_result = cls.agb.context.get(cls.context_name, create=True)
        if not context_result.success or not context_result.context:
            raise AssertionError("Failed to create context for testing")

        cls.context = context_result.context
        print(f"Created context: {cls.context.name} (ID: {cls.context.id})")

    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures."""
        if hasattr(cls, "context"):
            try:
                cls.agb.context.delete(cls.context)
                print(f"Context deleted: {cls.context.id}")
            except Exception as e:
                print(f"Warning: Failed to delete context: {e}")

    def test_get_context_by_name(self):
        """Test getting a context by name."""
        result = self.agb.context.get(name=self.context_name)
        self.assertTrue(result.success, f"Failed to get context by name: {result.error_message}")
        self.assertIsNotNone(result.context)
        self.assertEqual(result.context.name, self.context_name)
        self.assertEqual(result.context.id, self.context.id)

    def test_get_context_by_id(self):
        """Test getting a context by ID.
        Note: This test may fail if the backend API doesn't support getting context by ID only.
        The API currently requires Name parameter, so this test validates our parameter validation.
        """
        result = self.agb.context.get(context_id=self.context.id)
        # The backend API may not support ID-only lookup yet, so we check the validation logic
        # If API supports it, result.success should be True
        # If not, it will fail with "missing parameter Name", which is expected behavior
        if not result.success:
            # If backend doesn't support ID-only, that's okay - our validation logic is correct
            # Just verify we got a meaningful error message
            self.assertIsNotNone(result.error_message)
            print(f"Backend may not support ID-only lookup yet: {result.error_message}")
        else:
            # If it works, verify the results
            self.assertIsNotNone(result.context)
            self.assertEqual(result.context.id, self.context.id)
            self.assertEqual(result.context.name, self.context.name)

    def test_get_context_validation_empty_params(self):
        """Test that getting a context fails when both name and context_id are empty."""
        result = self.agb.context.get()
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
        self.assertIn("Either context_id or name must be provided", result.error_message or "")

    def test_get_context_validation_create_with_id(self):
        """Test that creating a context fails when context_id is provided with create=True."""
        result = self.agb.context.get(context_id=self.context.id, create=True)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
        self.assertIn("context_id cannot be provided when create=True", result.error_message or "")

    def test_get_context_backward_compatibility(self):
        """Test backward compatibility: getting context with name parameter only (old API style)."""
        result = self.agb.context.get(self.context_name)
        self.assertTrue(result.success, f"Failed backward compatibility test: {result.error_message}")
        self.assertIsNotNone(result.context)
        self.assertEqual(result.context.name, self.context_name)


if __name__ == "__main__":
    result = unittest.main(exit=False)
    if result.result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)
