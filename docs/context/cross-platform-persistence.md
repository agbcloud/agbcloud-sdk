# Cross-Platform data persistence guide

## Overview

This guide explains how to use the **MappingPolicy** feature in AGB SDK to enable cross-environment data persistence, allowing context data created in one session environment to be accessible in another. This is particularly useful when you need to share data between different session types (e.g., browser sessions and code sessions) or when migrating workflows across different image environments.

## Quick Reference

```python
from agb import AGB
from agb.context_sync import MappingPolicy, SyncPolicy, UploadPolicy, DownloadPolicy, DeletePolicy, ExtractPolicy

# Create mapping policy for cross-platform access
mapping_policy = MappingPolicy(path="/original/path")

# Create sync policy with mapping
sync_policy = SyncPolicy(
    upload_policy=UploadPolicy(),
    download_policy=DownloadPolicy(),
    delete_policy=DeletePolicy(),
    extract_policy=ExtractPolicy(),
    mapping_policy=mapping_policy
)

# Use in session creation
session_params.add_context_sync(context_id, "/target/path", sync_policy)
```

## Understanding the Problem

By default, context data persistence is tied to the specific path where it was created. The **MappingPolicy** feature solves this limitation by allowing you to map the original path to a different target path in new sessions. This means:

- Data created at `/tmp/mapping` can be accessed in a new session using a completely different path like `/home/data`
- The new session doesn't need to use the same path - it can use any path you specify, and MappingPolicy will map the original data to this new location

This enables true cross-environment data persistence between different image types (browser, code, etc.) with flexible path configuration.

## How MappingPolicy Works

When you create a context sync configuration with a MappingPolicy:

1. **Original Path**: The `path` in MappingPolicy specifies the original Linux path where data was stored in the previous session
2. **Target Path**: The `path` in ContextSync specifies where you want to access that data in the current session
3. **Manual Mapping**: You need to manually specify the original path in MappingPolicy, and the system will map the data from that original path to your specified target path, enabling cross-environment access between different image types

## Basic Usage

### Step 1: Create and Persist Data in First Session

```python
import os
import time
from agb import AGB
from agb.context_sync import ContextSync, SyncPolicy, UploadPolicy, DownloadPolicy, DeletePolicy, ExtractPolicy
from agb.session_params import CreateSessionParams

# Initialize AGB client
ab = AGB()

# Create a context
context_result = ab.context.get(name="cross-platform-context", create=True)
context = context_result.context

# Define the original path (e.g., in a browser session)
original_path = "/tmp/mapping"

# Create sync policy for the first session (no mapping needed)
sync_policy = SyncPolicy(
    upload_policy=UploadPolicy(),
    download_policy=DownloadPolicy(),
    delete_policy=DeletePolicy(),
    extract_policy=ExtractPolicy()
)

# Create session with context sync
context_sync = ContextSync.new(context.id, original_path, sync_policy)
session_params = CreateSessionParams(
    image_id="agb-browser-use-1",
    context_syncs=[context_sync],
    labels={"purpose": "data-creation"}
)

# Create session
session_result = ab.create(session_params)
session = session_result.session

# Create test data
test_file_path = f"{original_path}/test-file.txt"
test_content = "This file was created in the first session"

# Create file in session
create_cmd = f'echo "{test_content}" > "{test_file_path}"'
session.command.execute(create_cmd)

# Sync to persist data
import asyncio
sync_result = asyncio.run(session.context.sync())
print(f"Data synced successfully: {sync_result.success}")

# Clean up session
ab.delete(session)
```

### Step 2: Access Data in Different Session with MappingPolicy

