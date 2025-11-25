# Extensions API

The Extensions API provides functionality for managing browser extensions in AGB sessions. This allows you to upload, manage, and load browser extensions in your automated browsing sessions.

## Overview

The Extensions API consists of two main components:

1. **ExtensionsService** - Manages extension lifecycle (create, list, update, delete)
2. **ExtensionOption** - Configuration object for integrating extensions with browser sessions

## ExtensionsService

The `ExtensionsService` class provides methods to manage browser extensions as cloud resources.

### Constructor

```python
from agb.extension import ExtensionsService

# Create ExtensionsService with a specific context name
extensions_service = ExtensionsService(agb, "my_extensions")

# Or let the service auto-generate a context name
extensions_service = ExtensionsService(agb)
```

**Parameters:**
- `agb` (AGB): The AGB client instance
- `context_id` (str, optional): The context name for storing extensions. If not provided, a name will be auto-generated.

### Methods

#### create(local_path)

Uploads a new browser extension from a local ZIP file.

```python
extension = extensions_service.create("/path/to/extension.zip")
print(f"Extension ID: {extension.id}")
print(f"Extension Name: {extension.name}")
```

**Parameters:**
- `local_path` (str): Path to the local ZIP file containing the extension

**Returns:**
- `Extension`: An Extension object with the ID and name of the uploaded extension

**Raises:**
- `FileNotFoundError`: If the local file doesn't exist
- `ValueError`: If the file is not a ZIP file

#### list()

Lists all extensions in the current context.

```python
extensions = extensions_service.list()
for ext in extensions:
    print(f"ID: {ext.id}, Name: {ext.name}")
```

**Returns:**
- `List[Extension]`: A list of Extension objects

#### update(extension_id, new_local_path)

Updates an existing extension with a new ZIP file.

```python

# extension.id is the ID value returned from the create method call
updated_extension = extensions_service.update(extension.id, "/path/to/new_extension.zip")
print(f"   Updated extension: {updated_extension.id}")
```

**Parameters:**
- `extension_id` (str): The ID of the extension to update
- `new_local_path` (str): Path to the new ZIP file

**Returns:**
- `Extension`: An Extension object with the ID and name of the updated extension

**Raises:**
- `FileNotFoundError`: If the new local file doesn't exist
- `ValueError`: If the extension ID doesn't exist

#### delete(extension_id)

Deletes an extension from the current context.

```python
success = extensions_service.delete(extension.id)
if success:
    print("Extension deleted successfully")
```

**Parameters:**
- `extension_id` (str): The ID of the extension to delete

**Returns:**
- `bool`: True if deletion was successful, False otherwise

#### create_extension_option(extension_ids)

Creates an ExtensionOption for integrating extensions with browser sessions.

```python
# Create extensions
ext1 = extensions_service.create("/path/to/ext1.zip")
ext2 = extensions_service.create("/path/to/ext2.zip")

# Create extension option for browser integration
ext_option = extensions_service.create_extension_option([ext1.id, ext2.id])
print(f"   Extension option created with {len(ext_option.extension_ids)} extensions")
```

**Parameters:**
- `extension_ids` (List[str]): List of extension IDs to include

**Returns:**
- `ExtensionOption`: Configuration object for browser extension integration

## Extension

Represents a browser extension as a cloud resource.

### Properties

- `id` (str): Unique identifier for the extension
- `name` (str): Name of the extension
- `created_at` (str, optional): Creation timestamp

## ExtensionOption

Configuration options for browser extension integration.

### Properties

- `context_id` (str): ID of the extension context
- `extension_ids` (List[str]): List of extension IDs to be loaded

## Integration with Browser Sessions

To use extensions in browser sessions, you need to integrate them using the `BrowserContext`:

```python
from agb.session_params import BrowserContext

# Create extension option
ext_option = extensions_service.create_extension_option([ext1.id, ext2.id])

# Create browser context with extensions
browser_context = BrowserContext(
    context_id="browser_session",
    auto_upload=True,
    extension_option=ext_option
)

# Create session with browser context
session_params = CreateSessionParams(
    labels={"type": "browser_with_extensions"},
    image_id="agb-browser-use-1",
    browser_context=browser_context
)

session_result = agb.create(session_params)
session = session_result.session
if session is not None:
    print(f"   Session created: {session.session_id}")
else:
    raise Exception("Session creation failed: session is None")
```