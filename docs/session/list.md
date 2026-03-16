# List Sessions

Query and filter active sessions in your account.

## What you'll do

List active sessions with optional pagination and label-based filtering.

## Prerequisites

- `AGB_API_KEY`

## Quickstart

::: code-group

```python [Python]
from agb import AGB

agb = AGB()
result = agb.list()

if result.success:
    print("Total sessions:", result.total_count)
    for session_id in result.session_ids:
        print("Session ID:", session_id)
```

```typescript [TypeScript]
import { AGB } from "agbcloud-sdk";

const agb = new AGB();
const result = await agb.list();

if (result.success) {
  console.log("Total sessions:", result.totalCount);
  for (const sessionId of result.sessionIds ?? []) {
    console.log("Session ID:", sessionId);
  }
}
```

:::

## Common tasks

### Paginate results

::: code-group

```python [Python]
result = agb.list(page=2, limit=10)
if result.success:
    print("Total:", result.total_count)
    print("Next token:", result.next_token)
```

```typescript [TypeScript]
const result = await agb.list();
if (result.success) {
  console.log("Total:", result.totalCount);
  console.log("Next token:", result.nextToken);
}
```

:::

### Filter by labels

::: code-group

```python [Python]
result = agb.list(labels={"project": "demo", "environment": "testing"})
if result.success:
    for session_id in result.session_ids:
        print("Session ID:", session_id)
```

```typescript [TypeScript]
const result = await agb.list({ project: "demo", environment: "testing" });
if (result.success) {
  for (const sessionId of result.sessionIds ?? []) {
    console.log("Session ID:", sessionId);
  }
}
```

:::

## Response fields

| Field | Description |
|-------|-------------|
| `session_ids` / `sessionIds` | List of active session IDs |
| `total_count` / `totalCount` | Total number of sessions matching the query |
| `next_token` / `nextToken` | Token for fetching the next page |

## Best practices

- Use labels consistently when creating sessions to enable effective filtering
- `list()` returns only **active** sessions; released sessions will not appear

## Related

- [Session Overview](./overview.md)
- [Session Labels](./labels.md)
