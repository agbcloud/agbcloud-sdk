# Context Usage Guide

## Overview

Context is one of the core features of the AGB SDK, providing persistent storage capabilities that allow you to share and reuse data across different sessions. Context functionality is particularly suitable for scenarios that require maintaining state, storing files, or passing data between different sessions.

## Core Concepts

### Context Object
Context is a persistent storage container with the following characteristics:
- **Unique Identifier**: Each Context has a unique ID
- **Name**: A recognizable name for easy identification
- **Lifecycle**: Context exists independently of sessions and can be used across multiple sessions
- **File Storage**: Supports file upload, download, delete, and list operations
- **Sync Mechanism**: Supports automatic or manual data synchronization

### Context Synchronization
Context synchronization refers to the process of syncing local files with cloud storage:
- **Upload Sync**: Upload local files to cloud Context
- **Download Sync**: Download files from cloud Context to local
- **Policy Control**: Can configure automatic sync policies and timing

## Basic Usage

### 1. Initialize AGB Client

```python
from agb import AGB

# Method 1: Initialize with API Key directly
agb = AGB(api_key="your_api_key_here")
```

### 2. Create or Get Context

```python
# Create new Context
context_result = agb.context.create("my-project-context")
if context_result.success:
    context = context_result.context
    print(f"Created successfully: {context.name} (ID: {context.id})")
else:
    print(f"Creation failed: {context_result.error_message}")

# Or get existing Context (create if doesn't exist)
context_result = agb.context.get("my-project-context", create=True)
if context_result.success:
    context = context_result.context
    print(f"Retrieved successfully: {context.name} (ID: {context.id})")
```

### 3. List All Contexts

```python
# List all available Contexts
from agb.context import ContextListParams

list_result = agb.context.list(ContextListParams())
if list_result.success:
    print(f"Found {len(list_result.contexts)} Contexts:")
    for ctx in list_result.contexts:
        print(f"  - {ctx.name} (ID: {ctx.id}, Created: {ctx.created_at})")
```

## File Operations

### 1. Upload Files

```python
agb = AGB()
context = agb.context.get('test',True).context
upload_result = agb.context.get_file_upload_url(
    context_id=context.id,
    file_path="/tmp/my-file.txt"
)

if upload_result.success:
    # Use presigned URL to upload file
    import requests

    with open("local-file.txt", "rb") as f:
        response = requests.put(upload_result.url, data=f)
        if response.status_code in [200, 204]:
            print("File uploaded successfully")
        else:
            print(f"Upload failed: {response.status_code}")
else:
    print(f"Failed to get upload URL: {upload_result.error_message}")
```

### 2. Download Files

```python
agb = AGB()
context = agb.context.get('test',True).context
# Get download URL
download_result = agb.context.get_file_download_url(
    context_id=context.id,
    file_path="/tmp/my-file.txt"
)

if download_result.success:
    # Use presigned URL to download file
    import requests

    response = requests.get(download_result.url)
    if response.status_code == 200:
        with open("downloaded-file.txt", "wb") as f:
            f.write(response.content)
        print("File downloaded successfully")
    else:
        print(f"Download failed: {response.status_code}")
```

### 3. List Files

```python
agb = AGB()
context = agb.context.get('test',True).context
# List files in Context
files_result = agb.context.list_files(
    context_id=context.id,
    parent_folder_path="/tmp",
    page_number=1,
    page_size=50
)

if files_result.success:
    print(f"Found {len(files_result.entries)} files:")
    for file_info in files_result.entries:
        print(f"  - {file_info.file_path} (Size: {file_info.size} bytes)")
```

### 4. Delete Files

```python
agb = AGB()
context = agb.context.get('test',True).context
# Delete file
delete_result = agb.context.delete_file(
    context_id=context.id,
    file_path="/data/my-file.txt"
)

if delete_result.success:
    print("File deleted successfully",delete_result.data)
else:
    print(f"Delete failed: {delete_result.error_message}")
```

## Context Synchronization in Sessions

### 1. Create Session with Context Sync

```python
from agb.session_params import CreateSessionParams
from agb.context_sync import ContextSync, SyncPolicy

agb = AGB()
sync_policy = SyncPolicy()
context = agb.context.get('test',True).context

# Create Context sync configuration
context_sync = ContextSync.new(
    context_id=context.id,
    path="/home/wuying/my-data",  # Mount path in session
    policy=sync_policy
)

# Create session parameters
session_params = CreateSessionParams(
    image_id="agb-code-space-1",
    context_syncs=[context_sync]
)

# Create session
session_result = agb.create(session_params)
if session_result.success:
    session = session_result.session
    print(f"Session created successfully: {session.session_id}")
    agb.delete(session)
else:
    print(f"Session creation failed: {session_result.error_message}")
```

### 2. File Operations in Session

```python
# Create file in session
file_path = "/tmp/test-file.txt"
create_result = session.file_system.write_file(file_path, "Hello, Context!")

if create_result.success:
    print("File created successfully")

    # Manually trigger sync
    sync_result = await session.context.sync()
    if sync_result.success:
        print("Sync successful")
    else:
        print(f"Sync failed: {sync_result.error_message}")
else:
    print(f"File creation failed: {create_result.error_message}")
```

### 3. Monitor Sync Status

