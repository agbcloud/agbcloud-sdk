#!/usr/bin/env python3
"""
Integration tests for context sync with MappingPolicy.
This test simulates: Browser session -> persist data -> Code session -> access data
"""

import os
import time
import unittest
import asyncio

from agb import AGB
from agb.context_sync import (
    ContextSync,
    SyncPolicy,
    UploadPolicy,
    DownloadPolicy,
    DeletePolicy,
    ExtractPolicy,
    MappingPolicy,
)
from agb.session_params import CreateSessionParams

class TestContextSyncWithMappingPolicyIntegration(unittest.TestCase):
    """Test cross-platform context synchronization with MappingPolicy."""

    def setUp(self):
        """Set up test fixtures."""
        # Skip in CI environment or if API key is not available
        self.api_key = os.getenv("AGB_API_KEY")
        if not self.api_key or os.getenv("CI"):
            self.skipTest("Skipping integration test: No API key available or running in CI")

        # Initialize the AGB client
        self.ab = AGB(self.api_key)

    def test_context_sync_with_mapping_policy(self):
        """Test that context sync works with MappingPolicy for cross-platform persistence."""
        print("\n" + "="*80)
        print("🚀 STARTING CONTEXT SYNC WITH MAPPING POLICY TEST")
        print("="*80)

        # 1. Create a unique context name
        context_name = f"test-mapping-policy-{int(time.time())}"
        print(f"📝 Creating context with name: {context_name}")

        context_result = self.ab.context.get(name=context_name, create=True)
        self.assertTrue(context_result.success, f"Failed to create context: {getattr(context_result, 'error_message', 'Unknown error')}")
        self.assertIsNotNone(context_result.context, "Context object is None despite success=True")

        context = context_result.context
        print(f"✅ Created context: {context.name} (ID: {context.id})")
        print(f"📊 Context creation request ID: {context_result.request_id}")

        try:
            # Define paths
            browser_path = "/tmp/mapping"
            code_path = "/home/data"
            test_file_name = "cross-platform-test.txt"
            test_content = "This file was created in browser session and should be accessible in code session"

            # ========== Phase 1: Create Browser session and persist data ==========
            print("========== Phase 1: Browser Session - Create and Persist Data ==========")

            # Create sync policy for Browser session (no mapping policy needed for first session)
            browser_sync_policy = SyncPolicy(
                upload_policy=UploadPolicy(),
                download_policy=DownloadPolicy(),
                delete_policy=DeletePolicy(),
                extract_policy=ExtractPolicy()
            )

            # Create Browser session with context sync
            browser_context_sync = ContextSync.new(context.id, browser_path, browser_sync_policy)
            browser_session_params = CreateSessionParams(
                image_id="agb-browser-use-1",
                context_syncs=[browser_context_sync],
                labels={"test": "mapping-policy-Browser"}
            )

            # Create Browser session
            # Wait 10s before creating session to ensure resource availability
            print("Waiting 10s before creating Browser session...")
            time.sleep(10)
            browser_session_result = self.ab.create(browser_session_params)
            self.assertTrue(browser_session_result.success, f"Failed to create Browser session: {browser_session_result.error_message}")
            self.assertIsNotNone(browser_session_result.session, "Browser session object is None")

            browser_session = browser_session_result.session
            print(f"Created Browser session: {browser_session.session_id}")

            # Wait for Browser session to be ready
            print("Waiting for Browser session to be ready...")
            time.sleep(15)

            # Create test file in Browser session
            test_file_path = f"{browser_path}/{test_file_name}"
            print(f"Creating test file in Browser: {test_file_path}")
            create_file_cmd = f'echo {test_content} > "{test_file_path}"'
            browser_cmd_result = browser_session.command.execute(create_file_cmd)
            self.assertIsNotNone(browser_cmd_result)
            print(f"Browser file creation result: {browser_cmd_result.output}")

            # Verify file exists in Browser session
            verify_file_cmd = f'cat "{test_file_path}"'
            verify_result = browser_session.command.execute(verify_file_cmd)
            self.assertIsNotNone(verify_result)
            print(f"Browser file content: {verify_result.output}")
            self.assertIn(test_content, verify_result.output, "File should contain test content in browser")

            # Sync Browser session to upload data
            print("Syncing Browser session to upload data...")
            browser_sync_result = asyncio.run(browser_session.context.sync())
            self.assertTrue(browser_sync_result.success)
            print(f"Browser context sync successful (RequestID: {browser_sync_result.request_id})")

            # Wait for upload to complete
            print("Waiting for upload to complete...")
            time.sleep(10)

            # Delete Browser session
            print("Deleting Browser session...")
            browser_delete_result = self.ab.delete(browser_session)
            print(f"Browser session deleted: {browser_session.session_id} (RequestID: {browser_delete_result.request_id})")

            # Wait for resource release
            print("Waiting 10s for Browser session resource release...")
            time.sleep(10)

            # ========== Phase 2: Create Code session with MappingPolicy and verify data ==========
            print("========== Phase 2: Code Session - Access Data via MappingPolicy ==========")

            # Create mapping policy with Browser path
            mapping_policy = MappingPolicy(path=browser_path)

            # Create sync policy with mapping policy for Code session
            code_sync_policy = SyncPolicy(
                upload_policy=UploadPolicy(),
                download_policy=DownloadPolicy(),
                delete_policy=DeletePolicy(),
                extract_policy=ExtractPolicy(),
                mapping_policy=mapping_policy
            )

            # Create Code session with context sync and mapping policy
            code_context_sync = ContextSync.new(context.id, code_path, code_sync_policy)
            code_session_params = CreateSessionParams(
                image_id="agb-code-space-2",
                context_syncs=[code_context_sync],
                labels={"test": "mapping-policy-Code"}
            )

            # Create Code session
            # Wait 10s before creating session to ensure resource availability
            print("Waiting 10s before creating Code session...")
            time.sleep(10)
            code_session_result = self.ab.create(code_session_params)
            self.assertTrue(code_session_result.success, f"Failed to create Code session: {code_session_result.error_message}")
            self.assertIsNotNone(code_session_result.session, "Code session object is None")

            code_session = code_session_result.session
            print(f"Created Code session: {code_session.session_id} with mapping from {browser_path} to {code_path}")

            try:
                # Wait for Code session to be ready and data to be downloaded
                print("Waiting for Code session to be ready and data to be downloaded...")
                time.sleep(15)

                # Verify file exists in Code session at the mapped path
                code_test_file_path = f"{code_path}/{test_file_name}"
                print(f"Verifying file exists in Code at: {code_test_file_path}")

                # Check if file exists
                check_file_cmd = f'test -f "{code_test_file_path}" && echo "FILE_EXISTS" || echo "FILE_NOT_FOUND"'
                check_result = code_session.command.execute(check_file_cmd)
                self.assertIsNotNone(check_result)
                print(f"Code file check result: {check_result.output}")

                # Verify file exists
                self.assertIn("FILE_EXISTS", check_result.output, "File should exist in Code session at mapped path")

                # Read file content in Code session
                read_file_cmd = f'cat "{code_test_file_path}"'
                read_result = code_session.command.execute(read_file_cmd)
                self.assertIsNotNone(read_result)
                print(f"Code file content: {read_result.output}")

                # Verify file content matches
                self.assertTrue(
                    test_content in read_result.output or test_content.strip() in read_result.output,
                    "File content in Code should match the content created in Browser"
                )

                # Verify context info
                context_info = code_session.context.info()
                self.assertIsNotNone(context_info.request_id)

                if context_info.context_status_data:
                    print("Context status data in Code session:")
                    for i, data in enumerate(context_info.context_status_data):
                        print(f"Context Status Data [{i}]:")
                        print(f"  ContextId: {data.context_id}")
                        print(f"  Path: {data.path}")
                        print(f"  Status: {data.status}")
                        print(f"  TaskType: {data.task_type}")

                    # Verify the context data
                    for data in context_info.context_status_data:
                        if data.context_id == context.id:
                            self.assertEqual(data.path, code_path, "Path should match the Code path")

                print("========== Cross-platform mapping policy test completed successfully ==========")
                print("✓ Data created in Browser session was successfully accessed in Code session via MappingPolicy")

            finally:
                # Ensure Code session is deleted
                delete_result = self.ab.delete(code_session)
                print(f"Code session deleted: {code_session.session_id} (RequestID: {delete_result.request_id})")
                # Wait for resource release
                print("Waiting 10s for Code session resource release...")
                time.sleep(10)

        finally:
            # Ensure context is deleted
            delete_context_result = self.ab.context.delete(context)
            print(f"Context deleted: {context.id} (RequestID: {delete_context_result.request_id})")

if __name__ == "__main__":
    unittest.main()
