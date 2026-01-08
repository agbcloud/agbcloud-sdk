# Run code in the cloud (rich outputs)

## What you’ll do

Run Python/JavaScript/Java/R code in an AGB session and read **rich execution outputs** (text/HTML/images/JSON) returned by the SDK.

## Output formats you can get

The enhanced code execution API can return rich outputs in multiple formats:

- Plain text output
- HTML content
- Images (PNG, JPEG, SVG)
- Charts and visualizations
- Markdown content
- LaTeX expressions
- JSON data

## Prerequisites

- `AGB_API_KEY` (see [`docs/api-key.md`](../api-key.md))
- A valid `image_id` for code execution (e.g. `agb-code-space-1`)
- (Optional) A Python environment with `agbcloud-sdk` installed

## Quickstart

Minimal runnable example: create a session, run code, print text output, then clean up.

```python
from agb import AGB
from agb.session_params import CreateSessionParams

agb = AGB()
create_result = agb.create(CreateSessionParams(image_id="agb-code-space-1"))
if not create_result.success:
    raise SystemExit(f"Session creation failed: {create_result.error_message}")

session = create_result.session
exec_result = session.code.run_code("print('Hello, AGB!')", "python")
if not exec_result.success:
    raise SystemExit(f"Execution failed: {exec_result.error.value}")

for item in exec_result.results:
    if item.text:
        print(item.text)

agb.delete(session)
```

## Common tasks

### Read rich outputs (HTML / PNG / SVG / JSON)

```python
exec_result = session.code.run_code(
    "import matplotlib.pyplot as plt; plt.plot([1,2,3]); plt.title('demo'); plt.show()",
    "python",
)

if exec_result.success:
    for item in exec_result.results:
        if item.text:
            print(item.text)
        if item.html:
            print("HTML output available")
        if item.png:
            print("PNG image available (base64)")
        if item.jpeg:
            print("JPEG image available (base64)")
        if item.svg:
            print("SVG output available")
        if item.json:
            print("JSON output available")
else:
    print(exec_result.error.value)

### Read Markdown / LaTeX / chart outputs

```python
for item in exec_result.results:
    if item.markdown:
        print("Markdown output available")
    if item.latex:
        print("LaTeX output available")
    if item.chart:
        print("Chart output available")
```
```

### Access logs (stdout / stderr)

```python
if exec_result.success and exec_result.logs:
    if exec_result.logs.stdout:
        print("STDOUT:", exec_result.logs.stdout)
    if exec_result.logs.stderr:
        print("STDERR:", exec_result.logs.stderr)
```

### Increase timeout for long-running code

```python
session.code.run_code("import time; time.sleep(100)", "python", timeout_s=120)
```

## Best practices

- Always delete sessions when done (`agb.delete(session)`), even on failures.
- Make `image_id` explicit in examples; remind users it must exist in their account.
- If you run untrusted code, validate inputs and enforce timeouts/limits.
- Prefer small, incremental code blocks for debugging (then compose into a pipeline).

## Troubleshooting

### Session creation fails

- **Likely cause**: invalid `AGB_API_KEY` or invalid `image_id`.
- **Fix**: verify `AGB_API_KEY` is set and the `image_id` exists in your account.

### Execution times out

- **Likely cause**: default timeout is too small for the workload.
- **Fix**: pass a larger `timeout_s`, or break the workload into smaller steps.

## Related

- API reference: [`docs/api-reference/capabilities/code_execution.md`](../api-reference/capabilities/code_execution.md)
- Examples: [`docs/examples/code_execution/README.md`](../examples/code_execution/README.md)