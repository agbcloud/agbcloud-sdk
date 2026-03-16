# Class: ExtensionsService

## 📖 Related Tutorial

- [Browser Automation Guide](../../../browser/overview.md) - Learn how to use browser extensions and automation

## Overview

The Extension module provides capabilities for working with browser extensions
and extending the functionality of the AGB platform.

Provides methods to manage user browser extensions.
This service integrates with the existing context functionality for file operations.

**Usage** (Simplified - Auto-detection):
```typescript
// Service automatically detects if context exists and creates if needed
const extensionsService = new ExtensionsService(agb, "browser_extensions");

// Or use with empty contextId to auto-generate context name
const extensionsService = new ExtensionsService(agb);  // Uses default generated name

// Use the service immediately - initialization happens automatically
const extension = await extensionsService.create("/path/to/plugin.zip");
```

**Integration with ExtensionOption (Simplified)**:
```typescript
// Create extensions and configure for browser sessions
const extensionsService = new ExtensionsService(agb, "my_extensions");
const ext1 = await extensionsService.create("/path/to/ext1.zip");
const ext2 = await extensionsService.create("/path/to/ext2.zip");

// Create extension option for browser integration (no contextId needed!)
const extOption = extensionsService.createExtensionOption([ext1.id, ext2.id]);

// Use with BrowserContext for session creation
const browserContext = new BrowserContext({
  contextId: "browser_session",
  autoUpload: true,
  extensionOption: extOption  // All extension config encapsulated
});
```

**Context Management**:
- If contextId provided and exists: Uses the existing context
- If contextId provided but doesn't exist: Creates context with provided name
- If contextId empty or not provided: Generates default name and creates context
- No need to manually manage context creation or call initialize()
- Context initialization happens automatically on first method call

## Table of contents


### Accessors

- [contextId](#contextid)

### Methods

- [cleanup](#cleanup)
- [create](#create)
- [createExtensionOption](#createextensionoption)
- [delete](#delete)
- [list](#list)
- [update](#update)

## Accessors

### contextId

• `get` **contextId**(): `string`

#### Returns

`string`

## Methods

### cleanup

▸ **cleanup**(): `Promise`\&lt;`boolean`\&gt;

Cleans up the auto-created context if it was created by this service.

#### Returns

`Promise`\&lt;`boolean`\&gt;

Promise that resolves to true if cleanup was successful or not needed,
         false if cleanup failed.

Note:
  This method only works if the context was auto-created by this service.
  For existing contexts, no cleanup is performed.

**`Example`**

```typescript
const agb = new AGB({ apiKey: 'your_api_key' });
const service = new ExtensionsService(agb);
await service.create('/path/to/my-extension.zip');
const success = await service.cleanup();
console.log('Cleanup success:', success);
```

___

### create

▸ **create**(`localPath`): `Promise`\&lt;``Extension``\&gt;

Uploads a new browser extension from a local path into the current context.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `localPath` | `string` | Path to the local extension file (must be a .zip file). |

#### Returns

`Promise`\&lt;``Extension``\&gt;

Promise that resolves to an Extension object.

**`Throws`**

If the local file doesn't exist.

**`Throws`**

If the file format is not supported (only .zip is supported).

**`Throws`**

If upload fails.

**`Example`**

```typescript
const agb = new AGB({ apiKey: 'your_api_key' });
const service = new ExtensionsService(agb);
const extension = await service.create('/path/to/my-extension.zip');
console.log(`Extension ID: ${extension.id}`);
await service.cleanup();
```

___

### createExtensionOption

▸ **createExtensionOption**(`extensionIds`): ``ExtensionOption``

Create an ExtensionOption for the current context with specified extension IDs.

This is a convenience method that creates an ExtensionOption using the current
service's contextId and the provided extension IDs. This option can then be
used with BrowserContext for browser session creation.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `extensionIds` | `string`[] | List of extension IDs to include in the option. These should be extensions that exist in the current context. |

#### Returns

``ExtensionOption``

ExtensionOption configuration object for browser extension integration.

**`Throws`**

If extensionIds is empty or invalid.

**`Example`**

```typescript
// Create extensions
const ext1 = await extensionsService.create("/path/to/ext1.zip");
const ext2 = await extensionsService.create("/path/to/ext2.zip");

// Create extension option for browser integration
const extOption = extensionsService.createExtensionOption([ext1.id, ext2.id]);

// Use with BrowserContext
const browserContext = new BrowserContext({
  contextId: "browser_session",
  autoUpload: true,
  extensionContextId: extOption.contextId,
  extensionIds: extOption.extensionIds
});
```

___

### delete

▸ **delete**(`extensionId`): `Promise`\&lt;`boolean`\&gt;

Deletes a browser extension from the current context.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `extensionId` | `string` | ID of the extension to delete. |

#### Returns

`Promise`\&lt;`boolean`\&gt;

Promise that resolves to true if deletion was successful, false otherwise.

**`Example`**

```typescript
const agb = new AGB({ apiKey: 'your_api_key' });
const service = new ExtensionsService(agb, 'my_extensions');
const ext = await service.create('/path/to/my-extension.zip');
const success = await service.delete(ext.id);
console.log('Delete success:', success);
await service.cleanup();
```

___

### list

▸ **list**(): `Promise`\&lt;``Extension``[]\&gt;

Lists all available browser extensions within this context from the cloud.
Uses the context service to list files under the extensions directory.

#### Returns

`Promise`\&lt;``Extension``[]\&gt;

Promise that resolves to an array of Extension objects.

**`Throws`**

If listing extensions fails.

**`Example`**

```typescript
const agb = new AGB({ apiKey: 'your_api_key' });
const service = new ExtensionsService(agb, 'my_extensions');
await service.create('/path/to/ext1.zip');
const extensions = await service.list();
console.log(`Found ${extensions.length} extensions`);
await service.cleanup();
```

___

### update

▸ **update**(`extensionId`, `newLocalPath`): `Promise`\&lt;``Extension``\&gt;

Updates an existing browser extension in the current context with a new file.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `extensionId` | `string` | ID of the extension to update. |
| `newLocalPath` | `string` | Path to the new local extension file. |

#### Returns

`Promise`\&lt;``Extension``\&gt;

Promise that resolves to an Extension object.

**`Throws`**

If the new local file doesn't exist.

**`Throws`**

If the extension doesn't exist in the context.

**`Throws`**

If update fails.

**`Example`**

```typescript
const agb = new AGB({ apiKey: 'your_api_key' });
const service = new ExtensionsService(agb, 'my_extensions');
const ext = await service.create('/path/to/ext-v1.zip');
const updated = await service.update(ext.id, '/path/to/ext-v2.zip');
console.log('Extension updated:', updated.name);
await service.cleanup();
```

## Related Resources

- [Browser API Reference](../capabilities/browser.md)

