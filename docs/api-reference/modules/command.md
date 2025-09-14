# Command Module API Reference

The Command module provides shell command execution capabilities in the AGB cloud environment. It allows you to run shell commands with configurable timeouts and comprehensive output capture.

## Class Definition

```python
from agb.modules.command import Command, CommandResult

class Command(BaseService):
    def __init__(self, session)
```

## Methods

### `execute_command(command, timeout_ms=1000)`

Execute a shell command in the cloud environment with a specified timeout.

**Parameters:**
- `command` (str): The shell command to execute.
- `timeout_ms` (int, optional): The timeout for the command execution in milliseconds. Default is 1000ms (1 second).

**Returns:**
- `CommandResult`: Result object containing success status, command output, and error message if any.

**Example:**
```python
# Basic command execution
result = session.command.execute_command("ls -la")
if result.success:
    print("Command output:")
    print(result.output)
else:
    print("Command failed:", result.error_message)

# Command with custom timeout
result = session.command.execute_command("find / -name '*.txt'", timeout_ms=5000)
if result.success:
    print("Files found:")
    print(result.output)
```

## CommandResult Class

Result object returned by command execution operations.

For detailed information about the response object, see: **[CommandResult](../responses/command-result.md)**

### Usage Example

```python
result = session.command.execute_command("echo 'Hello World'")

print(f"Request ID: {result.request_id}")
print(f"Success: {result.success}")

if result.success:
    print(f"Output: {result.output}")
else:
    print(f"Error: {result.error_message}")
    # Output may still contain partial results
    if result.output:
        print(f"Partial output: {result.output}")
```

## Common Commands

### File System Operations

```python
# List directory contents
result = session.command.execute_command("ls -la /tmp")

# Check disk usage
result = session.command.execute_command("df -h")

# Find files
result = session.command.execute_command("find /tmp -name '*.txt'")

# Check file permissions
result = session.command.execute_command("ls -l /tmp/myfile.txt")

# Create directory
result = session.command.execute_command("mkdir -p /tmp/newdir")

# Remove files
result = session.command.execute_command("rm -f /tmp/tempfile.txt")
```

### System Information

```python
# System information
result = session.command.execute_command("uname -a")

# Process information
result = session.command.execute_command("ps aux")

# Memory information
result = session.command.execute_command("free -h")

# Current working directory
result = session.command.execute_command("pwd")

# Environment variables
result = session.command.execute_command("env")

# Current user
result = session.command.execute_command("whoami")
```

### Text Processing

```python
# Count lines in file
result = session.command.execute_command("wc -l /tmp/data.txt")

# Search in files
result = session.command.execute_command("grep 'pattern' /tmp/*.txt")

# Sort file contents
result = session.command.execute_command("sort /tmp/data.txt")

# Get first/last lines
result = session.command.execute_command("head -10 /tmp/data.txt")
result = session.command.execute_command("tail -10 /tmp/data.txt")
```

### Network Operations

```python
# Check network connectivity
result = session.command.execute_command("ping -c 3 google.com")

# Download files
result = session.command.execute_command("wget -O /tmp/file.txt https://example.com/file.txt")

# Check open ports
result = session.command.execute_command("netstat -tuln")
```

## Usage Patterns

### Basic Command Execution

```python
from agb import AGB

def execute_basic_commands():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        commands = [
            "echo 'Hello from AGB'",
            "date",
            "ls -la /tmp",
            "whoami"
        ]

        for cmd in commands:
            result = session.command.execute_command(cmd)
            print(f"Command: {cmd}")
            if result.success:
                print(f"Output: {result.output}")
            else:
                print(f"Error: {result.error_message}")
            print("-" * 40)

    finally:
        agb.delete(session)

execute_basic_commands()
```

### Command Chaining and Pipes

```python
def execute_piped_commands():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        # Create test data
        session.command.execute_command("echo -e 'apple\\nbanana\\ncherry\\napple\\ndate' > /tmp/fruits.txt")

        # Use pipes and command chaining
        piped_commands = [
            "cat /tmp/fruits.txt | sort",
            "cat /tmp/fruits.txt | sort | uniq",
            "cat /tmp/fruits.txt | grep 'a' | wc -l",
            "ls -la /tmp | grep '.txt' | wc -l"
        ]

        for cmd in piped_commands:
            result = session.command.execute_command(cmd, timeout_ms=2000)
            print(f"Command: {cmd}")
            if result.success:
                print(f"Output: {result.output.strip()}")
            else:
                print(f"Error: {result.error_message}")
            print("-" * 50)

    finally:
        agb.delete(session)

execute_piped_commands()
```

### File Processing Pipeline

