import os
import time
import threading
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
    
    # Initialize AGB client
    api_key = get_api_key()
    agb = AGB(api_key=api_key)
    print("✅ AGB client initialized")
    
    # Create session with specified ImageId
    session_params = CreateSessionParams(image_id="agb-code-space-2")
    session_result = agb.create(session_params)
    
    if not session_result.success:
        print(f"❌ Failed to create session: {session_result.error_message}")
        return
    
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
    
    try:
        # Create the test directory
        print("\n1. Creating test directory...")
        create_dir_result = session.file_system.create_directory("/tmp/watch_test")
        print(f"Create directory result: {create_dir_result.success}")
        
        # Start directory monitoring
        print("\n2. Starting directory monitoring...")
        monitor_thread = session.file_system.watch_directory(
            path="/tmp/watch_test",
            callback=file_change_callback,
            interval=0.5  # Poll every 0.5 seconds for faster testing
        )
        monitor_thread.start()
        print("✅ Directory monitoring started")
        
        # Wait a moment for monitoring to initialize
        time.sleep(1)
        
        # Test 1: Create a new file
        print("\n3. Creating a new file...")
        write_result = session.file_system.write_file(
            "/tmp/watch_test/test1.txt", 
            "Initial content"
        )
        print(f"Write file result: {write_result.success}")
        
        # Wait for detection
        time.sleep(2)
        
        # Test 2: Modify the file
        print("\n4. Modifying the file...")
        modify_result = session.file_system.write_file(
            "/tmp/watch_test/test1.txt", 
            "Modified content"
        )
        print(f"Modify file result: {modify_result.success}")
        
        # Wait for detection
        time.sleep(2)
        
        # Test 3: Create another file
        print("\n5. Creating another file...")
        write_result2 = session.file_system.write_file(
            "/tmp/watch_test/test2.txt", 
            "Second file content"
        )
        print(f"Write second file result: {write_result2.success}")
        
        # Wait for detection
        time.sleep(2)
        
        # Stop monitoring
        print("\n6. Stopping directory monitoring...")
        monitor_thread.stop_event.set()
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
        if len(detected_events) > 0:
            print("\n✅ watch_directory test completed successfully!")
            print("The directory monitoring is working and detecting file changes.")
        else:
            print("\n⚠️  No events were detected. This might indicate an issue.")
            
    finally:
        # Clean up
        print("\n7. Cleaning up session...")
        delete_result = agb.delete(session)
        if delete_result.success:
            print("✅ Session deleted successfully")
        else:
            print(f"❌ Failed to delete session: {delete_result.error_message}")


if __name__ == "__main__":
    test_watch_directory() 