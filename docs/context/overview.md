# Use context for persistence across sessions

## Overview

**Context Sync** is the core feature for data persistence in the AGB SDK: it automatically synchronizes files from your session to cloud storage and restores them in new sessions.

## Core concepts

### The relationship between Context, ContextSync, and Session

```
Context (Persistent Storage)    ContextSync (Sync Config)        Session (Execution Environment)
┌─────────────────┐            ┌────────────────────┐            ┌─────────────────┐
│ ID: SdkCtx-xxx  │───────────►│ ContextID          │───────────►│ Mount Path      │
│ Name: my-ctx    │            │ Path: /home/project│            │ /home/project   │
│ Cloud Storage   │            │ Policy: Sync Rules │            │ in Session      │
└─────────────────┘            └────────────────────┘            └─────────────────┘
```

- **Context**: Persistent storage entity with a unique ID and name, backed by cloud storage.
- **ContextSync**: Sync configuration that mounts a Context into a Session at a given path with a sync policy.
- **Session**: Runtime environment; the mount path is where the Context is visible inside the Session.

## What you'll do

Create a **Context** (persistent storage), attach it to sessions via **ContextSync**, and synchronize data across sessions.

## Prerequisites

- `AGB_API_KEY`
- A valid `image_id` (commonly `agb-code-space-1` for code/file workflows)
- Permission to create contexts and sessions in your account

## Quickstart

Minimal runnable example: create/get a context, mount it into a session, then delete the session.

::: code-group

```python [Python]
from agb import AGB
from agb.context_sync import ContextSync, SyncPolicy
from agb.session_params import CreateSessionParams

agb = AGB()

context_result = agb.context.get("my-project", create=True)
if not context_result.success:
    raise SystemExit(f"Context get/create failed: {context_result.error_message}")
context = context_result.context

sync = ContextSync.new(
    context_id=context.id,
    path="/home/project",
    policy=SyncPolicy(),
)

create_result = agb.create(
    CreateSessionParams(image_id="agb-code-space-1", context_syncs=[sync])
)
if not create_result.success:
    raise SystemExit(f"Session creation failed: {create_result.error_message}")

session = create_result.session
agb.delete(session)
```

```typescript [TypeScript]
import { AGB, CreateSessionParams } from "agbcloud-sdk";
import { ContextSync, newSyncPolicy } from "agbcloud-sdk/context-sync";

const agb = new AGB();

const contextResult = await agb.context.get("my-project", true);
if (!contextResult.success || !contextResult.context) {
  throw new Error(`Context get/create failed: ${contextResult.errorMessage}`);
}
const context = contextResult.context;

const sync = ContextSync.new(context.id, "/home/project", newSyncPolicy());

const createResult = await agb.create(
  new CreateSessionParams({
    imageId: "agb-code-space-1",
    contextSync: [sync],
  })
);
if (!createResult.success || !createResult.session) {
  throw new Error(`Session creation failed: ${createResult.errorMessage}`);
}

const session = createResult.session;
await agb.delete(session);
```

:::

## Best practices

### 1. Use meaningful names when creating contexts

::: code-group

```python [Python]
context_result = agb.context.get("project-alpha-workspace", create=True)  # ✅
context_result = agb.context.get("ctx-123", create=True)                  # ❌
```

```typescript [TypeScript]
const result = await agb.context.get("project-alpha-workspace", true);  // ✅
const result2 = await agb.context.get("ctx-123", true);                 // ❌
```

:::

> **Important**: The same context cannot be used across different API keys or regions. Even with the same name, a different API key or region yields a different context.

### 2. Configure sync policies appropriately

#### Standard workflow (recommended)

Suitable for most scenarios; automatically downloads and uploads data:

::: code-group

```python [Python]
from agb.context_sync import (
    SyncPolicy, UploadPolicy, DownloadPolicy, DeletePolicy,
    UploadMode, UploadStrategy, DownloadStrategy,
)

sync_policy = SyncPolicy(
    upload_policy=UploadPolicy(
        auto_upload=True,
        upload_strategy=UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE,
        upload_mode=UploadMode.FILE,
    ),
    download_policy=DownloadPolicy(
        auto_download=True,
        download_strategy=DownloadStrategy.DOWNLOAD_ASYNC,
    ),
    delete_policy=DeletePolicy(sync_local_file=True),
)
```

