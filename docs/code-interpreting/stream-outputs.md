# Real-time streaming from `run`

## What you'll do

Execute code and receive **real-time stdout/stderr output** via WebSocket streaming, enabling live progress monitoring for long-running code executions.

## Prerequisites

- `AGB_API_KEY`
- A valid `image_id` for code execution (e.g. `agb-code-space-1`)
- Session must have a valid WebSocket URL (`ws_url`)

## Quickstart

Minimal runnable example: execute a long-running script and print stdout chunks in real-time.

::: code-group

```python [Python]
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-code-space-1"))
if not create_result.success:
    raise SystemExit(f"Session creation failed: {create_result.error_message}")

session = create_result.session
try:
    def on_stdout(chunk: str) -> None:
        print(f"[STDOUT] {chunk}", end="")

    def on_stderr(chunk: str) -> None:
        print(f"[STDERR] {chunk}", end="")

    def on_error(error: Exception) -> None:
        print(f"[ERROR] {error}")

    exec_result = session.code.run(
        "import time\nfor i in range(5):\n    print(f'Progress: {i+1}/5')\n    time.sleep(1)\nprint('Done!')",
        "python",
        stream_beta=True,
        on_stdout=on_stdout,
        on_stderr=on_stderr,
        on_error=on_error,
    )

    if exec_result.success:
        print(f"\nExecution completed in {exec_result.execution_time:.2f}s")
finally:
    agb.delete(session)
```

```typescript [TypeScript]
import { AGB, CreateSessionParams } from "agbcloud-sdk";

const agb = new AGB();
const createResult = await agb.create(
  new CreateSessionParams({ imageId: "agb-code-space-1" })
);
if (!createResult.success || !createResult.session) {
  throw new Error(`Session creation failed: ${createResult.errorMessage}`);
}

const session = createResult.session;
try {
  const execResult = await session.code.run(
    "import time\n" +
    "for i in range(5):\n" +
    "    print(f'Progress: {i+1}/5')\n" +
    "    time.sleep(1)\n" +
    "print('Done!')",
    "python",
    60,
    true, // stream_beta
    (chunk: string) => console.log(`[STDOUT] ${chunk}`),
    (chunk: string) => console.log(`[STDERR] ${chunk}`),
    (error: Error) => console.log(`[ERROR] ${error}`)
  );

  if (execResult.success) {
    console.log(`\nExecution completed in ${execResult.executionTime?.toFixed(2)}s`);
  }
} finally {
  await agb.delete(session);
}
```

:::

## Parameters

### Basic parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `code` | `str` | required | The code to execute |
| `language` | `str` | required | Programming language (`python`, `javascript`, `r`, `java`) |
| `timeout_s` | `int` | `60` | Execution timeout in seconds |

### Streaming parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stream_beta` | `bool` | `False` | **Set to `True` to enable WebSocket streaming** |
| `on_stdout` | `Callable[[str], None]` | `None` | Callback for each stdout chunk (streaming only) |
| `on_stderr` | `Callable[[str], None]` | `None` | Callback for each stderr chunk (streaming only) |
| `on_error` | `Callable[[Any], None]` | `None` | Callback for streaming errors |

### How streaming is triggered

Streaming mode is activated when `stream_beta=True`. The other streaming-related parameters (`on_stdout`, `on_stderr`, `on_error`) are only effective when streaming is enabled.

::: code-group

```python [Python]
# Non-streaming (default): waits for completion, returns all output at once
result = session.code.run("print('hello')", "python")

# Streaming: receives output chunks in real-time via WebSocket
result = session.code.run(
    "print('hello')",
    "python",
    stream_beta=True,
    on_stdout=lambda chunk: print(chunk, end="")
)
```

```typescript [TypeScript]
// Non-streaming (default): waits for completion, returns all output at once
const result = await session.code.run("print('hello')", "python");

// Streaming: receives output chunks in real-time via WebSocket
const result = await session.code.run(
  "print('hello')",
  "python",
  60,
  true, // stream_beta
  (chunk) => process.stdout.write(chunk)
);
```

:::

## Why streaming?

### The problem

In the traditional request-response model, code execution blocks until completion. For long-running tasks:

- **No visibility**: Users see nothing until execution finishes
- **Poor UX**: Long waits with no feedback feel unresponsive
- **Hard to debug**: No way to monitor progress or detect issues early

