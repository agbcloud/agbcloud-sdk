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


### Methods

- [run](#run)

## Properties
## Methods
### run

▸ **run**(`code`, `language`, `timeoutS?`, `options?`): `Promise`\&lt;``EnhancedCodeExecutionResult``\&gt;

Execute code in the specified language with a timeout.

This is the primary public method for code execution. For real-time
streaming output, set streamBeta=true and provide callback functions.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `code` | `string` | `undefined` | Source code to execute |
| `language` | `string` | `undefined` | Language identifier. Case-insensitive. Supported values: 'python', 'javascript', 'java', 'r'. Aliases: 'py' -&gt; 'python', 'js'/'node' -&gt; 'javascript'. |
| `timeoutS` | `number` | `60` | Timeout in seconds (default 60) |
| `options?` | `Object` | `undefined` | Optional streaming parameters |
| `options.onError?` | (`err`: `unknown`) =&gt; `void` | `undefined` | Callback invoked when an error occurs during streaming |
| `options.onStderr?` | (`chunk`: `string`) =&gt; `void` | `undefined` | Callback invoked with each stderr chunk during streaming |
| `options.onStdout?` | (`chunk`: `string`) =&gt; `void` | `undefined` | Callback invoked with each stdout chunk during streaming |
| `options.streamBeta?` | `boolean` | `undefined` | If true, use WebSocket streaming for real-time output |

#### Returns

`Promise`\&lt;``EnhancedCodeExecutionResult``\&gt;

Promise resolving to EnhancedCodeExecutionResult with results and logs

**`Example`**

```typescript
// Simple execution
const result = await session.code.run("print('Hello')", "python");
console.log(result.results);

// Streaming execution for long-running code
const result = await session.code.run(
  "import time\nfor i in range(5):\n    print(f'Progress: {i+1}/5')\n    time.sleep(1)",
  "python",
  60,
  { streamBeta: true, onStdout: (chunk) => console.log(chunk) }
);
```

## Best Practices

1. Validate code syntax before execution
2. Set appropriate execution timeouts
3. Handle execution errors and exceptions
4. Use proper resource limits to prevent resource exhaustion
5. Clean up temporary files after code execution


## Related Resources

- [Session API Reference](../session.md)

