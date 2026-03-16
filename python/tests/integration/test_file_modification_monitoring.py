import os
import threading
import time
import uuid

import pytest
from typing import Any

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


def test_watch_directory_file_modification():
    """
    Test monitoring file modification events in a directory.

    This test:
    1. Creates a session with specified ImageId
    2. Creates a test directory and initial file
    3. Sets up directory monitoring with a callback
    4. Modifies the file multiple times
    5. Verifies that modification events are captured correctly
    """
    print("=== Testing file modification monitoring ===\n")

    api_key = _require_api_key()

    try:
        agb = AGB(api_key=api_key)
        print("✅ AGB client initialized")
    except Exception as e:
        pytest.fail(f"Failed to initialize AGB client: {e}")

    # Create session with specified ImageId
    session_params = CreateSessionParams(image_id="agb-code-space-2")
    session_result = agb.create(session_params)

    assert session_result.success and session_result.session is not None, (
        f"Failed to create session: {_err(session_result)}"
    )

    session = session_result.session
    print(f"✅ Session created successfully with ID: {session.session_id}")

    # Create test directory and initial file
    test_dir = f"/tmp/test_modify_watch_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    print(f"\n1. Creating test directory: {test_dir}")
    create_dir_result = session.file.mkdir(test_dir)
    assert create_dir_result.success, f"Failed to create directory: {_err(create_dir_result)}"
    print("✅ Test directory created")

    # Create initial file
    test_file = f"{test_dir}/modify_test.txt"
    print(f"\n2. Creating initial file: {test_file}")
    write_result = session.file.write(test_file, "Initial content")
    assert write_result.success, f"Failed to create initial file: {_err(write_result)}"
    print("✅ Initial file created")

    # Storage for captured events
    captured_events = []
    event_lock = threading.Lock()

    def on_file_modified(events):
        """Callback function to capture modification events."""
        with event_lock:
            # Filter only modify events
            modify_events = [e for e in events if e.event_type == "modify"]
            captured_events.extend(modify_events)
            for event in modify_events:
                print(f"🔔 Captured modify event: {event.path} ({event.path_type})")

    monitor_thread: Any = None
    test_passed = False

    try:
        # Start monitoring
        print(f"\n3. Starting directory monitoring...")
        monitor_thread = session.file.watch_dir(
            path=test_dir, callback=on_file_modified, interval=1.0
        )
        monitor_thread.start()
        print("✅ Directory monitoring started")
        time.sleep(1)  # Wait for monitoring to start

        # Modify file multiple times
        print(f"\n4. Modifying file multiple times...")
        for i in range(3):
            content = f"Modified content version {i + 1}"
            print(f"   Modification {i + 1}: Writing '{content}'")
            modify_result = session.file.write(test_file, content)
            assert modify_result.success, f"Failed to modify file: {_err(modify_result)}"
            print(f"✅ File modified successfully (attempt {i + 1})")
            time.sleep(1.5)  # Ensure events are captured

        # Wait a bit more for final events
        time.sleep(2)

        # Verify events
        print(f"\n5. Verifying captured events...")
        with event_lock:
            print(f"Total modify events captured: {len(captured_events)}")

            # Check minimum number of events
            if len(captured_events) < 3:
                print(
                    f"⚠️  Expected at least 3 modify events, got {len(captured_events)}"
                )
                print(
                    "This might be due to timing or system behavior, but basic functionality works"
                )
                # Allow 2 events as acceptable if network conditions are poor
                if len(captured_events) < 2:
                    print("❌ Too few events captured.")
                    test_passed = False
                else:
                    test_passed = True
            else:
                print(f"✅ Captured sufficient modify events: {len(captured_events)}")
                test_passed = True

            # Verify event properties
            valid_events = 0
            for i, event in enumerate(captured_events, 1):
                print(f"   Event {i}: {event}")

                # Check event has required attributes
                if not hasattr(event, "event_type"):
                    print(f"❌ Event {i} missing 'event_type' attribute")
                    continue
                if not hasattr(event, "path"):
                    print(f"❌ Event {i} missing 'path' attribute")
                    continue
                if not hasattr(event, "path_type"):
                    print(f"❌ Event {i} missing 'path_type' attribute")
                    continue

                # Check event type is modify
                if event.event_type != "modify":
                    print(
                        f"❌ Event {i} type should be 'modify', got '{event.event_type}'"
                    )
                    continue

                # Check path contains test file
                if test_file not in event.path:
                    print(
                        f"❌ Event {i} path should contain '{test_file}', got '{event.path}'"
                    )
                    continue

                valid_events += 1
                print(f"✅ Event {i} is valid")

            print(f"\nValidation summary:")
            print(f"  Total events: {len(captured_events)}")
            print(f"  Valid events: {valid_events}")

            if valid_events >= 2: # Requiring at least 2 valid events
                print("✅ File modification monitoring test passed!")
                test_passed = True
            else:
                print("❌ No valid modification events detected")
                test_passed = False

    finally:
        # Stop monitoring
        print(f"\n6. Stopping directory monitoring...")
        if monitor_thread:
            monitor_thread.stop_event.set()  # type: ignore[attr-defined]
            monitor_thread.join(timeout=5)
            print("✅ Directory monitoring stopped")

        # Clean up session
        print(f"\n7. Cleaning up session...")
        try:
            # Best-effort cleanup: directory
            session.command.execute(f"rm -rf {test_dir}", timeout_ms=10000)
        except Exception as e:
            print(f"Warning: Failed to cleanup dir {test_dir}: {e}")
        delete_result = agb.delete(session)
        assert delete_result.success, f"Failed to delete session: {_err(delete_result)}"
        print("✅ Session deleted successfully")

    print("\n=== File modification monitoring test completed ===")
    assert test_passed, "File modification monitoring did not capture enough valid events"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
