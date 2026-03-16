# MCP Tools

Call MCP (Model Context Protocol) tools directly from a session.

## What you'll do

List available tools and execute them to interact with various capabilities in the AGB cloud environment.

## Prerequisites

- `AGB_API_KEY`
- An active session

## Quickstart

::: code-group

```python [Python]
# List available tools
result = session.list_mcp_tools()
if result.success:
    for tool in result.tools:
        print(f"{tool.name}: {tool.description}")

# Call a tool
result = session.call_mcp_tool("tool_name", {"param1": "value1"})
if result.success:
    print("Result:", result.data)
```

```typescript [TypeScript]
// List available tools
const toolsResult = await session.listMcpTools();
if (toolsResult.success) {
  for (const tool of toolsResult.tools ?? []) {
    console.log(`${tool.name}: ${tool.description}`);
  }
}

// Call a tool
const result = await session.callMcpTool("tool_name", { param1: "value1" });
if (result.success) {
  console.log("Result:", result.data);
}
```

:::

## Common tasks

### List available tools

::: code-group

```python [Python]
result = session.list_mcp_tools()
if result.success:
    print(f"Available tools: {len(result.tools)}")
    for tool in result.tools:
        print(f"  - {tool.name}: {tool.description}")
```

```typescript [TypeScript]
const result = await session.listMcpTools();
if (result.success) {
  console.log(`Available tools: ${result.tools?.length}`);
  for (const tool of result.tools ?? []) {
    console.log(`  - ${tool.name}: ${tool.description}`);
  }
}
```

:::

### Call a tool with parameters

::: code-group

```python [Python]
result = session.call_mcp_tool("tool_name", {"param1": "value1", "param2": "value2"})
if result.success:
    print("Tool executed successfully")
    print("Result:", result.data)
else:
    print("Tool call failed:", result.error_message)
```

```typescript [TypeScript]
const result = await session.callMcpTool("tool_name", { param1: "value1", param2: "value2" });
if (result.success) {
  console.log("Tool executed successfully");
  console.log("Result:", result.data);
} else {
  console.error("Tool call failed:", result.errorMessage);
}
```

:::

## Best practices

- Use `list_mcp_tools()` to discover available tools for your session's image
- Available tools depend on the image type (browser images have UI tools, code images have different tools)
- Always check `result.success` before using the result data

## Related

- [Session Overview](./overview.md)
