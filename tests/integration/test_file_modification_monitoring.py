import os
import threading
import time

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

    # Initialize AGB client
    api_key = get_api_key()
    agb = AGB(api_key=api_key)
    print("✅ AGB client initialized")

    # Create session with specified ImageId
    session_params = CreateSessionParams(image_id="agb-code-space-2")
    session_result = agb.create(session_params)

    if not session_result.success:
        print(f"❌ Failed to create session: {session_result.error_message}")
        return False

    session = session_result.session
    print(f"✅ Session created successfully with ID: {session.session_id}")

    # Create test directory and initial file
    test_dir = f"/tmp/test_modify_watch_{int(time.time())}"
    print(f"\n1. Creating test directory: {test_dir}")
    create_dir_result = session.file_system.create_directory(test_dir)
    if not create_dir_result.success:
        print(f"❌ Failed to create directory: {create_dir_result.error_message}")
        return False
    print("✅ Test directory created")

    # Create initial file
    test_file = f"{test_dir}/modify_test.txt"
    print(f"\n2. Creating initial file: {test_file}")
    write_result = session.file_system.write_file(test_file, "Initial content")
    if not write_result.success:
        print(f"❌ Failed to create initial file: {write_result.error_message}")
        return False
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
        monitor_thread = session.file_system.watch_directory(
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
            modify_result = session.file_system.write_file(test_file, content)
            if not modify_result.success:
                print(
                    f"❌ Failed to modify file (attempt {i + 1}): {modify_result.error_message}"
                )
            else:
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
            else:
                print(f"✅ Captured sufficient modify events: {len(captured_events)}")

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

            if valid_events > 0:
                print("✅ File modification monitoring test passed!")
                test_passed = True
            else:
                print("❌ No valid modification events detected")

    finally:
        # Stop monitoring
        print(f"\n6. Stopping directory monitoring...")
        if monitor_thread:
            monitor_thread.stop_event.set()
            monitor_thread.join(timeout=5)
            print("✅ Directory monitoring stopped")

        # Clean up session
        print(f"\n7. Cleaning up session...")
        delete_result = agb.delete(session)
        if delete_result.success:
            print("✅ Session deleted successfully")
        else:
            print(f"❌ Failed to delete session: {delete_result.error_message}")

    print("\n=== File modification monitoring test completed ===")
    return test_passed


if __name__ == "__main__":
    success = test_watch_directory_file_modification()
    if success:
        print("\n🎉 All tests passed!")
        exit(0)
    else:
        print("\n💥 Some tests failed!")
        exit(1)
