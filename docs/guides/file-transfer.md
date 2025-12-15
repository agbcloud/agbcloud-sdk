# File Transfer Guide

## Overview

The AGB SDK provides file transfer capabilities to upload files from your local machine to the cloud session and download files from the cloud session to your local machine. This uses pre-signed URLs for secure and efficient file transfers.

**Key Points:**
- The file transfer context is **automatically managed by the server**
- On first use, the context is **automatically created** when you call `get_file_transfer_context_path()`
- When the session ends, the context is **automatically deleted**
- You don't need to manually create, configure, or manage the file transfer context

## Quick Start

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-2")
session = agb.create(params).session

# Get the file transfer context path (context is auto-created on first use)
context_path = session.file_system.get_file_transfer_context_path()

# Upload a file
upload_result = session.file_system.upload_file(
    local_path="/local/file.txt",
    remote_path=context_path + "/remote_file.txt"
)

# Download a file
download_result = session.file_system.download_file(
    remote_path=context_path + "/remote_file.txt",
    local_path="/local/downloaded_file.txt"
)

agb.delete(session)  # Context is automatically deleted when session ends
```

## Getting the Context Path

Before uploading or downloading files, you need to get the context path. The context is automatically created by the server on first use - you don't need to do anything special:

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-2")
session = agb.create(params).session

# Get the file transfer context path
# The context is automatically created by the server if it doesn't exist
context_path = session.file_system.get_file_transfer_context_path()

if context_path is None:
    # This should rarely happen - only if there's a server issue
    print("File transfer context not available")
else:
    print(f"Context path: {context_path}")
    # Use this path as the base for remote file paths

agb.delete(session)
```

## Uploading Files

Upload files from your local machine to the cloud session:

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-2")
session = agb.create(params).session

# Get context path (automatically created if needed)
context_path = session.file_system.get_file_transfer_context_path()
if context_path is None:
    print("File transfer not available")
    agb.delete(session)
    exit(1)

# Upload a local file
local_file = "/path/to/local/file.txt"
remote_path = context_path + "/uploaded_file.txt"

upload_result = session.file_system.upload_file(
    local_path=local_file,
    remote_path=remote_path,
    wait=True,  # Wait for sync to complete
    wait_timeout=60.0  # Timeout in seconds
)

if upload_result.success:
    print(f"✅ Upload successful!")
    print(f"   Bytes sent: {upload_result.bytes_sent}")
    print(f"   Request ID: {upload_result.request_id_upload_url}")
else:
    print(f"❌ Upload failed: {upload_result.error}")

agb.delete(session)
```

## Downloading Files

Download files from the cloud session to your local machine:

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-2")
session = agb.create(params).session

# Get context path (automatically created if needed)
context_path = session.file_system.get_file_transfer_context_path()
if context_path is None:
    print("File transfer not available")
    agb.delete(session)
    exit(1)

# Download a remote file
remote_path = context_path + "/file_to_download.txt"
local_file = "/path/to/local/downloaded_file.txt"

download_result = session.file_system.download_file(
    remote_path=remote_path,
    local_path=local_file,
    overwrite=True,  # Overwrite if file exists
    wait=True,  # Wait for sync to complete
    wait_timeout=300.0  # Timeout in seconds
)

if download_result.success:
    print(f"✅ Download successful!")
    print(f"   Bytes received: {download_result.bytes_received}")
    print(f"   Request ID: {download_result.request_id_download_url}")
else:
    print(f"❌ Download failed: {download_result.error}")

agb.delete(session)
```

## Complete Upload/Download Workflow

Here's a complete example that uploads a file, processes it in the cloud, and downloads the result:

