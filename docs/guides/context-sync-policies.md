# Context Sync Policies Guide

## Overview

Context sync policies control the synchronization behavior of data between local and cloud storage. By properly configuring sync policies, you can optimize performance, control resource usage, and ensure data consistency.

## Sync Policy Components

### 1. UploadPolicy

Controls file upload behavior and timing.

```python
from agb.context_sync import UploadPolicy, UploadStrategy

# Basic configuration
upload_policy = UploadPolicy(
    auto_upload=True,  # Enable automatic upload
    upload_strategy=UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE  # Upload strategy
)
```

**Parameters:**
- `auto_upload` (bool): Whether to enable automatic upload
- `upload_strategy` (UploadStrategy): Upload strategy
  - `UPLOAD_BEFORE_RESOURCE_RELEASE`: Upload before resource release

### 2. DownloadPolicy

Controls file download behavior.

```python
from agb.context_sync import DownloadPolicy, DownloadStrategy

# Basic configuration
download_policy = DownloadPolicy(
    auto_download=True,  # Enable automatic download
    download_strategy=DownloadStrategy.DOWNLOAD_ASYNC  # Async download
)
```

**Parameters:**
- `auto_download` (bool): Whether to enable automatic download
- `download_strategy` (DownloadStrategy): Download strategy
  - `DOWNLOAD_ASYNC`: Async download

### 3. DeletePolicy

Controls file deletion sync behavior.

```python
from agb.context_sync import DeletePolicy

# Basic configuration
delete_policy = DeletePolicy(
    sync_local_file=True  # Sync local file deletion to cloud
)
```

**Parameters:**
- `sync_local_file` (bool): Whether to sync local file deletion to cloud

### 4. ExtractPolicy

Controls file extraction and decompression behavior.

```python
from agb.context_sync import ExtractPolicy

# Basic configuration
extract_policy = ExtractPolicy(
    extract=True,  # Enable file extraction
    delete_src_file=True,  # Delete source file after extraction
    extract_current_folder=False  # Don't extract to current folder
)
```

**Parameters:**
- `extract` (bool): Whether to enable file extraction
- `delete_src_file` (bool): Whether to delete source file after extraction
- `extract_current_folder` (bool): Whether to extract to current folder

### 5. BWList (Black/White List)

Controls which file paths participate in sync.

```python
from agb.context_sync import BWList, WhiteList

# Create white list
white_list = WhiteList(
    path="/home/wuying/data",  # Include path
    exclude_paths=["/home/wuying/data/temp", "/home/wuying/data/cache"]  # Exclude sub-paths
)

# Create black/white list configuration
bw_list = BWList(white_lists=[white_list])
```

## Complete Sync Policy Configuration

```python
from agb.context_sync import (
    SyncPolicy, UploadPolicy, DownloadPolicy,
    DeletePolicy, ExtractPolicy, BWList, WhiteList,
    UploadStrategy, DownloadStrategy
)

# Create complete sync policy
sync_policy = SyncPolicy(
    # Upload policy
    upload_policy=UploadPolicy(
        auto_upload=True,
        upload_strategy=UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE
    ),

    # Download policy
    download_policy=DownloadPolicy(
        auto_download=True,
        download_strategy=DownloadStrategy.DOWNLOAD_ASYNC
    ),

    # Delete policy
    delete_policy=DeletePolicy(
        sync_local_file=True
    ),

    # Extract policy
    extract_policy=ExtractPolicy(
        extract=True,
        delete_src_file=False,  # Keep source file
        extract_current_folder=True
    ),

    # Black/white list
    bw_list=BWList(
        white_lists=[
            WhiteList(
                path="/home/wuying/project",
                exclude_paths=[
                    "/home/wuying/project/temp",
                    "/home/wuying/project/logs",
                    "/home/wuying/project/.git"
                ]
            )
        ]
    )
)
```

## Use Cases and Recommended Configurations

### 1. Development Environment Configuration

Suitable for frequent code modification scenarios:

```python
dev_sync_policy = SyncPolicy(
    upload_policy=UploadPolicy(
        auto_upload=True,
        upload_strategy=UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE
    ),
    download_policy=DownloadPolicy(
        auto_download=True,
        download_strategy=DownloadStrategy.DOWNLOAD_ASYNC
    ),
    delete_policy=DeletePolicy(sync_local_file=True),
    extract_policy=ExtractPolicy(
        extract=True,
        delete_src_file=False,
        extract_current_folder=True
    ),
    bw_list=BWList(
        white_lists=[
            WhiteList(
                path="/home/wuying/project",
                exclude_paths=[
                    "/home/wuying/project/node_modules",
                    "/home/wuying/project/.git",
                    "/home/wuying/project/temp"
                ]
            )
        ]
    )
)
```