```python
# Define the target path for the new session
target_path = "/home/data"

# Create mapping policy with the original path
mapping_policy = MappingPolicy(path=original_path)

# Create sync policy with mapping policy
sync_policy_with_mapping = SyncPolicy(
    upload_policy=UploadPolicy(),
    download_policy=DownloadPolicy(),
    delete_policy=DeletePolicy(),
    extract_policy=ExtractPolicy(),
    mapping_policy=mapping_policy
)

# Create new session with mapping
context_sync = ContextSync.new(context.id, target_path, sync_policy_with_mapping)
session_params = CreateSessionParams(
    image_id="agb-code-space-1",
    context_syncs=[context_sync],
    labels={"purpose": "data-access"}
)

# Create session
session_result = ab.create(session_params)
session = session_result.session

# Wait for data to be downloaded
time.sleep(15)

# Access the file at the new path
target_file_path = f"{target_path}/test-file.txt"
read_cmd = f'cat "{target_file_path}"'
result = session.command.execute(read_cmd)

print(f"File content: {result.output}")
# Output: This file was created in the first session

# Clean up
ab.delete(session)
ab.context.delete(context)
```

## Advanced Usage

### Complete Cross-Platform Workflow Example

This example demonstrates a complete workflow that creates data in one session type and accesses it in another:

```python
import os
import time
import asyncio
from agb import AGB
from agb.context_sync import (
    ContextSync, SyncPolicy, UploadPolicy, DownloadPolicy,
    DeletePolicy, ExtractPolicy, MappingPolicy
)
from agb.session_params import CreateSessionParams

class CrossPlatformDataManager:
    def __init__(self, api_key):
        self.ab = AGB(api_key)

    def create_context(self, context_name):
        """Create a new context for cross-platform data sharing"""
        context_result = self.ab.context.get(name=context_name, create=True)
        return context_result.context

    def create_data_session(self, context, original_path, image_id="agb-browser-use-1"):
        """Create a session to generate and persist data"""
        # Create sync policy without mapping for data creation
        sync_policy = SyncPolicy(
            upload_policy=UploadPolicy(),
            download_policy=DownloadPolicy(),
            delete_policy=DeletePolicy(),
            extract_policy=ExtractPolicy()
        )

        # Create session
        context_sync = ContextSync.new(context.id, original_path, sync_policy)
        session_params = CreateSessionParams(
            image_id=image_id,
            context_syncs=[context_sync],
            labels={"type": "data-creation"}
        )

        session_result = self.ab.create(session_params)
        return session_result.session

    def create_access_session(self, context, original_path, target_path, image_id="agb-code-space-1"):
        """Create a session to access data via mapping policy"""
        # Create mapping policy
        mapping_policy = MappingPolicy(path=original_path)

        # Create sync policy with mapping
        sync_policy = SyncPolicy(
            upload_policy=UploadPolicy(),
            download_policy=DownloadPolicy(),
            delete_policy=DeletePolicy(),
            extract_policy=ExtractPolicy(),
            mapping_policy=mapping_policy
        )

        # Create session
        context_sync = ContextSync.new(context.id, target_path, sync_policy)
        session_params = CreateSessionParams(
            image_id=image_id,
            context_syncs=[context_sync],
            labels={"type": "data-access"}
        )

        session_result = self.ab.create(session_params)
        return session_result.session

    def create_and_persist_data(self, session, path, filename, content):
        """Create data in session and persist it"""
        # Wait for session to be ready
        time.sleep(15)

        # Create directory if needed (Linux command)
        mkdir_cmd = f'mkdir -p "{path}"'
        session.command.execute(mkdir_cmd)

        # Create file (Linux command)
        file_path = f"{path}/{filename}"
        create_cmd = f'echo "{content}" > "{file_path}"'
        result = session.command.execute(create_cmd)

        # Verify file creation (Linux command)
        verify_cmd = f'cat "{file_path}"'
        verify_result = session.command.execute(verify_cmd)
        print(f"Created file content: {verify_result.output}")

        # Sync to persist
        sync_result = asyncio.run(session.context.sync())
        print(f"Data persistence result: {sync_result.success}")

        return sync_result.success

    def access_persisted_data(self, session, path, filename):
        """Access previously persisted data in new session"""
        # Wait for data to be downloaded
        time.sleep(15)

        # Check if file exists (Linux command)
        file_path = f"{path}/{filename}"
        check_cmd = f'test -f "{file_path}" && echo "EXISTS" || echo "NOT_FOUND"'
        check_result = session.command.execute(check_cmd)

        if "EXISTS" in check_result.output:
            # Read file content (Linux command)
            read_cmd = f'cat "{file_path}"'
            read_result = session.command.execute(read_cmd)
            print(f"Accessed file content: {read_result.output}")
            return read_result.output
        else:
            print("File not found in target session")
            return None

# Usage example
def main():
    # Initialize manager
    manager = CrossPlatformDataManager("your-api-key")

    # Create context
    context = manager.create_context(f"cross-platform-demo-{int(time.time())}")

    try:
        # Define paths
        browser_path = "/tmp/mapping"
        code_path = "/home/data"
        filename = "cross-platform-test.txt"
        content = "Data created in browser session, accessed in code session"

        # Phase 1: Create data in browser session
        print("=== Phase 1: Creating data in browser session ===")
        browser_session = manager.create_data_session(context, browser_path)

        try:
            success = manager.create_and_persist_data(
                browser_session, browser_path, filename, content
            )
            if not success:
                raise Exception("Failed to persist data")
        finally:
            manager.ab.delete(browser_session)

        # Phase 2: Access data in code session
        print("=== Phase 2: Accessing data in code session ===")
        code_session = manager.create_access_session(context, browser_path, code_path)

        try:
            accessed_content = manager.access_persisted_data(
                code_session, code_path, filename
            )

            if accessed_content and content in accessed_content:
                print("✅ Cross-platform data access successful!")
            else:
                print("❌ Cross-platform data access failed!")
        finally:
            manager.ab.delete(code_session)

    finally:
        # Clean up context
        manager.ab.context.delete(context)

if __name__ == "__main__":
    main()
```

