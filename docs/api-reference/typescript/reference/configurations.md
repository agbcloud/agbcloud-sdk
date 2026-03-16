# Class: CreateSessionParams

## 📖 Related Tutorial

- [Session Management Guide](../../../session/overview.md) - Learn how to configure sessions

## Overview

Configuration parameters for creating and managing AGB sessions.

Parameters for creating a session (imageId, labels, contextSync, browserContext, etc.).

## Table of contents


### Properties

- [browserContext](#browsercontext)
- [idleReleaseTimeout](#idlereleasetimeout)
- [imageId](#imageid)
- [labels](#labels)
- [mcpPolicyId](#mcppolicyid)
- [policyId](#policyid)

## Properties

```typescript
contextSync: [`ContextSync`](../data_context/synchronization.md)[]
```


### browserContext

• `Optional` **browserContext**: ``BrowserContext``

___

### idleReleaseTimeout

• `Optional` **idleReleaseTimeout**: `number`

___

### imageId

• `Optional` **imageId**: `string`

___

### labels

• `Optional` **labels**: `Record`\&lt;`string`, `string`\&gt;

___

### mcpPolicyId

• `Optional` **mcpPolicyId**: `string`

___

### policyId

• `Optional` **policyId**: `string`

## Related Resources

- [AGB API Reference](../agb.md)