```python
import tempfile
import os
import time
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
params = CreateSessionParams(image_id="agb-code-space-2")
session = agb.create(params).session

# Get context path (automatically created if needed)
context_path = session.file_system.get_file_transfer_context_path()
if context_path is None:
    print("File transfer not available")
    agb.delete(session)
    exit(1)

# Create a temporary local file
with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
    f.write("Test content for file transfer\n")
    local_upload_file = f.name

try:
    # Step 1: Upload file
    remote_path = context_path + f"/test_file_{int(time.time())}.txt"
    print(f"📤 Uploading: {local_upload_file} -> {remote_path}")

    upload_result = session.file_system.upload_file(
        local_path=local_upload_file,
        remote_path=remote_path,
        wait=True,
        wait_timeout=60.0
    )

    if not upload_result.success:
        print(f"Upload failed: {upload_result.error}")
        exit(1)

    print(f"✅ Upload successful ({upload_result.bytes_sent} bytes)")

    # Step 2: Process file in cloud (example: read and modify)
    read_result = session.file_system.read_file(remote_path)
    if read_result.success:
        modified_content = read_result.content.upper()
        session.file_system.write_file(remote_path, modified_content)
        print("✅ File processed in cloud")

    # Step 3: Download processed file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        local_download_file = f.name

    print(f"📥 Downloading: {remote_path} -> {local_download_file}")

    download_result = session.file_system.download_file(
        remote_path=remote_path,
        local_path=local_download_file,
        wait=True,
        wait_timeout=300.0
    )

    if download_result.success:
        print(f"✅ Download successful ({download_result.bytes_received} bytes)")

        # Verify downloaded content
        with open(local_download_file, "r") as f:
            downloaded_content = f.read()
        print(f"Downloaded content: {downloaded_content}")

    # Clean up
    os.unlink(local_download_file)

finally:
    # Clean up uploaded file
    os.unlink(local_upload_file)
    agb.delete(session)  # Context is automatically deleted when session ends
```

## Advanced Options

### Upload with Custom Content Type and Progress Callback

```python
def progress_callback(bytes_sent):
    print(f"Uploaded {bytes_sent} bytes...")

upload_result = session.file_system.upload_file(
    local_path="/path/to/image.png",
    remote_path=context_path + "/image.png",
    content_type="image/png",  # Specify content type
    wait=True,
    wait_timeout=120.0,
    progress_cb=progress_callback  # Progress updates
)
```

### Upload Without Waiting

```python
# Upload without waiting for sync to complete
upload_result = session.file_system.upload_file(
    local_path="/path/to/file.txt",
    remote_path=context_path + "/file.txt",
    wait=False  # Don't wait for sync
)

# Check result immediately
if upload_result.success:
    print("Upload initiated (sync in progress)")
```

## Best Practices

### 1. Always Check Context Path Availability

```python
context_path = session.file_system.get_file_transfer_context_path()
if context_path is None:
    # Handle case where file transfer is not available
    print("File transfer context not available")
    return
```

### 2. Use Appropriate Timeouts

```python
# For small files
upload_result = session.file_system.upload_file(
    local_path="small_file.txt",
    remote_path=context_path + "/small_file.txt",
    wait_timeout=30.0  # 30 seconds
)

# For large files
upload_result = session.file_system.upload_file(
    local_path="large_file.zip",
    remote_path=context_path + "/large_file.zip",
    wait_timeout=300.0  # 5 minutes
)
```

### 3. Handle Errors Gracefully

```python
upload_result = session.file_system.upload_file(
    local_path=local_file,
    remote_path=remote_path
)

if not upload_result.success:
    if "Context ID not available" in (upload_result.error or ""):
        print("File transfer context not initialized")
    elif "not found" in (upload_result.error or "").lower():
        print("Local file not found")
    else:
        print(f"Upload error: {upload_result.error}")
```

### 4. Clean Up Remote Files After Use

```python
# After downloading a file, clean up the remote copy if needed
if download_result.success:
    # Use context API to delete remote file
    context_id = session.file_system._file_transfer.context_id
    if context_id:
        delete_result = agb.context.delete_file(context_id, remote_path)
        if delete_result.success:
            print("Remote file cleaned up")
```

## How It Works

The file transfer feature uses a **server-managed context** that is automatically created and deleted:

1. **First Use**: When you first call `get_file_transfer_context_path()`, the server automatically creates a `file_transfer` context for your session
2. **During Use**: The context persists throughout your session, allowing multiple uploads and downloads
3. **Session End**: When you call `agb.delete(session)`, the server automatically deletes the context and cleans up all associated resources

You don't need to:
- Manually create the context
- Configure context settings
- Manage context lifecycle
- Clean up the context

All of this is handled automatically by the server.

## Troubleshooting

### Context Path Returns None

If `get_file_transfer_context_path()` returns `None`, it usually means:
- The server is temporarily unavailable
- There was an error creating the context

**Solution**: Retry the operation or check your session status.

### Upload/Download Fails

Common causes:
- **Local file not found**: Check that the local file path is correct
- **Network issues**: Check your internet connection
- **Timeout**: Increase `wait_timeout` for large files
- **Permission issues**: Ensure you have read/write permissions

**Solution**: Check the error message in the result object for specific details.

## Related Documentation

- **[File Operations Guide](file-operations.md)** - Basic file operations (read, write, list)
- **[Session Management](session-management.md)** - Managing sessions and contexts
- **[API Reference](../api-reference/capabilities/file_system.md)** - Complete FileSystem API documentation