## Common Cross-Environment Scenarios

### Browser to Code Session Mapping

```python
# Original browser session path
browser_path = "/tmp/mapping"

# Target code session path
code_path = "/home/data"

# Create mapping policy
mapping_policy = MappingPolicy(path=browser_path)
```

### Code to Browser Session Mapping

```python
# Original code session path
code_path = "/home/project"

# Target browser session path
browser_path = "/tmp/workspace"

# Create mapping policy
mapping_policy = MappingPolicy(path=code_path)
```

## Troubleshooting

### Common Issues and Solutions

#### 1. File Not Found After Mapping

**Problem**: Files created in the original session are not found in the target session.

**Solutions**:
- Ensure the original session was properly synced before deletion
- Wait sufficient time for data download in the target session
- Verify that you are using MappingPolicy to correctly map the original path to the target path

```python
# Verify sync completion
sync_result = asyncio.run(session.context.sync())
if not sync_result.success:
    print("Sync failed, data may not be available for mapping")

# Wait longer for download
time.sleep(30)  # Increase wait time

# Check context status
context_info = session.context.info()
for data in context_info.context_status_data:
    print(f"Context {data.context_id}: {data.status}")
```

#### 2. Permission Issues

**Problem**: Target session cannot access mapped files due to Linux permission restrictions.

**Solutions**:
- Ensure the target session has appropriate Linux file permissions
- Use paths that are accessible to the session user in the Linux environment
- Check directory permissions in the target session using Linux commands

```python
# Check permissions (Linux command)
check_perms_cmd = f'ls -ld "{target_path}"'
result = session.command.execute(check_perms_cmd)
print(f"Directory permissions: {result.output}")
```
---

> 💡 **Tip**: Cross-environment data persistence is most effective when combined with proper context management and sync policies. Always test your cross-environment workflows between different session types (browser, code, etc.) in your development environment before deploying to production. Remember that all AGB environments run on Linux, so use Linux-compatible paths and commands.
