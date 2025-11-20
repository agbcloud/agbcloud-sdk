# FileSystem Module API Reference

The FileSystem module provides comprehensive file and directory operations in the AGB cloud environment. It supports reading, writing, creating, deleting, and managing files and directories with full error handling and metadata support.

## Class Definition

```python
from agb.modules.file_system import FileSystem, FileContentResult, DirectoryListResult, FileInfoResult, BoolResult

class FileSystem(BaseService):
    def __init__(self, session)
```

## Core Methods

### File Operations

#### `read_file(path)`

Read the content of a file. Automatically handles large files by chunking internally.

**Parameters:**
- `path` (str): Path to the file to read.

**Returns:**
- `FileContentResult`: Result containing file content and operation status.

**Example:**
```python
# Read a text file (automatically handles large files)
result = session.file_system.read_file("/tmp/example.txt")
if result.success:
    print("File content:")
    print(result.content)
else:
    print("Error:", result.error_message)
```

#### `write_file(path, content, mode="overwrite")`

Write content to a file. Automatically handles large files by chunking internally.

**Parameters:**
- `path` (str): Path where to write the file.
- `content` (str): Content to write to the file.
- `mode` (str, optional): Write mode ("overwrite" or "append"). Default is "overwrite".

**Returns:**
- `BoolResult`: Result object containing success status and error message.

**Example:**
```python
# Write text to file (automatically handles large files)
content = "Hello, World!\nThis is a test file."
result = session.file_system.write_file("/tmp/output.txt", content)
if result.success:
    print("File written successfully")
else:
    print("Write failed:", result.error_message)

# Append to existing file
result = session.file_system.write_file("/tmp/data.txt", content, mode="append")
```

#### `read_multiple_files(paths)`

Read multiple files in a single operation.

**Parameters:**
- `paths` (List[str]): List of file paths to read.

**Returns:**
- `MultipleFileContentResult`:Result object containing a dictionary mapping file paths to contents,and error message.

**Example:**
```python
file_paths = ["/tmp/file1.txt", "/tmp/file2.txt", "/tmp/file3.txt"]
result = session.file_system.read_multiple_files(file_paths)

if result.success:
    for path, content in result.contents.items():
        print(f"File {path}:")
        print(content)
        print("-" * 40)
else:
    print("Error:", result.error_message)
```

### Directory Operations

#### `list_directory(path)`

List the contents of a directory.

**Parameters:**
- `path` (str): Path to the directory to list.

**Returns:**
- `DirectoryListResult`: Result containing directory entries and error message.

**Example:**
```python
result = session.file_system.list_directory("/tmp")
if result.success:
    print("Directory contents:")
    for entry in result.entries:
        entry_type = "DIR" if entry.get("is_directory", False) else "FILE"
        print(f"{entry_type}: {entry.get('name', 'N/A')} ({entry.get('size', 'N/A')} bytes)")
else:
    print("Error:", result.error_message)
```

#### `create_directory(path)`

Create a directory (including parent directories if needed).

**Parameters:**
- `path` (str): Path of the directory to create.

**Returns:**
- `BoolResult`: Result object containing success status and error message.

**Example:**
```python
# Create single directory
result = session.file_system.create_directory("/tmp/new_folder")
if result.success:
    print("Directory created successfully")
else:
    print("creating directory failed:", result.error_message)
# Create nested directories
result = session.file_system.create_directory("/tmp/deep/nested/folder")
if result.success:
    print("Nested directories created")
else:
    print("creating directory failed:", result.error_message)
```

### File Information

#### `get_file_info(path)`

Get detailed information about a file or directory.

**Parameters:**
- `path` (str): Path to the file or directory.

**Returns:**
- `FileInfoResult`: Result object containing file info and error message.

**Example:**
```python
result = session.file_system.get_file_info("/tmp/example.txt")
if result.success:
    info = result.file_info
    print(f"Name: {info.get('name','N/A')}")
    print(f"Size: {info.get('size','N/A')} bytes")
    print(f"Type: {info.get('type','N/A')}")
    print(f"Modified: {info.get('modified_time','N/A')}")
    print(f"Permissions: {info.get('permissions','N/A')}")
else:
    print("Error:", result.error_message)
```

### File Management

#### `move_file(source, destination)`

Move a file or directory from source path to destination path.

**Parameters:**
- `source` (str): Source path of the file/directory to move.
- `destination` (str): Destination path.

**Returns:**
- `BoolResult`: Result object containing success status and error message.

