# Class: ContextManager

Context manager for the session: query context sync status and trigger sync (upload/download).

## Table of contents


### Methods

- [info](#info)
- [sync](#sync)
- [toJSON](#tojson)

## Methods

### info

▸ **info**(`contextId?`, `path?`, `taskType?`): `Promise`\&lt;``ContextInfoResult``\&gt;

Get context sync status (optionally filtered by contextId, path, taskType).

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `contextId?` | `string` | Optional context ID filter |
| `path?` | `string` | Optional path filter |
| `taskType?` | `string` | Optional task type filter |

#### Returns

`Promise`\&lt;``ContextInfoResult``\&gt;

Promise resolving to ContextInfoResult with items (contextId, path, status, etc.)

___

### sync

▸ **sync**(`contextId?`, `path?`, `mode?`, `maxRetries?`, `retryInterval?`, `callback?`): `Promise`\&lt;``ContextSyncResult``\&gt;

Trigger context sync (upload or download). Omit contextId and path to sync all contexts.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `contextId?` | `string` | `undefined` | Optional; if provided, path must also be provided |
| `path?` | `string` | `undefined` | Optional; sync only this context path |
| `mode?` | `string` | `undefined` | Optional sync mode |
| `maxRetries` | `number` | `150` | Max poll retries (default 150) |
| `retryInterval` | `number` | `1500` | Poll interval ms (default 1500) |
| `callback?` | (`success`: `boolean`) =&gt; `void` | `undefined` | Optional callback with success |

#### Returns

`Promise`\&lt;``ContextSyncResult``\&gt;

Promise resolving to ContextSyncResult

___

### toJSON

▸ **toJSON**(): `Record`\&lt;`string`, `unknown`\&gt;

#### Returns

`Record`\&lt;`string`, `unknown`\&gt;
