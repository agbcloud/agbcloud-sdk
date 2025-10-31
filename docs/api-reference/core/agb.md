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

### `list(labels=None, page=None, limit=None)`

Returns paginated list of session IDs filtered by labels.

#### Parameters

- **`labels`** (`Optional[Dict[str, str]]`, optional): Labels to filter sessions. Defaults to `None` (empty dict).
- **`page`** (`Optional[int]`, optional): Page number for pagination (starting from 1). Defaults to `None` (returns first page).
- **`limit`** (`Optional[int]`, optional): Maximum number of items per page. Defaults to `None` (uses default of 10).

#### Returns

- **`SessionListResult`**: Paginated list of session IDs that match the labels, including request_id, success status, and pagination information.

#### Examples

##### Basic Usage

```python
# List all sessions
result = agb.list()
if result.success:
    print(f"Found {result.total_count} total sessions")
    print(f"Showing {len(result.session_ids)} session IDs on this page")
    print(f"Request ID: {result.request_id}")

    for session_id in result.session_ids:
        print(f"Session ID: {session_id}")
else:
    print(f"Failed to list sessions: {result.error_message}")
```

##### Filtering by Labels

```python
# List sessions with specific labels
result = agb.list(labels={"project": "demo", "environment": "testing"})
if result.success:
    print(f"Found {len(result.session_ids)} sessions matching the labels")
    for session_id in result.session_ids:
        print(f"Session ID: {session_id}")
```

##### Pagination

```python
# Get page 2 with 5 items per page
result = agb.list(labels={"project": "demo"}, page=2, limit=5)
if result.success:
    print(f"Page 2 of results (showing {len(result.session_ids)} sessions)")
    print(f"Total sessions: {result.total_count}")
    print(f"Has more pages: {'yes' if result.next_token else 'no'}")
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

### `get(session_id)`

Get a session by its ID.

This method retrieves a session by calling the GetSession API and returns a SessionResult containing the Session object and request ID.

#### Parameters

- **`session_id`** (`str`): The ID of the session to retrieve.

#### Returns

- **`SessionResult`**: Result containing the Session instance, request ID, and success status.

#### Example

```python
# Get a session object
result = agb.get("your-session-id")
if result.success:
    session = result.session
    print(f"Session ID: {session.session_id}")
    print(f"Resource URL: {session.resource_url}")
    print(f"Request ID: {result.request_id}")

    # Use the session for operations
    # ... perform operations with session ...
else:
    print(f"Failed to get session: {result.error_message}")
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

### `context`
- **Type:** `ContextService`
- **Description:** Context service for managing session contexts and synchronization.

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

### GetSessionResult

Result object returned by get_session method.

```python
class GetSessionResult:
    request_id: str          # Unique request identifier
    http_status_code: int    # HTTP status code
    code: str               # Response code
    success: bool           # Whether the request succeeded
    data: GetSessionData    # Session data (if successful)
    error_message: str      # Error description (if failed)
```

### GetSessionData

Session data object contained in GetSessionResult.

```python
class GetSessionData:
    app_instance_id: str        # Application instance ID
    resource_id: str           # Resource ID
    session_id: str            # Session ID
    success: bool              # Success status
    http_port: str             # HTTP port
    network_interface_ip: str  # Network interface IP
    token: str                 # Authentication token
    vpc_resource: bool         # Whether it's a VPC resource
    resource_url: str          # Resource URL
```

### SessionListResult

Result object returned by the list method.

```python
class SessionListResult:
    request_id: str           # Unique request identifier
    success: bool            # Whether the request succeeded
    session_ids: List[str]   # List of session IDs
    next_token: str          # Token for next page (empty if no more pages)
    max_results: int         # Maximum results per page
    total_count: int         # Total number of sessions matching the filter
    error_message: str       # Error description (if failed)
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