```typescript [TypeScript]
import {
  newSyncPolicy, newUploadPolicy, newDownloadPolicy, newDeletePolicy,
  UploadStrategy, UploadMode, DownloadStrategy,
} from "agbcloud-sdk/context-sync";

const syncPolicy = newSyncPolicy({
  uploadPolicy: newUploadPolicy({
    autoUpload: true,
    uploadStrategy: UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE,
    uploadMode: UploadMode.FILE,
  }),
  downloadPolicy: newDownloadPolicy({
    autoDownload: true,
    downloadStrategy: DownloadStrategy.DOWNLOAD_ASYNC,
  }),
  deletePolicy: newDeletePolicy({ syncLocalFile: true }),
});
```

:::

#### Large file scenario

When syncing large or many files, use archive (compression) mode:

::: code-group

```python [Python]
from agb.context_sync import (
    SyncPolicy, UploadPolicy, DownloadPolicy, ExtractPolicy,
    UploadMode, UploadStrategy, DownloadStrategy,
)

sync_policy = SyncPolicy(
    upload_policy=UploadPolicy(
        auto_upload=True,
        upload_strategy=UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE,
        upload_mode=UploadMode.ARCHIVE,
    ),
    download_policy=DownloadPolicy(
        auto_download=True,
        download_strategy=DownloadStrategy.DOWNLOAD_ASYNC,
    ),
    extract_policy=ExtractPolicy(
        extract=True,
        delete_src_file=True,
        extract_current_folder=True,
    ),
)
```

```typescript [TypeScript]
const syncPolicy = newSyncPolicy({
  uploadPolicy: newUploadPolicy({
    autoUpload: true,
    uploadStrategy: UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE,
    uploadMode: UploadMode.ARCHIVE,
  }),
  downloadPolicy: newDownloadPolicy({
    autoDownload: true,
    downloadStrategy: DownloadStrategy.DOWNLOAD_ASYNC,
  }),
  extractPolicy: newExtractPolicy({
    extract: true,
    deleteSrcFile: true,
    extractCurrentFolder: true,
  }),
});
```

:::

> **Important**: If files in your persistence directory will grow in quantity and size, enable archive mode from the start. Switching between compression and non-compression is not supported; choose at initialization.

#### Read-only data scenario

When a session only needs to read data without writing back:

::: code-group

```python [Python]
sync_policy = SyncPolicy(
    upload_policy=UploadPolicy(auto_upload=False),
    download_policy=DownloadPolicy(
        auto_download=True,
        download_strategy=DownloadStrategy.DOWNLOAD_ASYNC,
    ),
)
```

```typescript [TypeScript]
const syncPolicy = newSyncPolicy({
  uploadPolicy: newUploadPolicy({ autoUpload: false }),
  downloadPolicy: newDownloadPolicy({
    autoDownload: true,
    downloadStrategy: DownloadStrategy.DOWNLOAD_ASYNC,
  }),
});
```

:::

### 3. Use whitelists to control sync scope

Only sync necessary directories; exclude build artifacts and the like:

::: code-group

```python [Python]
from agb.context_sync import SyncPolicy, BWList, WhiteList

bw_list = BWList(
    white_lists=[
        WhiteList(path="/src", exclude_paths=["/node_modules", "/dist"]),
        WhiteList(path="/config"),
    ],
)
sync_policy = SyncPolicy(
    upload_policy=UploadPolicy(auto_upload=True),
    download_policy=DownloadPolicy(auto_download=True),
    bw_list=bw_list,
)
```

```typescript [TypeScript]
const syncPolicy = newSyncPolicy({
  uploadPolicy: newUploadPolicy({ autoUpload: true }),
  downloadPolicy: newDownloadPolicy({ autoDownload: true }),
  bwList: {
    whiteLists: [
      { path: "/src", excludePaths: ["/node_modules", "/dist"] },
      { path: "/config", excludePaths: [] },
    ],
  },
});
```

:::

> **Important**: Whitelist paths are relative to the mount point. Wildcard patterns (e.g. `*.json`, `/data/*`) are not supported; use exact directory paths.

### 4. Select mount paths correctly

::: code-group

```python [Python]
context_sync = ContextSync.new(context.id, "/home/project", sync_policy)    # ✅
context_sync = ContextSync.new(context.id, "/tmp/workspace", sync_policy)   # ✅
# context_sync = ContextSync.new(context.id, "/opt", sync_policy)           # ❌
```

