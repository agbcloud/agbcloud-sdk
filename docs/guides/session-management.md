# Session Management Guide

## Overview

Sessions are the core concept in AGB SDK. A session represents an isolated cloud environment where you can execute code, run commands, manage files, and interact with cloud storage. This guide covers everything you need to know about managing sessions effectively.
**Important**: Image ID Management. When creating sessions, you need to specify an appropriate `image_id`. Please ensure you use valid image IDs that are available in your account. You can view and manage your available images in the [AGB Console Image Management](https://agb.cloud/console/image-management) page.

## Quick Reference (1 minute)
```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()

# Create session
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)

if result.success:
    session = result.session


# Clean up
agb.delete(session)
    # Use session modules
    session.code.run_code("print('Hello')", "python")
    session.command.execute_command("ls /tmp")
    session.file_system.read_file("/path/to/file")

    # Clean up
    agb.delete(session)
else:
    print(f"Failed to create session: {result.error_message}")
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
from agb import AGB
from agb.session_params import CreateSessionParams

# Custom session with specific image
params = CreateSessionParams(
    image_id="agb-code-space-1"
)

result = agb.create(params)

if result.success:
    session = result.session
    # Use session...
else:
    print(f"Failed to create session: {result.error_message}")
```

### Session Labels Management

Labels help organize and categorize sessions for easier management. You can set labels when creating sessions or manage them after session creation.

#### Creating Sessions with Labels

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()

# Create session with labels
params = CreateSessionParams(
    image_id="agb-code-space-1",
    labels={"project": "demo", "environment": "testing", "team": "backend"}
)
result = agb.create(params)
if result.success:
    session = result.session
    print(f"Session created with labels: {session.session_id}")
```

#### Setting Session Labels

```python
# Set labels for an existing session
labels = {"project": "demo", "environment": "production", "version": "v1.2.0"}
result = session.set_labels(labels)

if result.success:
    print("Labels set successfully")
else:
    print(f"Failed to set labels: {result.error_message}")
```

#### Getting Session Labels

```python
# Get current session labels
result = session.get_labels()

if result.success:
    print("Current session labels:")
    for key, value in result.data.items():
        print(f"  {key}: {value}")
else:
    print(f"Failed to get labels: {result.error_message}")
```

#### Label Validation

The AGB SDK automatically validates labels to ensure they meet the requirements:

```python
# Valid labels
valid_labels = {
    "project": "my-project",
    "environment": "staging",
    "team": "data-science"
}

# Invalid labels (will fail validation)
invalid_labels = {
    "": "empty-key",          # Empty key
    "project": "",            # Empty value
    "team": None,             # None value
    "invalid-list-key": "list-key"   # Non-string key
}

# Set labels with validation
result = session.set_labels(valid_labels)
if not result.success:
    print(f"Label validation failed: {result.error_message}")
```

### Session Information

```python
# Get session details
info_result = session.info()
if info_result.success:
    data = info_result.data
    print(f"Session ID: {data.get('session_id', 'N/A')}")
    print(f"Resource URL: {data.get('resource_url', 'N/A')}")
    print(f"Desktop Info: {data.get('app_id', 'N/A')}")
```

### Listing Sessions

The `list()` method allows you to query and retrieve session IDs from your AGB account. This is useful for managing multiple sessions, monitoring active environments, and organizing your cloud resources.

#### Basic Usage

```python
from agb import AGB

# Initialize the SDK
agb = AGB()

# List all active sessions
result = agb.list()

if result.success:
    print(f"Found {result.total_count} total sessions")
    print(f"Showing {len(result.session_ids)} session IDs on this page")
    print(f"Request ID: {result.request_id}")

    for session_id in result.session_ids:
        print(f"Session ID: {session_id}")
else:
    print(f"Failed to list sessions: {result.error_message}")

# Output:
# Found 0 total sessions
# Showing 0 session IDs on this page
# Request ID: 6620****-****-****-****-********C2C1
```

#### Filtering by Labels

You can filter sessions by labels to find specific environments:

```python
from agb import AGB

# Initialize the SDK
agb = AGB()

# List sessions with specific labels
result = agb.list(labels={"project": "demo", "environment": "testing"})

if result.success:
    print(f"Found {len(result.session_ids)} sessions matching the labels")
    for session_id in result.session_ids:
        print(f"Session ID: {session_id}")

# Output (after creating a session with matching labels):
# Found 1 sessions matching the labels
# Session ID: session-**********************sic
```

#### Pagination

For accounts with many sessions, use pagination to retrieve results in manageable chunks:

```python
from agb import AGB

# Initialize the SDK
agb = AGB()

# Get page 2 with 10 items per page
result = agb.list(labels={"project": "demo"}, page=2, limit=10)

if result.success:
    print(f"Page 2 of results (showing {len(result.session_ids)} sessions)")
    print(f"Total sessions: {result.total_count}")
    print(f"Next page token: {result.next_token}")

# Output (when there are no sessions on page 2):
# Page 2 of results (showing 0 sessions)
# Total sessions: 0
# Next page token: None
```

#### Important Notes

**Active Sessions Only:**
- The `list()` method **only returns currently active sessions**
- Sessions that have been deleted or released (either manually via `delete()` or automatically due to timeout) will **not** be included in the results
- To check if a specific session is still active, use the `get()` method or `session.info()` method

**Return Value:**
- The method returns session IDs (strings) rather than full Session objects
- Use `agb.get(session_id)` to retrieve a full Session object if needed

**Key Features:**
- **Flexible Filtering**: List all sessions or filter by any combination of labels
- **Pagination Support**: Use `page` and `limit` parameters for easy pagination
- **Request ID**: All responses include a `request_id` for tracking and debugging
- **Efficient**: Returns only session IDs for better performance


### Deleting Sessions

```python
# Delete a specific session
delete_result = agb.delete(session)
if delete_result.success:
    print("Session deleted successfully")
else:
    print(f"Failed to delete session: {delete_result.error_message}")
```


## Session Release

Sessions can be released in two ways, and understanding these mechanisms is crucial for proper session management.

### Release Mechanisms

**1. Manual Deletion**

You can manually delete a session using the `delete()` method:

```python
from agb import AGB

# Delete a session manually
delete_result = agb.delete(session)
if delete_result.success:
    print("Session deleted successfully")
else:
    print(f"Failed to delete session: {delete_result.error_message}")
```

**2. Automatic Timeout Release**

If you don't manually delete a session, it will be automatically released after a configured timeout period:

- **Configuration**: Timeout duration is set in the [AGB Console](https://agb.cloud/console)
- **Behavior**: Once the timeout is reached, the session is automatically released
- **Recovery**: After release (manual or automatic), the session cannot be recovered - the session ID becomes invalid

### Important Notes About Session Release

- Released sessions (either manually or by timeout) will **not** appear in `agb.list()` results
- Once released, all non-persistent data in the session is permanently lost
- Use [Context Synchronization](context-usage-guide.md) to preserve important data across sessions
- Session IDs become invalid after release and cannot be used for recovery

### Checking Session Status

Before attempting to recover a session, you can check if it's still active:

```python
from agb import AGB

# Check if a session is still active
agb = AGB()
sessions = agb.list()
session_ids = [session.session_id for session in sessions]

if "your_session_id" in session_ids:
    print("Session is still active")
else:
    print("Session has been released or does not exist")
```

## Session Recovery

In certain scenarios, you may need to recover a Session object using its session ID. The SDK provides the `get` method to retrieve an existing session.

### Using the get Method

The `get` method is the recommended way to recover a session. It retrieves session information from the cloud and returns a ready-to-use Session object with the API request ID.

```python
from agb import AGB

# Initialize the SDK
agb = AGB()

# Retrieve session using its ID
session_id = "your_existing_session_id"
get_result = agb.get(session_id)

if get_result.success:
    session = get_result.session
    print(f"Retrieved session: {session.session_id}")
    print(f"Request ID: {get_result.request_id}")

    # You can now perform any session operations
    result = session.command.execute_command("echo 'Hello, World!'")
    if result.success:
        print(result.output)
else:
    print(f"Failed to retrieve session: {get_result.error_message}")
```

### Important Considerations

**Session Recovery Limitations:**

1. **Released Sessions Cannot Be Recovered**: If the session ID corresponds to a cloud environment that has been actually released (either through active deletion via `Session.delete()` or automatic timeout release), it cannot be recovered using the session ID. In such cases, you must:
   - Create a new session
   - Use data persistence (see [Data Persistence Guide](../examples/data_persistence/README.md#data-persistence)) to restore your data

2. **Session Status Validation**: Use the `Session.info()` method to determine if a session has been released. Only active (non-released) sessions can return information through the info interface.

## Best Practices

### 1. Always Clean Up Sessions

```python
from agb import AGB
from agb.session_params import CreateSessionParams

# ✅ Good: Always delete sessions
agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)

