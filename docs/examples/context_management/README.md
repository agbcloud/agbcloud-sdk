# Context Management Example

This example demonstrates how to use the AGB Context API to manage persistent storage contexts.

## Features Demonstrated

- **List Contexts**: Retrieve all available contexts
- **Create Context**: Create a new context or get an existing one
- **Update Context**: Modify context properties
- **Session Integration**: Create sessions with context synchronization
- **Cleanup**: Properly delete sessions and contexts

## Prerequisites

- Python 3.10+
- AGB SDK installed
- Valid AGB API key

## Setup

1. Set your API key as an environment variable:
   ```bash
   export AGB_API_KEY="your_api_key_here"
   ```

2. Or modify the `api_key` variable in the script directly.

## Running the Example

```bash
python main.py
```

## Expected Output

The example will:
1. List all existing contexts
2. Create or get a test context
3. Create a session with context synchronization
4. Update the context name
5. Clear context data (remove persistent data while keeping the context)
6. Clean up by deleting the session and context

## Key Concepts

### Context Lifecycle
- Contexts are persistent storage units that survive across sessions
- They can be created, updated, and deleted independently
- Contexts can be synchronized with sessions for data persistence

### Session Integration
- Sessions can be created with context synchronization
- This allows data to be automatically synced between the session and the context
- Context sync policies control how data is synchronized

### Error Handling
- All operations return result objects with success status
- Proper error handling ensures resources are cleaned up
- Detailed logging helps with debugging

## Related Documentation

- [Context API Reference](../../api-reference/data_context/context.md)
- [ContextManager API Reference](../../api-reference/data_context/context_manager.md)
- [Session API Reference](../../api-reference/02_session.md)
