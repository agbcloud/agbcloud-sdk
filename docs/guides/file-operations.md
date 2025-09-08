# File Operations Guide

## Overview

The AGB SDK provides comprehensive file system operations through the `file_system` module. You can read, write, create, delete, and manage files and directories in your cloud sessions. This guide covers all file operations from basic usage to advanced patterns.

## Quick Reference (1 minute)

```python
from agb import AGB

agb = AGB()
session = agb.create().session

# Basic file operations
session.file_system.write_file("/tmp/hello.txt", "Hello World!")
content = session.file_system.read_file("/tmp/hello.txt").content
print(content)  # "Hello World!"

# Directory operations
session.file_system.create_directory("/tmp/mydir")
files = session.file_system.list_directory("/tmp").entries
session.file_system.move_file("/tmp/hello.txt", "/tmp/trash/hello.txt")

agb.delete(session)
```

## Step-by-Step Guide (5-10 minutes)

### File Reading and Writing

```python
from agb import AGB

agb = AGB()
session = agb.create().session

# Write a text file
write_result = session.file_system.write_file(
    path="/tmp/example.txt",
    content="This is example content\nWith multiple lines"
)

if write_result.success:
    print("File written successfully")

    # Read the file back
    read_result = session.file_system.read_file("/tmp/example.txt")
    if read_result.success:
        print("File content:")
        print(read_result.content)
    else:
        print(f"Failed to read file: {read_result.error_message}")
else:
    print(f"Failed to write file: {write_result.error_message}")

agb.delete(session)
```

### Directory Management

```python
# Create directories
create_result = session.file_system.create_directory("/tmp/project")
if create_result.success:
    print("Directory created")

# Create nested directories
session.file_system.create_directory("/tmp/project/src")
session.file_system.create_directory("/tmp/project/docs")

# List directory contents
list_result = session.file_system.list_directory("/tmp/project")
if list_result.success:
    print("Directory contents:")
    for entry in list_result.entries:
        print(f"- {entry['name']} ({entry['type']})")
```

### File Information

```python
# Get file information
info_result = session.file_system.get_file_info("/tmp/example.txt")
if info_result.success:
    info = info_result.file_info
    print(f"File size: {info.get('size', 'unknown')} bytes")
    print(f"File type: {info.get('type', 'unknown')}")
    print(f"Last modified: {info.get('modified', 'unknown')}")
```

## Advanced Usage (15+ minutes)

### Batch File Operations

```python
def process_multiple_files(session, file_data):
    """Process multiple files in batch"""
    results = []

    for filename, content in file_data.items():
        # Write file
        write_result = session.file_system.write_file(filename, content)

        if write_result.success:
            # Verify by reading back
            read_result = session.file_system.read_file(filename)
            results.append({
                "filename": filename,
                "success": read_result.success,
                "content_length": len(read_result.content) if read_result.success else 0
            })
        else:
            results.append({
                "filename": filename,
                "success": False,
                "error": write_result.error_message
            })

    return results

# Usage
agb = AGB()
session = agb.create().session

files_to_create = {
    "/tmp/file1.txt": "Content of file 1",
    "/tmp/file2.txt": "Content of file 2",
    "/tmp/file3.txt": "Content of file 3"
}

results = process_multiple_files(session, files_to_create)
for result in results:
    status = "✅" if result["success"] else "❌"
    print(f"{status} {result['filename']}")

agb.delete(session)
```

### File Processing Pipeline

```python
def file_processing_pipeline(session, input_file, output_file):
    """Complete file processing pipeline"""

    # Step 1: Read input file
    read_result = session.file_system.read_file(input_file)
    if not read_result.success:
        return False, f"Failed to read input: {read_result.error_message}"

    # Step 2: Process content (example: convert to uppercase)
    original_content = read_result.content
    processed_content = original_content.upper()

    # Step 3: Write processed content
    write_result = session.file_system.write_file(output_file, processed_content)
    if not write_result.success:
        return False, f"Failed to write output: {write_result.error_message}"

    # Step 4: Verify output
    verify_result = session.file_system.read_file(output_file)
    if not verify_result.success:
        return False, f"Failed to verify output: {verify_result.error_message}"

    return True, {
        "input_size": len(original_content),
        "output_size": len(processed_content),
        "processed": True
    }

# Usage example
agb = AGB()
session = agb.create().session

# Create input file
session.file_system.write_file("/tmp/input.txt", "hello world\nthis is a test")

# Process file
success, result = file_processing_pipeline(
    session,
    "/tmp/input.txt",
    "/tmp/output.txt"
)

if success:
    print("Pipeline completed successfully:")
    print(f"Input size: {result['input_size']} bytes")
    print(f"Output size: {result['output_size']} bytes")
else:
    print(f"Pipeline failed: {result}")

agb.delete(session)
```

### Working with Different File Types

