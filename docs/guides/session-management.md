# Session Management Guide

## Overview

Sessions are the core concept in AGB SDK. A session represents an isolated cloud environment where you can execute code, run commands, manage files, and interact with cloud storage. This guide covers everything you need to know about managing sessions effectively.
**Important**: Image ID Management. When creating sessions, you need to specify an appropriate `image_id`. Please ensure you use valid image IDs that are available in your account You can view and manage your available images in the [AGB Console Image Management](https://agb.cloud/console/image-management) page.

## Quick Reference (1 minute)

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()

# Create session
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
session = result.session

# Use session modules
session.code.run_code("print('Hello')", "python")
session.command.execute_command("ls")
session.file_system.read_file("/path/to/file")
session.oss.upload_file("local.txt", "remote.txt")

# Clean up
agb.delete(session)
```

## Basic Usage (5 minutes)

### Creating Sessions

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()

# Simple session creation
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
if result.success:
    session = result.session
    print(f"Session created: {session.session_id}")
else:
    print(f"Failed to create session: {result.error_message}")
```

### Session Configuration

```python
# Custom session with specific image
params = CreateSessionParams(
    image_id="agb-code-space-1"
)

result = agb.create(params)
session = result.session
```

### Session Information

```python
# Get session details
info_result = session.info()
if info_result.success:
    data = info_result.data
    print(f"Session ID: {data.get('session_id')}")
    print(f"Resource URL: {data.get('resource_url')}")
    print(f"Desktop Info: {data.get('app_id', 'N/A')}")
```

### Listing Sessions

```python
# List all active sessions
sessions = agb.list()
print(f"Active sessions: {len(sessions)}")

for session in sessions:
    print(f"- {session.session_id}")
```

### Deleting Sessions

```python
# Delete a specific session
delete_result = agb.delete(session)
if delete_result.success:
    print("Session deleted successfully")
else:
    print(f"Failed to delete session: {delete_result.error_message}")
```

## Advanced Usage (15 minutes)

### Session Lifecycle Management

```python
class SessionManager:
    def __init__(self):
        self.agb = AGB()
        self.active_sessions = {}

    def create_session(self, name: str, image_id: str = None):
        """Create a named session with optional image ID"""
        params = CreateSessionParams(image_id=image_id or "agb-code-space-1")
        result = self.agb.create(params)

        if result.success:
            self.active_sessions[name] = result.session
            return result.session
        else:
            raise Exception(f"Failed to create session: {result.error_message}")

    def get_session(self, name: str):
        """Get session by name"""
        return self.active_sessions.get(name)

    def cleanup_all(self):
        """Clean up all managed sessions"""
        for name, session in self.active_sessions.items():
            try:
                self.agb.delete(session)
                print(f"Deleted session: {name}")
            except Exception as e:
                print(f"Error deleting session {name}: {e}")

        self.active_sessions.clear()

# Usage
manager = SessionManager()

# Create multiple sessions
dev_session = manager.create_session("development", "agb-code-space-1")
test_session = manager.create_session("testing", "agb-code-space-1")

# Use sessions
dev_session.code.run_code("print('Development environment')", "python")
test_session.code.run_code("print('Testing environment')", "python")

# Cleanup
manager.cleanup_all()
```

### Concurrent Session Management

```python
import concurrent.futures
from typing import List, Dict, Any

def create_session_with_task(agb: AGB, task_config: Dict[str, Any]):
    """Create session and execute a task"""
    params = CreateSessionParams(image_id=task_config.get("image_id", "agb-code-space-1"))
    result = agb.create(params)

    if not result.success:
        return {"error": result.error_message}

    session = result.session

    try:
        # Execute the task
        code_result = session.code.run_code(
            task_config["code"],
            task_config.get("language", "python")
        )

        return {
            "session_id": session.session_id,
            "result": code_result.result if code_result.success else code_result.error_message,
            "success": code_result.success
        }
    finally:
        # Always clean up
        agb.delete(session)

# Execute multiple tasks concurrently
agb = AGB()
tasks = [
    {"code": "print('Task 1')", "image_id": "agb-code-space-1"},
    {"code": "print('Task 2')", "image_id": "agb-code-space-1"},
    {"code": "print('Task 3')", "image_id": "agb-code-space-1"},
]

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(create_session_with_task, agb, task)
        for task in tasks
    ]

    results = [future.result() for future in concurrent.futures.as_completed(futures)]

for result in results:
    print(f"Session {result.get('session_id', 'unknown')}: {result.get('result', result.get('error'))}")
```

### Session Monitoring and Health Checks

```python
import time
from typing import Optional

class SessionMonitor:
    def __init__(self, session):
        self.session = session
        self.last_health_check = None

    def health_check(self) -> bool:
        """Check if session is healthy"""
        try:
            # Simple health check - execute a basic command
            result = self.session.code.run_code("print('health_check')", "python")
            self.last_health_check = time.time()
            return result.success
        except Exception:
            return False

    def get_session_info(self) -> Optional[dict]:
        """Get detailed session information"""
        try:
            info_result = self.session.info()
            return info_result.data if info_result.success else None
        except Exception:
            return None

    def is_session_active(self) -> bool:
        """Check if session is still active"""
        info = self.get_session_info()
        return info is not None

# Usage
agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
session = result.session

monitor = SessionMonitor(session)

# Periodic health checks
for i in range(5):
    if monitor.health_check():
        print(f"Health check {i+1}: OK")
        info = monitor.get_session_info()
        if info:
            print(f"  Session ID: {info.get('session_id')}")
    else:
        print(f"Health check {i+1}: FAILED")
        break

    time.sleep(2)

# Cleanup
agb.delete(session)
```


## Best Practices

### 1. Always Clean Up Sessions

```python
# ✅ Good: Always delete sessions
agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
session = result.session

try:
    # Your code here
    session.code.run_code("print('Hello')", "python")
finally:
    agb.delete(session)

# ✅ Better: Use context manager pattern
class SessionContext:
    def __init__(self, agb: AGB):
        self.agb = agb
        self.session = None

    def __enter__(self):
        params = CreateSessionParams(image_id="agb-code-space-1")
        result = self.agb.create(params)
        if not result.success:
            raise Exception(f"Failed to create session: {result.error_message}")
        self.session = result.session
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.agb.delete(self.session)

# Usage
agb = AGB()
with SessionContext(agb) as session:
    session.code.run_code("print('Hello')", "python")
# Session automatically cleaned up
```

### 2. Handle Errors Gracefully

```python
def safe_session_operation(agb: AGB, operation_func):
    """Safely execute an operation with proper error handling"""
    params = CreateSessionParams(image_id="agb-code-space-1")
    result = agb.create(params)
    if not result.success:
        return {"success": False, "error": result.error_message}

    session = result.session

    try:
        return operation_func(session)
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        try:
            agb.delete(session)
        except Exception as cleanup_error:
            print(f"Warning: Failed to cleanup session: {cleanup_error}")

# Usage
def my_operation(session):
    result = session.code.run_code("print('Hello')", "python")
    return {"success": result.success, "output": result.result}

agb = AGB()
result = safe_session_operation(agb, my_operation)
print(result)
```

### 3. Use Labels for Organization

```python
# Organize sessions with meaningful image IDs
params = CreateSessionParams(image_id="agb-code-space-1")

result = agb.create(params)
```

### 4. Monitor Resource Usage

```python
def monitor_session_usage(session, operation_name: str):
    """Monitor session resource usage during operations"""
    start_time = time.time()

    # Get initial session info
    initial_info = session.info()

    try:
        # Your operation here
        yield session
    finally:
        # Get final session info
        final_info = session.info()
        duration = time.time() - start_time

        print(f"Operation '{operation_name}' completed in {duration:.2f}s")
        if initial_info.success and final_info.success:
            print("Session remained healthy throughout operation")

# Usage
agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
session = result.session

with monitor_session_usage(session, "data_processing") as monitored_session:
    monitored_session.code.run_code("import pandas as pd; print('Processing data...')", "python")

agb.delete(session)
```

## Troubleshooting

### Common Issues

**Session Creation Fails**
```python
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
if not result.success:
    print(f"Error: {result.error_message}")
    # Common causes:
    # - Invalid API key
    # - Network connectivity issues
    # - Service temporarily unavailable
    # - Account limits exceeded
```

**Session Becomes Unresponsive**
```python
# Check session health
info_result = session.info()
if not info_result.success:
    print("Session may be unresponsive, creating new session...")
    agb.delete(session)  # Clean up old session
    params = CreateSessionParams(image_id="agb-code-space-1")
    result = agb.create(params)  # Create new session
```

**Memory or Resource Limits**
```python
# Monitor resource usage and recreate sessions periodically
operation_count = 0
max_operations_per_session = 100

for task in tasks:
    if operation_count >= max_operations_per_session:
        # Recreate session to free resources
        agb.delete(session)
        params = CreateSessionParams(image_id="agb-code-space-1")
        result = agb.create(params)
        session = result.session
        operation_count = 0

    # Execute task
    session.code.run_code(task["code"], "python")
    operation_count += 1
```

## Related Documentation

- **[Code Execution Guide](code-execution.md)** - Using the code module
- **[Command Execution Tutorial](../guides/command-execution.md)** - Shell command operations
- **[File Operations Tutorial](../guides/file-operations.md)** - File system management
- **[Authentication Guide](authentication.md)** - API key setup and security
- **[API Reference](../api-reference/core/session.md)** - Complete session API documentation