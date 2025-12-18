"""Async integration tests for Session pause and resume operations."""
import os
import sys
import asyncio
import unittest
from uuid import uuid4
from dotenv import load_dotenv

from agb import AGB, CreateSessionParams
from agb.config import Config
from agb.model.response import SessionPauseResult, SessionResumeResult
from agb.exceptions import SessionError


def get_test_api_key():
    """Get API key for testing."""
    return os.environ.get("AGB_API_KEY")


def get_test_endpoint():
    """Get endpoint for testing."""
    return os.environ.get("AGB_ENDPOINT")


class TestSessionPauseResumeAsync(unittest.IsolatedAsyncioTestCase):
    """Async integration tests for Session pause and resume operations."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for the entire test class."""
        # Load environment variables from .env file
        load_dotenv()

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

    async def asyncSetUp(self):
        """Set up test fixtures for each test method."""
        self.test_sessions = []  # Track sessions for cleanup in each test

    async def asyncTearDown(self):
        """Clean up test sessions after each test method."""
        print("\nCleaning up test sessions for this test...")
        for session in self.test_sessions:
            try:
                # Delete session (synchronous operation)
                result = self.agb.delete(session)
                if result.success:
                    print(f"  ✓ Deleted session: {session.session_id}")
                else:
                    print(f"  ✗ Failed to delete session: {session.session_id}")
            except Exception as e:
                print(f"  ✗ Error deleting session {session.session_id}: {e}")
        # Clear the list for next test
        self.test_sessions = []

    def _create_test_session(self):
        """Helper method to create a test session (synchronous)."""
        session_name = f"test-async-pause-resume-{uuid4().hex[:8]}"
        print(f"\nCreating test session: {session_name}")

        # Create session with image_id as requested
        params = CreateSessionParams(
            image_id="agb-computer-use-ubuntu-2204",
            labels={"project": "agb-demo", "environment": "testing", "test": session_name},
        )
        result = self.agb.create(params)
        self.assertTrue(result.success, f"Failed to create session: {result.error_message}")
        self.assertIsNotNone(result.session)

        session = result.session
        self.test_sessions.append(session)
        print(f"  ✓ Session created: {session.session_id}")

        return session

    async def test_async_pause_and_resume_session_success(self):
        """Test successful async pause and resume operations on a session."""
        print("\n" + "="*60)
        print("TEST: Async Pause and Resume Session Success")
        print("="*60)

        # Create a test session
        session = self._create_test_session()

        # Verify session is initially in RUNNING state
        print(f"\nStep 1: Verifying session is initially RUNNING...")
        get_result = self.agb.get_session(session.session_id)
        self.assertTrue(get_result.success, f"Failed to get session: {get_result.error_message}")
        if hasattr(get_result.data, 'status') and get_result.data.status:
            self.assertIn(get_result.data.status, ["RUNNING"])
        else:
            # If status is not available, just proceed with pause
            print(f"  ✓ Session exists: {session.session_id}")

        # Pause the session asynchronously
        print(f"\nStep 2: Pausing session asynchronously...")
        pause_result = await self.agb.pause_async(session)

        # Verify pause result
        self.assertIsInstance(pause_result, SessionPauseResult)
        self.assertTrue(pause_result.success, f"Pause failed: {pause_result.error_message}")
        print(f"  ✓ Session pause initiated successfully")
        print(f"    Request ID: {pause_result.request_id}")

        # Wait a bit for pause to complete
        print(f"\nStep 3: Waiting for session to pause...")
        await asyncio.sleep(2)

        # Check session status after pause
        get_result = self.agb.get_session(session.session_id)
        self.assertTrue(get_result.success, f"Failed to get session: {get_result.error_message}")
        # Session should be PAUSED or still PAUSING
        print(f"  ✓ Session status after pause: {get_result.data.status if hasattr(get_result.data, 'status') and get_result.data.status else 'Status not available'}")

        # Resume the session asynchronously
        print(f"\nStep 4: Resuming session asynchronously...")
        resume_result = await self.agb.resume_async(session, timeout=120, poll_interval=3)

        # Verify resume result
        self.assertIsInstance(resume_result, SessionResumeResult)
        self.assertTrue(resume_result.success, f"Resume failed: {resume_result.error_message}")
        print(f"  ✓ Session resumed successfully")
        print(f"    Request ID: {resume_result.request_id}")

        # Verify session is RUNNING after resume
        get_result = self.agb.get_session(session.session_id)
        self.assertTrue(get_result.success, f"Failed to get session: {get_result.error_message}")
        if hasattr(get_result.data, 'status') and get_result.data.status:
            self.assertEqual(get_result.data.status, "RUNNING")
        print(f"  ✓ Session is RUNNING after resume: {session.session_id}")

    async def test_async_pause_nonexistent_session(self):
        """Test async pause operation on non-existent session."""
        print("\n" + "="*60)
        print("TEST: Async Pause Non-Existent Session")
        print("="*60)

        # Create a mock session object with invalid session ID
        from agb.session import Session
        invalid_session = Session(self.agb, "non-existent-session-12345")

        print(f"\nAttempting to async pause non-existent session: {invalid_session.session_id}")

        # This should return a failed SessionPauseResult
        pause_result = await self.agb.pause_async(invalid_session)

        # Verify that the result is a SessionPauseResult and indicates failure
        self.assertIsInstance(pause_result, SessionPauseResult)
        self.assertFalse(pause_result.success)
        print(f"  ✓ Returned SessionPauseResult with success=False as expected")
        print(f"    Error: {pause_result.error_message}")
        # Check if the error message contains session-related information
        self.assertTrue(pause_result.error_message is not None and len(pause_result.error_message) > 0)

    async def test_async_resume_nonexistent_session(self):
        """Test async resume operation on non-existent session."""
        print("\n" + "="*60)
        print("TEST: Async Resume Non-Existent Session")
        print("="*60)

        # Create a mock session object with invalid session ID
        from agb.session import Session
        invalid_session = Session(self.agb, "non-existent-session-12345")

        print(f"\nAttempting to async resume non-existent session: {invalid_session.session_id}")

        # This should return a failed SessionResumeResult
        resume_result = await self.agb.resume_async(invalid_session)

        # Verify that the result is a SessionResumeResult and indicates failure
        self.assertIsInstance(resume_result, SessionResumeResult)
        self.assertFalse(resume_result.success)
        print(f"  ✓ Returned SessionResumeResult with success=False as expected")
        print(f"    Error: {resume_result.error_message}")
        # Check if the error message contains session-related information
        self.assertTrue(resume_result.error_message is not None and len(resume_result.error_message) > 0)

    async def test_async_pause_with_custom_parameters(self):
        """Test async pause operation with custom timeout and poll interval."""
        print("\n" + "="*60)
        print("TEST: Async Pause with Custom Parameters")
        print("="*60)

        # Create a test session
        session = self._create_test_session()

        # Pause with custom parameters using async method
        print(f"\nPausing session asynchronously with custom parameters...")
        pause_result = await self.agb.pause_async(session, timeout=300, poll_interval=3.0)

        self.assertIsInstance(pause_result, SessionPauseResult)
        self.assertTrue(pause_result.success, f"Pause with custom params failed: {pause_result.error_message}")
        print(f"  ✓ Async session pause with custom parameters successful")
        print(f"    Request ID: {pause_result.request_id}")

        # Wait for pause to complete
        await asyncio.sleep(2)

        # Verify session is in appropriate state after pause
        get_result = self.agb.get_session(session.session_id)
        self.assertTrue(get_result.success)
        print(f"  ✓ Session status: {get_result.data.status if hasattr(get_result.data, 'status') and get_result.data.status else 'Status not available'}")

    async def test_async_resume_with_custom_parameters(self):
        """Test async resume operation with custom timeout and poll interval."""
        print("\n" + "="*60)
        print("TEST: Async Resume with Custom Parameters")
        print("="*60)

        # Create a test session
        session = self._create_test_session()

        # First pause the session
        print(f"\nStep 1: Pausing session first...")
        pause_result = await self.agb.pause_async(session)
        self.assertTrue(pause_result.success)
        print(f"  ✓ Session paused successfully")

        # Wait for pause to complete
        await asyncio.sleep(2)

        # Resume with custom parameters using async method
        print(f"\nStep 2: Resuming session asynchronously with custom parameters...")
        resume_result = await self.agb.resume_async(session, timeout=300, poll_interval=3.0)

        self.assertIsInstance(resume_result, SessionResumeResult)
        self.assertTrue(resume_result.success, f"Resume with custom params failed: {resume_result.error_message}")
        print(f"  ✓ Async session resume with custom parameters successful")
        print(f"    Request ID: {resume_result.request_id}")

        # Verify session after resume
        get_result = self.agb.get_session(session.session_id)
        self.assertTrue(get_result.success)
        if hasattr(get_result.data, 'status') and get_result.data.status:
            self.assertEqual(get_result.data.status, "RUNNING")
        print(f"  ✓ Session status after resume: {get_result.data.status if hasattr(get_result.data, 'status') and get_result.data.status else 'Status not available'}")

    async def test_async_multiple_pause_resume_cycles(self):
        """Test multiple async pause and resume cycles on the same session."""
        print("\n" + "="*60)
        print("TEST: Multiple Async Pause and Resume Cycles")
        print("="*60)

        # Create a test session
        session = self._create_test_session()

        # Perform multiple pause/resume cycles
        num_cycles = 2
        for i in range(num_cycles):
            print(f"\n--- Cycle {i+1}/{num_cycles} ---")

            # Pause
            print(f"  Pausing session asynchronously...")
            pause_result = await self.agb.pause_async(session, timeout=300, poll_interval=3)
            self.assertTrue(pause_result.success, f"Cycle {i+1}: Pause failed: {pause_result.error_message}")
            print(f"    ✓ Pause successful (Request ID: {pause_result.request_id})")

            # Wait
            await asyncio.sleep(2)

            # Resume
            print(f"  Resuming session asynchronously...")
            resume_result = await self.agb.resume_async(session, timeout=300, poll_interval=3)
            self.assertTrue(resume_result.success, f"Cycle {i+1}: Resume failed: {resume_result.error_message}")
            print(f"    ✓ Resume successful (Request ID: {resume_result.request_id})")

            # Wait before next cycle
            if i < num_cycles - 1:
                await asyncio.sleep(1)

        print(f"\n  ✓ Completed {num_cycles} async pause/resume cycles successfully")

    async def test_async_concurrent_operations(self):
        """Test concurrent async pause operations on different sessions."""
        print("\n" + "="*60)
        print("TEST: Concurrent Async Pause Operations")
        print("="*60)

        # Create multiple test sessions
        num_sessions = 2
        sessions = []
        print(f"\nCreating {num_sessions} test sessions...")
        for i in range(num_sessions):
            session = self._create_test_session()
            sessions.append(session)
            await asyncio.sleep(0.5)  # Small delay between creations

        # Pause all sessions concurrently
        print(f"\nPausing {num_sessions} sessions concurrently...")
        pause_tasks = [
            self.agb.pause_async(session, timeout=300, poll_interval=3)
            for session in sessions
        ]
        pause_results = await asyncio.gather(*pause_tasks, return_exceptions=True)

        # Verify all pause operations
        for i, result in enumerate(pause_results):
            if isinstance(result, Exception):
                print(f"  ✗ Session {i+1} pause failed with exception: {result}")
                self.fail(f"Session {i+1} pause raised exception: {result}")
            else:
                self.assertIsInstance(result, SessionPauseResult)
                self.assertTrue(result.success, f"Session {i+1} pause failed: {result.error_message}")
                print(f"  ✓ Session {i+1} paused successfully (Request ID: {result.request_id})")

        # Wait for all pauses to complete
        await asyncio.sleep(3)

        # Resume all sessions concurrently
        print(f"\nResuming {num_sessions} sessions concurrently...")
        resume_tasks = [
            self.agb.resume_async(session, timeout=300, poll_interval=3)
            for session in sessions
        ]
        resume_results = await asyncio.gather(*resume_tasks, return_exceptions=True)

        # Verify all resume operations
        for i, result in enumerate(resume_results):
            if isinstance(result, Exception):
                print(f"  ✗ Session {i+1} resume failed with exception: {result}")
                self.fail(f"Session {i+1} resume raised exception: {result}")
            else:
                self.assertIsInstance(result, SessionResumeResult)
                self.assertTrue(result.success, f"Session {i+1} resume failed: {result.error_message}")
                print(f"  ✓ Session {i+1} resumed successfully (Request ID: {result.request_id})")

        print(f"\n  ✓ All concurrent operations completed successfully")


if __name__ == "__main__":
    # Print environment info
    print("\n" + "="*60)
    print("ENVIRONMENT CONFIGURATION")
    print("="*60)
    load_dotenv()
    print(f"API Key: {'✓ Set' if get_test_api_key() else '✗ Not Set'}")
    print(f"Endpoint: {get_test_endpoint() or 'Using default'}")
    print("="*60 + "\n")

    unittest.main(verbosity=2)