if result.success:
    session = result.session

    try:
    # Your code here
        session.code.run_code("print('Hello')", "python")
    finally:
        agb.delete(session)
else:
    print(f"Failed to create session: {result.error_message}")

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
from agb import AGB
from agb.session_params import CreateSessionParams

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
from agb import AGB
from agb.session_params import CreateSessionParams

# ✅ Good: Organize sessions with meaningful labels
params = CreateSessionParams(
    image_id="agb-code-space-1",
    labels={
        "project": "data-pipeline",
        "environment": "production",
        "team": "analytics",
        "version": "v2.1.0"
    }
)

result = agb.create(params)

if result.success:
    session = result.session

    # ✅ Better: Use consistent labeling strategy
    class LabelManager:
        @staticmethod
        def create_project_labels(project_name: str, environment: str, **kwargs):
            """Create standardized labels for project sessions"""
            labels = {
                "project": project_name,
                "environment": environment,
                "created_by": "agb-sdk",
                "timestamp": str(int(time.time()))
            }
            labels.update(kwargs)
            return labels

    # Usage
    labels = LabelManager.create_project_labels(
        "ml-training",
        "staging",
        model_version="v1.3.2",
        gpu_enabled="true"
    )

    params = CreateSessionParams(image_id="agb-code-space-1", labels=labels)
    result = agb.create(params)

    if result.success:
        session = result.session

        # Update labels during session lifecycle
