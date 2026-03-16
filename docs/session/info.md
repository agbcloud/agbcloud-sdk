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

## Related

- [Session Overview](./overview.md)
- [Session Lifecycle](./lifecycle.md)
