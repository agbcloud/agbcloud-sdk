# Class: Code

## 📖 Related Tutorial

- [Code Execution Guide](../../../code-interpreting/overview.md) - Execute code in isolated environments

## Overview

The Code module provides secure code execution capabilities in isolated environments.
It supports multiple programming languages including Python, JavaScript, and more.


## Requirements

- Requires `agb-code-space-1` image for code execution features

Code execution module for running code in the session (Python, JavaScript, Java, R).

## Hierarchy

- ``BaseService``

  ↳ **`Code`**

## Table of contents


### Properties

- [session](#session)

### Methods

- [callMcpTool](#callmcptool)
- [handleError](#handleerror)
- [run](#run)
- [toJSON](#tojson)

## Properties

```typescript
execute: (`code`: `string`, `language`: `string`, `timeoutS`: `number`) => `Promise`<``EnhancedCodeExecutionResult``>
```


#### Type declaration

▸ (`code`, `language`, `timeoutS?`): `Promise`\&lt;``EnhancedCodeExecutionResult``\&gt;

##### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `code` | `string` | `undefined` |
| `language` | `string` | `undefined` |
| `timeoutS` | `number` | `60` |

##### Returns

`Promise`\&lt;``EnhancedCodeExecutionResult``\&gt;

___

### session

• `Protected` **session**: ``SessionLike``

#### Inherited from

`BaseService`.`session`

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

### run

▸ **run**(`code`, `language`, `timeoutS?`): `Promise`\&lt;``EnhancedCodeExecutionResult``\&gt;

Run code in the session.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `code` | `string` | `undefined` | Source code to execute |
| `language` | `string` | `undefined` | Language identifier (e.g. "python", "javascript", "java", "r") |
| `timeoutS` | `number` | `60` | Timeout in seconds (default 60) |

#### Returns

`Promise`\&lt;``EnhancedCodeExecutionResult``\&gt;

Promise resolving to EnhancedCodeExecutionResult with results and logs

___

### toJSON

▸ **toJSON**(): `Record`\&lt;`string`, `unknown`\&gt;

#### Returns

`Record`\&lt;`string`, `unknown`\&gt;

#### Inherited from

`BaseService`.`toJSON`

## Best Practices

1. Validate code syntax before execution
2. Set appropriate execution timeouts
3. Handle execution errors and exceptions
4. Use proper resource limits to prevent resource exhaustion
5. Clean up temporary files after code execution


## Related Resources

- [Session API Reference](../session.md)

