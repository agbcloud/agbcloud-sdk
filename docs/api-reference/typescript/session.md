# Class: Session

## 📖 Related Tutorial

- [Session Management Guide](../../session/overview.md) - Detailed tutorial on session lifecycle and management

## Overview

The Session module provides methods for creating, managing, and terminating sessions
in the AGB cloud environment. Sessions are the foundation for all operations.

Represents an active session in the AGB cloud environment.
Provides access to command, file system, code execution, browser, computer, and context modules.

## Table of contents


### Properties


### Methods

- [callMcpTool](#callmcptool)
- [delete](#delete)
- [getLabels](#getlabels)
- [getLink](#getlink)
- [getMetrics](#getmetrics)
- [info](#info)
- [keepAlive](#keepalive)
- [listMcpTools](#listmcptools)
- [setLabels](#setlabels)
- [toJSON](#tojson)

## Properties

```typescript
appInstanceId: `string` = `""`
browser: [`Browser`](capabilities/browser.md)
code: [`Code`](capabilities/code_execution.md)
command: [`Command`](capabilities/shell_commands.md)
computer: [`Computer`](capabilities/computer.md)
context: [`ContextManager`](data_context/context_manager.md)
enableBrowserReplay: `boolean` = `false`
file: [`FileSystem`](capabilities/file_system.md)
imageId: `string` = `""`
resourceId: `string` = `""`
resourceUrl: `string` = `""`
```


## Methods

### callMcpTool

▸ **callMcpTool**(`toolName`, `args`, `readTimeout?`, `connectTimeout?`): `Promise`\&lt;``McpToolResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `toolName` | `string` |
| `args` | `Record`\&lt;`string`, `unknown`\&gt; |
| `readTimeout?` | `number` |
| `connectTimeout?` | `number` |

#### Returns

`Promise`\&lt;``McpToolResult``\&gt;

___

### delete

▸ **delete**(`syncContext?`): `Promise`\&lt;``DeleteResult``\&gt;

Release (delete) this session. Optionally sync context before releasing.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `syncContext` | `boolean` | `false` | If true, sync context (e.g. upload browser data) before releasing |

#### Returns

`Promise`\&lt;``DeleteResult``\&gt;

Promise resolving to DeleteResult

___

### getLabels

▸ **getLabels**(): `Promise`\&lt;``OperationResult``\&gt;

Get labels for the session.

#### Returns

`Promise`\&lt;``OperationResult``\&gt;

Promise resolving to OperationResult with data containing labels object

___

### getLink

▸ **getLink**(`protocolType?`, `port?`): `Promise`\&lt;``OperationResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `protocolType?` | `string` |
| `port?` | `number` |

#### Returns

`Promise`\&lt;``OperationResult``\&gt;

___

### getMetrics

▸ **getMetrics**(`readTimeout?`, `connectTimeout?`): `Promise`\&lt;``SessionMetricsResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `readTimeout?` | `number` |
| `connectTimeout?` | `number` |

#### Returns

`Promise`\&lt;``SessionMetricsResult``\&gt;

### info

▸ **info**(): `Promise`\&lt;``OperationResult``\&gt;

Get session resource info (sessionId, resourceUrl, desktopInfo, etc.).

#### Returns

`Promise`\&lt;``OperationResult``\&gt;

Promise resolving to OperationResult with resource data

___

### keepAlive

▸ **keepAlive**(): `Promise`\&lt;``OperationResult``\&gt;

#### Returns

`Promise`\&lt;``OperationResult``\&gt;

___

### listMcpTools

▸ **listMcpTools**(`imageId?`): `Promise`\&lt;``McpToolsResult``\&gt;

#### Parameters

| Name | Type |
| :------ | :------ |
| `imageId?` | `string` |

#### Returns

`Promise`\&lt;``McpToolsResult``\&gt;

___

### setLabels

▸ **setLabels**(`labels`): `Promise`\&lt;``OperationResult``\&gt;

Set labels on the session (key-value metadata).

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `labels` | `Record`\&lt;`string`, `string`\&gt; | Non-empty object of string key-value pairs |

#### Returns

`Promise`\&lt;``OperationResult``\&gt;

Promise resolving to OperationResult

___

### toJSON

▸ **toJSON**(): `Record`\&lt;`string`, `unknown`\&gt;

Serialize session to a plain object (sessionId, resourceUrl, imageId, etc.).

#### Returns

`Record`\&lt;`string`, `unknown`\&gt;

Plain object with session fields

## Related Resources

- [AGB API Reference](./agb.md)
- [Context API Reference](./data_context/context.md)
- [Context Manager API Reference](./data_context/context_manager.md)

