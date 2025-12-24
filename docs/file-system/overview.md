# File system

## Overview

The AGB SDK provides comprehensive file system operations through the `file_system` module. You can read, write, create, delete, and manage files and directories in your cloud sessions. This guide covers all file operations from basic usage to advanced patterns.

## Quick Reference (1 minute)

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)

if result.success:
    session = result.session

    # Basic file operations
    session.file_system.write_file("/tmp/hello.txt", "Hello World!")
    content = session.file_system.read_file("/tmp/hello.txt").content
    print(content)  # "Hello World!"

    # Directory operations
    session.file_system.create_directory("/tmp/trash/")
    files = session.file_system.list_directory("/tmp").entries
    session.file_system.move_file("/tmp/hello.txt", "/tmp/trash/hello.txt")

    agb.delete(session)
else:
    print(f"Failed to create session: {result.error_message}")
```