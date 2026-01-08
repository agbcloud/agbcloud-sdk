# Best practices

## What you’ll do

Apply practical patterns to keep context usage reliable, performant, and easy to manage.

## Prerequisites

- `AGB_API_KEY`

## Common recommendations

- **Naming**: use stable names (e.g. `project-{project_id}-{env}`) so you can reuse contexts across sessions.
- **Paths**: use a consistent mount path in sessions (e.g. `/home/project`).
- **Sync policies**: tune auto upload/download/delete behavior for your workflow (see `docs/context/sync-policies.md`).
- **Pagination**: always paginate `list_files` for large directories.
- **Cleanup**: delete contexts you no longer need (and consider deleting files before deleting the context).

## Related

- Overview: [`docs/context/overview.md`](overview.md)
- Sync policies: [`docs/context/sync-policies.md`](sync-policies.md)

