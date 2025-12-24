
# Directory monitoring

Monitor directory changes in real-time to automatically respond to file modifications, creations, or deletions.

```python
import threading
import time
from agb import AGB

def simple_directory_monitoring():
    """Basic directory monitoring example"""
    from agb.session_params import CreateSessionParams

    agb = AGB()
    session_params = CreateSessionParams(image_id="agb-code-space-1")
    result = agb.create(session_params)

    if result.success:
        session = result.session

        # Create directory to monitor
        session.file_system.create_directory("/tmp/watch_demo")

        # Define callback function
        def on_file_change(events):
            """Handle file change events"""
            print(f"Detected {len(events)} changes:")
            for event in events:
                print(f"  {event.event_type}: {event.path} ({event.path_type})")

        try:
            # Start monitoring
            monitor_thread = session.file_system.watch_directory(
                path="/tmp/watch_demo",
                callback=on_file_change,
                interval=1.0  # Check every 1 second
            )
            monitor_thread.start()
            print("Directory monitoring started...")

            # Simulate file operations
            print("Creating files...")
            session.file_system.write_file("/tmp/watch_demo/file1.txt", "Content 1")
            time.sleep(2)

            session.file_system.write_file("/tmp/watch_demo/file2.txt", "Content 2")
            time.sleep(2)

            print("Modifying file...")
            session.file_system.write_file("/tmp/watch_demo/file1.txt", "Modified content")
            time.sleep(2)

            # Stop monitoring
            print("Stopping monitoring...")
            monitor_thread.stop_event.set()
            monitor_thread.join()
        finally:
            agb.delete(session)
    else:
        print(f"Failed to create session: {result.error_message}")

simple_directory_monitoring()
```

**Advanced Monitoring with Event Processing:**

```python
def advanced_directory_monitoring():
    """Advanced monitoring with event processing and filtering"""
    from agb.session_params import CreateSessionParams

    agb = AGB()
    session_params = CreateSessionParams(image_id="agb-code-space-1")
    result = agb.create(session_params)

    if not result.success:
        print(f"Create session failed: {result.error_message}")

    session = result.session
    # Create monitoring directory
    session.file_system.create_directory("/tmp/project_watch")

    # Event statistics
    event_stats = {"create": 0, "modify": 0, "delete": 0}
    processed_files = set()

    def process_file_events(events):
        """Process and filter file events"""
        for event in events:
            # Update statistics
            event_stats[event.event_type] = event_stats.get(event.event_type, 0) + 1

            # Only process .txt files
            if event.path.endswith('.txt'):
                if event.event_type == "create":
                    print(f"📄 New text file: {event.path}")
                    processed_files.add(event.path)
                elif event.event_type == "modify":
                    print(f"✏️  Modified: {event.path}")
                elif event.event_type == "delete":
                    print(f"🗑️  Deleted: {event.path}")
                    processed_files.discard(event.path)

        # Print current stats
        print(f"Stats - Create: {event_stats.get('create', 0)}, "
              f"Modify: {event_stats.get('modify', 0)}, "
              f"Delete: {event_stats.get('delete', 0)}")

    try:
        # Start monitoring with custom interval
        monitor_thread = session.file_system.watch_directory(
            path="/tmp/project_watch",
            callback=process_file_events,
            interval=0.5  # More frequent checking
        )
        monitor_thread.start()

        # Simulate project work
        print("Simulating project work...")

        # Create multiple files
        for i in range(3):
            session.file_system.write_file(f"/tmp/project_watch/doc{i}.txt", f"Document {i}")
            session.file_system.write_file(f"/tmp/project_watch/data{i}.json", f'{{"id": {i}}}')
            time.sleep(1)

        # Modify some files
        session.file_system.write_file("/tmp/project_watch/doc0.txt", "Updated document 0")
        time.sleep(1)

        print(f"Total processed .txt files: {len(processed_files)}")
        print(f"Final statistics: {event_stats}")

        # Stop monitoring
        monitor_thread.stop_event.set()
        monitor_thread.join()

    finally:
        agb.delete(session)

advanced_directory_monitoring()
```

