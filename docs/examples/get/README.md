# Get API Example

This example demonstrates how to use the `get` API to retrieve a session by its ID.

## Description

The `get` API allows you to retrieve a session object by providing its session ID. This is useful when you have a session ID from a previous operation and want to access or manage that session.

## Prerequisites

- Python 3.10 or higher
- Valid API key set in `AGB_API_KEY` environment variable
- agb package installed

## Installation

```bash
pip install agbcloud-sdk
```

## Usage

```bash
# Set your API key
export AGB_API_KEY="your-api-key-here"

# Run the example
python main.py
```

## Code Example

```python
import os
from agb import AGB

# Initialize AGB client
api_key = os.getenv("AGB_API_KEY")
agb = AGB(api_key=api_key)

# Retrieve a session by ID
session_id = "your-session-id"
result = agb.get(session_id)

if result.success:
    session = result.session
    print(f"Retrieved session: {session.session_id}")
    print(f"Request ID: {result.request_id}")
    # Use the session for further operations
    # ...
else:
    print(f"Failed to get session: {result.error_message}")
```

## API Reference

### get

```python
def get(session_id: str) -> SessionResult
```

Get a session by its ID.

This method retrieves a session by calling the GetSession API
and returns a SessionResult containing the Session object and request ID.

**Parameters:**
- `session_id` (str): The ID of the session to retrieve

**Returns:**
- `SessionResult`: Result object containing:
  - `success` (bool): Whether the operation succeeded
  - `session` (Session): The Session instance if successful
  - `request_id` (str): The API request ID
  - `error_message` (str): Error message if failed

## Expected Output

```
Creating a session...
Created session with ID: session-xxxxxxxxxxxxx

Retrieving session using Get API...
Successfully retrieved session:
  Session ID: session-xxxxxxxxxxxxx
  Request ID: DAD825FE-2CD8-19C8-BB30-CC3BA26B9398
  Resource URL: https://example.com/resource
  Resource ID: resource-xxxxxxxxxxxxx
  App Instance ID: app-xxxxxxxxxxxxx
  VPC Resource: False
  Network Interface IP: 192.168.1.100
  Http Port: 8080
  Token: token-xxxxxxxxxxxxx

Session is ready for use

Cleaning up...
Session session-xxxxxxxxxxxxx deleted successfully
```

## Notes

- The session ID must be valid and from an existing session
- The get API internally calls the GetSession API endpoint
- The returned session object can be used for all session operations (commands, files, etc.)
- Always clean up sessions when done to avoid resource waste
- The session object contains additional information like resource URL, VPC settings, and network details

## Error Handling

The `get` method returns a `SessionResult` object with error information:

1. **Empty session_id**: Result will have `success=False`
   ```python
   result = agb.get("")
   if not result.success:
       print(f"Error: {result.error_message}")  # "session_id is required"
   ```

2. **None session_id**: Result will have `success=False`
   ```python
   result = agb.get(None)
   if not result.success:
       print(f"Error: {result.error_message}")  # "session_id is required"
   ```

3. **Whitespace-only session_id**: Result will have `success=False`
   ```python
   result = agb.get("   ")
   if not result.success:
       print(f"Error: {result.error_message}")  # "session_id is required"
   ```

4. **Non-existent session**: Result will have `success=False`
   ```python
   result = agb.get("non-existent-session-id")
   if not result.success:
       print(f"Error: {result.error_message}")  # "Failed to get session..."
   ```

## Session Information

When successfully retrieved, the session object provides access to:

- **session_id**: Unique identifier for the session
- **resource_url**: URL to access the session resource
- **resource_id**: Internal resource identifier
- **app_instance_id**: Application instance identifier
- **http_port**: HTTP port for the session
- **token**: Authentication token for the session

## Complete Example

See `main.py` for a complete working example that demonstrates:

1. Creating a new session
2. Retrieving the session using the Get API
3. Displaying session information
4. Cleaning up resources by deleting the session