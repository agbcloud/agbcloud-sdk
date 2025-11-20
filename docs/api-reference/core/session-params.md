# Session Parameters API Reference

Parameters for creating and managing sessions in the AGB cloud environment.

## CreateSessionParams Class

Parameters for creating a new session.

### Class Definition

```python
class CreateSessionParams:
    def __init__(
        self,
        labels: Optional[Dict[str, str]] = None,
        image_id: str ,
        context_syncs: Optional[List["ContextSync"]] = None,
        browser_context: Optional[BrowserContext] = None,
    )
```

### Parameters

#### `image_id`
- **Type:** `Optional[str]`
- **Default:** `None`
- **Description:** ID of the image to use for the session.
- **Required parameter** - if not provided, will result in a `PARAM_ERROR`.
#### `labels`
- **Type:** `Optional[Dict[str, str]]`
- **Default:** `None`
- **Description:** Key-value pairs for labeling and organizing sessions.
- **Example:** `{"environment": "development", "team": "backend"}`

#### `context_syncs`
- **Type:** `Optional[List[ContextSync]]`
- **Default:** `None`
- **Description:** List of context synchronization configurations for persistent data storage across sessions.

**ContextSync Parameters:**
- `context_id` (str): ID of the context to synchronize
- `path` (str): Path where the context should be mounted in the session
- `policy` (Optional[SyncPolicy]): Synchronization policy configuration

**SyncPolicy Options:**
- `upload_policy`: Defines the upload policy for context synchronization
  - `auto_upload` (bool): Enable automatic upload (default: True)
  - `upload_strategy`(UploadStrategy):
    - `UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE`: Upload strategy for context synchronization(Default)
  - `upload_mode` (UploadMode):
    - `UploadMode.FILE`: Upload files in original format(Default)
    - `UploadMode.ARCHIVE`: Compress files into ZIP format for efficient storage
- `download_policy`: Defines the download policy for context synchronization
  - `auto_download` (bool): Enable automatic download (default: True)
  - `download_strategy` (DownloadStrategy): Download strategy for context synchronization
    - `DownloadStrategy.DOWNLOAD_ASYNC`: Download files asynchronously (default)
- `delete_policy`: Defines the delete policy for context synchronization
  - `sync_local_file` (bool): Enables synchronization of local file deletions(default: True)
- `extract_policy`: Defines the extract policy for context synchronization
  - `extract` (bool): Enables file extraction (default: True)
  - `delete_src_file` (bool): Enables deletion of source file after extraction (default: True)
  - `extract_current_folder` (bool): Extract to current folder instead of creating new folder (default: False)
- `recycle_policy`: Defines the recycle policy for context synchronization
  - `lifecycle` (Lifecycle): Defines how long the context data should be retained (only the following values are supported)
    - `Lifecycle.LIFECYCLE_1DAY`: Keep data for 1 day
    - `Lifecycle.LIFECYCLE_3DAYS`: Keep data for 3 days
    - `Lifecycle.LIFECYCLE_5DAYS`: Keep data for 5 days
    - `Lifecycle.LIFECYCLE_10DAYS`: Keep data for 10 days
    - `Lifecycle.LIFECYCLE_15DAYS`: Keep data for 15 days
    - `Lifecycle.LIFECYCLE_30DAYS`: Keep data for 30 days
    - `Lifecycle.LIFECYCLE_90DAYS`: Keep data for 90 days
    - `Lifecycle.LIFECYCLE_180DAYS`: Keep data for 180 days
    - `Lifecycle.LIFECYCLE_360DAYS`: Keep data for 360 days
    - `Lifecycle.LIFECYCLE_FOREVER`: Keep data permanently (default)
  - `paths` (List[str]): Specific paths to apply recycle policy (default: [""])
    - **Note**: Wildcard patterns (* ? [ ]) are NOT supported. Use exact directory/file paths only
- `bw_list`: Black/white list configuration for selective sync
  - `white_lists` (List[WhiteList]): List of white list configurations
    - `path` (str): Path to include in white list
    - `exclude_paths` (List[str]): Paths to exclude from the white list

#### `browser_context`
- **Type:** `Optional[BrowserContext]`
- **Default:** `None`
- **Description:** Browser context configuration for sessions that require browser automation capabilities.

**BrowserContext Parameters:**
- `context_id` (str): ID of the browser context to bind to the session. This identifies the browser instance for the session.
- `auto_upload` (bool, optional): Whether to automatically upload browser data when the session ends. Defaults to True.
- `extension_option` (Optional[ExtensionOption], optional): Extension configuration object containing context_id and extension_ids. This encapsulates all extension-related configuration. Defaults to None.

**Auto-generated Properties:**
When `extension_option` is provided, the following properties are automatically set:
- `extension_context_id` (Optional[str]): ID of the extension context for browser extensions. Set automatically from extension_option.
- `extension_ids` (Optional[List[str]]): List of extension IDs to synchronize. Set automatically from extension_option.
- `extension_context_syncs` (Optional[List[ContextSync]]): Auto-generated context syncs for extensions. None if no extension configuration provided, or List[ContextSync] if extensions are configured.

**ExtensionOption Configuration:**
- `context_id` (str): ID of the extension context for browser extensions. This should match the context where extensions are stored.
- `extension_ids` (List[str]): List of extension IDs to be loaded in the browser session. Each ID should correspond to a valid extension in the context.

