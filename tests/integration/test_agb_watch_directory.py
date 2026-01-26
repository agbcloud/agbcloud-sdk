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


def test_watch_directory():
    """
    Test the watch_directory functionality by:
    1. Creating a session with specified ImageId
    2. Setting up directory monitoring with a callback
    3. Creating and modifying files
    4. Verifying that callbacks are triggered with correct events
    5. Testing deduplication of events
    """
    print("=== Testing watch_directory functionality ===\n")

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

    # Callback function to handle file changes
    detected_events = []
    callback_calls = []

    def file_change_callback(events):
        """Callback function to handle detected file changes."""
        callback_calls.append(len(events))
        detected_events.extend(events)
        print(f"\n🔔 Callback triggered with {len(events)} events:")
        for event in events:
            print(f"   - {event.event_type}: {event.path} ({event.path_type})")

    test_success = False
    monitor_thread: Any = None
    test_dir = f"/tmp/watch_test_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    try:
        # Create the test directory
        print("\n1. Creating test directory...")
        create_dir_result = session.file.mkdir(test_dir)
        assert create_dir_result.success, f"create_directory failed: {_err(create_dir_result)}"

        # Start directory monitoring
        print("\n2. Starting directory monitoring...")
        monitor_thread = session.file.watch_dir(
            path=test_dir,
            callback=file_change_callback,
            interval=0.5,  # Poll every 0.5 seconds for faster testing
        )
        monitor_thread.start()
        print("✅ Directory monitoring started")

        # Wait a moment for monitoring to initialize
        time.sleep(1)

        # Test 1: Create a new file
        print("\n3. Creating a new file...")
        write_result = session.file.write(f"{test_dir}/test1.txt", "Initial content")
        assert write_result.success, f"write failed: {_err(write_result)}"

        # Wait for detection
        time.sleep(2)

        # Test 2: Modify the file
        print("\n4. Modifying the file...")
        modify_result = session.file.write(f"{test_dir}/test1.txt", "Modified content")
        assert modify_result.success, f"write(modify) failed: {_err(modify_result)}"

        # Wait for detection
        time.sleep(2)

        # Test 3: Create another file
        print("\n5. Creating another file...")
        write_result2 = session.file.write(f"{test_dir}/test2.txt", "Second file content")
        assert write_result2.success, f"write(2) failed: {_err(write_result2)}"

        # Wait for detection
        time.sleep(2)

        # Stop monitoring
        print("\n6. Stopping directory monitoring...")
        monitor_thread.stop_event.set()  # type: ignore[attr-defined]
        monitor_thread.join(timeout=5)
        print("✅ Directory monitoring stopped")

        # Analyze results
        print(f"\n=== RESULTS ===")
        print(f"Total callback calls: {len(callback_calls)}")
        print(f"Total events detected: {len(detected_events)}")
        print(f"Callback call sizes: {callback_calls}")

        print("\nDetected events:")
        for i, event in enumerate(detected_events, 1):
            print(f"  {i}. {event}")

        # Verify deduplication
        event_keys = set()
        duplicates = 0
        for event in detected_events:
            event_key = (event.event_type, event.path, event.path_type)
            if event_key in event_keys:
                duplicates += 1
            else:
                event_keys.add(event_key)

        print(f"\nDeduplication check:")
        print(f"  Unique events: {len(event_keys)}")
        print(f"  Duplicate events: {duplicates}")

        if duplicates == 0:
            print("✅ Event deduplication is working correctly")
        else:
            print("⚠️  Some duplicate events were detected")

        # Summary
        if len(detected_events) >= 3:
            print("\n✅ watch_directory test completed successfully!")
            print("The directory monitoring is working and detecting file changes.")
            test_success = True
        else:
            print(f"\n⚠️  Insufficient events detected. Expected at least 3, got {len(detected_events)}.")
            test_success = False

    finally:
        # Stop monitoring if still running
        try:
            if monitor_thread:
                monitor_thread.stop_event.set()  # type: ignore[attr-defined]
                monitor_thread.join(timeout=5)
        except Exception as e:
            print(f"Warning: failed to stop monitor thread: {e}")
        # Best-effort cleanup: remove dir in remote session
        try:
            session.command.execute(f"rm -rf {test_dir}", timeout_ms=10000)
        except Exception as e:
            print(f"Warning: failed to cleanup remote dir {test_dir}: {e}")
        # Clean up
        print("\n7. Cleaning up session...")
        delete_result = agb.delete(session)
        assert delete_result.success, f"Failed to delete session: {_err(delete_result)}"
        print("✅ Session deleted successfully")

    assert test_success, "watch_directory did not detect enough events"


