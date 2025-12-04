# Extension API Reference

## 🧩 Related Tutorial

- [Browser Automation Guide](../../guides/browser-automation.md) - Learn how to use browser extensions and automation

## Overview

The Extension module provides capabilities for working with browser extensions
and extending the functionality of the AGB platform.




#### EXTENSIONS\_BASE\_PATH

```python
EXTENSIONS_BASE_PATH = "/tmp/extensions"
```

## Extension

```python
class Extension()
```

Represents a browser extension as a cloud resource.

## ExtensionOption

```python
class ExtensionOption()
```

Configuration options for browser extension integration.

This class encapsulates the necessary parameters for setting up
browser extension synchronization and context management.

**Attributes**:

- `context_id` _str_ - ID of the extension context for browser extensions
- `extension_ids` _List[str]_ - List of extension IDs to be loaded/synchronized

### validate

```python
def validate() -> bool
```

Validate the extension option configuration.

**Returns**:

    bool: True if configuration is valid, False otherwise.

## ExtensionsService

```python
class ExtensionsService()
```

Provides methods to manage user browser extensions.
This service integrates with the existing context functionality for file operations.

**Usage** (Simplified - Auto-detection):
```python
# Service automatically detects if context exists and creates if needed
extensions_service = ExtensionsService(agb, "browser_extensions")

# Or use with empty context_id to auto-generate context name
extensions_service = ExtensionsService(agb)  # Uses default generated name

# Use the service immediately
extension = extensions_service.create("/path/to/plugin.zip")
```

**Integration with ExtensionOption (Simplified)**:
```python
# Create extensions and configure for browser sessions
extensions_service = ExtensionsService(agb, "my_extensions")
ext1 = extensions_service.create("/path/to/ext1.zip")
ext2 = extensions_service.create("/path/to/ext2.zip")

# Create extension option for browser integration (no context_id needed!)
ext_option = extensions_service.create_extension_option([ext1.id, ext2.id])

# Use with BrowserContext for session creation
browser_context = BrowserContext(
    context_id="browser_session",
    auto_upload=True,
    extension_option=ext_option  # All extension config encapsulated
)
```

**Context Management**:
- If context_id provided and exists: Uses the existing context
- If context_id provided but doesn't exist: Creates context with provided name
- If context_id empty or not provided: Generates default name and creates context
- No need to manually manage context creation

### list

```python
def list() -> List[Extension]
```

Lists all available browser extensions within this context from the cloud.
Uses the context service to list files under the extensions directory.

**Returns**:

    List[Extension]: A list of Extension objects.

### create

```python
def create(local_path: str) -> Extension
```

Uploads a new browser extension from a local path into the current context.

**Arguments**:

- `local_path` _str_ - Path to the local extension file (must be .zip).


**Returns**:

    Extension: The created Extension object.


**Raises**:

    FileNotFoundError: If the local file does not exist.
    ValueError: If the file format is not supported.

### update

```python
def update(extension_id: str, new_local_path: str) -> Extension
```

Updates an existing browser extension in the current context with a new file.

**Arguments**:

- `extension_id` _str_ - The ID of the extension to update.
- `new_local_path` _str_ - Path to the new local extension file.


**Returns**:

    Extension: The updated Extension object.


**Raises**:

    FileNotFoundError: If the new local file does not exist.
    ValueError: If the extension ID is not found.

### cleanup

```python
def cleanup() -> bool
```

Cleans up the auto-created context if it was created by this service.

**Returns**:

    bool: True if cleanup was successful or not needed, False if cleanup failed.


**Notes**:

  This method only works if the context was auto-created by this service.
  For existing contexts, no cleanup is performed.

### delete

```python
def delete(extension_id: str) -> bool
```

Deletes a browser extension from the current context.

**Arguments**:

- `extension_id` _str_ - The ID of the extension to delete.


**Returns**:

    bool: True if deletion was successful, False otherwise.

### create\_extension\_option

```python
def create_extension_option(extension_ids: List[str]) -> ExtensionOption
```

Create an ExtensionOption for the current context with specified extension IDs.

This is a convenience method that creates an ExtensionOption using the current
service's context_id and the provided extension IDs. This option can then be
used with BrowserContext for browser session creation.

**Arguments**:

- `extension_ids` _List[str]_ - List of extension IDs to include in the option.
  These should be extensions that exist in the current context.


**Returns**:

    ExtensionOption: Configuration object for browser extension integration.


**Raises**:

    ValueError: If extension_ids is empty or invalid.


**Example**:

```python
# Create extensions
ext1 = extensions_service.create("/path/to/ext1.zip")
ext2 = extensions_service.create("/path/to/ext2.zip")

# Create extension option for browser integration
ext_option = extensions_service.create_extension_option([ext1.id, ext2.id])

# Use with BrowserContext
browser_context = BrowserContext(
  context_id="browser_session",
  auto_upload=True,
  extension_context_id=ext_option.context_id,
  extension_ids=ext_option.extension_ids
)
```

## Related Resources

- [Browser API Reference](../capabilities/browser.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
