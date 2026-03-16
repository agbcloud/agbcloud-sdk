# Session Labels

Organize and filter sessions using custom key-value labels.

## What you'll do

Set, get, and use labels to organize sessions by project, environment, team, or any custom criteria.

## Prerequisites

- `AGB_API_KEY`
- An active session (for get/set operations)

## Quickstart

::: code-group

```python [Python]
# Set labels
session.set_labels({"project": "demo", "environment": "production"})

# Get labels
result = session.get_labels()
if result.success:
    print(result.data)
```

```typescript [TypeScript]
// Set labels
await session.setLabels({ project: "demo", environment: "production" });

// Get labels
const result = await session.getLabels();
if (result.success) {
  console.log(result.data);
}
```

:::

## Common tasks

### Set labels on creation

::: code-group

```python [Python]
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
session = agb.create(
    CreateSessionParams(
        image_id="agb-code-space-1",
        labels={"project": "demo", "environment": "testing", "team": "backend"},
    )
).session
```

```typescript [TypeScript]
import { AGB, CreateSessionParams } from "agbcloud-sdk";

const agb = new AGB();
const session = (await agb.create(
  new CreateSessionParams({
    imageId: "agb-code-space-1",
    labels: { project: "demo", environment: "testing", team: "backend" },
  })
)).session;
```

:::

### Update labels after creation

::: code-group

```python [Python]
result = session.set_labels({"project": "demo", "environment": "production"})
if result.success:
    print("Labels updated")
```

```typescript [TypeScript]
const result = await session.setLabels({ project: "demo", environment: "production" });
if (result.success) {
  console.log("Labels updated");
}
```

:::

### Get current labels

::: code-group

```python [Python]
result = session.get_labels()
if result.success:
    print("Current labels:", result.data)
```

```typescript [TypeScript]
const result = await session.getLabels();
if (result.success) {
  console.log("Current labels:", result.data);
}
```

:::

### Filter sessions by labels

::: code-group

```python [Python]
result = agb.list(labels={"project": "demo"})
if result.success:
    print(f"Found {len(result.session_ids)} sessions")
```

```typescript [TypeScript]
const result = await agb.list({ project: "demo" });
if (result.success) {
  console.log(`Found ${result.sessionIds?.length} sessions`);
}
```

:::

## Best practices

- Use consistent label keys across your organization (e.g., `project`, `environment`, `team`)
- Set labels during session creation for easier filtering
- Use labels to group sessions for batch operations or monitoring

## Related

- [Session Overview](./overview.md)
- [List Sessions](./list.md)
