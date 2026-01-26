# Session recovery

In certain scenarios, you may need to recover a Session object using its session ID. The SDK provides the `get` method to retrieve an existing session.

## Using the get Method

The `get` method is the recommended way to recover a session. It retrieves session information from the cloud and returns a ready-to-use Session object with the API request ID.

```python
from agb import AGB

# Initialize the SDK
agb = AGB()

# Retrieve session using its ID
session_id = "your_existing_session_id"
get_result = agb.get(session_id)

if get_result.success:
    session = get_result.session
    print(f"Retrieved session: {session.session_id}")
    print(f"Request ID: {get_result.request_id}")

    # You can now perform any session operations
    result = session.command.execute("echo 'Hello, World!'")
    if result.success:
        print(result.output)
else:
    print(f"Failed to retrieve session: {get_result.error_message}")
```

## Important Considerations

**Session Recovery Limitations:**

1. **Released Sessions Cannot Be Recovered**: If the session ID corresponds to a cloud environment that has been actually released (either through active deletion via `Session.delete()` or automatic timeout release), it cannot be recovered using the session ID. In such cases, you must:
   - Create a new session
   - Use data persistence (see [Data Persistence Guide](../examples/data_persistence/README.md#data-persistence)) to restore your data

2. **Session Status Validation**: Use the `Session.info()` method to determine if a session has been released. Only active (non-released) sessions can return information through the info interface.
