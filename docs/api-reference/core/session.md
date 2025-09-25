# Session API Reference

Session classes represent active sessions in the AGB cloud environment. They provide access to various modules and session management functionality.

## Class Hierarchy

```python
BaseSession
└── Session (backward compatibility)
```

## BaseSession Class

The base class for all session types, providing common functionality.

### Class Definition

```python
class BaseSession:
    def __init__(self, agb: "AGB", session_id: str)
```

### Properties

#### `session_id`
- **Type:** `str`
- **Description:** Unique identifier for the session.

#### `resource_url`
- **Type:** `str`
- **Description:** URL for accessing session resources.

#### `image_id`
- **Type:** `str`
- **Description:** ID of the image used for this session.

### Module Access

All sessions have access to the following modules:

#### `code`
- **Type:** `Code`
- **Description:** Code execution module (Python, JavaScript).

#### `command`
- **Type:** `Command`
- **Description:** Shell command execution module.

#### `file_system`
- **Type:** `FileSystem`
- **Description:** File and directory operations module.


### Methods

#### `info()`

Get detailed session information including resource details.

**Returns:**
- `OperationResult`: Result containing session information and operation status.

**Example:**
```python
info_result = session.info()
if info_result.success:
    data = info_result.data
    print(f"Session ID: {data['session_id']}")
    print(f"Resource URL: {data['resource_url']}")
else:
    print(f"Failed to get session info: {info_result.error_message}")
```

#### `get_api_key()`

Get the API key associated with this session.

**Returns:**
- `str`: The API key.

#### `get_session_id()`

Get the session ID.

**Returns:**
- `str`: The session ID.

#### `get_client()`

Get the HTTP client for making API calls.

**Returns:**
- `Client`: The HTTP client instance.

## Session Class

Backward compatibility class that extends BaseSession.

### Class Definition

```python
class Session(BaseSession):
    def __init__(self, agb: "AGB", session_id: str)
```

This class is identical to BaseSession and is kept for backward compatibility.

## Usage Examples

### Basic Session Usage

```python
from agb import AGB
from agb.session_params import CreateSessionParams

# Create AGB client
agb = AGB(api_key="your_api_key")

# Create a session
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
if result.success:
    session = result.session

    # Use different modules
    code_result = session.code.run_code("print('Hello World')", "python")
    cmd_result = session.command.execute_command("ls -la")
    file_content = session.file_system.read_file("/path/to/file")

    # Get session information
    info = session.info()
    if info.success:
        print(f"Session info: {info.data}")
```

### Module Availability

All sessions have access to all modules:

```python
# Check module availability (all will be True)
print(hasattr(session, 'code'))        # True
print(hasattr(session, 'command'))     # True
print(hasattr(session, 'file_system')) # True
```

### Session Information

```python
# Get detailed session information
info_result = session.info()
if info_result.success:
    data = info_result.data

    # Basic session info
    session_id = data.get('session_id')
    resource_url = data.get('resource_url')

    # Desktop info (if available)
    if 'app_id' in data:
        app_id = data['app_id']
        auth_code = data['auth_code']
        ticket = data['ticket']

    print(f"Session {session_id} is ready at {resource_url}")
```

## Error Handling

### Session Creation Errors

```python
from agb import AGB
from agb.session_params import CreateSessionParams

params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
if not result.success:
    print(f"Session creation failed: {result.error_message}")
    if result.request_id:
        print(f"Request ID: {result.request_id}")
```

### Module Operation Errors

```python
# Code execution with error handling
try:
    result = session.code.run_code("invalid python code", "python")
    if result.success:
        print(f"Output: {result.result}")
    else:
        print(f"Code execution failed: {result.error_message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

### 1. Always Check Results

```python
result = session.code.run_code(code, "python")
if result.success:
    # Process successful result
    output = result.result
else:
    # Handle error
    print(f"Error: {result.error_message}")
```

### 2. Session Lifecycle Management

```python
from agb import AGB
from agb.session_params import CreateSessionParams

try:
    # Create session
    params = CreateSessionParams(image_id="agb-code-space-1")
    result = agb.create(params)
    if result.success:
        session = result.session

        # Use session
        # ... perform operations ...

finally:
    # Always clean up
    if 'session' in locals():
        agb.delete(session)
```

### 3. Resource Management

```python
from agb import AGB
from agb.session_params import CreateSessionParams

# Use context manager pattern (if available)
def with_session(agb, operation):
    params = CreateSessionParams(image_id="agb-code-space-1")
    result = agb.create(params)
    if not result.success:
        raise Exception(f"Failed to create session: {result.error_message}")

    try:
        session = result.session
        return operation(session)
    finally:
        agb.delete(session)

# Usage
def my_operation(session):
    return session.code.run_code("print('Hello')", "python")

result = with_session(agb, my_operation)
```

## Related Content

- 🔧 **API Reference**: [AGB API](agb.md)
- 📋 **Parameters**: [Session Parameters](session-params.md)
- 💡 **Examples**: [Session Examples](../../examples/README.md)
- 📚 **Guides**: [Session Management](../../guides/session-management.md)