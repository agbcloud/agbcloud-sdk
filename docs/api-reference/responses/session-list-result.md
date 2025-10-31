# SessionListResult

`SessionListResult` is the response type returned by session listing operations in the AGB SDK.

## Overview

The `SessionListResult` class represents the outcome of operations that retrieve a paginated list of session IDs, such as `AGB.list()`.

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `error_message` | `str` | Error message if the operation failed |
| `session_ids` | `List[str]` | List of session IDs matching the filter criteria |
| `next_token` | `str` | Token for retrieving the next page (empty if no more pages) |
| `max_results` | `int` | Maximum number of results per page |
| `total_count` | `int` | Total number of sessions matching the filter criteria |

## Usage

```python
from agb import AGB

# Initialize AGB client
agb = AGB()

# List all sessions
result = agb.list()

# Check if successful
if result.success:
    print(f"Found {result.total_count} total sessions")
    print(f"Showing {len(result.session_ids)} session IDs on this page")
    print(f"Request ID: {result.request_id}")

    for session_id in result.session_ids:
        print(f"Session ID: {session_id}")

    # Check if there are more pages
    if result.next_token:
        print("More pages available")
else:
    print(f"Failed to list sessions: {result.error_message}")
```

## Success Response

When the operation is successful:

```python
result.success = True
result.session_ids = ["session_123", "session_456", "session_789"]
result.total_count = 25
result.max_results = 10
result.next_token = "token_for_next_page"
result.error_message = ""
result.request_id = "req_123456789"
```

## Error Response

When the operation fails:

```python
result.success = False
result.session_ids = []
result.total_count = 0
result.max_results = 0
result.next_token = ""
result.error_message = "Invalid labels format"
result.request_id = "req_123456789"
```

## Pagination

The `SessionListResult` supports pagination through the `next_token` mechanism:

```python
from agb import AGB

agb = AGB()

# Get first page
result = agb.list(limit=5)
if result.success:
    print(f"Page 1: {len(result.session_ids)} sessions")

    # Get next page if available
    if result.next_token:
        # Note: Direct next_token usage requires internal API access
        # Use page parameter instead for public API
        next_result = agb.list(page=2, limit=5)
        if next_result.success:
            print(f"Page 2: {len(next_result.session_ids)} sessions")
```

## Filtering by Labels

List sessions with specific labels:

```python
# Filter sessions by project
result = agb.list(labels={"project": "demo"})

if result.success:
    print(f"Found {len(result.session_ids)} sessions for project 'demo'")
    for session_id in result.session_ids:
        print(f"  - {session_id}")

# Filter with multiple labels
result = agb.list(labels={
    "project": "demo",
    "environment": "production"
})

if result.success:
    print(f"Found {len(result.session_ids)} production demo sessions")
```
## Methods

All response objects inherit from `ApiResponse` and have access to the `request_id` property for tracking API requests.

## Related Types

- **[SessionResult](session-result.md)** - Result type for single session operations
- **[GetSessionResult](get-session-result.md)** - Result type for session information retrieval
- **[BaseSession](../core/session.md)** - The session object type

## Error Handling

Always check the `success` property before accessing the session list:

```python
result = agb.list(labels={"project": "demo"})

if result.success:
    # Safe to access session data
    if result.session_ids:
        print(f"Found {len(result.session_ids)} sessions:")
        for session_id in result.session_ids:
            print(f"  - {session_id}")
    else:
        print("No sessions found matching the criteria")

    # Pagination info
    print(f"Total sessions: {result.total_count}")
    print(f"Page size: {result.max_results}")
    print(f"Has more pages: {'yes' if result.next_token else 'no'}")
else:
    # Handle error
    print(f"Error: {result.error_message}")
    print(f"Request ID: {result.request_id}")
```