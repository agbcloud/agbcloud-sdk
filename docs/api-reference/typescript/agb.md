# Class: AGB

## 📖 Related Tutorial

- [Quick Start Guide](../../quickstart.md) - Get started with the AGB Python SDK

## Overview

The main AGB module provides the core functionality for creating and managing sessions
with the AGB cloud platform. It serves as the entry point for all SDK operations.

Main class for interacting with the AGB cloud runtime environment.
Use this class to create, list, and manage sessions.

## Table of contents


### Properties


### Methods

- [create](#create)
- [delete](#delete)
- [get](#get)
- [list](#list)
- [toJSON](#tojson)

## Properties

```typescript
apiKey: `string`
client: ``Client``
config: ``Config``
context: [`ContextService`](data_context/context.md)
```


## Methods

### create

▸ **create**(`params?`): `Promise`\&lt;``SessionResult``\&gt;

Create a new session in the AGB cloud environment.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `params?` | ``null`` \| [`CreateSessionParams`](reference/configurations.md) | Parameters for creating the session (imageId is required) |

#### Returns

`Promise`\&lt;``SessionResult``\&gt;

Promise resolving to SessionResult with success, session, requestId, and optional errorMessage

**`Example`**

```typescript
const agb = new AGB({ apiKey: 'your_api_key' });
const result = await agb.create({ imageId: 'agb-code-space-1' });
if (result.success && result.session) {
  await result.session.file.readFile('/etc/hostname');
  await agb.delete(result.session);
}
```

___

### delete

▸ **delete**(`session`, `syncContext?`): `Promise`\&lt;``DeleteResult``\&gt;

Delete (release) a session.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `session` | [`Session`](session.md) | `undefined` | The session to delete |
| `syncContext` | `boolean` | `false` | If true, sync context before releasing (e.g. upload browser data) |

#### Returns

`Promise`\&lt;``DeleteResult``\&gt;

Promise resolving to DeleteResult with success and requestId

___

### get

▸ **get**(`sessionId`): `Promise`\&lt;``SessionResult``\&gt;

Get a Session instance by session ID.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `sessionId` | `string` | The session ID |

#### Returns

`Promise`\&lt;``SessionResult``\&gt;

Promise resolving to SessionResult with a Session object or error

### list

▸ **list**(`labels?`, `page?`, `limit?`): `Promise`\&lt;``SessionListResult``\&gt;

List sessions filtered by labels with pagination.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `labels?` | `Record`\&lt;`string`, `string`\&gt; | Optional key-value pairs to filter sessions |
| `page?` | `number` | Page number (1-based). If provided, fetches that page. |
| `limit?` | `number` | Maximum number of sessions per page (default 10) |

#### Returns

`Promise`\&lt;``SessionListResult``\&gt;

Promise resolving to SessionListResult with sessionIds, nextToken, totalCount, etc.

___

### toJSON

▸ **toJSON**(): `Record`\&lt;`string`, `unknown`\&gt;

Serialize client configuration to a plain object.

#### Returns

`Record`\&lt;`string`, `unknown`\&gt;

Object with endpoint and timeoutMs

## Related Resources

- [Session API Reference](./session.md)
- [Context API Reference](./data_context/context.md)