```python
def file_processing_pipeline():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        # Step 1: Create sample data
        create_result = session.command.execute_command("""
        cat > /tmp/data.csv << EOF
name,age,city
Alice,25,New York
Bob,30,London
Charlie,35,Paris
Diana,28,Tokyo
EOF
        """)

        if not create_result.success:
            print("Failed to create data file")
            return

        # Step 2: Process the data
        commands = [
            # Show the data
            ("cat /tmp/data.csv", "Show original data"),

            # Count lines
            ("wc -l /tmp/data.csv", "Count lines"),

            # Extract names only
            ("cut -d',' -f1 /tmp/data.csv | tail -n +2", "Extract names"),

            # Sort by age (assuming age is in column 2)
            ("sort -t',' -k2 -n /tmp/data.csv", "Sort by age"),

            # Find people over 30
            ("awk -F',' '$2 > 30 {print $1, $2}' /tmp/data.csv", "People over 30")
        ]

        for cmd, description in commands:
            result = session.command.execute_command(cmd, timeout_ms=3000)
            print(f"{description}:")
            print(f"Command: {cmd}")
            if result.success:
                print(f"Output:\n{result.output}")
            else:
                print(f"Error: {result.error_message}")
            print("=" * 60)

    finally:
        agb.delete(session)

file_processing_pipeline()
```

### System Monitoring

```python
def system_monitoring():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        monitoring_commands = [
            ("uptime", "System uptime"),
            ("free -h", "Memory usage"),
            ("df -h", "Disk usage"),
            ("ps aux | head -10", "Top processes"),
            ("env | grep -E '^(PATH|HOME|USER)'", "Key environment variables")
        ]

        print("System Monitoring Report")
        print("=" * 50)

        for cmd, description in monitoring_commands:
            result = session.command.execute_command(cmd, timeout_ms=2000)
            print(f"\n{description}:")
            if result.success:
                print(result.output)
            else:
                print(f"Error: {result.error_message}")
            print("-" * 30)

    finally:
        agb.delete(session)

system_monitoring()
```

### Interactive Command Patterns

```python
def interactive_command_patterns():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        # Simulate interactive workflow
        workflow_steps = [
            # Step 1: Setup workspace
            ("mkdir -p /tmp/workspace && cd /tmp/workspace", "Create workspace"),

            # Step 2: Create files
            ("echo 'Hello World' > hello.txt", "Create hello.txt"),
            ("echo 'Goodbye World' > goodbye.txt", "Create goodbye.txt"),

            # Step 3: Verify files
            ("ls -la /tmp/workspace/", "List workspace files"),

            # Step 4: Process files
            ("cat /tmp/workspace/*.txt | wc -w", "Count words in all txt files"),

            # Step 5: Archive files
            ("cd /tmp/workspace && tar -czf archive.tar.gz *.txt", "Create archive"),

            # Step 6: Verify archive
            ("ls -la /tmp/workspace/archive.tar.gz", "Check archive"),
            ("tar -tzf /tmp/workspace/archive.tar.gz", "List archive contents")
        ]

        for cmd, description in workflow_steps:
            print(f"Step: {description}")
            result = session.command.execute_command(cmd, timeout_ms=3000)

            if result.success:
                print(f"✅ Success: {result.output.strip()}")
            else:
                print(f"❌ Failed: {result.error_message}")
                break  # Stop on first failure
            print()

    finally:
        agb.delete(session)

interactive_command_patterns()
```

### Error Handling and Debugging

```python
def command_error_handling():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        # Commands that might fail
        test_commands = [
            ("ls /nonexistent/directory", "List non-existent directory"),
            ("cat /nonexistent/file.txt", "Read non-existent file"),
            ("rm /protected/file", "Remove protected file"),
            ("invalid_command_xyz", "Invalid command"),
            ("sleep 10", "Long running command (will timeout)")
        ]

        for cmd, description in test_commands:
            print(f"Testing: {description}")
            print(f"Command: {cmd}")

            # Use short timeout for the sleep command
            timeout = 500 if "sleep" in cmd else 2000
            result = session.command.execute_command(cmd, timeout_ms=timeout)

            if result.success:
                print(f"✅ Success: {result.output}")
            else:
                print(f"❌ Error: {result.error_message}")
                if result.output:
                    print(f"Partial output: {result.output}")

            print("-" * 50)

    finally:
        agb.delete(session)

command_error_handling()
```

## Best Practices

### 1. Always Check Command Results

```python
# ✅ Good: Always check success status
result = session.command.execute_command("ls -la")
if result.success:
    print("Output:", result.output)
else:
    print("Command failed:", result.error_message)

# ❌ Bad: Assuming commands always succeed
result = session.command.execute_command("ls -la")
print(result.output)  # May be empty if command failed
```

### 2. Use Appropriate Timeouts

```python
# ✅ Good: Set timeouts based on expected execution time
quick_result = session.command.execute_command("echo hello", timeout_ms=1000)
long_result = session.command.execute_command("find / -name '*.log'", timeout_ms=30000)

# ❌ Avoid: Using very short timeouts for complex operations
result = session.command.execute_command("find / -name '*.log'", timeout_ms=100)  # Too short
```

### 3. Handle Command Output Properly