session.set_labels({
    **labels,
    "status": "training_complete",
    "accuracy": "0.94"
})
```

### 4. Monitor Resource Usage

```python
from contextlib import contextmanager

@contextmanager
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
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)

if result.success:
    session = result.session

    with monitor_session_usage(session, "data_processing") as monitored_session:
        monitored_session.code.run_code("import pandas as pd; print('Processing data...')", "python")

    agb.delete(session)
else:
    print(f"Failed to create session: {result.error_message}")
```


## Troubleshooting

### Common Issues

**Session Creation Fails**
```python
from agb import AGB
from agb.session_params import CreateSessionParams

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
from agb import AGB
from agb.session_params import CreateSessionParams

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
from agb import AGB
from agb.session_params import CreateSessionParams

# Monitor resource usage and recreate sessions periodically
operation_count = 0
max_operations_per_session = 100

for task in tasks:
    if operation_count >= max_operations_per_session:
        # Recreate session to free resources
        agb.delete(session)
        params = CreateSessionParams(image_id="agb-code-space-1")
        result = agb.create(params)

        if result.success:
            session = result.session
            operation_count = 0
        else:
            print(f"Failed to recreate session: {result.error_message}")
            break

    # Execute task
    session.code.run_code(task["code"], "python")
    operation_count += 1
```

## Related Documentation
- **[Code Execution Guide](code-execution.md)** - Using the code module
- **[Command Execution Tutorial](../guides/command-execution.md)** - Shell command operations
- **[File Operations Tutorial](../guides/file-operations.md)** - File system management
- **[Authentication Guide](authentication.md)** - API key setup and security
- **[API Reference](../api-reference/session.md)** - Complete session API documentation
