# Troubleshooting

## Common Issues

**Session Creation Fails**
```python
from agb import AGB
from agb.session_params import CreateSessionParams

params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
if not result.success:
    print(f"Error: {result.error_message}")
    # Common causes:
    # - Invalid API key
    # - Network connectivity issues
    # - Service temporarily unavailable
    # - Account limits exceeded
```

**Session Becomes Unresponsive**
```python
from agb import AGB
from agb.session_params import CreateSessionParams

# Check session health
info_result = session.info()
if not info_result.success:
    print("Session may be unresponsive, creating new session...")
    agb.delete(session)  # Clean up old session
    params = CreateSessionParams(image_id="agb-code-space-1")
    result = agb.create(params)  # Create new session
```

**Memory or Resource Limits**
```python
from agb import AGB
from agb.session_params import CreateSessionParams

# Monitor resource usage and recreate sessions periodically
operation_count = 0
max_operations_per_session = 100

for task in tasks:
    if operation_count >= max_operations_per_session:
        # Recreate session to free resources
        agb.delete(session)
        params = CreateSessionParams(image_id="agb-code-space-1")
        result = agb.create(params)

        if result.success:
            session = result.session
            operation_count = 0
        else:
            print(f"Failed to recreate session: {result.error_message}")
            break

    # Execute task
    session.code.run_code(task["code"], "python")
    operation_count += 1
```
