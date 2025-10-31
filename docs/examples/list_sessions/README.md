# List Sessions Example

This example demonstrates how to use the `list()` API to query and filter sessions in AGB SDK.

## Overview

The `list()` API provides a simple and intuitive interface for querying sessions with optional filtering and pagination support. This example showcases the comprehensive session listing capabilities of the AGB SDK.

## Features Demonstrated

This example shows:

1. **List all sessions** - Query all sessions without any filters
2. **Filter by labels** - Query sessions that match specific labels
3. **Multiple label filtering** - Query sessions that match multiple label criteria
4. **Pagination** - Retrieve results page by page with configurable page size
5. **Iterate all pages** - Automatically fetch all results across multiple pages
6. **Session lifecycle management** - Create test sessions and clean up afterwards

## Prerequisites

Before running this example, ensure you have:

1. **AGB SDK installed**:
   ```bash
   pip install agbcloud-sdk
   ```

2. **API Key configured**:
   ```bash
   export AGB_API_KEY='your-api-key-here'
   ```

## Running the Example

```bash
cd docs/examples/list_sessions
python main.py
```

## Code Walkthrough

### 1. List All Sessions

```python
from agb import AGB

agb = AGB(api_key=api_key)

# List all sessions without any filter
result = agb.list()

if result.success:
    print(f"Total sessions: {result.total_count}")
    print(f"Sessions on this page: {len(result.session_ids)}")
    print(f"Request ID: {result.request_id}")
```

### 2. Filter by Single Label

```python
# Find all sessions with project='list-demo'
result = agb.list(labels={"project": "list-demo"})

if result.success:
    for session_id in result.session_ids:
        print(f"Session ID: {session_id}")
```

### 3. Filter by Multiple Labels

```python
# Find sessions that match ALL specified labels
result = agb.list(
    labels={
        "project": "list-demo",
        "environment": "dev"
    }
)
```

### 4. Pagination

```python
# Get first page with 2 items per page
result = agb.list(
    labels={"project": "list-demo"},
    page=1,
    limit=2
)

# Get second page
if result.next_token:
    result_page2 = agb.list(
        labels={"project": "list-demo"},
        page=2,
        limit=2
    )
```

### 5. Iterate All Pages

```python
all_session_ids = []
page = 1
limit = 2

while True:
    result = agb.list(
        labels={"owner": "demo-user"},
        page=page,
        limit=limit
    )

    if not result.success:
        break

    all_session_ids.extend(result.session_ids)

    # Break if no more pages
    if not result.next_token:
        break

    page += 1

print(f"Total sessions: {len(all_session_ids)}")
```

## API Reference

### Method Signature

```python
def list(
    labels: Optional[Dict[str, str]] = None,
    page: Optional[int] = None,
    limit: Optional[int] = None
) -> SessionListResult
```

### Parameters

- **labels** (Optional[Dict[str, str]]): Labels to filter sessions. All specified labels must match.
  - Default: `None` (no filtering, returns all sessions)
  - Example: `{"project": "demo", "environment": "prod"}`

- **page** (Optional[int]): Page number for pagination, starting from 1.
  - Default: `None` (returns first page)
  - Example: `2` (returns second page)

- **limit** (Optional[int]): Maximum number of items per page.
  - Default: `None` (uses default of 10)
  - Example: `20` (returns up to 20 items per page)

### Return Value

Returns a `SessionListResult` object with:

- **success** (bool): Whether the operation was successful
- **session_ids** (List[str]): List of session IDs matching the filter
- **total_count** (int): Total number of matching sessions
- **next_token** (str): Token for the next page (empty if no more pages)
- **max_results** (int): Maximum results per page
- **request_id** (str): Unique request identifier for tracking
- **error_message** (str): Error message if operation failed

## Example Output

When you run the example, you'll see output similar to:

```
✅ AGB client initialized

📝 Creating test sessions...
✅ Created session 1: session-abc123def456
   Request ID: req_789012345
✅ Created session 2: session-ghi789jkl012
   Request ID: req_345678901
✅ Created session 3: session-mno345pqr678
   Request ID: req_901234567

============================================================
Example 1: List all sessions (no filter)
============================================================
✅ Found 15 total sessions
📄 Showing 10 session IDs on this page
🔑 Request ID: req_567890123
📊 Max results per page: 10
   1. Session ID: session-abc123def456
   2. Session ID: session-ghi789jkl012
   3. Session ID: session-mno345pqr678

============================================================
Example 2: List sessions filtered by project label
============================================================
✅ Found 3 sessions with project='list-demo'
📄 Showing 3 session IDs on this page
🔑 Request ID: req_234567890
   1. Session ID: session-abc123def456
   2. Session ID: session-ghi789jkl012
   3. Session ID: session-mno345pqr678

============================================================
Example 3: List sessions filtered by multiple labels
============================================================
✅ Found 1 sessions with project='list-demo' AND environment='dev'
📄 Showing 1 session IDs
🔑 Request ID: req_678901234
   1. Session ID: session-abc123def456

============================================================
Example 4: List sessions with pagination (2 per page)
============================================================
📄 Page 1:
   Total count: 3
   Session IDs on this page: 2
   Request ID: req_012345678
   1. Session ID: session-abc123def456
   2. Session ID: session-ghi789jkl012

   Has next page (token: eyJwYWdlIjoyLCJsaW1...)

📄 Page 2:
   Session IDs on this page: 1
   Request ID: req_456789012
   1. Session ID: session-mno345pqr678

============================================================
Example 5: Retrieve all session IDs with pagination loop
============================================================
📄 Page 1: Found 2 session IDs , Max results : 2
📄 Page 2: Found 1 session IDs , Max results : 2

✅ Retrieved 3 total session IDs across 2 pages
   1. Session ID: session-abc123def456
   2. Session ID: session-ghi789jkl012
   3. Session ID: session-mno345pqr678

============================================================
🧹 Cleaning up test sessions...
============================================================
✅ Deleted session: session-abc123def456
   Request ID: req_890123456
✅ Deleted session: session-ghi789jkl012
   Request ID: req_234567890
✅ Deleted session: session-mno345pqr678
   Request ID: req_678901234

✨ Demo completed successfully!
```

## Related Documentation

- **[AGB API Reference](../../api-reference/core/agb.md)** - Complete AGB class documentation
- **[SessionListResult](../../api-reference/responses/session-list-result.md)** - Response object documentation
- **[Session Management Guide](../../guides/session-management.md)** - Comprehensive session management guide
- **[Authentication Guide](../../guides/authentication.md)** - API key setup and security