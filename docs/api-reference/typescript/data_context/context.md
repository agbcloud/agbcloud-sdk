# Class: ContextService

## 📖 Related Tutorial

- [Context Usage Guide](../../../context/overview.md) - Learn about context management and data persistence

## Overview

The Context module provides methods for managing session context and data persistence.
It allows you to store and retrieve data across session operations.

## Table of contents


### Methods

- [clear](#clear)
- [clearAsync](#clearasync)
- [create](#create)
- [delete](#delete)
- [deleteFile](#deletefile)
- [get](#get)
- [getFileDownloadUrl](#getfiledownloadurl)
- [getFileUploadUrl](#getfileuploadurl)
- [list](#list)
- [listFiles](#listfiles)
- [toJSON](#tojson)
- [update](#update)

## Methods

### clear

▸ **clear**(`contextId`, `timeout?`, `pollInterval?`): `Promise`\&lt;``ClearContextResult``\&gt;

#### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `contextId` | `string` | `undefined` |
| `timeout` | `number` | `60` |
| `pollInterval` | `number` | `2` |

#### Returns

`Promise`\&lt;``ClearContextResult``\&gt;

___

### clearAsync

▸ **clearAsync**(`contextId`): `Promise`\&lt;``ClearContextResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `contextId` | `string` |

#### Returns

`Promise`\&lt;``ClearContextResult``\&gt;

___

### create

▸ **create**(`name`): `Promise`\&lt;``ContextResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `name` | `string` |

#### Returns

`Promise`\&lt;``ContextResult``\&gt;

___

### delete

▸ **delete**(`context`): `Promise`\&lt;``OperationResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `context` | [`Context`](context.md) |

#### Returns

`Promise`\&lt;``OperationResult``\&gt;

___

### deleteFile

▸ **deleteFile**(`contextId`, `filePath`): `Promise`\&lt;``OperationResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `contextId` | `string` |
| `filePath` | `string` |

#### Returns

`Promise`\&lt;``OperationResult``\&gt;

___

### get

▸ **get**(`name?`, `create?`, `loginRegionId?`, `contextId?`): `Promise`\&lt;``ContextResult``\&gt;

#### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `name?` | `string` | `undefined` |
| `create` | `boolean` | `false` |
| `loginRegionId?` | `string` | `undefined` |
| `contextId?` | `string` | `undefined` |

#### Returns

`Promise`\&lt;``ContextResult``\&gt;

### getFileDownloadUrl

▸ **getFileDownloadUrl**(`contextId`, `filePath`): `Promise`\&lt;``FileUrlResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `contextId` | `string` |
| `filePath` | `string` |

#### Returns

`Promise`\&lt;``FileUrlResult``\&gt;

___

### getFileUploadUrl

▸ **getFileUploadUrl**(`contextId`, `filePath`): `Promise`\&lt;``FileUrlResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `contextId` | `string` |
| `filePath` | `string` |

#### Returns

`Promise`\&lt;``FileUrlResult``\&gt;

___

### list

▸ **list**(`params?`): `Promise`\&lt;``ContextListResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `params?` | ``ContextListParams`` |

#### Returns

`Promise`\&lt;``ContextListResult``\&gt;

___

### listFiles

▸ **listFiles**(`contextId`, `parentFolderPath?`, `pageNumber?`, `pageSize?`): `Promise`\&lt;``ContextFileListResult``\&gt;

#### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `contextId` | `string` | `undefined` |
| `parentFolderPath?` | `string` | `undefined` |
| `pageNumber` | `number` | `1` |
| `pageSize` | `number` | `50` |

#### Returns

`Promise`\&lt;``ContextFileListResult``\&gt;

___

### toJSON

▸ **toJSON**(): `Record`\&lt;`string`, `unknown`\&gt;

#### Returns

`Record`\&lt;`string`, `unknown`\&gt;

___

### update

▸ **update**(`context`): `Promise`\&lt;``OperationResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `context` | [`Context`](context.md) |

#### Returns

`Promise`\&lt;``OperationResult``\&gt;

## Related Resources

- [Session API Reference](../session.md)
- [Context Manager API Reference](./context_manager.md)

