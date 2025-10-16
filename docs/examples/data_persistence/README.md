# Data Persistence Examples

This directory contains examples demonstrating how to use AGB's context synchronization features for data persistence across sessions.

## Examples

### Context Sync Demo (`context_sync_demo.py`)

A comprehensive example showing how to:
- Create and manage contexts
- Synchronize contexts with sessions
- Persist data across multiple sessions
- Verify data persistence

**Key Features:**
- Context creation and management
- Session-based context synchronization
- Data persistence verification
- Proper cleanup and error handling

**Usage:**
```bash
python context_sync_demo.py
```

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

## Key Concepts

### Context Synchronization
- Contexts provide persistent storage that survives across sessions
- Data can be automatically synchronized between sessions and contexts
- Sync policies control how data is synchronized

### Data Persistence
- Files and data created in one session can be accessed in another
- Context sync ensures data is properly uploaded and downloaded
- Both manual and automatic sync modes are supported

### Error Handling
- All operations include proper error handling
- Resources are cleaned up even if errors occur
- Detailed logging helps with debugging

## Related Documentation

- [Context API Reference](../../api-reference/core/context.md)
- [ContextManager API Reference](../../api-reference/core/context-manager.md)
- [Session API Reference](../../api-reference/core/session.md)