```typescript [TypeScript]
const ctxSync = ContextSync.new(context.id, "/home/project", syncPolicy);   // ✅
const ctxSync2 = ContextSync.new(context.id, "/tmp/workspace", syncPolicy); // ✅
// ContextSync.new(context.id, "/opt", syncPolicy);                         // ❌
```

:::

### 5. Ensure data sync completes when deleting sessions

::: code-group

```python [Python]
agb.delete(session, sync_context=True)
```

```typescript [TypeScript]
await agb.delete(session);
```

:::

### 6. File expiration (RecyclePolicy)

::: code-group

```python [Python]
from agb.context_sync import SyncPolicy, RecyclePolicy, Lifecycle

sync_policy = SyncPolicy(
    upload_policy=UploadPolicy(auto_upload=True),
    download_policy=DownloadPolicy(auto_download=True),
    recycle_policy=RecyclePolicy(
        lifecycle=Lifecycle.LIFECYCLE_30DAYS,
        paths=[""],
    ),
)
```

```typescript [TypeScript]
import { Lifecycle, newRecyclePolicy } from "agbcloud-sdk/context-sync";

const syncPolicy = newSyncPolicy({
  uploadPolicy: newUploadPolicy({ autoUpload: true }),
  downloadPolicy: newDownloadPolicy({ autoDownload: true }),
  recyclePolicy: newRecyclePolicy({
    lifecycle: Lifecycle.LIFECYCLE_30DAYS,
    paths: [""],
  }),
});
```

:::

## Complete examples

### Scenario 1: Standard workflow

**Use cases**: Dev environment configs, small project files, user preferences. **Characteristics**: Few files, small size, frequent read/write.

::: code-group

```python [Python]
from agb import AGB
from agb.context_sync import (
    ContextSync, SyncPolicy, UploadPolicy, DownloadPolicy, DeletePolicy,
    UploadMode, UploadStrategy, DownloadStrategy,
)
from agb.session_params import CreateSessionParams

agb = AGB()
context = agb.context.get("my-project-workspace", create=True).context

sync_policy = SyncPolicy(
    upload_policy=UploadPolicy(
        auto_upload=True,
        upload_strategy=UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE,
        upload_mode=UploadMode.FILE,
    ),
    download_policy=DownloadPolicy(
        auto_download=True,
        download_strategy=DownloadStrategy.DOWNLOAD_ASYNC,
    ),
    delete_policy=DeletePolicy(sync_local_file=True),
)
context_sync = ContextSync.new(context.id, "/home/project/workspace", sync_policy)

result = agb.create(
    CreateSessionParams(image_id="agb-code-space-1", context_syncs=[context_sync])
)
session = result.session
# Work in the session...
agb.delete(session, sync_context=True)
```

```typescript [TypeScript]
import { AGB, CreateSessionParams } from "agbcloud-sdk";
import {
  ContextSync, newSyncPolicy, newUploadPolicy, newDownloadPolicy, newDeletePolicy,
  UploadStrategy, UploadMode, DownloadStrategy,
} from "agbcloud-sdk/context-sync";

const agb = new AGB();
const ctx = (await agb.context.get("my-project-workspace", true)).context!;

const syncPolicy = newSyncPolicy({
  uploadPolicy: newUploadPolicy({
    autoUpload: true,
    uploadStrategy: UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE,
    uploadMode: UploadMode.FILE,
  }),
  downloadPolicy: newDownloadPolicy({
    autoDownload: true,
    downloadStrategy: DownloadStrategy.DOWNLOAD_ASYNC,
  }),
  deletePolicy: newDeletePolicy({ syncLocalFile: true }),
});
const ctxSync = ContextSync.new(ctx.id, "/home/project/workspace", syncPolicy);

const result = await agb.create(
  new CreateSessionParams({ imageId: "agb-code-space-1", contextSync: [ctxSync] })
);
const session = result.session!;
// Work in the session...
await agb.delete(session);
```

:::

### Scenario 2: Large file archive mode

**Use cases**: Model files, large repos, log archives, browser user data. **Characteristics**: Many files, complex directories, large total size, higher transfer efficiency needed.

::: code-group

