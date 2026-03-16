import os
import time
import traceback

import pytest

from agb import AGB
from agb.session_params import CreateSessionParams


def _require_api_key() -> str:
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        pytest.skip("AGB_API_KEY environment variable not set")
    return api_key


def _err(result) -> str:
    return (
        f"success={getattr(result, 'success', None)!r}, "
        f"error_message={getattr(result, 'error_message', None)!r}, "
        f"request_id={getattr(result, 'request_id', None)!r}"
    )


def test_get_file_change():
    """Test get_file_change (_get_file_change) detects modifications under a directory."""
    api_key = _require_api_key()

    try:
        agb = AGB(api_key=api_key)
    except Exception as e:
        pytest.fail(f"Failed to initialize AGB client: {e}")

    session = None
    test_dir = f"/tmp/test_file_change_{int(time.time())}"
    test_file = f"{test_dir}/test_file.txt"

    try:
        session_params = CreateSessionParams(image_id="agb-code-space-2")
        session_result = agb.create(session_params)
        assert session_result.success and session_result.session is not None, (
            f"Failed to create session: {_err(session_result)}"
        )
        session = session_result.session

        # Create test directory
        create_dir_result = session.file.mkdir(test_dir)
        assert create_dir_result.success, f"create_directory failed: {_err(create_dir_result)}"

        # Write initial file content
        initial_content = "initial\nline2\n"
        write_result = session.file.write(test_file, initial_content)
        assert write_result.success, f"write(initial) failed: {_err(write_result)}"

        # Get initial state
        first_change_result = session.file._get_file_change(test_dir)
        assert first_change_result.success, f"_get_file_change(initial) failed: {_err(first_change_result)}"

        # Modify the file
        modified_content = "modified\nline2-changed\nline3\n"
        modify_result = session.file.write(test_file, modified_content)
        assert modify_result.success, f"write(modify) failed: {_err(modify_result)}"

        # Get changes
        second_change_result = session.file._get_file_change(test_dir)
        assert second_change_result.success, f"_get_file_change(after) failed: {_err(second_change_result)}"

        assert second_change_result.has_changes(), "Expected has_changes() to be True after file modification"
        assert len(second_change_result.events) > 0, "Expected at least one change event"

        # Stronger check: modified file should appear in modified list (or events)
        modified_files = second_change_result.get_modified_files()
        if modified_files:
            assert any(test_file in p for p in modified_files), f"Expected {test_file} in modified_files={modified_files!r}"
        else:
            assert any(test_file in getattr(e, "path", "") for e in second_change_result.events), (
                f"Expected an event path containing {test_file}"
            )

    except AssertionError:
        raise
    except Exception as e:
        traceback.print_exc()
        pytest.fail(f"Unexpected error during test: {e}")
    finally:
        # Best-effort cleanup in the remote session
        if session is not None:
            try:
                session.command.execute(f"rm -rf {test_dir}", timeout_ms=10000)
            except Exception as e:
                print(f"Warning: failed to cleanup remote dir {test_dir}: {e}")
            try:
                delete_result = agb.delete(session)
                assert delete_result.success, f"Failed to delete session: {_err(delete_result)}"
            except Exception as e:
                # Don't mask the original failure if any
                print(f"Warning: failed to delete session in teardown: {e}")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
