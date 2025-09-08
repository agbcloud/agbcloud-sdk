# AGB watch_directory Example

This example demonstrates how to use the AGB SDK's `watch_directory` functionality to monitor directory changes.

## Quick Start

```bash
# 1. Set API key
export AGB_API_KEY="your-api-key"

# 2. Run the example
python main.py
```

## What the Program Does

1. Create an AGB session
2. Create test directory `/tmp/agb_watch_demo`
3. Start directory monitoring
4. Automatically perform various file operations:
   - Use `touch` command to create empty files (hello.txt, config.ini)
   - Use `write_file` method to create files with content (data.json, readme.md)
   - Modify file content (2 times)
   - Use `rm` command to delete files
   - Create new files
5. Display detected file changes in real-time
6. Press Ctrl+C to stop
7. **Display detailed operation vs event comparison analysis**

## Core API Usage

```python
# Start directory monitoring
monitor_thread = session.file_system.watch_directory(
    path="/tmp/agb_watch_demo",        # Directory to monitor
    callback=file_change_callback,     # Change callback function
    interval=1.0,                      # Polling interval (optional)
    stop_event=stop_event              # Stop signal
)

# Callback function handles file changes
def file_change_callback(events):
    # Note: events will never be empty, API filters out empty events
    for event in events:
        print(f"{event.event_type}: {event.path}")

# Other APIs used in the example
session.command.execute_command("touch /path/to/file")  # Create empty file
session.file_system.write_file("/path/to/file", content)  # Write file content
session.command.execute_command("rm /path/to/file")      # Delete file
```

## 🆕 New Feature: Operation vs Event Comparison Analysis

The program displays a detailed analysis report at the end, including:

- 📋 List of all executed file operations (with timestamps)
- 🔍 List of all detected monitoring events (with timestamps)
- 🔗 Analysis of operation-to-event correspondence
- 📊 Statistics of various operation and event types
- 💡 Matching results and key findings
- 📖 Learning points summary

This helps developers understand:
- How file operations trigger monitoring events
- Monitoring delay and accuracy
- Event correspondence for different operation types

## 💡 API Design Highlights

- **Smart Filtering**: API automatically filters empty events, callback only receives events with actual changes
- **Simplified Usage**: Developers don't need to handle empty event lists
- **Efficient Monitoring**: Avoids meaningless callback invocations, improves performance

That's it! Simply run `main.py` to see the complete example and analysis report. 