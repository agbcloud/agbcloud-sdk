# Session API Reference

## Related Tutorial

- [Session Management Guide](/session/overview.md) - Detailed tutorial on session lifecycle and management

## Overview

The Session module provides methods for creating, managing, and terminating sessions
in the AGB cloud environment. Sessions are the foundation for all operations.




## Session

```python
class Session()
```

Session represents a session in the AGB cloud environment.

### set\_labels

```python
def set_labels(labels: Dict[str, str]) -> OperationResult
```

Sets the labels for this session.

**Arguments**:

- `labels` _Dict[str, str]_ - The labels to set for the session.


**Returns**:

    OperationResult: Result indicating success or failure with request ID.


**Raises**:

    SessionError: If the operation fails.

### get\_labels

```python
def get_labels() -> OperationResult
```

Gets the labels for this session.

**Returns**:

    OperationResult: Result containing the labels as data and request ID.


**Raises**:

    SessionError: If the operation fails.

### info

```python
def info() -> OperationResult
```

Get session information including resource details.

**Returns**:

    OperationResult: Result containing the session information as data and
  request ID.
  - success (bool): True if the operation succeeded
  - data (dict): Session information dictionary containing:
  - session_id (str): The session ID
  - resource_url (str): Resource URL for the session
  - app_id (str, optional): Application ID (if desktop session)
  - auth_code (str, optional): Authentication code (if desktop session)
  - connection_properties (dict, optional): Connection properties
  - resource_id (str, optional): Resource ID
  - resource_type (str, optional): Resource type
  - ticket (str, optional): Ticket for connection
  - error_message (str): Error details if the operation failed
  - request_id (str): Unique identifier for this API request

### get\_link

```python
def get_link(protocol_type: Optional[str] = None,
             port: Optional[int] = None) -> OperationResult
```

Get a link associated with the current session.

**Arguments**:

- `protocol_type` _Optional[str], optional_ - The protocol type to use for the
  link. Defaults to None.
- `port` _Optional[int], optional_ - The port to use for the link.
  Defaults to None.


**Returns**:

    OperationResult: Result containing the link URL as data and request ID.
  - success (bool): True if the operation succeeded
  - data (str): The link URL (when success is True)
  - error_message (str): Error details if the operation failed
  - request_id (str): Unique identifier for this API request


**Raises**:

    SessionError: If the request fails or the response is invalid.

### delete

```python
def delete(sync_context: bool = False) -> DeleteResult
```

Delete this session and release all associated resources.

**Arguments**:

- `sync_context` _bool, optional_ - Whether to sync context data (trigger file uploads)
  before deleting the session. Defaults to False.


**Returns**:

    DeleteResult: Result indicating success or failure with request ID.
  - success (bool): True if deletion succeeded
  - error_message (str): Error details if deletion failed
  - request_id (str): Unique identifier for this API request

### get\_status

```python
def get_status() -> "SessionStatusResult"
```

Get basic session status.

**Returns**:

    SessionStatusResult: Result containing session status information.
  - success (bool): True if the operation succeeded
  - status (str): Current session status
  - http_status_code (int): HTTP status code from the API response
  - code (str): Response code
  - error_message (str): Error details if the operation failed
  - request_id (str): Unique identifier for this API request

### call\_mcp\_tool

```python
def call_mcp_tool(tool_name: str,
                  args: Dict[str, Any],
                  read_timeout: Optional[int] = None,
                  connect_timeout: Optional[int] = None) -> McpToolResult
```

Call the specified MCP tool.

**Arguments**:

- `tool_name` _str_ - Tool name (e.g., "tap", "get_ui_elements").
- `args` _Dict[str, Any]_ - Tool arguments dictionary.
- `read_timeout` _Optional[int], optional_ - Read timeout in milliseconds.
  Defaults to None.
- `connect_timeout` _Optional[int], optional_ - Connection timeout in milliseconds.
  Defaults to None.


**Returns**:

    McpToolResult: Tool call result, data field contains tool return data in JSON string format.
  - success (bool): True if tool call succeeded
  - data (str): Tool return data in JSON string format (when success is True)
  - error_message (str): Error details if tool call failed
  - request_id (str): Unique identifier for this API request


**Raises**:

    SessionError: If the tool call fails.


**Example**:

```python
# Call mobile device tap tool
result = session.call_mcp_tool("tap", {"x": 100, "y": 200})

# Call get UI elements tool
result = session.call_mcp_tool("get_ui_elements", {})
```

### list\_mcp\_tools

```python
def list_mcp_tools(image_id: Optional[str] = None) -> McpToolsResult
```

List MCP tools available for the current session.

**Arguments**:

- `image_id` _Optional[str], optional_ - Image ID. Defaults to current session's
  image_id or "agb-code-space-1" if not specified.


**Returns**:

    McpToolsResult: Result containing the list of available MCP tools.
  - success (bool): True if the operation succeeded
  - tools (List[McpTool]): List of MCP tool objects, each containing name,
  description, input_schema, server, and tool fields
  - error_message (str): Error details if the operation failed
  - request_id (str): Unique identifier for this API request


**Example**:

```python
# List available tools
result = session.list_mcp_tools()
if result.success:
  for tool in result.tools:
      print(f"{tool.name}: {tool.description}")
```

### get\_metrics

```python
def get_metrics(read_timeout: Optional[int] = None,
                connect_timeout: Optional[int] = None) -> SessionMetricsResult
```

Get runtime metrics for this session.

**Arguments**:

- `read_timeout` _Optional[int]_ - Read timeout in milliseconds.
- `connect_timeout` _Optional[int]_ - Connect timeout in milliseconds.


**Returns**:

    SessionMetricsResult: Result containing session metrics data.

## Related Resources

- [AGB API Reference](agb.md)
- [Context API Reference](data_context/context.md)
- [Context Manager API Reference](data_context/context_manager.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
