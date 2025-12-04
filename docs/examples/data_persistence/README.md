# Data Persistence & Sync Examples

This directory demonstrates how to synchronize files between your local machine and the remote AGB session, ensuring data persistence across sessions.

## Overview

AGB provides a powerful synchronization mechanism that can:
- **Upload**: Automatically upload local files to the cloud session.
- **Download**: Automatically download generated files from the cloud session back to your local machine.
- **Watch**: (Optional) Continuously sync changes.

## Examples

### File Archive Mode (`file_archive_mode.py`)
Demonstrates the simplest way to persist data: downloading specific files (like generated charts or logs) after execution.

<<< ./file_archive_mode.py

### Context Sync Demo (`context_sync_demo.py`)
Shows bidirectional synchronization (uploading inputs, processing them, and downloading outputs).

<<<<<<< ours
- [Context API Reference](../../api-reference/data_context/context.md)
- [ContextManager API Reference](../../api-reference/data_context/context_manager.md)
- [Session API Reference](../../api-reference/02_session.md)
=======
<<< ./context_sync_demo.py
>>>>>>> theirs
