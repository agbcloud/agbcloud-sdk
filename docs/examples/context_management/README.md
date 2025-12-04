# Context Management Examples

This directory demonstrates how to upload files and data into the session environment using the Context Manager.

## Overview

The **Context Manager** allows you to prepare the environment before your code or commands run. It handles:
- Uploading local files to the remote session.
- Creating files from in-memory strings/bytes.
- Setting environment variables.

## Examples

### Basic Context Usage (`main.py`)
Shows how to upload a local file and verify its existence in the remote session.

<<<<<<< ours
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
=======
<<< ./main.py
>>>>>>> theirs