```python
# ✅ Good: Process output appropriately
result = session.command.execute_command("ls -la /tmp")
if result.success:
    lines = result.output.strip().split('\n')
    for line in lines:
        if line.startswith('-'):  # Regular files
            print(f"File: {line}")

# ✅ Good: Check for empty output
result = session.command.execute_command("find /tmp -name '*.nonexistent'")
if result.success:
    if result.output.strip():
        print("Found files:", result.output)
    else:
        print("No files found")
```

### 4. Use Safe Command Patterns

```python
# ✅ Good: Use safe file operations
def safe_file_operation(session, filepath):
    # Check if file exists first
    check_result = session.command.execute_command(f"test -f {filepath}")
    if check_result.success:
        # File exists, safe to operate
        return session.command.execute_command(f"cat {filepath}")
    else:
        return CommandResult(success=False, error_message="File does not exist")

# ✅ Good: Use absolute paths
result = session.command.execute_command("ls -la /tmp/myfile.txt")

# ❌ Avoid: Relative paths can be unpredictable
result = session.command.execute_command("ls -la myfile.txt")
```

### 5. Validate Command Input

```python
def safe_command_execution(session, command, timeout_ms=1000):
    """Execute command with basic validation"""

    # Basic validation
    if not command.strip():
        return {"success": False, "error": "Empty command"}

    # Length check
    if len(command) > 1000:
        return {"success": False, "error": "Command too long"}

    # Check for dangerous patterns (optional)
    dangerous_patterns = ["rm -rf /", ":(){ :|:& };:", "dd if=/dev/zero"]
    for pattern in dangerous_patterns:
        if pattern in command:
            return {"success": False, "error": f"Potentially dangerous command: {pattern}"}

    # Execute command
    result = session.command.execute_command(command, timeout_ms)

    return {
        "success": result.success,
        "output": result.output,
        "error": result.error_message if not result.success else None,
        "request_id": result.request_id
    }
```

## Error Handling

### Common Error Types

**Command Not Found:**
```python
result = session.command.execute_command("nonexistent_command")
if not result.success:
    if "command not found" in result.error_message.lower():
        print("Command does not exist")
```

**Permission Denied:**
```python
result = session.command.execute_command("cat /etc/shadow")
if not result.success:
    if "permission denied" in result.error_message.lower():
        print("Insufficient permissions")
```

**Timeout Errors:**
```python
result = session.command.execute_command("sleep 10", timeout_ms=1000)
if not result.success:
    if "timeout" in result.error_message.lower():
        print("Command timed out")
```

**File Not Found:**
```python
result = session.command.execute_command("cat /nonexistent/file.txt")
if not result.success:
    if "no such file" in result.error_message.lower():
        print("File does not exist")
```

### Robust Error Handling Pattern

```python
def robust_command_execution(session, command, max_retries=3):
    """Execute command with retry logic"""

    for attempt in range(max_retries):
        try:
            result = session.command.execute_command(command, timeout_ms=5000)

            if result.success:
                return result
            else:
                print(f"Attempt {attempt + 1} failed: {result.error_message}")

                # Don't retry certain types of errors
                if any(error_type in result.error_message.lower() for error_type in
                       ["command not found", "permission denied", "no such file"]):
                    print("Non-retryable error, stopping")
                    break

                if attempt < max_retries - 1:
                    print("Retrying...")

        except Exception as e:
            print(f"Attempt {attempt + 1} exception: {e}")
            if attempt < max_retries - 1:
                print("Retrying...")

    return None  # All attempts failed

# Usage
result = robust_command_execution(session, "ls -la /tmp")
if result and result.success:
    print("Command succeeded:", result.output)
else:
    print("Command failed after all retries")
```

## Integration with Other Modules

### Command + Code Integration

```python
# Use commands to setup environment for code execution
session.command.execute_command("mkdir -p /tmp/data")
session.command.execute_command("echo 'sample,data\\n1,2\\n3,4' > /tmp/data/input.csv")

# Process with code
code_result = session.code.run_code("""
import csv
with open('/tmp/data/input.csv', 'r') as f:
    reader = csv.reader(f)
    data = list(reader)
    print("Data loaded:", data)
""", "python")

# Verify with commands
verify_result = session.command.execute_command("ls -la /tmp/data/")
```

### Command + FileSystem Integration

```python
# Create file with FileSystem module
session.file_system.write_file("/tmp/test.txt", "Hello World")

# Process with commands
result = session.command.execute_command("wc -w /tmp/test.txt")
print("Word count:", result.output)

# Read result with FileSystem module
processed_result = session.file_system.read_file("/tmp/test.txt")
```

## Related Documentation

- **[Session API](../core/session.md)** - Session management and lifecycle
- **[Code Module](code.md)** - Code execution for complex processing
- **[FileSystem Module](filesystem.md)** - File operations integration
- **[Command Execution Tutorial](../../guides/command-execution.md)** - User guide for command execution
- **[Best Practices](../../guides/best-practices.md)** - Production deployment patterns