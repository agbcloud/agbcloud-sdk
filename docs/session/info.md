# Session Info

Get session details including the `resource_url` for accessing the cloud environment in a web browser with real-time video streaming and full mouse/keyboard control. The URL is valid for 30 minutes.

## Prerequisites

- `AGB_API_KEY`
- An active session

## Quickstart

::: code-group

```python [Python]
info_result = session.info()
if info_result.success:
    data = info_result.data
    print("Session ID:", data.get("session_id"))
    print("Resource URL:", data.get("resource_url"))
```

```typescript [TypeScript]
const infoResult = await session.info();
if (infoResult.success) {
  const data = infoResult.data as Record<string, unknown>;
  console.log("Session ID:", data?.sessionId);
  console.log("Resource URL:", data?.resourceUrl);
}
```

:::

## Response fields

| Field (Python / TypeScript) | Description |
|-----------------------------|-------------|
| `session_id` / `sessionId` | Unique identifier for the session |
| `resource_url` / `resourceUrl` | URL to access the cloud environment |

## Session properties

When a session is created, the following properties are available for advanced connectivity:

| Property (Python / TypeScript) | Description |
|--------------------------------|-------------|
| `link_url` / `linkUrl` | Direct HTTP endpoint for long-polling connections |
| `ws_url` / `wsUrl` | WebSocket endpoint for real-time streaming |
| `token` / `token` | Authentication token for WebSocket connections |

### Access session properties

::: code-group

```python [Python]
# Access session properties after creation
create_result = agb.create(CreateSessionParams(image_id="agb-code-space-1"))
session = create_result.session

# Long-connection properties
print("Link URL:", session.link_url)
print("WebSocket URL:", session.ws_url)
print("Token:", session.token)

# Use getters for explicit access
link_url = session.get_link_url()
token = session.get_token()
```

```typescript [TypeScript]
// Access session properties after creation
const createResult = await agb.create(
  new CreateSessionParams({ imageId: "agb-code-space-1" })
);
const session = createResult.session;

// Long-connection properties
console.log("Link URL:", session.linkUrl);
console.log("WebSocket URL:", session.wsUrl);
console.log("Token:", session.token);
```

:::

### When to use these properties

| Property | Use Case |
|----------|----------|
| `link_url` | Direct HTTP routing for MCP tool calls (internal SDK use) |
| `ws_url` + `token` | Real-time streaming (code execution with `stream_beta=True`) |

## Related

- [Session Overview](./overview.md)
- [Session Lifecycle](./lifecycle.md)
- [Code Streaming](../code-interpreting/stream-outputs.md)
