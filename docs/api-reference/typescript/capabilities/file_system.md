# Class: FileSystem

## 📖 Related Tutorial

- [File Operations Guide](../../../file-system/overview.md) - Complete guide to file system operations

## Overview

The File System module provides comprehensive file and directory operations
within the AGB cloud environment. It supports file upload, download, and manipulation.

File system module for reading, writing, listing, and managing files in the session.
Supports text and binary files, directory listing, search, upload/download, and file change monitoring.

## Hierarchy

- ``BaseService``

  ↳ **`FileSystem`**

## Table of contents


### Properties

- [DEFAULT\_CHUNK\_SIZE](#default_chunk_size)
- [session](#session)

### Methods

- [callMcpTool](#callmcptool)
- [createDirectory](#createdirectory)
- [deleteFile](#deletefile)
- [download](#download)
- [editFile](#editfile)
- [handleError](#handleerror)
- [listDirectory](#listdirectory)
- [moveFile](#movefile)
- [read](#read)
- [readFile](#readfile)
- [readMultipleFiles](#readmultiplefiles)
- [searchFiles](#searchfiles)
- [toJSON](#tojson)
- [transferPath](#transferpath)
- [upload](#upload)
- [watchDir](#watchdir)
- [watchDirectory](#watchdirectory)
- [writeFile](#writefile)

## Properties

```typescript
delete: (`path`: `string`) => `Promise`<``BoolResult``>
list: (`path`: `string`) => `Promise`<``DirectoryListResult``>
ls: (`path`: `string`) => `Promise`<``DirectoryListResult``>
mkdir: (`path`: `string`) => `Promise`<``BoolResult``>
remove: (`path`: `string`) => `Promise`<``BoolResult``>
rm: (`path`: `string`) => `Promise`<``BoolResult``>
write: (`path`: `string`, `content`: `string`, `mode`: ``"overwrite"`` | ``"append"`` | ``"create_new"``) => `Promise`<``BoolResult``>
```


### DEFAULT\_CHUNK\_SIZE

▪ `Static` `Readonly` **DEFAULT\_CHUNK\_SIZE**: `number` = `DEFAULT_CHUNK_SIZE`

___

#### Type declaration

▸ (`path`): `Promise`\&lt;``BoolResult``\&gt;

##### Parameters

| Name | Type |
| :------ | :------ |
| `path` | `string` |

##### Returns

`Promise`\&lt;``BoolResult``\&gt;

___

#### Type declaration

▸ (`path`): `Promise`\&lt;``DirectoryListResult``\&gt;

##### Parameters

| Name | Type |
| :------ | :------ |
| `path` | `string` |

##### Returns

`Promise`\&lt;``DirectoryListResult``\&gt;

___

#### Type declaration

▸ (`path`): `Promise`\&lt;``DirectoryListResult``\&gt;

##### Parameters

| Name | Type |
| :------ | :------ |
| `path` | `string` |

##### Returns

`Promise`\&lt;``DirectoryListResult``\&gt;

___

#### Type declaration

▸ (`path`): `Promise`\&lt;``BoolResult``\&gt;

##### Parameters

| Name | Type |
| :------ | :------ |
| `path` | `string` |

##### Returns

`Promise`\&lt;``BoolResult``\&gt;

___

#### Type declaration

▸ (`path`): `Promise`\&lt;``BoolResult``\&gt;

##### Parameters

| Name | Type |
| :------ | :------ |
| `path` | `string` |

##### Returns

`Promise`\&lt;``BoolResult``\&gt;

___

#### Type declaration

▸ (`path`): `Promise`\&lt;``BoolResult``\&gt;

##### Parameters

| Name | Type |
| :------ | :------ |
| `path` | `string` |

##### Returns

`Promise`\&lt;``BoolResult``\&gt;

___

### session

• `Protected` **session**: ``SessionLike``

#### Inherited from

`BaseService`.`session`

___

#### Type declaration

▸ (`path`, `content`, `mode?`): `Promise`\&lt;``BoolResult``\&gt;

##### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `path` | `string` | `undefined` |
| `content` | `string` | `undefined` |
| `mode` | ``"overwrite"`` \| ``"append"`` \| ``"create_new"`` | `"overwrite"` |

##### Returns

`Promise`\&lt;``BoolResult``\&gt;

## Methods

### callMcpTool

▸ **callMcpTool**(`name`, `args`, `readTimeout?`, `connectTimeout?`): `Promise`\&lt;``OperationResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `name` | `string` |
| `args` | `Record`\&lt;`string`, `unknown`\&gt; |
| `readTimeout?` | `number` |
| `connectTimeout?` | `number` |

#### Returns

`Promise`\&lt;``OperationResult``\&gt;

#### Inherited from

`BaseService`.`callMcpTool`

___

### createDirectory

▸ **createDirectory**(`path`): `Promise`\&lt;``BoolResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `path` | `string` |

#### Returns

`Promise`\&lt;``BoolResult``\&gt;

___

### deleteFile

▸ **deleteFile**(`path`): `Promise`\&lt;``BoolResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `path` | `string` |

#### Returns

`Promise`\&lt;``BoolResult``\&gt;

___

### download

▸ **download**(`remotePath`, `localPath`, `options?`): `Promise`\&lt;``DownloadResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `remotePath` | `string` |
| `localPath` | `string` |
| `options?` | `Object` |
| `options.overwrite?` | `boolean` |
| `options.pollInterval?` | `number` |
| `options.progressCallback?` | (`bytesReceived`: `number`) =&gt; `void` |
| `options.wait?` | `boolean` |
| `options.waitTimeout?` | `number` |

#### Returns

`Promise`\&lt;``DownloadResult``\&gt;

___

### editFile

▸ **editFile**(`path`, `edits`, `dryRun?`): `Promise`\&lt;``BoolResult``\&gt;

#### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `path` | `string` | `undefined` |
| `edits` | \{ `newText`: `string` ; `oldText`: `string`  }[] | `undefined` |
| `dryRun` | `boolean` | `false` |

#### Returns

`Promise`\&lt;``BoolResult``\&gt;

### handleError

▸ **handleError**(`e`): `unknown`

#### Parameters

| Name | Type |
| :------ | :------ |
| `e` | `unknown` |

#### Returns

`unknown`

#### Inherited from

`BaseService`.`handleError`

___

### listDirectory

▸ **listDirectory**(`path`): `Promise`\&lt;``DirectoryListResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `path` | `string` |

#### Returns

`Promise`\&lt;``DirectoryListResult``\&gt;

___

### moveFile

▸ **moveFile**(`source`, `destination`): `Promise`\&lt;``BoolResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `source` | `string` |
| `destination` | `string` |

#### Returns

`Promise`\&lt;``BoolResult``\&gt;

___

### read

▸ **read**(`path`): `Promise`\&lt;``FileContentResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `path` | `string` |

#### Returns

`Promise`\&lt;``FileContentResult``\&gt;

▸ **read**(`path`, `opts`): `Promise`\&lt;``FileContentResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `path` | `string` |
| `opts` | `Object` |
| `opts.format` | ``"text"`` |

#### Returns

`Promise`\&lt;``FileContentResult``\&gt;

▸ **read**(`path`, `opts`): `Promise`\&lt;``BinaryFileContentResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `path` | `string` |
| `opts` | `Object` |
| `opts.format` | ``"bytes"`` |

#### Returns

`Promise`\&lt;``BinaryFileContentResult``\&gt;

___

### readFile

▸ **readFile**(`path`): `Promise`\&lt;``FileContentResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `path` | `string` |

#### Returns

`Promise`\&lt;``FileContentResult``\&gt;

▸ **readFile**(`path`, `opts`): `Promise`\&lt;``FileContentResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `path` | `string` |
| `opts` | `Object` |
| `opts.format` | ``"text"`` |

#### Returns

`Promise`\&lt;``FileContentResult``\&gt;

▸ **readFile**(`path`, `opts`): `Promise`\&lt;``BinaryFileContentResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `path` | `string` |
| `opts` | `Object` |
| `opts.format` | ``"bytes"`` |

#### Returns

`Promise`\&lt;``BinaryFileContentResult``\&gt;

___

### readMultipleFiles

▸ **readMultipleFiles**(`paths`): `Promise`\&lt;``MultipleFileContentResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `paths` | `string`[] |

#### Returns

`Promise`\&lt;``MultipleFileContentResult``\&gt;

___

### searchFiles

▸ **searchFiles**(`path`, `pattern`, `excludePatterns?`): `Promise`\&lt;``FileSearchResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `path` | `string` |
| `pattern` | `string` |
| `excludePatterns?` | `string`[] |

#### Returns

`Promise`\&lt;``FileSearchResult``\&gt;

___

### toJSON

▸ **toJSON**(): `Record`\&lt;`string`, `unknown`\&gt;

#### Returns

`Record`\&lt;`string`, `unknown`\&gt;

#### Inherited from

`BaseService`.`toJSON`

___

### transferPath

▸ **transferPath**(): `Promise`\&lt;`undefined` \| `string`\&gt;

#### Returns

`Promise`\&lt;`undefined` \| `string`\&gt;

___

### upload

▸ **upload**(`localPath`, `remotePath`, `options?`): `Promise`\&lt;``UploadResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `localPath` | `string` |
| `remotePath` | `string` |
| `options?` | `Object` |
| `options.contentType?` | `string` |
| `options.pollInterval?` | `number` |
| `options.progressCallback?` | (`bytesSent`: `number`) =&gt; `void` |
| `options.wait?` | `boolean` |
| `options.waitTimeout?` | `number` |

#### Returns

`Promise`\&lt;``UploadResult``\&gt;

___

### watchDir

▸ **watchDir**(`dirPath`, `callback`, `interval?`): `Object`

#### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `dirPath` | `string` | `undefined` |
| `callback` | (`events`: ``FileChangeEvent``[]) =&gt; `void` | `undefined` |
| `interval` | `number` | `1000` |

#### Returns

`Object`

| Name | Type |
| :------ | :------ |
| `stop` | () =&gt; `void` |

**`Deprecated`**

Use watchDirectory instead

___

### watchDirectory

▸ **watchDirectory**(`path`, `callback`, `interval?`, `signal?`): `Promise`\&lt;`void`\&gt;

#### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `path` | `string` | `undefined` |
| `callback` | (`events`: ``FileChangeEvent``[]) =&gt; `void` | `undefined` |
| `interval` | `number` | `1000` |
| `signal?` | `AbortSignal` | `undefined` |

#### Returns

`Promise`\&lt;`void`\&gt;

___

### writeFile

▸ **writeFile**(`path`, `content`, `mode?`): `Promise`\&lt;``BoolResult``\&gt;

#### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `path` | `string` | `undefined` |
| `content` | `string` | `undefined` |
| `mode` | ``"overwrite"`` \| ``"append"`` \| ``"create_new"`` | `"overwrite"` |

#### Returns

`Promise`\&lt;``BoolResult``\&gt;

## Best Practices

1. Always check file permissions before operations
2. Use appropriate file paths and handle path separators correctly
3. Clean up temporary files after operations
4. Handle file operation errors gracefully
5. Use streaming for large file operations


## Related Resources

- [Session API Reference](../session.md)
- [Command API Reference](./shell_commands.md)

