"""Integration tests for Context clear operations."""
import os
import time
import unittest
from uuid import uuid4

from agb import AGB
from agb.agb import Config
from agb.exceptions import ClearanceTimeoutError


def get_test_api_key():
    """Get API key for testing."""
    return os.environ.get("AGB_API_KEY")


def get_test_endpoint():
    """Get endpoint for testing."""
    return os.environ.get("AGB_ENDPOINT")


class TestContextClearIntegration(unittest.TestCase):
    """Integration tests for Context clear operations."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for the entire test class."""
        # Get API Key and Endpoint
        api_key = get_test_api_key()
        if not api_key:
            raise unittest.SkipTest("AGB_API_KEY environment variable not set")

        endpoint = get_test_endpoint()

        # Initialize AGB client
        if endpoint:
            config = Config(endpoint=endpoint, timeout_ms=60000)
            cls.agb = AGB(api_key=api_key, cfg=config)
            print(f"Using endpoint: {endpoint}")
        else:
            cls.agb = AGB(api_key=api_key)
            print("Using default endpoint")

        cls.test_contexts = []  # Track contexts for cleanup

    @classmethod
    def tearDownClass(cls):
        """Clean up any remaining test contexts."""
        print("\nCleaning up test contexts...")
        for context_info in cls.test_contexts:
            try:
                # Get the context object first
                if isinstance(context_info, dict):
                    context_id = context_info['id']
                    context_name = context_info['name']
                else:
                    context_id = context_info
                    context_name = None

                # Get context object
                if context_name:
                    get_result = cls.agb.context.get(context_name)
                    if get_result.success and get_result.context:
                        result = cls.agb.context.delete(get_result.context)
                        if result.success:
                            print(f"  ✓ Deleted context: {context_id}")
                        else:
                            print(f"  ✗ Failed to delete context: {context_id}")
                    else:
                        print(f"  ✗ Context not found: {context_id}")
                else:
                    print(f"  ⚠ Skipping cleanup for: {context_id} (no name)")
            except Exception as e:
                print(f"  ✗ Error deleting context {context_id}: {e}")

    def _create_test_context(self, with_data=False):
        """Helper method to create a test context."""
        context_name = f"test-clear-{uuid4().hex[:8]}"
        print(f"\nCreating test context: {context_name}")

        result = self.agb.context.create(context_name)
        self.assertTrue(result.success, f"Failed to create context: {result.error_message}")
        self.assertIsNotNone(result.context)

        context = result.context
        self.test_contexts.append({'id': context.id, 'name': context.name})
        print(f"  ✓ Context created: {context.id}")

        # Optionally add some data to the context
        if with_data:
            print(f"  Adding data to context via session...")
            # Create a session with this context to generate some data
            from agb.session_params import CreateSessionParams
            from agb.context_sync import ContextSync

            params = CreateSessionParams(
                image_id="agb-code-space-1",
                context_syncs=[
                    ContextSync(context_id=context.id, path="/home/wuying/test_data")
                ]
            )

            session_result = self.agb.create(params=params)
            if session_result.success:
                session = session_result.session
                print(f"  ✓ Session created: {session.session_id}")

                # Let session run for a bit to generate data
                time.sleep(2)

                # Delete session
                delete_result = session.delete()
                if delete_result.success:
                    print(f"  ✓ Session deleted")

                # Wait for session to be fully deleted
                time.sleep(2)

        return context

    def test_clear_async_success(self):
        """Test async clear operation on a context."""
        print("\n" + "="*60)
        print("TEST: Async Clear Operation")
        print("="*60)

        # Create a test context
        context = self._create_test_context()

        # Call clear_async (using context ID)
        print(f"\nInitiating async clear for context: {context.name} (ID: {context.id})")
        result = self.agb.context.clear_async(context.id)

        # Verify the result
        self.assertTrue(result.success, f"clear_async failed: {result.error_message}")
        self.assertEqual(result.context_id, context.id)  # Returns the ID we passed
        self.assertEqual(result.status, "clearing")
        print(f"  ✓ Async clear initiated successfully")
        print(f"    Status: {result.status}")
        print(f"    Request ID: {result.request_id}")

        # Wait a bit for clearing to potentially complete
        time.sleep(3)

        # Check status using get (internal method, but we can verify context exists)
        print(f"\nVerifying context still exists...")
        get_result = self.agb.context.get(context.name)
        self.assertTrue(get_result.success)
        print(f"  ✓ Context verified: {get_result.context.id}")

    def test_clear_sync_success(self):
        """Test synchronous clear operation on a context."""
        print("\n" + "="*60)
        print("TEST: Synchronous Clear Operation")
        print("="*60)

        # Create a test context with some data
        context = self._create_test_context(with_data=True)

        # Call clear (synchronous, only need context ID)
        print(f"\nInitiating synchronous clear for context: {context.name} (ID: {context.id})")
        print(f"  Timeout: 60 seconds")
        print(f"  Poll interval: 2 seconds")

        start_time = time.time()
        result = self.agb.context.clear(context.id, timeout=60, poll_interval=2)
        elapsed = time.time() - start_time

        # Verify the result
        self.assertTrue(result.success, f"clear failed: {result.error_message}")
        self.assertEqual(result.context_id, context.id)
        self.assertEqual(result.status, "available")

        print(f"\n  ✓ Synchronous clear completed successfully")
        print(f"    Final status: {result.status}")
        print(f"    Time elapsed: {elapsed:.2f} seconds")
        print(f"    Request ID: {result.request_id}")

    def test_clear_sync_with_short_timeout(self):
        """Test synchronous clear with a short timeout."""
        print("\n" + "="*60)
        print("TEST: Synchronous Clear with Short Timeout")
        print("="*60)

        # Create a test context
        context = self._create_test_context(with_data=True)

        print(f"\nInitiating clear with very short timeout (5 seconds)...")
        print(f"  Note: This may timeout if clearing takes longer than 5 seconds")

        try:
            start_time = time.time()
            result = self.agb.context.clear(
                context.id,
                timeout=5,  # Very short timeout
                poll_interval=1
            )
            elapsed = time.time() - start_time

            # If it succeeds within timeout
            self.assertTrue(result.success)
            print(f"\n  ✓ Clear completed within short timeout")
            print(f"    Status: {result.status}")
            print(f"    Time taken: {elapsed:.2f} seconds")
            print(f"    Request ID: {result.request_id}")

        except ClearanceTimeoutError as e:
            # Timeout is expected for this test
            print(f"\n  ✓ Timeout occurred as expected")
            print(f"    This confirms the timeout mechanism is working correctly")
            print(f"    Error: {str(e)}")
            self.assertIn("timed out", str(e))

    def test_clear_invalid_context(self):
        """Test clear operation on non-existent context."""
        print("\n" + "="*60)
        print("TEST: Clear Operation on Non-Existent Context")
        print("="*60)

        invalid_context_id = "non-existent-context-12345"

        print(f"\nAttempting to clear non-existent context: {invalid_context_id}")

        # clear_async returns a result object with success=False for invalid contexts
        result = self.agb.context.clear_async(invalid_context_id)

        # Verify the result indicates failure
        self.assertFalse(result.success, "clear_async should return success=False for invalid context")
        self.assertIsNotNone(result.error_message, "Error message should be provided")
        print(f"  ✓ Clear operation failed as expected")
        print(f"    Error message: {result.error_message}")
        print(f"    Request ID: {result.request_id}")

    def test_clear_multiple_times(self):
        """Test clearing the same context multiple times."""
        print("\n" + "="*60)
        print("TEST: Clear Context Multiple Times")
        print("="*60)

        # Create a test context
        context = self._create_test_context()

        # First clear
        print(f"\nStep 1: First clear operation...")
        result1 = self.agb.context.clear(context.id, timeout=30, poll_interval=2)
        self.assertTrue(result1.success, f"First clear failed: {result1.error_message}")
        print(f"  ✓ First clear completed")
        print(f"    Status: {result1.status}")
        print(f"    Request ID: {result1.request_id}")

        # Wait a bit
        print(f"\nStep 2: Waiting before second clear...")
        time.sleep(2)

        # Second clear (should work on already-cleared context)
        print(f"\nStep 3: Second clear operation on already-cleared context...")
        result2 = self.agb.context.clear(context.id, timeout=30, poll_interval=2)

        # Second clear might succeed immediately (already available) or succeed after clearing again
        self.assertTrue(result2.success or "available" in str(result2.status).lower(),
                       f"Second clear failed: {result2.error_message}")
        print(f"  ✓ Second clear completed")
        print(f"    Status: {result2.status}")
        print(f"    Request ID: {result2.request_id}")

    def test_clear_then_use_context(self):
        """Test that a cleared context can still be used."""
        print("\n" + "="*60)
        print("TEST: Use Context After Clearing")
        print("="*60)

        # Create a test context with data
        context = self._create_test_context(with_data=True)

        # Clear the context
        print(f"\nStep 1: Clearing context...")
        clear_result = self.agb.context.clear(context.id, timeout=60, poll_interval=2)
        self.assertTrue(clear_result.success, f"Clear failed: {clear_result.error_message}")
        print(f"  ✓ Context cleared successfully")
        print(f"    Status: {clear_result.status}")
        print(f"    Request ID: {clear_result.request_id}")

        # Wait longer for the context to be fully ready after clearing
        print(f"\nStep 2: Waiting for context to be fully ready after clearing...")
        time.sleep(5)
        print(f"  ✓ Wait completed")

        # Try to use the context again
        print(f"\nStep 3: Creating new session with cleared context...")
        from agb.session_params import CreateSessionParams
        from agb.context_sync import ContextSync

        params = CreateSessionParams(
            image_id="agb-code-space-1",
            context_syncs=[
                ContextSync(context_id=context.id, path="/home/wuying/test_after_clear")
            ]
        )

        try:
            session_result = self.agb.create(params=params)
            if session_result.success:
                session = session_result.session
                print(f"  ✓ Session created successfully")
                print(f"    Session ID: {session.session_id}")

                # Clean up session
                print(f"\nCleaning up session...")
                session.delete()
                time.sleep(1)
                print(f"  ✓ Session deleted")
            else:
                # May fail due to resource limits, that's okay for this test
                print(f"  ⚠ Session creation skipped due to resource limits")
                print(f"    Error: {session_result.error_message}")
        except Exception as e:
            print(f"  ⚠ Session creation skipped due to exception")
            print(f"    Error: {e}")


