"""
Integration test to verify write behavior on deleted/released session.

This test verifies that calling write on a deleted session should return
success=False, but there may be a bug where it returns success=True.
"""

import os
import pytest
import time

from agb import AGB
from agb.session import Session
from agb.session_params import CreateSessionParams


class TestWriteFileOnDeletedSession:
    """Test write behavior on deleted/released sessions."""

    @pytest.fixture(scope="class")
    def agb_client(self):
        """Create AGB client for testing."""
        api_key = os.environ.get("AGB_API_KEY")
        if not api_key:
            pytest.skip("Skipping integration test: No API key available")
        return AGB(api_key=api_key)

    def test_write_on_deleted_session(self, agb_client):
        """
        Test that write should return success=False when called on a deleted session.

        Steps:
        1. Create a session
        2. Delete the session
        3. Attempt to call write on the deleted session
        4. Verify that success=False (this is the expected behavior)

        Note: This test may reveal a bug where success=True is returned incorrectly.
        """
        print("\n" + "=" * 60)
        print("Test: write on deleted session")
        print("=" * 60)

        # Step 1: Create a session
        print("\n1. Creating session...")
        params = CreateSessionParams(image_id="agb-code-space-2")
        create_result = agb_client.create(params)

        assert create_result.success, f"Failed to create session: {create_result.error_message}"
        session = create_result.session
        session_id = session.session_id
        print(f"   Session created with ID: {session_id}")
        print(f"   Request ID: {create_result.request_id}")

        try:
            # Step 2: Delete the session
            print("\n2. Deleting session...")
            delete_result = agb_client.delete(session)
            assert delete_result.success, f"Failed to delete session: {delete_result.error_message}"
            print(f"   Session deleted successfully")
            print(f"   Request ID: {delete_result.request_id}")

            # Wait a moment for session to be fully released
            print("\n3. Waiting for session to be fully released...")
            time.sleep(2)

            # Step 3: Attempt to call write on the deleted session
            print("\n4. Attempting to call write on deleted session...")
            test_path = "/tmp/test_deleted_session.txt"
            test_content = "This should fail because session is deleted"

            # Try using the original session object (which still has the session_id)
            write_result = session.file.write(test_path, test_content, mode="overwrite")

            # Step 4: Print and verify the result
            print("\n" + "=" * 60)
            print("Result of write on deleted session:")
            print("=" * 60)
            print(f"Success: {write_result.success}")
            print(f"Request ID: {write_result.request_id}")
            print(f"Error Message: {write_result.error_message}")
            print("=" * 60)

            # Expected behavior: success should be False
            if write_result.success:
                print("\n⚠️  BUG DETECTED: write returned success=True on deleted session!")
                print("   Expected: success=False")
                print("   Actual: success=True")
                print("\n   This indicates a potential bug where the API or SDK")
                print("   does not properly validate session status before executing write.")
            else:
                print("\n✅ CORRECT BEHAVIOR: write returned success=False on deleted session")

            # Assert the expected behavior
            assert not write_result.success, (
                f"write should return success=False on deleted session, "
                f"but got success=True. Error message: {write_result.error_message}"
            )

            # Also verify that an error message is present
            assert write_result.error_message, (
                "Error message should be present when write fails on deleted session"
            )

            print("\n✅ Test passed: write correctly returns success=False on deleted session")

        except AssertionError as e:
            # If the assertion fails, it means we found the bug
            print(f"\n❌ Test failed (bug confirmed): {e}")
            raise
        except Exception as e:
            # Other exceptions (like network errors) might also indicate the session is invalid
            print(f"\n⚠️  Exception occurred (may indicate session is invalid): {e}")
            print("   This could be a valid failure mode for a deleted session")
            # Re-raise to see the full traceback
            raise

    def test_write_on_deleted_session_with_recreated_session_object(self, agb_client):
        """
        Test write using a recreated Session object with the deleted session_id.

        This simulates the scenario where someone tries to reuse a session_id
        after the session has been deleted.
        """
        print("\n" + "=" * 60)
        print("Test: write with recreated Session object (deleted session_id)")
        print("=" * 60)

        # Step 1: Create a session
        print("\n1. Creating session...")
        params = CreateSessionParams(image_id="agb-code-space-2")
        create_result = agb_client.create(params)

        assert create_result.success, f"Failed to create session: {create_result.error_message}"
        session = create_result.session
        session_id = session.session_id
        print(f"   Session created with ID: {session_id}")

        try:
            # Step 2: Delete the session
            print("\n2. Deleting session...")
            delete_result = agb_client.delete(session)
            assert delete_result.success, f"Failed to delete session: {delete_result.error_message}"
            print(f"   Session deleted successfully")

            # Wait for session to be fully released
            time.sleep(2)

            # Step 3: Recreate a Session object with the deleted session_id
            print("\n3. Recreating Session object with deleted session_id...")
            stale_session = Session(agb_client, session_id)
            print(f"   Created Session object with session_id: {stale_session.session_id}")

            # Step 4: Attempt to call write
            print("\n4. Attempting to call write on recreated Session object...")
            test_path = "/tmp/test_recreated_session.txt"
            test_content = "This should fail because session_id is invalid"

            write_result = stale_session.file.write(test_path, test_content, mode="overwrite")

            # Step 5: Print and verify the result
            print("\n" + "=" * 60)
            print("Result of write on recreated Session (deleted session_id):")
            print("=" * 60)
            print(f"Success: {write_result.success}")
            print(f"Request ID: {write_result.request_id}")
            print(f"Error Message: {write_result.error_message}")
            print("=" * 60)

            # Expected behavior: success should be False
            if write_result.success:
                print("\n⚠️  BUG DETECTED: write returned success=True with deleted session_id!")
                print("   Expected: success=False")
                print("   Actual: success=True")
            else:
                print("\n✅ CORRECT BEHAVIOR: write returned success=False with deleted session_id")

            # Assert the expected behavior
            assert not write_result.success, (
                f"write should return success=False when using deleted session_id, "
                f"but got success=True. Error message: {write_result.error_message}"
            )

            assert write_result.error_message, (
                "Error message should be present when write fails with deleted session_id"
            )

            print("\n✅ Test passed: write correctly returns success=False with deleted session_id")

        except AssertionError as e:
            print(f"\n❌ Test failed (bug confirmed): {e}")
            raise
        except Exception as e:
            print(f"\n⚠️  Exception occurred: {e}")
            raise