**Example:**
```python
# Rename a file
result = session.file_system.move_file("/tmp/old_name.txt", "/tmp/new_name.txt")
if result.success:
    print("File renamed successfully")

# Move to different directory
result = session.file_system.move_file("/tmp/file.txt", "/tmp/backup/file.txt")
```

#### `search_files(path, pattern, exclude_patterns)`

Search for files matching a pattern.

**Parameters:**
- `path` (str): The base directory path to search in.
- `pattern` (str): The glob pattern to search for.
- `exclude_patterns` (List[str], optional):Optional list of patterns to exclude from the search.

**Returns:**
- `DirectoryListResult`: Result object containing matching file paths and error message.

**Example:**
```python
# Search for all .txt files
result = session.file_system.search_files("/tmp", "*.txt")
if result.success:
    print("Found files:")
    for entry in result.entries:
        print(f"- {entry['name']}")

# Non-recursive search
earch_pattern = "*.log"
exclude_patterns = ["runtime*.log"]
result = session.file_system.search_files("/tmp", earch_pattern, exclude_patterns)
```

### Advanced Operations

#### `edit_file(path, edits, dry_run)`

Edit a file by replacing occurrences of oldText with newText.

**Parameters:**
- `path` (str): Path to the file to edit.
- `edits` (List[Dict[str, str]]):A list of dictionaries specifying oldText and newText.
- `dry_run` (bool): If True, preview changes without applying them.(Default: False)

**Returns:**
- `BoolResult`: Result object containing success status and error message.

**Example:**
```python
# Edit line 3 of a file
edits = [
    {"action": "append", "content": "\nThis line was appended."},
    {"action": "prepend", "content": "This line was prepended.\n"}
]
result = session.file_system.edit_file("/tmp/config.txt", edits, True)
if result.success:
    print("File edited successfully")
else:
    print("Edit failed:", result.error_message)
```

#### `watch_directory(path, callback, interval=1.0, stop_event=None)`

Monitor a directory for file changes and execute a callback function when changes are detected.

**Parameters:**
- `path` (str): Directory path to monitor for changes.
- `callback` (Callable): Function to call when changes are detected. Receives a list of `FileChangeEvent` objects.
- `interval` (float, optional): Polling interval in seconds. Default is 1.0.
- `stop_event` (threading.Event, optional): Event to stop monitoring. If not provided, a new Event is created and returned via the thread object..

**Returns:**
- `threading.Thread`: Monitoring thread. Call `thread.start()` to begin monitoring and `thread.stop_event.set()` to stop.

**Example:**
```python
import threading
import time

# Create session with image_id
from agb.session_params import CreateSessionParams
session_params = CreateSessionParams(image_id="agb-code-space-1")
session = agb.create(session_params).session

# Define callback function
def handle_changes(events):
    for event in events:
        print(f"{event.event_type}: {event.path} ({event.path_type})")

# Start monitoring
monitor_thread = session.file_system.watch_directory(
    path="/tmp/watch_folder",
    callback=handle_changes,
    stop_event = threading.Event()
)
monitor_thread.start()

# Do some work...
session.file_system.write_file("/tmp/watch_folder/test.txt", "content")
time.sleep(2)

# Stop monitoring
monitor_thread.stop_event.set()
monitor_thread.join()
```



## Response Types

