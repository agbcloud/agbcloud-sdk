# Configurations API Reference

## ⚙️ Related Tutorial

- [Session Management Guide](../../guides/session-management.md) - Learn how to configure sessions

## Overview

Configuration parameters for creating and managing AGB sessions.




## BrowserContext

```python
class BrowserContext()
```

Browser context configuration for session.

This class provides browser context configuration for cloud sessions, supports browser fingerprint
context persistence, supports automatic extension synchronization when ExtensionOption is provided.

Key Features:
- Browser context binding for sessions
- Automatic browser data upload on session end
- Optional browser fingerprint integration with automatic context sync generation
- Optional extension integration with automatic context sync generation
- Clean API with ExtensionOption encapsulation

**Attributes**:

- `context_id` _str_ - ID of the browser context to bind to the session
- `auto_upload` _bool_ - Whether to automatically upload browser data when session ends
- `fingerprint_context` _Optional[BrowserFingerprintContext]_ - Browser fingerprint context configuration object containing
  fingerprint_context_id.
- `extension_option` _Optional[ExtensionOption]_ - Extension configuration object containing
  context_id and extension_ids.
- `extension_context_id` _Optional[str]_ - ID of the extension context for browser extensions.
  Set automatically from extension_option.
- `extension_ids` _Optional[List[str]]_ - List of extension IDs to synchronize.
  Set automatically from extension_option.
- `extension_context_syncs` _Optional[List[ContextSync]]_ - Auto-generated context syncs for extensions.
  None if no extension configuration provided,
  or List[ContextSync] if extensions are configured.

  Extension Configuration:
  - **ExtensionOption**: Pass an ExtensionOption object with context_id and extension_ids
  - **No Extensions**: Don't provide extension_option parameter (extension_context_syncs will be None)

  Usage Examples:
    ```python
    # With extensions using ExtensionOption
    from agb.extension import ExtensionOption

    ext_option = ExtensionOption(
        context_id="my_extensions",
        extension_ids=["ext1", "ext2"]
    )

    browser_context = BrowserContext(
        context_id="browser_session",
        auto_upload=True,
        extension_option=ext_option
    )

    # Without extensions (minimal configuration)
    browser_context = BrowserContext(
        context_id="browser_session",
        auto_upload=True
    )
    # extension_context_syncs will be None
    ```

### get\_extension\_context\_syncs

```python
def get_extension_context_syncs() -> List[ContextSync]
```

Get context syncs for extensions.

**Returns**:

    List[ContextSync]: Context sync configurations for extensions.
  Returns empty list if no extensions configured.

### get\_fingerprint\_context\_sync

```python
def get_fingerprint_context_sync() -> ContextSync
```

Get context sync for fingerprint.

**Returns**:

    ContextSync: Context sync configurations for fingerprint.
  Returns None if fingerprint configuration is invalid.

## CreateSessionParams

```python
class CreateSessionParams()
```

Parameters for creating a new session in the AGB cloud environment.

**Attributes**:

- `labels` _Optional[Dict[str, str]]_ - Custom labels for the Session. These can be
  used for organizing and filtering sessions.
- `image_id` _Optional[str]_ - ID of the image to use for the session.

- `context_syncs` _Optional[List[ContextSync]]_ - List of context synchronization configurations.
- `browser_context` _Optional[BrowserContext]_ - Optional configuration for browser data synchronization.

#### BROWSER\_DATA\_PATH

```python
BROWSER_DATA_PATH = "/tmp/agb_browser_data"
```

#### BROWSER\_FINGERPRINT\_PERSIST\_PATH

```python
BROWSER_FINGERPRINT_PERSIST_PATH = "/tmp/agb_browser_fingerprint"
```

## Config

```python
class Config()
```

Configuration class for AGB client.

### default\_config

```python
def default_config() -> Config
```

Return the default configuration

### load\_config

```python
def load_config(cfg: Optional[Config] = None) -> Config
```

Load configuration with the specified precedence order.

## Related Resources

- [AGB API Reference](../agb.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
