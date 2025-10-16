# AGB API Reference

The main client class for interacting with the AGB cloud runtime environment.

## Class Definition

```python
class AGB:
    def __init__(self, api_key: str = "", cfg: Optional[Config] = None)
```

## Constructor

### Parameters

#### `api_key`
- **Type:** `str`
- **Default:** `""`
- **Description:** API key for authentication. If not provided, it will be loaded from the `AGB_API_KEY` environment variable.

#### `cfg`
- **Type:** `Optional[Config]`
- **Default:** `None`
- **Description:** Configuration object. If not provided, default configuration will be used.

### Example

```python
from agb import AGB

# Using API key directly
agb = AGB(api_key="your_api_key_here")

# Using environment variable
# Set AGB_API_KEY environment variable first
agb = AGB()

# With custom configuration
from agb.config import Config
config = Config(endpoint="https://custom.endpoint.com")
agb = AGB(api_key="your_api_key", cfg=config)
```

## Methods

### `create(params=None)`

Create a new session in the AGB cloud environment.

#### Parameters

- **`params`** (`Optional[CreateSessionParams]`): Parameters for creating the session. Defaults to `None`.

#### Returns

- **`SessionResult`**: Result containing the created session and request ID.

#### Example

```python
from agb.session_params import CreateSessionParams

# Create with default parameters
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
if result.success:
    session = result.session
    print(f"Created session: {session.session_id}")

# Create with custom parameters
params = CreateSessionParams(
    image_id="agb-code-space-1"
)
result = agb.create(params)
```

### `list()`

List all available sessions.

#### Returns

- **`List[BaseSession]`**: A list of all available sessions.

#### Example

```python
sessions = agb.list()
for session in sessions:
    print(f"Session ID: {session.session_id}")
    if hasattr(session, 'image_id'):
        print(f"Image ID: {session.image_id}")
```

### `delete(session, sync_context=False)`

Delete a session by session object.

#### Parameters

- **`session`** (`BaseSession`): The session to delete.
- **`sync_context`** (`bool`, optional): Whether to sync context before deletion. Defaults to `False`.

#### Returns

- **`DeleteResult`**: Result indicating success or failure and request ID.

#### Example

```python
# Create a session
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
if result.success:
    session = result.session

    # Use the session
    # ... perform operations ...

    # Delete the session without context sync
    delete_result = agb.delete(session)
    if delete_result.success:
        print("Session deleted successfully")
    else:
        print(f"Failed to delete session: {delete_result.error_message}")

    # Delete the session with context sync
    delete_result = agb.delete(session, sync_context=True)
    if delete_result.success:
        print("Session deleted with context sync")
    else:
        print(f"Failed to delete session: {delete_result.error_message}")
```

## Properties

### `api_key`
- **Type:** `str`
- **Description:** The API key used for authentication.

### `endpoint`
- **Type:** `str`
- **Description:** The API endpoint URL.

### `timeout_ms`
- **Type:** `int`
- **Description:** Request timeout in milliseconds. Maximum allowed timeout is 60 seconds (60000ms).

### `client`
- **Type:** `Client`
- **Description:** The underlying HTTP client for API communication.

## Response Objects

### SessionResult

Result object returned by session creation methods.

```python
class SessionResult:
    request_id: str          # Unique request identifier
    success: bool           # Whether session creation succeeded
    session: BaseSession    # The created session (if successful)
    error_message: str      # Error description (if failed)
```

### DeleteResult

Result object returned by session deletion methods.

```python
class DeleteResult:
    request_id: str     # Unique request identifier
    success: bool      # Whether deletion succeeded
    error_message: str # Error description (if failed)
```

## Configuration

### Environment Variables

- **`AGB_API_KEY`**: API key for authentication (used when not provided in constructor)

### Default Configuration

```python
# Default endpoint and timeout
default_config = {
    "endpoint": "sdk-api.agb.cloud",
    "timeout_ms": 30000  # 30 seconds (maximum: 60000ms = 60 seconds)
}
```

## Best Practices

### 1. Always Check Results

```python
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
if result.success:
    # Proceed with session
    session = result.session
else:
    # Handle error
    print(f"Error: {result.error_message}")
```

### 2. Proper Resource Management

```python
# Always clean up sessions
try:
    params = CreateSessionParams(image_id="agb-code-space-1")
    result = agb.create(params)
    if result.success:
        session = result.session
        # ... use session ...
finally:
    if 'session' in locals():
        agb.delete(session, sync_context=True)
```

### 3. Use Environment Variables for API Keys

```bash
# Set environment variable
export AGB_API_KEY="your_api_key_here"
```

```python
# Use environment variable
agb = AGB()  # Automatically uses AGB_API_KEY
```

### 4. Set Appropriate Timeouts

```python
# Use appropriate timeout values based on your needs
# Default: 30 seconds, Maximum: 60 seconds
config = Config(timeout_ms=45000)  # 45 seconds
agb = AGB(api_key="your_key", cfg=config)

# For quick operations
quick_config = Config(timeout_ms=10000)  # 10 seconds

# For long-running operations (up to the 60s limit)
long_config = Config(timeout_ms=60000)  # 60 seconds (maximum)
```

### 5. Handle Network Errors

```python
import time

def create_session_with_retry(agb, max_retries=3):
    for attempt in range(max_retries):
        try:
            params = CreateSessionParams(image_id="agb-code-space-1")
    result = agb.create(params)
            if result.success:
                return result
            else:
                print(f"Attempt {attempt + 1} failed: {result.error_message}")
        except Exception as e:
            print(f"Network error on attempt {attempt + 1}: {e}")

        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff

    return None
```

## Related Content

- 📋 **Parameters**: [Session Parameters](./session-params.md)
- 🔧 **Sessions**: [Session API](./session.md)
- 💡 **Examples**: [Usage Examples](../../examples/README.md)
- 📚 **Guides**: [Best Practices](../../guides/best-practices.md)