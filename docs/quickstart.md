# Quick Start

## 👋 I'm a Beginner - Complete Tutorial

### 1. Installation

::: code-group

```bash [Python]
pip install agbcloud-sdk
export AGB_API_KEY="your_key"
```

```bash [TypeScript]
npm install agbcloud-sdk
export AGB_API_KEY="your_key"
```

:::

### 2. First Example
**Important**: When using AGB, you need to specify an appropriate `image_id`. Please ensure you use valid image IDs that are available in your account. You can view and manage your available images in the [AGB Console Image Management](https://agb.cloud/console/image-management) page.

::: code-group

```python [Python]
from agb import AGB
from agb.session_params import CreateSessionParams

# Create client
agb = AGB()

# Create code execution session
params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
if not result.success:
    print(f"Session creation failed: {result.error_message}")
    exit(1)

session = result.session

# Execute code
result = session.code.run("print('Hello AGB!')", "python")
if result.success and result.results:
    for exec_result in result.results:
        if exec_result.text:
            print(exec_result.text)

# Cleanup
agb.delete(session)
```

```typescript [TypeScript]
import { AGB, CreateSessionParams } from "agbcloud-sdk";

const agb = new AGB();

const params = new CreateSessionParams({ imageId: "agb-code-space-1" });
const result = await agb.create(params);
if (!result.success || !result.session) {
  console.error("Session creation failed:", result.errorMessage);
  process.exit(1);
}

const session = result.session;

const execResult = await session.code.run("print('Hello AGB!')", "python");
if (execResult.success && execResult.results) {
  for (const item of execResult.results) {
    if (item.text) console.log(item.text);
  }
}

await agb.delete(session);
```

:::


### 3. Explore More Features

::: code-group

```python [Python]
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()

params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
if not result.success:
    print(f"Session creation failed: {result.error_message}")
    exit(1)
session = result.session

# Code execution
code_result = session.code.run("import os; print(os.getcwd())", "python")

# Command execution
cmd_result = session.command.execute("ls -la")

# File operations
session.file.write("/tmp/test.txt", "Hello World!")
file_result = session.file.read("/tmp/test.txt")

if code_result.success and code_result.results:
    print("Code output:", code_result.results[0].text)
print("Command output:", cmd_result.output)
print("File content:", file_result.content)

agb.delete(session)
```

```typescript [TypeScript]
import { AGB, CreateSessionParams } from "agbcloud-sdk";

const agb = new AGB();

const params = new CreateSessionParams({ imageId: "agb-code-space-1" });
const result = await agb.create(params);
if (!result.success || !result.session) {
  console.error("Session creation failed:", result.errorMessage);
  process.exit(1);
}
const session = result.session;

// Code execution
const codeResult = await session.code.run("import os; print(os.getcwd())", "python");

// Command execution
const cmdResult = await session.command.execute("ls -la");

// File operations
await session.file.write("/tmp/test.txt", "Hello World!");
const fileResult = await session.file.read("/tmp/test.txt");

if (codeResult.success && codeResult.results?.length) {
  console.log("Code output:", codeResult.results[0].text);
}
console.log("Command output:", cmdResult.output);
console.log("File content:", fileResult.content);

await agb.delete(session);
```

:::

### 4. Next Steps

- 📚 [Session Management Guide](/session/overview.md) - Understanding session management
- 🐍 [Code Execution Guide](/code-interpreting/overview.md) - Deep dive into code execution
- 💾 [File Operations Guide](/file-system/overview.md) - File and directory management


## 🚀 I Have Experience - Quick Start

### Core Concepts

::: code-group

```python [Python]
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()

params = CreateSessionParams(image_id="agb-code-space-1")
result = agb.create(params)
if not result.success:
    print(f"Session creation failed: {result.error_message}")
    exit(1)
session = result.session

session.code.run(code, "python")       # Code execution
session.command.execute("ls -la")      # Shell commands
session.file.read("/path/file")        # File operations
```

```typescript [TypeScript]
import { AGB, CreateSessionParams } from "agbcloud-sdk";

const agb = new AGB();

const params = new CreateSessionParams({ imageId: "agb-code-space-1" });
const result = await agb.create(params);
if (!result.success || !result.session) {
  console.error("Session creation failed:", result.errorMessage);
  process.exit(1);
}
const session = result.session;

await session.code.run(code, "python");       // Code execution
await session.command.execute("ls -la");      // Shell commands
await session.file.read("/path/file");        // File operations
```

:::

### Key Differences

**vs Traditional Tools**:
- ✅ **Cloud Environment with No Configuration**: No need to install Python/Node.js locally
- ✅ **Unified API**: Integrated code execution, commands, files, and cloud storage
- ✅ **Session Isolation**: Independent cloud environment for each session
- ✅ **Type Safety**: Strongly typed sessions and response objects

**vs Other Cloud Services**:
- ✅ **Multi-language Support**: Python + JavaScript + Java + R
- ✅ **Complete File System**: More than just code execution
- ✅ **Command Line Access**: Full shell environment

### Advanced Usage

::: code-group

```python [Python]
params = CreateSessionParams(image_id="agb-code-space-1")

result = agb.create(params)
if result.success:
    session = result.session
else:
    print(f"Creation failed: {result.error_message}")

# Batch operations
sessions = []
for i in range(3):
    params = CreateSessionParams(image_id="agb-code-space-1")
    result = agb.create(params)
    if result.success:
        sessions.append(result.session)

for session in sessions:
    agb.delete(session)
```

```typescript [TypeScript]
const params = new CreateSessionParams({ imageId: "agb-code-space-1" });

const result = await agb.create(params);
if (result.success && result.session) {
  const session = result.session;
} else {
  console.error("Creation failed:", result.errorMessage);
}

// Batch operations
const sessions = [];
for (let i = 0; i < 3; i++) {
  const params = new CreateSessionParams({ imageId: "agb-code-space-1" });
  const result = await agb.create(params);
  if (result.success && result.session) {
    sessions.push(result.session);
  }
}

for (const session of sessions) {
  await agb.delete(session);
}
```

:::

### Production Environment Configuration

::: code-group

```python [Python]
import os

agb = AGB()

from agb.config import Config
config = Config(
    endpoint="your-custom-endpoint.com",
    timeout_ms=60000,
)
agb = AGB(cfg=config)
```

```typescript [TypeScript]
const agb = new AGB();

const agbCustom = new AGB({
  config: {
    endpoint: "your-custom-endpoint.com",
    timeoutMs: 60000,
  },
});
```

:::