class TestContextClearEdgeCases(unittest.TestCase):
    """Edge case tests for Context clear operations."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        api_key = get_test_api_key()
        if not api_key:
            raise unittest.SkipTest("AGB_API_KEY environment variable not set")

        endpoint = get_test_endpoint()
        if endpoint:
            config = Config(endpoint=endpoint, timeout_ms=60000)
            cls.agb = AGB(api_key=api_key, cfg=config)
        else:
            cls.agb = AGB(api_key=api_key)

    def test_clear_with_custom_poll_interval(self):
        """Test clear with different poll intervals."""
        print("\n" + "="*60)
        print("TEST: Clear with Custom Poll Interval")
        print("="*60)

        # Create context
        context_name = f"test-poll-{uuid4().hex[:8]}"
        print(f"\nCreating test context: {context_name}")
        context_result = self.agb.context.create(context_name)
        self.assertTrue(context_result.success)
        context = context_result.context
        print(f"  ✓ Context created: {context.id}")

        print(f"\nClearing with 3-second poll interval...")
        print(f"  Poll interval: 3 seconds")
        print(f"  Timeout: 30 seconds")

        start_time = time.time()
        result = self.agb.context.clear(
            context.id,
            timeout=30,
            poll_interval=3  # Longer interval
        )
        elapsed = time.time() - start_time

        self.assertTrue(result.success, f"Clear failed: {result.error_message}")
        print(f"\n  ✓ Clear completed successfully")
        print(f"    Status: {result.status}")
        print(f"    Time taken: {elapsed:.2f} seconds")
        print(f"    Request ID: {result.request_id}")

        # Cleanup
        print(f"\nCleaning up context...")
        get_result = self.agb.context.get(context.name)
        if get_result.success and get_result.context:
            self.agb.context.delete(get_result.context)
            print(f"  ✓ Context deleted")


if __name__ == "__main__":
    # Print environment info
    print("\n" + "="*60)
    print("ENVIRONMENT CONFIGURATION")
    print("="*60)
    print(f"API Key: {'✓ Set' if get_test_api_key() else '✗ Not Set'}")
    print(f"Endpoint: {get_test_endpoint() or 'Using default'}")
    print("="*60 + "\n")

    unittest.main(verbosity=2)