```python
import json
import csv
from io import StringIO

def handle_json_file(session, filepath, data):
    """Handle JSON file operations"""
    # Write JSON data
    json_content = json.dumps(data, indent=2)
    write_result = session.file_system.write_file(filepath, json_content)

    if write_result.success:
        # Read and parse JSON
        read_result = session.file_system.read_file(filepath)
        if read_result.success:
            parsed_data = json.loads(read_result.content)
            return True, parsed_data

    return False, None

def handle_csv_file(session, filepath, data):
    """Handle CSV file operations"""
    # Create CSV content
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    csv_content = output.getvalue()

    # Write CSV file
    write_result = session.file_system.write_file(filepath, csv_content)

    if write_result.success:
        # Read and parse CSV
        read_result = session.file_system.read_file(filepath)
        if read_result.success:
            reader = csv.DictReader(StringIO(read_result.content))
            parsed_data = list(reader)
            return True, parsed_data

    return False, None

# Usage examples
agb = AGB()
session = agb.create().session

# JSON example
json_data = {"name": "John", "age": 30, "city": "New York"}
success, result = handle_json_file(session, "/tmp/data.json", json_data)
if success:
    print("JSON data:", result)

# CSV example
csv_data = [
    {"name": "Alice", "age": 25, "city": "Boston"},
    {"name": "Bob", "age": 30, "city": "Chicago"}
]
success, result = handle_csv_file(session, "/tmp/data.csv", csv_data)
if success:
    print("CSV data:", result)

agb.delete(session)
```

### Directory Monitoring

Monitor directory changes in real-time to automatically respond to file modifications, creations, or deletions.

```python
import threading
import time
from agb import AGB

def simple_directory_monitoring():
    """Basic directory monitoring example"""
    from agb.session_params import CreateSessionParams
    
    agb = AGB()
    session_params = CreateSessionParams(image_id="agb-code-space-2")
    session = agb.create(session_params).session
    
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

simple_directory_monitoring()
```

**Advanced Monitoring with Event Processing:**

```python
def advanced_directory_monitoring():
    """Advanced monitoring with event processing and filtering"""
    from agb.session_params import CreateSessionParams
    
    agb = AGB()
    session_params = CreateSessionParams(image_id="agb-code-space-2")
    session = agb.create(session_params).session
    
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

## Best Practices

### 1. Always Check Operation Results

```python
# ✅ Good: Always check success status
write_result = session.file_system.write_file("/tmp/file.txt", "content")
if write_result.success:
    print("File written successfully")
else:
    print(f"Write failed: {write_result.error_message}")

# ❌ Bad: Assuming operations always succeed
session.file_system.write_file("/tmp/file.txt", "content")
# No error checking - could fail silently
```

### 2. Use Absolute Paths

```python
# ✅ Good: Use absolute paths
session.file_system.write_file("/tmp/myfile.txt", "content")

# ❌ Avoid: Relative paths can be unpredictable
session.file_system.write_file("myfile.txt", "content")
```

### 3. Large Files Are Handled Automatically

```python
def write_content(session, filepath, content):
    """Write content to file - large files are handled automatically"""
    # No need to check file size - the system handles chunking automatically
    result = session.file_system.write_file(filepath, content)
    return result.success, result.error_message

# Example: Write a large file (automatically chunked)
large_content = "x" * (2 * 1024 * 1024)  # 2MB content
success, error = write_content(session, "/tmp/large_file.txt", large_content)
if success:
    print("Large file written successfully with automatic chunking")
else:
    print(f"Write failed: {error}")
```

### 4. Clean Up Temporary Files

```python
def with_temp_file(session, content, operation):
    """Context manager pattern for temporary files"""
    temp_file = f"/tmp/temp_{hash(content)}.txt"

    try:
        # Create temp file
        write_result = session.file_system.write_file(temp_file, content)
        if not write_result.success:
            raise Exception(f"Failed to create temp file: {write_result.error_message}")

        # Perform operation
        return operation(session, temp_file)

    finally:
        # Clean up
        session.file_system.move_file(temp_file, "/tmp/trash/" + temp_file.split("/")[-1])

# Usage
def process_file(session, filepath):
    read_result = session.file_system.read_file(filepath)
    return read_result.content.upper() if read_result.success else None

result = with_temp_file(session, "hello world", process_file)
print(result)  # "HELLO WORLD"
```

## Troubleshooting

### Common Issues

**File Not Found Errors**
```python
read_result = session.file_system.read_file("/nonexistent/file.txt")
if not read_result.success:
    if "not found" in read_result.error_message.lower():
        print("File doesn't exist - create it first")
    else:
        print(f"Other error: {read_result.error_message}")
```

**Permission Errors**
```python
# Some paths may not be writable
write_result = session.file_system.write_file("/etc/restricted.txt", "content")
if not write_result.success:
    if "permission" in write_result.error_message.lower():
        print("Permission denied - try /tmp/ directory")
        # Retry with /tmp/
        write_result = session.file_system.write_file("/tmp/file.txt", "content")
```

**Directory Creation Issues**
```python
# Create parent directories first
def ensure_directory_exists(session, filepath):
    """Ensure parent directory exists before writing file"""
    import os
    parent_dir = os.path.dirname(filepath)

    if parent_dir and parent_dir != "/":
        create_result = session.file_system.create_directory(parent_dir)
        if not create_result.success:
            print(f"Warning: Could not create directory {parent_dir}")

    return parent_dir

# Usage
filepath = "/tmp/deep/nested/file.txt"
ensure_directory_exists(session, filepath)
session.file_system.write_file(filepath, "content")
```

## Related Documentation

- **[Code Execution Guide](code-execution.md)** - Using files in code execution
- **[OSS Integration Guide](oss-integration.md)** - Cloud storage for persistent files
- **[Session Management](session-management.md)** - Managing file system sessions
- **[API Reference](../api-reference/modules/filesystem.md)** - Complete FileSystem API documentation