### The solution

WebSocket streaming provides real-time output as code executes:

- **Live progress**: See stdout/stderr as it happens
- **Better UX**: Immediate feedback keeps users informed
- **Early detection**: Spot errors or issues during execution, not just after

### When to use streaming

| Scenario | Streaming? | Reason |
|----------|------------|--------|
| Quick scripts (< 5s) | Not needed | Output arrives fast enough |
| Long computations | **Recommended** | Monitor progress |
| Data processing pipelines | **Recommended** | Track each stage |
| Training ML models | **Recommended** | Observe training logs |
| Interactive demos | **Recommended** | Live feedback for users |

## Common tasks

### Monitor long-running data processing

::: code-group

```python [Python]
def on_stdout(chunk: str) -> None:
    # Parse and display progress
    if "rows processed" in chunk:
        print(f"📊 {chunk.strip()}")

exec_result = session.code.run(
    """
import time
for i in range(100):
    print(f"{i+1} rows processed")
    time.sleep(0.1)
""",
    "python",
    stream_beta=True,
    on_stdout=on_stdout,
)
```

```typescript [TypeScript]
const execResult = await session.code.run(
  "import time\n" +
  "for i in range(100):\n" +
  "    print(f'{i+1} rows processed')\n" +
  "    time.sleep(0.1)",
  "python",
  60,
  true,
  (chunk: string) => {
    if (chunk.includes("rows processed")) {
      console.log(`📊 ${chunk.trim()}`);
    }
  }
);
```

:::

### Handle stderr separately

::: code-group

```python [Python]
def on_stdout(chunk: str) -> None:
    print(f"[OUT] {chunk}", end="")

def on_stderr(chunk: str) -> None:
    print(f"[ERR] {chunk}", end="", file=sys.stderr)

exec_result = session.code.run(
    code,
    "python",
    stream_beta=True,
    on_stdout=on_stdout,
    on_stderr=on_stderr,
)
```

```typescript [TypeScript]
const execResult = await session.code.run(
  code,
  "python",
  60,
  true,
  (chunk: string) => console.log(`[OUT] ${chunk}`),
  (chunk: string) => console.error(`[ERR] ${chunk}`)
);
```

:::

### Handle streaming errors

::: code-group

```python [Python]
def on_error(error: Exception) -> None:
    print(f"Streaming error: {error}")

exec_result = session.code.run(
    code,
    "python",
    stream_beta=True,
    on_stdout=on_stdout,
    on_error=on_error,
)
```

```typescript [TypeScript]
const execResult = await session.code.run(
  code,
  "python",
  60,
  true,
  (chunk) => console.log(chunk),
  undefined, // on_stderr
  (error: Error) => console.error(`Streaming error: ${error}`)
);
```

:::

## Best practices

- **Use streaming for long-running code**: If execution takes more than a few seconds, streaming improves user experience.
- **Handle errors gracefully**: Always provide an `on_error` callback to catch streaming failures.
- **Keep callbacks fast**: Callbacks should process output quickly; don't block in callbacks.
- **Combine with timeout**: Set an appropriate `timeout_s` to prevent runaway executions.
- **Clean up sessions**: Always delete sessions in a `finally` block, even on errors.

## Troubleshooting

### Streaming doesn't start

- **Likely cause**: `stream_beta` is not set to `True`, or session lacks WebSocket support.
- **Fix**: Ensure `stream_beta=True` and the session has a valid `ws_url`.

### No output received

- **Likely cause**: Callbacks not provided or code produces no stdout/stderr.
- **Fix**: Verify `on_stdout` and `on_stderr` callbacks are correctly set; test with simple `print()` statements.

### Streaming interrupted

- **Likely cause**: Network issue or WebSocket disconnection.
- **Fix**: Check `on_error` callback for details; the execution may still complete via fallback.

### Performance overhead

- **Likely cause**: Heavy processing in callbacks.
- **Fix**: Keep callbacks lightweight; buffer output if complex processing is needed.

## Related

- Overview: [`docs/code-interpreting/overview.md`](overview.md)
- Rich outputs: [`docs/code-interpreting/rich-outputs.md`](rich-outputs.md)
- API reference: [`docs/api-reference/python/capabilities/code_execution.md`](../api-reference/python/capabilities/code_execution.md)
