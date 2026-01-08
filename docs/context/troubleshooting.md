# Troubleshooting

## What you’ll do

Diagnose common context issues: create/get failures, sync failures, and permission problems.

## Prerequisites

- `AGB_API_KEY`

## Common issues

### Context creation failed

- **Likely cause**: invalid API key, missing permissions, or a naming conflict.
- **Fix**: verify credentials and permissions; try a unique context name.

### File sync failed

- **Likely cause**: sync policy mismatch, wrong mount path, or network/API errors.
- **Fix**: verify `context_id` and mount `path`, then check `session.context.info()` for error details.

### Permission issues

- **Likely cause**: API key does not have access to the context or org/project.
- **Fix**: verify the API key belongs to the right account and has required permissions.

## Related

- Overview: [`docs/context/overview.md`](overview.md)
- Sync in sessions: [`docs/context/sync-in-sessions.md`](sync-in-sessions.md)