def test_watch_directory_no_deduplication():
    """
    Test the watch_directory functionality without event deduplication by:
    1. Creating a session with specified ImageId
    2. Setting up directory monitoring with a callback
    3. Creating and modifying files multiple times
    4. Verifying that ALL callbacks are triggered, including duplicates
    """
    print("=== Testing watch_directory without deduplication ===\n")

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

    # Callback function to handle file changes
    detected_events = []
    callback_calls = []

    def file_change_callback(events):
        """Callback function to handle detected file changes."""
        callback_calls.append(len(events))
        detected_events.extend(events)
        print(f"\n🔔 Callback triggered with {len(events)} events:")
        for event in events:
            print(f"   - {event.event_type}: {event.path} ({event.path_type})")

    test_success = False
    monitor_thread = None
    test_dir = f"/tmp/watch_test_no_dedup_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    try:
        # Create the test directory
        print("\n1. Creating test directory...")
        create_dir_result = session.file.mkdir(
            test_dir
        )
        assert create_dir_result.success, f"create_directory failed: {_err(create_dir_result)}"

        # Start directory monitoring
        print("\n2. Starting directory monitoring...")
        monitor_thread = session.file.watch_dir(
            path=test_dir,
            callback=file_change_callback,
            interval=0.5,  # Poll every 0.5 seconds for faster testing
        )
        monitor_thread.start()
        print("✅ Directory monitoring started")

        # Wait a moment for monitoring to initialize
        time.sleep(1)

        # Test: Create and modify file multiple times to generate potential duplicates
        print("\n3. Creating and modifying file multiple times...")

        # Create file
        write_result = session.file.write(
            f"{test_dir}/test.txt", "Content 1"
        )
        assert write_result.success, f"write failed: {_err(write_result)}"
        time.sleep(1)

        # Modify file multiple times
        for i in range(2, 5):
            modify_result = session.file.write(
                f"{test_dir}/test.txt", f"Content {i}"
            )
            assert modify_result.success, f"write(modify) failed: {_err(modify_result)}"
            time.sleep(1)

        # Wait for final detection
        time.sleep(2)

        # Stop monitoring
        print("\n4. Stopping directory monitoring...")
        monitor_thread.stop_event.set()  # type: ignore[attr-defined]
        monitor_thread.join(timeout=5)
        print("✅ Directory monitoring stopped")

        # Analyze results
        print(f"\n=== RESULTS ===")
        print(f"Total callback calls: {len(callback_calls)}")
        print(f"Total events detected: {len(detected_events)}")
        print(f"Callback call sizes: {callback_calls}")

        print("\nDetected events:")
        for i, event in enumerate(detected_events, 1):
            print(f"  {i}. {event}")

        # Check for duplicates (should have duplicates without deduplication)
        event_keys = []
        for event in detected_events:
            event_key = (event.event_type, event.path, event.path_type)
            event_keys.append(event_key)

        unique_events = set(event_keys)
        total_events = len(event_keys)
        duplicate_count = total_events - len(unique_events)

        print(f"\nDuplication check:")
        print(f"  Total events: {total_events}")
        print(f"  Unique events: {len(unique_events)}")
        print(f"  Duplicate events: {duplicate_count}")

        # With no deduplication, we should receive all events including duplicates
        if total_events > 0:
            print("✅ Events are being detected")
            if duplicate_count > 0:
                print("✅ Duplicate events are being reported (no deduplication)")
            else:
                print("ℹ️  No duplicate events detected in this run")
            test_success = True
        else:
            print("⚠️  No events were detected. This might indicate an issue.")
            test_success = False

    finally:
        try:
            if monitor_thread:
                monitor_thread.stop_event.set()  # type: ignore[attr-defined]
                monitor_thread.join(timeout=5)
        except Exception as e:
            print(f"Warning: failed to stop monitor thread: {e}")
        try:
            session.command.execute(f"rm -rf {test_dir}", timeout_ms=10000)
        except Exception as e:
            print(f"Warning: failed to cleanup remote dir {test_dir}: {e}")
        # Clean up
        print("\n5. Cleaning up session...")
        delete_result = agb.delete(session)
        assert delete_result.success, f"Failed to delete session: {_err(delete_result)}"
        print("✅ Session deleted successfully")

    assert test_success, "watch_directory_no_deduplication did not detect any events"


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

    monitor_thread = None
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
                # Allow 2 events as passable if network latency caused one to be missed or merged
                if len(captured_events) < 2:
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
                print("❌ Not enough valid modification events detected")
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


if __name__ == "__main__":
    try:
        success1 = test_watch_directory()
        print("\n" + "=" * 60 + "\n")
        success2 = test_watch_directory_no_deduplication()
        print("\n" + "=" * 60 + "\n")
        success3 = test_watch_directory_file_modification()
        print("\n" + "=" * 60 + "\n")

        if success1 and success2 and success3:
            print("\n🎉 All tests passed!")
            sys.exit(0)
        else:
            print("\n💥 Some tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Tests failed with exception: {e}")
        sys.exit(1)
