# Context basics

## What you’ll do

Create, get, and list contexts.

## Prerequisites

- `AGB_API_KEY`

## Quickstart

```python
from agb import AGB

agb = AGB()
result = agb.context.get("my-project-context", create=True)
if not result.success:
    raise SystemExit(result.error_message)

context = result.context
print("Context:", context.name, context.id)
```

## Common tasks

### Create a new context

```python
create_result = agb.context.create("my-project-context")
print(create_result.success, create_result.error_message)
```

### Get an existing context (create if missing)

```python
get_result = agb.context.get("my-project-context", create=True)
print(get_result.success, get_result.error_message)
```

### List all contexts

```python
from agb.context import ContextListParams

list_result = agb.context.list(ContextListParams())
if list_result.success:
    for ctx in list_result.contexts:
        print(ctx.name, ctx.id, ctx.created_at)
```

## Best practices

- Use stable, meaningful names for contexts (project/user/environment).

## Troubleshooting

### Context creation failed

- **Likely cause**: invalid API key, missing permissions, or name conflicts.
- **Fix**: verify credentials and permissions; try a unique name.

## Related

- Overview: [`docs/context/overview.md`](overview.md)
- API reference: [`docs/api-reference/data_context/context.md`](../api-reference/data_context/context.md)

