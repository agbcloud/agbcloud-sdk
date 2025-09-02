# OSS Results

This document covers the response types for Object Storage Service (OSS) operations in the AGB SDK.

## Overview

OSS results are returned by operations that interact with cloud storage in the AGB environment.

## Response Types

### OSSClientResult

Returned by OSS client initialization operations.

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `client_config` | `dict` | OSS client configuration data |
| `error_message` | `str` | Error message if the operation failed |

**Example:**
```python
client_result = session.oss.env_init(
    access_key_id="your_access_key",
    access_key_secret="your_secret",
    endpoint="oss-cn-hangzhou.aliyuncs.com"
)
if client_result.success:
    print("OSS client initialized successfully")
else:
    print(f"Error: {client_result.error_message}")
```

### OSSUploadResult

Returned by `session.oss.upload()` operations.

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `content` | `str` | Upload result content |
| `error_message` | `str` | Error message if the operation failed |

**Example:**
```python
upload_result = session.oss.upload("my-bucket", "path/to/file.txt", "/tmp/local_file.txt")
if upload_result.success:
    print(f"Upload successful: {upload_result.content}")
else:
    print(f"Upload failed: {upload_result.error_message}")
```

### OSSDownloadResult

Returned by `session.oss.download()` operations.

| Property | Type | Description |
|----------|------|-------------|
| `request_id` | `str` | Unique identifier for the API request |
| `success` | `bool` | Whether the operation was successful |
| `content` | `str` | Downloaded file content or local path |
| `error_message` | `str` | Error message if the operation failed |

**Example:**
```python
download_result = session.oss.download("my-bucket", "path/to/file.txt", "/tmp/downloaded_file.txt")
if download_result.success:
    print(f"Download successful: {download_result.content}")
else:
    print(f"Download failed: {download_result.error_message}")
```

## Common Operations

### Client Initialization
```python
# Initialize OSS client
client_result = session.oss.env_init(
    access_key_id="your_access_key_id",
    access_key_secret="your_access_key_secret",
    endpoint="oss-cn-hangzhou.aliyuncs.com",
    region="cn-hangzhou"
)

if client_result.success:
    print("OSS client ready")
else:
    print(f"Client initialization failed: {client_result.error_message}")
```

### File Upload
```python
# Upload single file
upload_result = session.oss.upload(
    bucket="my-bucket",
    object_key="uploads/file.txt",
    local_path="/tmp/file.txt"
)

# Upload with metadata
upload_result = session.oss.upload(
    bucket="my-bucket",
    object_key="uploads/file.txt",
    local_path="/tmp/file.txt",
    metadata={"content-type": "text/plain"}
)
```

### File Download
```python
# Download to local path
download_result = session.oss.download(
    bucket="my-bucket",
    object_key="uploads/file.txt",
    local_path="/tmp/downloaded_file.txt"
)

# Download to memory
download_result = session.oss.download(
    bucket="my-bucket",
    object_key="uploads/file.txt"
)
if download_result.success:
    content = download_result.content
    print(f"Downloaded content: {content}")
```

### Directory Operations
```python
# Upload directory (as zip)
upload_result = session.oss.upload(
    bucket="my-bucket",
    object_key="backups/project.zip",
    local_path="/tmp/my_project"  # Directory path
)

# Download and extract directory
download_result = session.oss.download(
    bucket="my-bucket",
    object_key="backups/project.zip",
    local_path="/tmp/restored_project"
)
```

## Best Practices

### Error Handling
```python
result = session.oss.upload("my-bucket", "file.txt", "/tmp/file.txt")
if result.success:
    print(f"Upload successful: {result.content}")
else:
    print(f"Upload failed: {result.error_message}")
    print(f"Request ID: {result.request_id}")
```

### Credential Management
```python
import os

# Use environment variables for credentials
client_result = session.oss.env_init(
    access_key_id=os.getenv("OSS_ACCESS_KEY_ID"),
    access_key_secret=os.getenv("OSS_ACCESS_KEY_SECRET"),
    endpoint=os.getenv("OSS_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com")
)
```

### Batch Operations
```python
# Upload multiple files
files_to_upload = [
    ("my-bucket", "file1.txt", "/tmp/file1.txt"),
    ("my-bucket", "file2.txt", "/tmp/file2.txt"),
    ("my-bucket", "file3.txt", "/tmp/file3.txt")
]

for bucket, object_key, local_path in files_to_upload:
    result = session.oss.upload(bucket, object_key, local_path)
    if result.success:
        print(f"Uploaded: {object_key}")
    else:
        print(f"Failed to upload {object_key}: {result.error_message}")
```

### Progress Monitoring
```python
# For large file uploads, monitor progress
upload_result = session.oss.upload(
    bucket="my-bucket",
    object_key="large_file.zip",
    local_path="/tmp/large_file.zip"
)

if upload_result.success:
    print(f"Upload completed: {upload_result.content}")
else:
    print(f"Upload failed: {upload_result.error_message}")
```

## Related Documentation

- **[OSS Module](../modules/oss.md)** - OSS operations documentation
- **[Session Management](../core/session.md)** - Session object documentation
- **[File System Results](filesystem-results.md)** - Local file operations