```python
# Get Context info
context_info = session.context.info()
if context_info.success:
    print(f"Context status data count: {len(context_info.context_status_data)}")

    for status_data in context_info.context_status_data:
        print(f"Context ID: {status_data.context_id}")
        print(f"Path: {status_data.path}")
        print(f"Status: {status_data.status}")
        print(f"Task Type: {status_data.task_type}")
        print(f"Start Time: {status_data.start_time}")
        print(f"Finish Time: {status_data.finish_time}")
        if status_data.error_message:
            print(f"Error Message: {status_data.error_message}")
```

## Advanced Features

### 1. Custom Sync Policies

```python
from agb.context_sync import (
    SyncPolicy, UploadPolicy, DownloadPolicy,
    DeletePolicy, ExtractPolicy, UploadStrategy, DownloadStrategy
)

# Create custom upload policy
upload_policy = UploadPolicy(
    auto_upload=True,
    upload_strategy=UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE
)

# Create custom download policy
download_policy = DownloadPolicy(
    auto_download=True,
    download_strategy=DownloadStrategy.DOWNLOAD_ASYNC
)

# Create custom delete policy
delete_policy = DeletePolicy(sync_local_file=True)

# Create custom extract policy
extract_policy = ExtractPolicy(
    extract=True,
    delete_src_file=True,
    extract_current_folder=False
)

# Combine into complete sync policy
sync_policy = SyncPolicy(
    upload_policy=upload_policy,
    download_policy=download_policy,
    delete_policy=delete_policy,
    extract_policy=extract_policy
)
```

### 2. Query Context Info with Parameters

```python
# Query specific Context and path info
context_info = session.context.info(
    context_id=context.id,
    path="/home/wuying/my-data",
    task_type="upload"  # Only query upload tasks
)

if context_info.success:
    print(f"Filtered status data: {len(context_info.context_status_data)}")
    for data in context_info.context_status_data:
        if data.context_id == context.id:
            print(f"Found matching Context: {data.path} - {data.status}")
```

### 3. Cross-Session Data Persistence

```python
context_sync = ContextSync.new(context_id=context.id, path="/home/wuying/my-data", policy=SyncPolicy())
session_params = CreateSessionParams(image_id="agb-code-space-1", context_syncs=[context_sync])

session1_result = agb.create(session_params)
if session1_result.success:
    session1 = session1_result.session

    # Create file in first session
    file_path = "/home/wuying/my-data/persistent-data.txt"
    create_result = session1.file_system.write_file(file_path, "This is persistent data")

    if create_result.success:
        print("File created successfully in session1")
    else:
        print(f"File creation failed: {create_result.error_message}")
        agb.delete(session1, sync_context=True)
        return

    # Sync to cloud
    await session1.context.sync()

    # Delete session (will auto-sync)
    agb.delete(session1, sync_context=True)

# Second session: Use data
session2_result = agb.create(session_params)
if session2_result.success:
    session2 = session2_result.session
    result = session2.file_system.read_file(file_path)

    # Check if file exists
    if result.success:
        print("Data persistence successful!")
        print(f"Read data: {result.content}")
    else:
        print(f"Failed to read file: {result.error_message}")

    agb.delete(session2)
```

## Best Practices

### 1. Context Naming Conventions
```python
# Use meaningful names
context_name = f"project-{project_id}-{user_id}"
context_name = f"data-processing-{timestamp}"
context_name = f"model-training-{model_version}"
```

### 2. Path Management
```python
# Use structured paths
base_path = "/tmp"
project_path = f"{base_path}/project-{project_id}"
model_path = f"{project_path}/models"
data_path = f"{project_path}/datasets"
```

### 3. Error Handling
```python
def safe_context_operation(operation_func, *args, **kwargs):
    """Safe Context operation wrapper"""
    try:
        result = operation_func(*args, **kwargs)
        if not result.success:
            print(f"Operation failed: {result.error_message}")
            return None
        return result
    except Exception as e:
        print(f"Operation exception: {str(e)}")
        return None

# Usage example
agb = AGB()
result = safe_context_operation(
    agb.context.get,
    "my-context",
    create=True
)
if result:  # Check if result is not None
    print(f"Context created: {result.context.name}")
```

### 4. Resource Cleanup
```python
def cleanup_context_resources(agb_client, context):
    """Clean up Context related resources"""
    try:
        # Delete all files in Context
        files_result = agb_client.context.list_files(
            context_id=context.id,
            parent_folder_path="/"
        )

        if files_result.success:
            for file_info in files_result.entries:
                agb_client.context.delete_file(
                    context_id=context.id,
                    file_path=file_info.file_path
                )

        # Delete Context
        agb_client.context.delete(context)
        print(f"Context {context.name} cleanup completed")

    except Exception as e:
        print(f"Cleanup failed: {str(e)}")
```

## Common Issues

### 1. Context Creation Failed
- Check if API Key is valid
- Confirm Context name doesn't already exist
- Check network connection

### 2. File Sync Failed
- Confirm Context sync policy is configured correctly
- Check if file path exists
- View error messages in sync status info

### 3. Permission Issues
- Confirm API Key has sufficient permissions
- Check if Context belongs to current user

### 4. Performance Optimization
- Use batch operations to reduce API calls
- Set reasonable sync policies to avoid frequent syncing
- Use pagination for large file lists

## Summary

Context functionality provides powerful persistent storage capabilities for the AGB SDK. Through proper use of Context and sync mechanisms, you can:

- Share data between different sessions
- Implement persistent data storage
- Support large file transfer and management
- Provide flexible data sync policies

Through the examples and best practices in this guide, you can fully leverage Context functionality to build more powerful and reliable applications.