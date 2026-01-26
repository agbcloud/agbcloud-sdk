# Rich outputs from `run`

## What you’ll do

Run code and consume **rich outputs** returned by `session.code.run(...)`, including text, HTML, images, Markdown, LaTeX, JSON, and charts.

## Prerequisites

- `AGB_API_KEY`
- A valid `image_id` for code execution (e.g. `agb-code-space-1`)

## Quickstart

Minimal runnable example: generate a matplotlib plot, then save the returned PNG output.

```python
import base64

from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-code-space-1"))
if not create_result.success:
    raise SystemExit(f"Session creation failed: {create_result.error_message}")

session = create_result.session
try:
    exec_result = session.code.run(
        "import matplotlib.pyplot as plt\n"
        "plt.plot([1, 2, 3], [1, 4, 9])\n"
        "plt.title('AGB rich output demo')\n"
        "plt.show()\n",
        "python",
    )
    if not exec_result.success:
        raise SystemExit(f"Execution failed: {exec_result.error_message}")

    for item in exec_result.results:
        if item.png:
            with open("plot.png", "wb") as f:
                f.write(base64.b64decode(item.png))
            print("Saved: plot.png")
            break
    else:
        raise RuntimeError("No PNG output returned. Check image_id/runtime and the code.")
finally:
    agb.delete(session)
```

## Common tasks

### Understand the output fields

Each `ExecutionResult` may include:

- `text`: plain text output
- `html`: HTML string
- `markdown`: Markdown string
- `png` / `jpeg`: image data (string, typically base64)
- `svg`: SVG string
- `json`: structured JSON-like object
- `latex`: LaTeX string
- `chart`: chart payload

### Detect what you received

```python
for item in exec_result.results:
    if item.text:
        print("text")
    if item.html:
        print("html")
    if item.markdown:
        print("markdown")
    if item.png:
        print("png")
    if item.jpeg:
        print("jpeg")
    if item.svg:
        print("svg")
    if item.json is not None:
        print("json")
    if item.latex:
        print("latex")
    if item.chart is not None:
        print("chart")
```

### Save a returned PNG/JPEG to disk

```python
import base64

for item in exec_result.results:
    if item.png:
        with open("output.png", "wb") as f:
            f.write(base64.b64decode(item.png))
    if item.jpeg:
        with open("output.jpg", "wb") as f:
            f.write(base64.b64decode(item.jpeg))
```

### Access stdout/stderr logs

```python
if exec_result.logs:
    if exec_result.logs.stdout:
        print("STDOUT:", exec_result.logs.stdout)
    if exec_result.logs.stderr:
        print("STDERR:", exec_result.logs.stderr)
```

### Increase timeout for long-running code

```python
session.code.run("import time; time.sleep(100)", "python", timeout_s=120)
```

## Best practices

- Treat rich outputs as optional: always check which fields are present.
- Save large artifacts via files (upload/download) when possible; don’t rely on huge in-memory outputs.
- Always delete sessions when done (`agb.delete(session)`), even on failures.

## Troubleshooting

### `exec_result.success` is false

- **Likely cause**: runtime error, invalid language, or timeout.
- **Fix**: inspect `exec_result.error_message` and `exec_result.logs.stderr` for details; increase `timeout_s` if needed.

### Images don’t render

- **Likely cause**: you’re treating image payloads as raw bytes while they are base64 strings.
- **Fix**: decode with `base64.b64decode(...)` and write as binary.

## Related

- Overview: [`docs/code-interpreting/overview.md`](overview.md)
- API reference: [`docs/api-reference/capabilities/code_execution.md`](../api-reference/capabilities/code_execution.md)
- Examples: [`docs/examples/code_execution/README.md`](../examples/code_execution/README.md)