For detailed information about response objects, see:
- **[FileContentResult](../responses/filesystem-results.md#filecontentresult)** - File content and operation status
- **[DirectoryListResult](../responses/filesystem-results.md#directorylistresult)** - Directory entries and metadata
- **[FileInfoResult](../responses/filesystem-results.md#fileinforesult)** - File metadata and information
- **[MultipleFileContentResult](../responses/filesystem-results.md#multiplefilecontentresult)** - Multiple file contents
- **[FileSearchResult](../responses/filesystem-results.md#filesearchresult)** - File search results

### FileChangeEvent

Represents a single file change event from directory monitoring.

```python
class FileChangeEvent:
    event_type: str              # Type of change ("create", "modify", "delete")
    path: str                    # Path of the file or directory that changed
    path_type: str               # Type of path ("file" or "directory")
```

**Methods:**
- `to_dict()`: Convert to dictionary representation
- `from_dict(data)`: Create from dictionary (class method)

### FileChangeResult

Result object for file change monitoring operations.

```python
class FileChangeResult(ApiResponse):
    request_id: str                    # Unique request identifier
    success: bool                      # Operation success status
    events: List[FileChangeEvent]      # List of detected changes
    error_message: str                 # Error description if failed
```

**Methods:**
- `has_changes()`: Returns True if any changes were detected
- `get_created_files()`: Returns list of created file paths
- `get_modified_files()`: Returns list of modified file paths
- `get_deleted_files()`: Returns list of deleted file paths

## Usage Patterns

### Basic File Operations

```python
from agb import AGB

def basic_file_operations():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        # Create a file
        content = "Hello, AGB FileSystem!\nThis is line 2.\nThis is line 3."
        write_result = session.file_system.write_file("/tmp/test.txt", content)

        if write_result.success:
            print("✅ File created successfully")

            # Read the file back
            read_result = session.file_system.read_file("/tmp/test.txt")
            if read_result.success:
                print("📄 File content:")
                print(read_result.content)
            else: 
                print("❌ Failed to read file",read_result.error_message)

            # Get file information
            info_result = session.file_system.get_file_info("/tmp/test.txt")
            if info_result.success:
                info = info_result.file_info
                print(f"📊 File size: {info.get('size')} bytes")
                print(f"📅 Modified: {info.get('modified_time','N/A')}")
            else:
                print("❌ Failed to get file info",info_result.error_message)

    finally:
        agb.delete(session)

basic_file_operations()
```

### Directory Management

```python
def directory_management():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        # Create directory structure
        dirs_to_create = [
            "/tmp/project",
            "/tmp/project/src",
            "/tmp/project/docs",
            "/tmp/project/tests"
        ]

        for directory in dirs_to_create:
            result = session.file_system.create_directory(directory)
            if result.success:
                print(f"✅ Created: {directory}")

        # Create files in directories
        files_to_create = {
            "/tmp/project/README.md": "# My Project\nThis is a sample project.",
            "/tmp/project/src/main.py": "print('Hello, World!')",
            "/tmp/project/tests/test_main.py": "def test_main():\n    assert True"
        }

        for filepath, content in files_to_create.items():
            result = session.file_system.write_file(filepath, content)
            if result.success:
                print(f"📄 Created file: {filepath}")

        # List directory contents
        list_result = session.file_system.list_directory("/tmp/project")
        if list_result.success:
            print("\n📁 Project structure:")
            for entry in list_result.entries:
                entry_type = "📁" if entry.get("is_directory") else "📄"
                print(f"  {entry_type} {entry['name']}")

        # Search for Python files
        search_result = session.file_system.search_files("/tmp/project", "*.py")
        if search_result.success:
            print("\n🔍 Python files found:")
            for entry in search_result.entries:
                print(f"  - {entry}")

    finally:
        agb.delete(session)

directory_management()
```

### Batch File Processing

```python
def batch_file_processing():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        # Create multiple test files
        test_files = {}
        for i in range(5):
            filename = f"/tmp/data_{i}.txt"
            content = f"File {i}\nContent line 1\nContent line 2\nValue: {i * 10}"
            test_files[filename] = content

        # Write all files
        for filepath, content in test_files.items():
            result = session.file_system.write_file(filepath, content)
            if result.success:
                print(f"✅ Created: {filepath}")

        # Read multiple files at once
        file_paths = list(test_files.keys())
        read_result = session.file_system.read_multiple_files(file_paths)

        if read_result.success:
            print("\n📚 Batch read results:")
            for filepath, content in read_result.contents.items():
                lines = content.split('\n')
                print(f"📄 {filepath}: {len(lines)} lines")

        # Process files: extract values and create summary
        summary_lines = ["File Summary", "=" * 20]

        for filepath, content in read_result.contents.items():
            lines = content.split('\n')
            for line in lines:
                if line.startswith("Value:"):
                    value = line.split(":")[1].strip()
                    filename = filepath.split("/")[-1]
                    summary_lines.append(f"{filename}: {value}")

        # Write summary file
        summary_content = '\n'.join(summary_lines)
        summary_result = session.file_system.write_file("/tmp/summary.txt", summary_content)

        if summary_result.success:
            print("\n📊 Summary file created")

            # Read and display summary
            summary_read = session.file_system.read_file("/tmp/summary.txt")
            if summary_read.success:
                print("Summary content:")
                print(summary_read.content)

    finally:
        agb.delete(session)

batch_file_processing()
```

### File Processing Pipeline

```python
def file_processing_pipeline():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        # Step 1: Create input data
        input_data = """name,age,city,salary
Alice,25,New York,50000
Bob,30,London,60000
Charlie,35,Paris,70000
Diana,28,Tokyo,55000
Eve,32,Berlin,65000"""

        session.file_system.write_file("/tmp/employees.csv", input_data)
        print("✅ Input data created")

        # Step 2: Process data with code
        processing_code = """
import csv
from io import StringIO

# Read the CSV data
with open('/tmp/employees.csv', 'r') as f:
    csv_content = f.read()

# Parse CSV
reader = csv.DictReader(StringIO(csv_content))
employees = list(reader)

# Process data
high_earners = [emp for emp in employees if int(emp['salary']) > 55000]
avg_salary = sum(int(emp['salary']) for emp in employees) / len(employees)

# Create reports
high_earners_report = "High Earners Report\\n" + "=" * 20 + "\\n"
for emp in high_earners:
    high_earners_report += f"{emp['name']}: ${emp['salary']} in {emp['city']}\\n"

summary_report = f"Summary Report\\n" + "=" * 15 + "\\n"
summary_report += f"Total employees: {len(employees)}\\n"
summary_report += f"High earners (>$55k): {len(high_earners)}\\n"
summary_report += f"Average salary: ${avg_salary:,.2f}\\n"

# Write reports
with open('/tmp/high_earners.txt', 'w') as f:
    f.write(high_earners_report)

with open('/tmp/summary.txt', 'w') as f:
    f.write(summary_report)

print("Reports generated successfully")
"""

        code_result = session.code.run_code(processing_code, "python")
        if code_result.success:
            print("✅ Data processing completed")
            print(code_result.result)

        # Step 3: Read generated reports
        report_files = ["/tmp/high_earners.txt", "/tmp/summary.txt"]
        reports_result = session.file_system.read_multiple_files(report_files)

        if reports_result.success:
            print("\n📊 Generated Reports:")
            for filepath, content in reports_result.contents.items():
                report_name = filepath.split("/")[-1]
                print(f"\n📄 {report_name}:")
                print(content)

        # Step 4: Create final archive info
        archive_info = f"""Archive Information
Generated: {__import__('datetime').datetime.now().isoformat()}
Files processed: employees.csv
Reports created: high_earners.txt, summary.txt
Processing status: Complete
"""

        session.file_system.write_file("/tmp/archive_info.txt", archive_info)
        print("\n✅ Archive information created")

    finally:
        agb.delete(session)

file_processing_pipeline()
```

### Directory Monitoring

```python
import threading
import time
from agb import AGB

def directory_monitoring_example():
    from agb.session_params import CreateSessionParams

    agb = AGB()
    session_params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(session_params).session

    try:
        # Create directory to monitor
        session.file_system.create_directory("/tmp/monitor_demo")

        # Track changes
        changes_log = []

        def log_changes(events):
            """Log all file changes with timestamps"""
            timestamp = time.strftime("%H:%M:%S")
            for event in events:
                log_entry = f"[{timestamp}] {event.event_type.upper()}: {event.path}"
                changes_log.append(log_entry)
                print(log_entry)

        # Start monitoring
        monitor_thread = session.file_system.watch_directory(
            path="/tmp/monitor_demo",
            callback=log_changes,
            interval=0.5
        )
        monitor_thread.start()
        print("🔍 Directory monitoring started")

        # Simulate file operations
        print("\n📝 Creating files...")
        for i in range(3):
            filename = f"/tmp/monitor_demo/file_{i}.txt"
            content = f"This is file {i}\nCreated at {time.strftime('%Y-%m-%d %H:%M:%S')}"
            session.file_system.write_file(filename, content)
            time.sleep(1)

        print("\n✏️ Modifying files...")
        session.file_system.write_file(
            "/tmp/monitor_demo/file_0.txt",
            "Modified content for file 0"
        )
        time.sleep(1)

        print("\n📁 Creating subdirectory...")
        session.file_system.create_directory("/tmp/monitor_demo/subdir")
        session.file_system.write_file(
            "/tmp/monitor_demo/subdir/nested.txt",
            "Nested file content"
        )
        time.sleep(2)

        # Stop monitoring
        print("\n🛑 Stopping monitoring...")
        monitor_thread.stop_event.set()
        monitor_thread.join()

        # Summary
        print(f"\n📊 Summary: {len(changes_log)} changes detected")
        for log_entry in changes_log:
            print(f"  {log_entry}")

    finally:
        agb.delete(session)

directory_monitoring_example()
```

## Best Practices

### 1. Always Check Operation Results

```python
# ✅ Good: Always check success status
result = session.file_system.read_file("/tmp/file.txt")
if result.success:
    print("Content:", result.content)
else:
    print("Error:", result.error_message)

# ❌ Bad: Assuming operations always succeed
result = session.file_system.read_file("/tmp/file.txt")
print(result.content)  # May be empty if read failed
```

### 2. Use Absolute Paths

```python
# ✅ Good: Use absolute paths
session.file_system.write_file("/tmp/myfile.txt", "content")

# ❌ Avoid: Relative paths can be unpredictable
session.file_system.write_file("myfile.txt", "content")
```

### 3. Handle Large Files Appropriately

```python
# ✅ Good: Use appropriate methods for large files
large_content = "x" * 1000000  # 1MB content
result = session.file_system.write_file("/tmp/large.txt", large_content)

# ✅ Good: Check file size before operations
info_result = session.file_system.get_file_info("/tmp/large.txt")
if info_result.success:
    size = info_result.file_info.get('size', 0)
    if size > 1024 * 1024:  # > 1MB
        print("Large file detected, using appropriate method")
```

### 4. Organize Files Logically

```python
# ✅ Good: Create organized directory structure
session.file_system.create_directory("/tmp/project/data")
session.file_system.create_directory("/tmp/project/output")
session.file_system.create_directory("/tmp/project/logs")

# Write files to appropriate locations
session.file_system.write_file("/tmp/project/data/input.csv", data)
session.file_system.write_file("/tmp/project/output/results.txt", results)
session.file_system.write_file("/tmp/project/logs/process.log", log_info)
```

### 5. Clean Up Temporary Files

```python
def with_temp_files(session, operation):
    """Context manager pattern for temporary files"""
    temp_files = []

    try:
        # Create temp files
        for i in range(3):
            temp_path = f"/tmp/temp_{i}_{hash(str(i))}.txt"
            session.file_system.write_file(temp_path, f"temp content {i}")
            temp_files.append(temp_path)

        # Perform operation
        return operation(session, temp_files)

    finally:
        # Clean up temp files
        for temp_file in temp_files:
            session.command.execute_command(f"rm -f {temp_file}")
```

### 6. Directory Monitoring Best Practices

```python
# ✅ Good: Always stop monitoring threads properly
def safe_directory_monitoring(session, directory_path):
    """Safe directory monitoring with proper cleanup"""

    def handle_changes(events):
        for event in events:
            print(f"Change detected: {event.event_type} - {event.path}")

    monitor_thread = session.file_system.watch_directory(
        path=directory_path,
        callback=handle_changes,
        interval=1.0
    )

    try:
        monitor_thread.start()
        # Do your work here
        time.sleep(10)
    finally:
        # Always stop the monitoring thread
        monitor_thread.stop_event.set()
        monitor_thread.join(timeout=5)  # Wait max 5 seconds
        if monitor_thread.is_alive():
            print("Warning: Monitor thread did not stop gracefully")

# ✅ Good: Use appropriate polling intervals
# Fast monitoring (0.1-0.5s) for real-time needs
# Normal monitoring (1-2s) for general use
# Slow monitoring (5-10s) for low-priority changes

# ❌ Bad: Not stopping monitoring threads
monitor_thread = session.file_system.watch_directory("/tmp", callback)
monitor_thread.start()
# Missing: monitor_thread.stop_event.set() and join()
```

## Integration with Other Modules

### FileSystem + Code Integration

```python
# Create data file
session.file_system.write_file("/tmp/data.json", '{"values": [1, 2, 3, 4, 5]}')

# Process with code
session.code.run_code("""
import json
with open('/tmp/data.json', 'r') as f:
    data = json.load(f)

processed = [x * 2 for x in data['values']]
result = {'original': data['values'], 'processed': processed}

with open('/tmp/result.json', 'w') as f:
    json.dump(result, f, indent=2)

print("Data processed and saved")
""", "python")

# Read result
result = session.file_system.read_file("/tmp/result.json")
```

### FileSystem + Command Integration

```python
# Create file with FileSystem
session.file_system.write_file("/tmp/data.txt", "line1\nline2\nline3")

# Process with commands
session.command.execute_command("wc -l /tmp/data.txt")
session.command.execute_command("sort /tmp/data.txt > /tmp/sorted.txt")

# Read result with FileSystem
result = session.file_system.read_file("/tmp/sorted.txt")
```

## Related Documentation

- **[Session API](../core/session.md)** - Session management and lifecycle
- **[Code Module](code.md)** - Code execution for file processing
- **[Command Module](command.md)** - Shell commands for file operations
- **[File Operations Guide](../../guides/file-operations.md)** - User guide for file operations
- **[Best Practices](../../guides/best-practices.md)** - Production deployment patterns