### 2. Production Environment Configuration

Suitable for stable production environments:

```python
prod_sync_policy = SyncPolicy(
    upload_policy=UploadPolicy(
        auto_upload=True,
        upload_strategy=UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE
    ),
    download_policy=DownloadPolicy(
        auto_download=True,
        download_strategy=DownloadStrategy.DOWNLOAD_ASYNC
    ),
    delete_policy=DeletePolicy(sync_local_file=False),  # Don't auto delete
    extract_policy=ExtractPolicy(
        extract=True,
        delete_src_file=True,
        extract_current_folder=False
    ),
    bw_list=BWList(
        white_lists=[
            WhiteList(
                path="/home/wuying/data",
                exclude_paths=[]  # Don't exclude any paths
            )
        ]
    )
)
```

### 3. Big Data Processing Configuration

Suitable for processing large amounts of data:

```python
big_data_sync_policy = SyncPolicy(
    upload_policy=UploadPolicy(
        auto_upload=False,  # Disable auto upload, manual control
        upload_strategy=UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE
    ),
    download_policy=DownloadPolicy(
        auto_download=False,  # Disable auto download, on-demand download
        download_strategy=DownloadStrategy.DOWNLOAD_ASYNC
    ),
    delete_policy=DeletePolicy(sync_local_file=True),
    extract_policy=ExtractPolicy(
        extract=True,
        delete_src_file=True,
        extract_current_folder=True
    ),
    bw_list=BWList(
        white_lists=[
            WhiteList(
                path="/home/wuying/datasets",
                exclude_paths=[
                    "/home/wuying/datasets/raw",  # Exclude raw data
                    "/home/wuying/datasets/temp"
                ]
            )
        ]
    )
)
```

## Using Sync Policies in Sessions

```python
from agb.session_params import CreateSessionParams
from agb.context_sync import ContextSync

# Create session parameters
session_params = CreateSessionParams(image_id="agb-code-space-1")

# Create Context sync configuration
context_sync = ContextSync.new(
    context_id=context.id,
    path="/home/wuying/my-workspace",
    policy=sync_policy  # Use the policy defined above
)

session_params.context_syncs = [context_sync]

# Create session
session_result = agb.create(session_params)
```

## Monitor Sync Status

```python
# Get sync status
context_info = session.context.info()

print(f"Sync status data: {len(context_info.context_status_data)} items")
for status in context_info.context_status_data:
    print(f"Context ID: {status.context_id}")
    print(f"Path: {status.path}")
    print(f"Status: {status.status}")
    print(f"Task Type: {status.task_type}")
    print(f"Start Time: {status.start_time}")
    print(f"Finish Time: {status.finish_time}")
    if status.error_message:
        print(f"Error Message: {status.error_message}")
    print("---")
```

## Manual Sync Control

```python
# Manually trigger sync
sync_result = await session.context.sync()
if sync_result.success:
    print("Sync successful")
else:
    print(f"Sync failed: {sync_result.error_message}")

# Auto sync when deleting session
delete_result = agb.delete(session, sync_context=True)
```

## Best Practices

### 1. Sync Strategy Settings
- Development environment: Enable auto upload for frequent changes
- Test environment: Enable auto upload with moderate frequency
- Production environment: Enable auto upload for stability

### 2. Use Black/White List Filtering
- Exclude temporary files and cache
- Exclude version control directories (.git, .svn)
- Exclude log files
- Exclude large dependency directories (node_modules, venv)

### 3. Choose Policies Based on Data Characteristics
- Code files: Frequent sync, keep source files
- Data files: On-demand sync, can delete source files
- Model files: Manual sync, avoid auto deletion

### 4. Monitor Sync Status
- Regularly check sync status
- Handle sync errors
- Log sync activities

## Troubleshooting

### 1. Sync Failed
```python
# Check sync status
context_info = session.context.info()
for status in context_info.context_status_data:
    if status.error_message:
        print(f"Sync error: {status.error_message}")
```

### 2. Files Not Synced
- Check black/white list configuration
- Confirm file path is correct
- Check file permissions

### 3. Performance Issues
- Optimize black/white list
- Consider batch syncing large files

By properly configuring sync policies, you can ensure efficient and reliable data synchronization between local and cloud storage while optimizing resource usage and performance.
