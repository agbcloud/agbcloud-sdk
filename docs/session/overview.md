# Manage sessions

Sessions are the core concept in AGB SDK. A session represents an isolated cloud environment where you can execute code, run commands, manage files, and interact with cloud storage. This guide covers everything you need to know about managing sessions effectively.

**Important**: Image ID Management. When creating sessions, you need to specify an appropriate `image_id`. Please ensure you use valid image IDs that are available in your account. You can view and manage your available images in the [AGB Console Image Management](https://agb.cloud/console/image-management) page.

## What you’ll do

Create, use, list, label, and delete **sessions** (isolated cloud environments) in the AGB SDK.

## Prerequisites

- `AGB_API_KEY`
- A valid `image_id` (for the runtime you need, e.g. `agb-code-space-1`)
- Permission to create sessions in your account

## Quickstart

Minimal runnable example: create a session, run one action, then delete it.

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-code-space-1"))
if not create_result.success:
    raise SystemExit(f"Session creation failed: {create_result.error_message}")

session = create_result.session

# Do something in the session
session.code.run("print('Hello from AGB')", "python")

agb.delete(session)
```

## Common tasks

### Create a session

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
result = agb.create(CreateSessionParams(image_id="agb-code-space-1"))
if result.success:
    session = result.session
    print("Session created:", session.session_id)
else:
    print("Creation failed:", result.error_message)
```

### Get session info

```python
info_result = session.info()
if info_result.success:
    data = info_result.data
    print("Session ID:", data.get("session_id", "N/A"))
    print("Resource URL:", data.get("resource_url", "N/A"))
```

### List active sessions

The `list()` method returns **active session IDs** for your account.

```python
from agb import AGB

agb = AGB()
result = agb.list()

if result.success:
    print("Total sessions:", result.total_count)
    print("This page:", len(result.session_ids))
    for session_id in result.session_ids:
        print("Session ID:", session_id)
else:
    print("List failed:", result.error_message)
```

### Paginate session listing

```python
result = agb.list(labels={"project": "demo"}, page=2, limit=10)
if result.success:
    print("Total:", result.total_count)
    print("Next token:", result.next_token)
```

### Set and get labels

You can set labels on creation, or update them after creation.

```python
create_result = agb.create(
    CreateSessionParams(
        image_id="agb-code-space-1",
        labels={"project": "demo", "environment": "testing", "team": "backend"},
    )
)
```

```python
set_result = session.set_labels({"project": "demo", "environment": "production"})
print("Set labels:", set_result.success, set_result.error_message)

get_result = session.get_labels()
if get_result.success:
    print(get_result.data)
```

### Filter sessions by labels

Filter works best after you consistently apply labels during creation and updates.

```python
result = agb.list(labels={"project": "demo", "environment": "testing"})
if result.success:
    for session_id in result.session_ids:
        print("Session ID:", session_id)
```

### Call MCP tools

You can call MCP (Model Context Protocol) tools directly from a session. This allows you to interact with various capabilities available in the AGB cloud environment.

```python
# List available MCP tools
result = session.list_mcp_tools()
if result.success:
    print(f"Available tools: {len(result.tools)}")
    for tool in result.tools:
        print(f"  - {tool.name}: {tool.description}")

# Call an MCP tool
result = session.call_mcp_tool("tool_name", {"param1": "value1", "param2": "value2"})
if result.success:
    print("Tool executed successfully")
    print("Result:", result.data)  # Result is in JSON string format
else:
    print("Tool call failed:", result.error_message)
```

**Note**: The available tools depend on the image type. For example, browser images may have UI interaction tools, while code images may have different tools. Use `list_mcp_tools()` to discover available tools for your session's image.

### Delete a session (recommended)

```python
delete_result = agb.delete(session)
print("Deleted:", delete_result.success, delete_result.error_message)
```

### Understand auto-release (timeout)

- If you don’t delete a session, it may be automatically released after an inactivity timeout (configured in the AGB console).
- Released/deleted sessions will **not** appear in `agb.list()` and the session ID becomes invalid.
- Use Context sync if you need persistence across sessions: [`docs/context/overview.md`](../context/overview.md)

## Best practices

- Always delete sessions when done (including error paths).
- Make `image_id` explicit in examples; remind users it must exist in their account.
- Use labels to organize sessions (project/env/team) and simplify filtering.
- Treat `agb.list()` as “active sessions only”; do not use it as an audit log.
- For data persistence, use Context synchronization instead of relying on session lifetime.

## Troubleshooting

### Session creation failed

- **Likely cause**: invalid `AGB_API_KEY`, invalid `image_id`, or missing permissions.
- **Fix**: verify credentials and image availability in the console.

### My session is not in `agb.list()`

- **Likely cause**: `agb.list()` returns only active sessions; your session may have been deleted or auto-released.
- **Fix**: create a new session; use Context sync for persistence if needed.

### `delete()` fails

- **Likely cause**: session already released, or network/API issue.
- **Fix**: retry, and check the returned `error_message` for details.

## Related

- API reference: [`docs/api-reference/session.md`](../api-reference/session.md)
- API reference (client): [`docs/api-reference/agb.md`](../api-reference/agb.md)
- Examples: [`docs/examples/session_management/README.md`](../examples/session_management/README.md)
- Persistence: [`docs/context/overview.md`](../context/overview.md)