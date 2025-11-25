#!/usr/bin/env python3
"""
Integration test for RecyclePolicy functionality in context synchronization.
Tests different lifecycle options and path validation based on context_sync.py RecyclePolicy class.
Based on test_upload_with_file_archive.py format and external project test content.
"""

import os
import time
import unittest
import random
import asyncio

from agb import AGB
from agb.context_manager import ContextStatusData
from agb.session_params import CreateSessionParams
from agb.context_sync import ContextSync, SyncPolicy, RecyclePolicy, Lifecycle

def generate_unique_id():
    """Generate unique ID for test isolation."""
    timestamp = int(time.time() * 1000000) + random.randint(0, 999)
    random_part = random.randint(0, 9999)
    return f"{timestamp}-{random_part}"

class TestRecyclePolicyIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for RecyclePolicy functionality in context synchronization."""

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

    async def test_create_session_with_default_recycle_policy(self):
        """Test creating session with default RecyclePolicy (LIFECYCLE_FOREVER)."""
        print("\n=== Testing default RecyclePolicy functionality ===")

        # Step 1: Create context using context.get method
        context_name = f"test-default-recycle-context-{self.unique_id}"
        print(f"Creating context with name: {context_name}")
        
        context_result = self.agb.context.get(context_name, create=True)
        self.assertTrue(context_result.success, f"Failed to create context: {context_result.error_message}")
        self.assertIsNotNone(context_result.context)
        
        context = context_result.context
        print(f"Generated context: {context.name} (ID: {context.id})")
        print(f"Context get request ID: {context_result.request_id}")

        session = None  # Initialize session variable
        try:
            # Step 2: Create session with default RecyclePolicy (LIFECYCLE_FOREVER)
            recycle_policy = RecyclePolicy()  # Uses default LIFECYCLE_FOREVER and paths=[""]
            
            # Verify default values
            self.assertEqual(recycle_policy.lifecycle, Lifecycle.LIFECYCLE_FOREVER)
            self.assertEqual(recycle_policy.paths, [""])

            sync_path = f"/tmp/test-default-recycle-{self.unique_id}"
            recycle_policy = RecyclePolicy(paths=["test"])
            self.assertEqual(recycle_policy.paths, ["test"])

            sync_policy = SyncPolicy(recycle_policy=recycle_policy)

            context_sync = ContextSync(
                context_id=context.id,
                path=sync_path,
                policy=sync_policy
            )

            session_params = CreateSessionParams(
                image_id="agb-code-space-2",
                labels={
                    "test": f"recycle-policy-default-{self.unique_id}",
                    "type": "default-lifecycle"
                },
                context_syncs=[context_sync]
            )

            print("Creating session with default RecyclePolicy (LIFECYCLE_FOREVER)...")
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
            result = session.file_system.create_directory(f"{sync_path}/test")
            self.assertTrue(result.success)
            print(f"Created directory {sync_path}")
            result = session.file_system.write_file(f'{sync_path}/test/test.txt', "test data")
            self.assertTrue(result.success)
            print(f"Wrote file to {sync_path}/test.txt")
            read_result = session.file_system.read_file(f"{sync_path}/test/test.txt")
            self.assertTrue(read_result.success)
            self.assertEqual(read_result.content, "test data")
            print("✅ All default RecyclePolicy functionality tests passed!")

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

    async def test_create_session_with_custom_recycle_policy(self):
        """Test creating session with custom RecyclePolicy settings."""
        print("\n=== Testing custom RecyclePolicy functionality ===")

        context_name = f"test-custom-recycle-context-{self.unique_id}"
        context_result = self.agb.context.get(context_name, create=True)
        
        self.assertTrue(context_result.success, f"Failed to create context: {context_result.error_message}")
        self.assertIsNotNone(context_result.context)

        context = context_result.context
        print(f"Generated context: {context.name} (ID: {context.id})")

        session = None  # Initialize session variable
        try:
            # Create custom RecyclePolicy with 1-day lifecycle and specific paths
            custom_recycle_policy = RecyclePolicy(
                lifecycle=Lifecycle.LIFECYCLE_1DAY,
                paths=["test-data"]
            )

            # Verify custom values
            self.assertEqual(custom_recycle_policy.lifecycle, Lifecycle.LIFECYCLE_1DAY)
            self.assertEqual(custom_recycle_policy.paths, ["test-data"])

            sync_policy = SyncPolicy(recycle_policy=custom_recycle_policy)

            context_sync = ContextSync.new(
                context_id=context.id,
                path="/tmp/custom-recycle-test",
                policy=sync_policy
            )

            self.assertEqual(context_sync.context_id, context.id)
            self.assertEqual(context_sync.path, "/tmp/custom-recycle-test")
            self.assertEqual(context_sync.policy.recycle_policy.lifecycle, Lifecycle.LIFECYCLE_1DAY)

            print("✅ ContextSync.new works correctly with custom RecyclePolicy")

            # Create session with the contextSync
            session_params = CreateSessionParams(
                image_id="agb-code-space-2",
                labels={
                    "test": f"recycle-policy-custom-{self.unique_id}",
                    "type": "custom-lifecycle"
                },
                context_syncs=[context_sync]
            )

            print("Creating session with custom RecyclePolicy (1-day lifecycle)...")
            session_result = self.agb.create(session_params)

            self.assertTrue(session_result.success, f"Failed to create session: {session_result.error_message}")
            self.assertIsNotNone(session_result.session)
            self.assertIsNotNone(session_result.request_id)

            session = session_result.session
            self.test_sessions.append(session)

            print(f"✅ Session created successfully with ID: {session.session_id}")
            print(f"Session creation request ID: {session_result.request_id}")

            # Verify session properties
            self.assertIsNotNone(session.session_id)
            self.assertGreater(len(session.session_id), 0)

            result = session.file_system.create_directory("/tmp/custom-recycle-test/test-data")
            self.assertTrue(result.success)
            print(f"Created directory /tmp/custom-recycle-test/test-data")
            
            write_result = session.file_system.write_file("/tmp/custom-recycle-test/test-data/test.txt", "test data")
            self.assertTrue(write_result.success)
            read_result = session.file_system.read_file("/tmp/custom-recycle-test/test-data/test.txt")
            self.assertTrue(read_result.success)
            self.assertEqual(read_result.content, "test data")
            print("Session with custom recyclePolicy created and verified successfully")

        finally:
            # Cleanup
            print("Cleaning up: Deleting the session...")
            if session is not None and session in self.test_sessions:
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

    def test_context_sync_with_invalid_recycle_policy_path(self):
        """Test that ContextSync throws error when creating with invalid recyclePolicy path."""
        print("\n=== Testing ContextSync creation with invalid recyclePolicy path ===")

        print("Testing RecyclePolicy creation with invalid wildcard path...")

        # Test that RecyclePolicy constructor throws an error for invalid path
        with self.assertRaises(ValueError) as context:
            RecyclePolicy(
                lifecycle=Lifecycle.LIFECYCLE_1DAY,
                paths=["/invalid/path/*"]  # Invalid path with wildcard
            )

        # Verify the error message
        expected_message = "Wildcard patterns are not supported in recycle policy paths. Got: /invalid/path/*. Please use exact directory paths instead."
        self.assertIn("Wildcard patterns are not supported in recycle policy paths", str(context.exception))
        self.assertIn("/invalid/path/*", str(context.exception))

        print("RecyclePolicy correctly threw error for invalid path")

        # Test with multiple invalid paths
        with self.assertRaises(ValueError):
            RecyclePolicy(
                lifecycle=Lifecycle.LIFECYCLE_1DAY,
                paths=["/valid/path", "/invalid/path?", "/another/invalid/*"]
            )

        print("RecyclePolicy correctly threw error for multiple invalid paths")

    def test_recycle_policy_invalid_lifecycle(self):
        """Test invalid Lifecycle values."""
        print("\n=== Testing invalid Lifecycle values ===")

        # Test with invalid lifecycle value (string instead of Lifecycle enum)
        with self.assertRaises(ValueError) as context:
            RecyclePolicy(
                lifecycle="invalid_lifecycle",  # Invalid: should be Lifecycle enum
                paths=[""]
            )

        # Verify error message contains expected information
        error_message = str(context.exception)
        expected_substrings = [
            "Invalid lifecycle value",
            "invalid_lifecycle",
            "Valid values are:"
        ]

        for substring in expected_substrings:
            self.assertIn(substring, error_message)

        print(f"Invalid lifecycle 'invalid_lifecycle' correctly failed validation: {error_message}")
        print("Invalid Lifecycle values test completed successfully")

    def test_recycle_policy_combined_invalid(self):
        """Test combination of invalid Lifecycle and invalid paths."""
        print("\n=== Testing combination of invalid Lifecycle and invalid paths ===")

        # Test with both invalid lifecycle and invalid path
        with self.assertRaises(ValueError) as context:
            RecyclePolicy(
                lifecycle="invalid_lifecycle",  # Invalid lifecycle
                paths=["/invalid/path/*"]       # Invalid path with wildcard
            )

        # Should fail on lifecycle validation first (since it's checked first in __post_init__)
        error_message = str(context.exception)
        self.assertIn("Invalid lifecycle value", error_message)

        print(f"Policy with both invalid lifecycle and invalid path correctly failed validation: {error_message}")
        print("Combined invalid configuration test completed successfully")
if __name__ == "__main__":
    unittest.main()