```python [Python]
from agb import AGB
from agb.context_sync import (
    ContextSync, SyncPolicy, UploadPolicy, DownloadPolicy, DeletePolicy, ExtractPolicy,
    UploadMode, UploadStrategy, DownloadStrategy,
)
from agb.session_params import CreateSessionParams

agb = AGB()
context = agb.context.get("browser-user-data", create=True).context

sync_policy = SyncPolicy(
    upload_policy=UploadPolicy(
        auto_upload=True,
        upload_strategy=UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE,
        upload_mode=UploadMode.ARCHIVE,
    ),
    download_policy=DownloadPolicy(
        auto_download=True, download_strategy=DownloadStrategy.DOWNLOAD_ASYNC,
    ),
    extract_policy=ExtractPolicy(
        extract=True, delete_src_file=True, extract_current_folder=True,
    ),
    delete_policy=DeletePolicy(sync_local_file=True),
)
context_sync = ContextSync.new(
    context.id, "/home/project/.config/google-chrome", sync_policy,
)

result = agb.create(
    CreateSessionParams(image_id="agb-code-space-1", context_syncs=[context_sync])
)
session = result.session
agb.delete(session, sync_context=True)
```

```typescript [TypeScript]
import { AGB, CreateSessionParams } from "agbcloud-sdk";
import {
  ContextSync, newSyncPolicy, newUploadPolicy, newDownloadPolicy,
  newDeletePolicy, newExtractPolicy,
  UploadStrategy, UploadMode, DownloadStrategy,
} from "agbcloud-sdk/context-sync";

const agb = new AGB();
const ctx = (await agb.context.get("browser-user-data", true)).context!;

const syncPolicy = newSyncPolicy({
  uploadPolicy: newUploadPolicy({
    autoUpload: true,
    uploadStrategy: UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE,
    uploadMode: UploadMode.ARCHIVE,
  }),
  downloadPolicy: newDownloadPolicy({
    autoDownload: true, downloadStrategy: DownloadStrategy.DOWNLOAD_ASYNC,
  }),
  extractPolicy: newExtractPolicy({
    extract: true, deleteSrcFile: true, extractCurrentFolder: true,
  }),
  deletePolicy: newDeletePolicy({ syncLocalFile: true }),
});
const ctxSync = ContextSync.new(
  ctx.id, "/home/project/.config/google-chrome", syncPolicy,
);

const result = await agb.create(
  new CreateSessionParams({ imageId: "agb-code-space-1", contextSync: [ctxSync] })
);
const session = result.session!;
await agb.delete(session);
```

:::

## Common tasks

Detailed content is split into smaller pages:

- Context basics (create/get/list): [`docs/context/basics.md`](basics.md)
- Context file operations (upload/download/list/delete): [`docs/context/file-operations.md`](file-operations.md)
- Sync in sessions (manual sync, status, modes): [`docs/context/sync-in-sessions.md`](sync-in-sessions.md)
- Sync policies (advanced): [`docs/context/sync-policies.md`](sync-policies.md)
- Cross-platform persistence: [`docs/context/cross-platform-persistence.md`](cross-platform-persistence.md)

## FAQ & Troubleshooting

### Data not persisting

**Symptom**: Files are missing when creating a new session.

**Cause**: Data was not fully synced before the session was deleted.

**Solution**:

::: code-group

```python [Python]
agb.delete(session, sync_context=True)
```

```typescript [TypeScript]
await agb.delete(session);
```

:::

### Permission denied

**Symptom**: Permission error when creating or writing files.

**Solution**: Use a directory with write permissions as the mount path (see "Select mount paths correctly" above).

### Whitelist not working

**Symptom**: Files do not sync as expected despite whitelist configuration.

**Cause**: Paths use wildcards or absolute paths; they should be relative to the mount point.

**Solution**:

```python
# ❌ Wrong: Wildcards
# WhiteList(path="*.json")
# WhiteList(path="/src/*")

# ❌ Wrong: Absolute path when relative to mount is intended
# If mount is /home/project, do not use /home/project/src

# ✅ Correct: Paths relative to mount point
WhiteList(path="/src")
WhiteList(path="/config")
```

More troubleshooting: [`docs/context/best-practices.md`](best-practices.md), [`docs/context/troubleshooting.md`](troubleshooting.md).

## Related

- API reference (Context): [`docs/api-reference/python/data_context/context.md`](../api-reference/python/data_context/context.md)
- API reference (sync): [`docs/api-reference/python/data_context/synchronization.md`](../api-reference/python/data_context/synchronization.md)
- Examples: [`docs/examples/data_persistence/README.md`](../examples/data_persistence/README.md)
