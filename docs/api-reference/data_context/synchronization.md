# Synchronization

This module defines classes and policies for context synchronization in the AGB SDK. It allows you to configure how data is synced between the local environment and the remote session.

## ContextSync

`ContextSync` defines the configuration for synchronizing a specific context to a path within the session.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `context_id` | `str` | ID of the context to synchronize. |
| `path` | `str` | Path where the context should be mounted in the session. |
| `policy` | `Optional[SyncPolicy]` | Defines the synchronization policy. |

### Methods

#### `new(cls, context_id: str, path: str, policy: Optional[SyncPolicy] = None)`
Creates a new context sync configuration.

#### `with_policy(self, policy: SyncPolicy)`
Sets the synchronization policy for this configuration.

---

## SyncPolicy

`SyncPolicy` defines the detailed policies for various aspects of synchronization.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `upload_policy` | `Optional[UploadPolicy]` | Policy for uploading files. |
| `download_policy` | `Optional[DownloadPolicy]` | Policy for downloading files. |
| `delete_policy` | `Optional[DeletePolicy]` | Policy for deleting files. |
| `extract_policy` | `Optional[ExtractPolicy]` | Policy for extracting archives. |
| `recycle_policy` | `Optional[RecyclePolicy]` | Policy for recycling/retention. |
| `bw_list` | `Optional[BWList]` | Black/White list configuration. |

---

## Policy Details

### UploadPolicy

Defines how files are uploaded.

- **`auto_upload`** (`bool`): Enables automatic upload (Default: `True`).
- **`upload_strategy`** (`UploadStrategy`): Strategy for upload (Default: `UPLOAD_BEFORE_RESOURCE_RELEASE`).
- **`upload_mode`** (`UploadMode`): Mode of upload (`FILE` or `ARCHIVE`) (Default: `FILE`).

### DownloadPolicy

Defines how files are downloaded.

- **`auto_download`** (`bool`): Enables automatic download (Default: `True`).
- **`download_strategy`** (`DownloadStrategy`): Strategy for download (Default: `DOWNLOAD_ASYNC`).

### DeletePolicy

Defines how deletions are handled.

- **`sync_local_file`** (`bool`): Enables synchronization of local file deletions (Default: `True`).

### ExtractPolicy

Defines how archives are handled.

- **`extract`** (`bool`): Enables file extraction (Default: `True`).
- **`delete_src_file`** (`bool`): Deletes source file after extraction (Default: `True`).
- **`extract_current_folder`** (`bool`): Extract to current folder (Default: `False`).

### RecyclePolicy

Defines data retention policies.

- **`lifecycle`** (`Lifecycle`): How long context data is retained (Default: `LIFECYCLE_FOREVER`).
- **`paths`** (`List[str]`): Paths subject to this policy (Default: `[""]` - all paths).

---

## Enums

### UploadStrategy
- `UPLOAD_BEFORE_RESOURCE_RELEASE`: Upload changes before the session resource is released.

### DownloadStrategy
- `DOWNLOAD_ASYNC`: Download files asynchronously.

### UploadMode
- `FILE`: Upload as individual files.
- `ARCHIVE`: Upload as an archive.

### Lifecycle
Options range from `LIFECYCLE_1DAY` to `LIFECYCLE_360DAYS` and `LIFECYCLE_FOREVER`.

