# SessionResult

`SessionResult` is the response type returned by session creation operations in the AGB SDK.

## Overview

The `SessionResult` class represents the outcome of operations that create or return a session object, such as `AGB.create()`.

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `error_message` | `str` | Error message if the operation failed |
| `session` | `Optional[BaseSession]` | The session object (if successful) |

## Usage

```python
from agb import AGB
from agb.session_params import CreateSessionParams

# Initialize AGB client
agb = AGB()

# Create a session
params = CreateSessionParams(
    image_id="agb-code-space-1"
)
result = agb.create(params)

# Check if successful
if result.success:
    session = result.session
    print(f"Session created: {session.session_id}")
    print(f"Request ID: {result.request_id}")
else:
    print(f"Failed to create session: {result.error_message}")
```

## Success Response

When the operation is successful:

```python
result.success = True
result.session = <Session object>
result.error_message = ""
result.request_id = "req_123456789"
```

## Error Response

When the operation fails:

```python
result.success = False
result.session = None
result.error_message = "Invalid image_id provided"
result.request_id = "req_123456789"
```

## Methods

All response objects inherit from `ApiResponse` and have access to the `request_id` property for tracking API requests.

## Related Types

- **[BaseSession](../core/session.md)** - The session object returned on success
- **[CreateSessionParams](../core/session-params.md)** - Parameters for session creation
- **[DeleteResult](delete-result.md)** - Result type for session deletion

## Error Handling

Always check the `success` property before accessing the `session`:

```python
result = agb.create(params)

if result.success:
    # Safe to access session
    session = result.session
    # Use session...
else:
    # Handle error
    print(f"Error: {result.error_message}")
    print(f"Request ID: {result.request_id}")
```
