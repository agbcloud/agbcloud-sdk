# DeleteResult

`DeleteResult` is the response type returned by session deletion operations in the AGB SDK.

## Overview

The `DeleteResult` class represents the outcome of operations that delete resources, such as `AGB.delete()`.

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `error_message` | `str` | Error message if the operation failed |

## Usage

```python
from agb import AGB

# Initialize AGB client
agb = AGB()

# Create a session first
result = agb.create()
if result.success:
    session = result.session

    # Delete the session
    delete_result = agb.delete(session)

    # Check if deletion was successful
    if delete_result.success:
        print("Session deleted successfully")
        print(f"Request ID: {delete_result.request_id}")
    else:
        print(f"Failed to delete session: {delete_result.error_message}")
```

## Success Response

When the operation is successful:

```python
delete_result.success = True
delete_result.error_message = ""
delete_result.request_id = "req_123456789"
```

## Error Response

When the operation fails:

```python
delete_result.success = False
delete_result.error_message = "Session not found or already deleted"
delete_result.request_id = "req_123456789"
```

## Methods

All response objects inherit from `ApiResponse` and have access to the `request_id` property for tracking API requests.

## Common Error Scenarios

### Session Not Found
```python
# Attempting to delete a non-existent session
delete_result.error_message = "Session not found"
```

### Session Already Deleted
```python
# Attempting to delete an already deleted session
delete_result.error_message = "Session already deleted"
```

### Permission Denied
```python
# Insufficient permissions to delete the session
delete_result.error_message = "Permission denied"
```

## Related Types

- **[SessionResult](session-result.md)** - Result type for session creation
- **[BaseSession](../core/session.md)** - The session object to be deleted

## Best Practices

### Always Check Success
```python
delete_result = agb.delete(session)

if delete_result.success:
    print("Session deleted successfully")
else:
    print(f"Deletion failed: {delete_result.error_message}")
    # Log the request ID for debugging
    print(f"Request ID: {delete_result.request_id}")
```

### Error Handling
```python
try:
    delete_result = agb.delete(session)
    if not delete_result.success:
        # Handle specific error cases
        if "not found" in delete_result.error_message.lower():
            print("Session was already deleted")
        else:
            print(f"Unexpected error: {delete_result.error_message}")
except Exception as e:
    print(f"Exception during deletion: {e}")
```

## Example: Complete Session Lifecycle

```python
from agb import AGB

agb = AGB()

# Create session
create_result = agb.create()
if create_result.success:
    session = create_result.session
    print(f"Created session: {session.session_id}")

    # Use session...
    # ... perform operations ...

    # Delete session
    delete_result = agb.delete(session)
    if delete_result.success:
        print("Session deleted successfully")
    else:
        print(f"Failed to delete: {delete_result.error_message}")
else:
    print(f"Failed to create session: {create_result.error_message}")
```
