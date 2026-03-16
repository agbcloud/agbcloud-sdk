# Context basics

## What you’ll do

Create, get, and list contexts.

## Prerequisites

- `AGB_API_KEY`

## Quickstart

::: code-group

```python [Python]
from agb import AGB

agb = AGB()
result = agb.context.get("my-project-context", create=True)
if not result.success:
    raise SystemExit(result.error_message)

context = result.context
print("Context:", context.name, context.id)
```

```typescript [TypeScript]
import { AGB } from "agbcloud-sdk";

const agb = new AGB();
const result = await agb.context.get("my-project-context", true);
if (!result.success || !result.context) {
  throw new Error(result.errorMessage);
}

const context = result.context;
console.log("Context:", context.name, context.id);
```

:::

## Common tasks

### Create a new context

::: code-group

```python [Python]
create_result = agb.context.create("my-project-context")
print(create_result.success, create_result.error_message)
```

```typescript [TypeScript]
const createResult = await agb.context.create("my-project-context");
console.log(createResult.success, createResult.errorMessage);
```

:::

### Get an existing context (create if missing)

::: code-group

```python [Python]
get_result = agb.context.get("my-project-context", create=True)
print(get_result.success, get_result.error_message)
```

```typescript [TypeScript]
const getResult = await agb.context.get("my-project-context", true);
console.log(getResult.success, getResult.errorMessage);
```

:::

### List all contexts

::: code-group

```python [Python]
from agb.context import ContextListParams

list_result = agb.context.list(ContextListParams())
if list_result.success:
    for ctx in list_result.contexts:
        print(ctx.name, ctx.id, ctx.created_at)
```

```typescript [TypeScript]
const listResult = await agb.context.list();
if (listResult.success) {
  for (const ctx of listResult.contexts ?? []) {
    console.log(ctx.name, ctx.id, ctx.createdAt);
  }
}
```

:::

## Best practices

- Use stable, meaningful names for contexts (project/user/environment).

## Troubleshooting

### Context creation failed

- **Likely cause**: invalid API key, missing permissions, or name conflicts.
- **Fix**: verify credentials and permissions; try a unique name.

## Related

- Overview: [`docs/context/overview.md`](overview.md)
- API reference: [`docs/api-reference/python/data_context/context.md`](../api-reference/python/data_context/context.md)