**Extension Context Sync Policy:**
when extension_option is provided and contains valid extension configuration (context_id and extension_ids), the system automatically creates a `ContextSync` with the following policy:
- **Upload Policy**: `auto_upload=False`
- **Delete Policy**: `sync_local_file=False`
- **Extract Policy**: `extract=True, delete_src_file=True`
- **Path**: `/tmp/extensions/` (default extension mount path)
- **White List**: Automatically configured for each extension ID
### Usage Examples

#### Basic Session Creation

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB(api_key="your_api_key")

# Create session with default parameters
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
if result.success:
    session = result.session
    print(f"Created session: {session.session_id}")
```

#### Session with Advanced Context Sync Configuration

##### Archive Mode for Efficient Storage

```python
from agb import AGB, ContextSync, SyncPolicy, UploadPolicy, UploadMode
from agb.session_params import CreateSessionParams

agb = AGB()

# Create or get a context
context_result = agb.context.get("my-project-context", create=True)
context = context_result.context

# Configure context sync with Archive mode for efficient storage
upload_policy = UploadPolicy(
    auto_upload=True,
    upload_mode=UploadMode.ARCHIVE  # Files will be compressed into ZIP
)
sync_policy = SyncPolicy(upload_policy=upload_policy)

context_sync = ContextSync.new(
    context_id=context.id,
    path="/workspace/project",
    policy=sync_policy
)

# Create session with context synchronization
params = CreateSessionParams(
    image_id="agb-code-space-1",
    labels={"project": "my-app", "environment": "development"},
    context_syncs=[context_sync]
)

result = agb.create(params)
if result.success:
    session = result.session
    print(f"Created session with context sync: {session.session_id}")

    # Files created in /workspace/project will be automatically
    # synchronized to the context storage
```

##### Temporary Files with Lifecycle Management

```python
from agb import AGB, ContextSync, SyncPolicy, RecyclePolicy, Lifecycle
from agb.session_params import CreateSessionParams

agb = AGB()

# Create or get a context
context_result = agb.context.get("cache-context", create=True)
context = context_result.context

# Configure recycle policy for temporary files
recycle_policy = RecyclePolicy(
    lifecycle=Lifecycle.LIFECYCLE_1DAY,
    paths=["test-data", "logs"]  # Use relative paths; "" means apply to all paths
)

sync_policy = SyncPolicy(recycle_policy=recycle_policy)
context_sync = ContextSync.new(context.id, "/tmp/cache", sync_policy)

# Create session with recycle policy
params = CreateSessionParams(
    image_id="agb-code-space-1",
    labels={"type": "cache", "retention": "1day"},
    context_syncs=[context_sync]
)

result = agb.create(params)
if result.success:
    session = result.session
    print(f"Created session with recycle policy: {session.session_id}")

    # Files in /tmp/cache and /tmp/logs will be automatically
    # deleted after 1 day
```

#### Session with Browser Context Configuration

##### Basic Browser Context

```python
# Basic browser context without extensions
from agb.session_params import BrowserContext, CreateSessionParams

browser_context = BrowserContext(
    context_id="browser_session",
    auto_upload=True
)

params = CreateSessionParams(
    image_id="agb-code-space-1",
    browser_context=browser_context
)
```

##### Browser Context with Extensions

```python
# Browser context with extensions
from agb.session_params import BrowserContext, CreateSessionParams
from agb.extension import ExtensionOption

# Configure extensions
ext_option = ExtensionOption(
    context_id="my_extensions",
    extension_ids=["ext_abc123.zip", "ext_def456.zip"]
)

# Create browser context with extension support
browser_context = BrowserContext(
    context_id="browser_session",
    auto_upload=True,
    extension_option=ext_option
)

params = CreateSessionParams(
    image_id="agb-code-space-1",
    browser_context=browser_context
)

# The browser_context will automatically generate extension_context_syncs
# for synchronizing browser extension data from the specified context
```

##### Complete Browser Session Creation

```python
# Complete session creation with browser context and extensions
from agb import AGB
from agb.session_params import BrowserContext, CreateSessionParams
from agb.extension import ExtensionOption

agb = AGB()

# Configure extension option
ext_option = ExtensionOption(
    context_id="browser_extensions_context",
    extension_ids=["chrome_extension_1", "chrome_extension_2"]
)

# Create browser context
browser_context = BrowserContext(
    context_id="main_browser_session",
    auto_upload=True,
    extension_option=ext_option
)

# Create session with browser context
params = CreateSessionParams(
    image_id="agb-code-space-1",
    labels={"type": "browser_automation", "extensions": "enabled"},
    browser_context=browser_context
)

result = agb.create(params)
if result.success:
    session = result.session
    print(f"Created browser session: {session.session_id}")
    # Browser extensions will be automatically loaded from the specified context
```

## Available Images

You can get available image IDs (like `agb-xxxx-xxx-x`) through the [AGB Console Image Management](https://agb.cloud/console/image-management).


### Image Selection

```python
# Use specific image
params = CreateSessionParams(image_id="agb-code-space-1")
```

## Related Content

- 🔧 **API Reference**: [AGB API](agb.md)
- 💡 **Examples**: [Session Examples](../../examples/README.md)
- 📚 **Best Practices**: [Best Practices Guide](../../guides/best-practices.md)