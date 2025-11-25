import os

from agb import AGB
from agb.session_params import CreateSessionParams


def get_api_key():
    """Get API Key from environment variables"""
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        raise ValueError(
            "AGB_API_KEY environment variable not set. Please set the environment variable."
        )
    return api_key


def test_get_file_change():
    """
    Test the get_file_change functionality by:
    1. Creating a session with specified ImageId
    2. Writing a file to /tmp/test/ directory
    3. Calling get_file_change to get initial state
    4. Modifying the file
    5. Calling get_file_change again to observe changes
    """
    # Initialize AGB client
    api_key = get_api_key()
    agb = AGB(api_key=api_key)

    # Create session with specified ImageId
    session_params = CreateSessionParams(image_id="agb-code-space-2")
    session_result = agb.create(session_params)

    if not session_result.success:
        print(f"Failed to create session: {session_result.error_message}")
        return

    session = session_result.session
    print(f"Session created successfully with ID: {session.session_id}")

    try:
        # Create the test directory
        create_dir_result = session.file_system.create_directory("/tmp/test")
        print(f"Create directory result: {create_dir_result.success}")

        # Write initial file content
        initial_content = (
            "This is the initial content of the test file.\nLine 2 of initial content."
        )
        write_result = session.file_system.write_file(
            "/tmp/test/test_file.txt", initial_content
        )
        print(f"Write file result: {write_result.success}")
        assert (
            write_result.success
        ), f"Failed to write file: {write_result.error_message}"

        # Call _get_file_change for the first time (initial state)
        first_change_result = session.file_system._get_file_change("/tmp/test")
        print(f"First get_file_change result: {first_change_result}")
        print(f"First change success: {first_change_result.success}")
        print(f"First change events count: {len(first_change_result.events)}")
        print(f"First change has changes: {first_change_result.has_changes()}")
        if first_change_result.events:
            print("First change events:")
            for event in first_change_result.events:
                print(f"  - {event}")
        print(f"First change raw data: {first_change_result.raw_data}")

        # Modify the file
        modified_content = "This is the MODIFIED content of the test file.\nLine 2 has been changed.\nAdded a new line 3."
        modify_result = session.file_system.write_file(
            "/tmp/test/test_file.txt", modified_content
        )
        print(f"Modify file result: {modify_result.success}")
        assert (
            modify_result.success
        ), f"Failed to modify file: {modify_result.error_message}"

        # Call _get_file_change for the second time (after modification)
        second_change_result = session.file_system._get_file_change("/tmp/test")
        print(f"Second get_file_change result: {second_change_result}")
        print(f"Second change success: {second_change_result.success}")
        print(f"Second change events count: {len(second_change_result.events)}")
        print(f"Second change has changes: {second_change_result.has_changes()}")
        if second_change_result.events:
            print("Second change events:")
            for event in second_change_result.events:
                print(f"  - {event}")
        print(f"Second change raw data: {second_change_result.raw_data}")

        # Analyze specific change types
        modified_files = second_change_result.get_modified_files()
        created_files = second_change_result.get_created_files()
        deleted_files = second_change_result.get_deleted_files()
        print(f"Modified files: {modified_files}")
        print(f"Created files: {created_files}")
        print(f"Deleted files: {deleted_files}")

        # Compare the results
        print("\n=== COMPARISON ===")
        print("First call result:")
        print(f"  Events: {len(first_change_result.events)}")
        print(f"  Has changes: {first_change_result.has_changes()}")
        print("\nSecond call result:")
        print(f"  Events: {len(second_change_result.events)}")
        print(f"  Has changes: {second_change_result.has_changes()}")
        print(
            f"  Event details: {[str(event) for event in second_change_result.events]}"
        )

    finally:
        # Clean up
        delete_result = agb.delete(session)
        if delete_result.success:
            print("Session deleted successfully")
        else:
            print(f"Failed to delete session: {delete_result.error_message}")


if __name__ == "__main__":
    test_get_file_change()
