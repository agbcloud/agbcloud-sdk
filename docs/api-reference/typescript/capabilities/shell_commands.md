# Class: Command

## 📖 Related Tutorial

- [Command Execution Guide](../../../command/overview.md) - Learn how to execute commands in sessions

## Overview

The Command module provides methods for executing shell commands within a session
in the AGB cloud environment. It supports command execution with configurable timeouts.

Command module for executing shell commands in the session.

## Hierarchy

- ``BaseService``

  ↳ **`Command`**

## Table of contents


### Properties


### Methods

- [execute](#execute)

## Properties

```typescript
exec: (`command`: `string`, `timeoutMs`: `number`, `cwd?`: `string`, `envs?`: `Record`<`string`, `string`>) => `Promise`<``CommandResult``>
run: (`command`: `string`, `timeoutMs`: `number`, `cwd?`: `string`, `envs?`: `Record`<`string`, `string`>) => `Promise`<``CommandResult``>
```


#### Type declaration

▸ (`command`, `timeoutMs?`, `cwd?`, `envs?`): `Promise`\&lt;``CommandResult``\&gt;

Execute a shell command in the session.

##### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `command` | `string` | `undefined` | The command string to execute |
| `timeoutMs` | `number` | `1000` | Timeout in milliseconds (default 1000) |
| `cwd?` | `string` | `undefined` | Optional working directory |
| `envs?` | `Record`\&lt;`string`, `string`\&gt; | `undefined` | Optional environment variables (key-value pairs) |

##### Returns

`Promise`\&lt;``CommandResult``\&gt;

Promise resolving to CommandResult with stdout, stderr, exitCode

___

#### Type declaration

▸ (`command`, `timeoutMs?`, `cwd?`, `envs?`): `Promise`\&lt;``CommandResult``\&gt;

##### Parameters

| Name | Type | Default value |
| :------ | :------ | :------ |
| `command` | `string` | `undefined` |
| `timeoutMs` | `number` | `1000` |
| `cwd?` | `string` | `undefined` |
| `envs?` | `Record`\&lt;`string`, `string`\&gt; | `undefined` |

##### Returns

`Promise`\&lt;``CommandResult``\&gt;
## Methods
### execute

▸ **execute**(`command`, `timeoutMs?`, `cwd?`, `envs?`): `Promise`\&lt;``CommandResult``\&gt;

Execute a shell command in the session.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `command` | `string` | `undefined` | The command string to execute |
| `timeoutMs` | `number` | `1000` | Timeout in milliseconds (default 1000) |
| `cwd?` | `string` | `undefined` | Optional working directory |
| `envs?` | `Record`\&lt;`string`, `string`\&gt; | `undefined` | Optional environment variables (key-value pairs) |

#### Returns

`Promise`\&lt;``CommandResult``\&gt;

Promise resolving to CommandResult with stdout, stderr, exitCode

## Best Practices

1. Always specify appropriate timeout values based on expected command duration
2. Handle command execution errors gracefully
3. Use absolute paths when referencing files in commands, or use the `cwd` parameter
4. Use the `cwd` parameter to set working directory instead of `cd` commands
5. Use the `envs` parameter to set environment variables instead of `export` commands
6. Check `exit_code` for more precise error handling (0 means success)
7. Use `stdout` and `stderr` separately for better output parsing
8. Be aware that commands run with session user permissions
9. Clean up temporary files created by commands


## Related Resources

- [Session API Reference](../session.md)
- [File System API Reference](./file_system.md)

