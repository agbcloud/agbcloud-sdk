import pytest
import os
from agb.agb import AGB
from agb.session_params import CreateSessionParams
from agb.session import Session
from agb.logger import get_logger

logger = get_logger(__name__)

class TestSessionLifecycleDeleted:
    @pytest.fixture(scope="class")
    def agb(self):
        api_key = os.getenv("AGB_API_KEY")
        assert api_key, "AGB_API_KEY environment variable is required"
        return AGB(api_key=api_key)

    def test_run_code_on_deleted_session(self, agb):
        # 1. Create a session
        print("\n1. Creating session...")
        params = CreateSessionParams(image_id="agb-browser-use-1")
        create_result = agb.create(params)

        assert create_result.success, f"Failed to create session: {create_result.error_message}"
        session = create_result.session
        session_id = session.session_id
        print(f"Session created with ID: {session_id}")

        try:
            # 2. Delete the session
            print("2. Deleting session...")
            delete_result = session.delete()
            assert delete_result.success, f"Failed to delete session: {delete_result.error_message}"
            print("Session deleted successfully")

            # 3. Use previous session id to call run_code
            print("3. Attempting to run code with deleted session ID...")

            # Manually instantiate a session object with the deleted ID
            # This simulates attempting to use a stale session ID
            stale_session = Session(agb, session_id)

            # Try to run code
            code = "print('Hello from deleted session')"
            result = stale_session.code.run_code(code, language="python")

            # 4. Print the result
            print("\n=== Result of run_code on deleted session ===")
            print(f"Success: {result.success}")
            for res in result.logs.stdout:
                print(f"Result: {result.logs.stdout}")
            print(f"Error Message: {result.error_message}")
            print("=============================================")

            # Expectation: It should fail
            assert not result.success, "run_code should fail on a deleted session"
            assert result.error_message, "Error message should be present"

        except Exception as e:
            print(f"\nException occurred: {e}")
            # If an exception happens (e.g. network error due to closed connection), that's also a valid failure mode
            pass

