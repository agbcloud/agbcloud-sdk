# Session Management Examples

This directory contains examples demonstrating the complete lifecycle of AGB sessions.

## Key Concepts

### Session Creation
- Use `CreateSessionParams` to configure your session (image, timeouts).
- Always check `result.success` before proceeding.

### Session Retrieval
- You can reconnect to any active session using `agb.get(session_id)`.
- This is useful for stateless applications (e.g., web servers) that need to resume control of a session.

### Session Pooling
- For high-throughput applications, creating a new session for every request is inefficient.
- Maintaining a pool of "warm" sessions allows for faster execution and better resource utilization.

### Session Metrics
- Use `session.get_metrics()` to retrieve real-time resource usage information.
- Metrics include CPU usage, memory usage, disk usage, and network statistics.
- Useful for monitoring session performance and resource consumption.

### Cleanup
- Always call `agb.delete(session)` in a `finally` block or when the session is no longer needed to avoid unnecessary charges.

## Examples

### Basic Session Lifecycle
Basic session creation, listing, and deletion.

<<< ./create_session.py

### Reconnecting to Sessions
How to retrieve an existing session by ID.

<<< ./get_session.py

### Session Pooling
Implementation of a thread-safe session pool for high-concurrency applications.

<<< ./session_pool.py

### Session Metrics
Demonstrates how to retrieve real-time session metrics including CPU, memory, disk, and network usage.

<<< ./get_metrics.py

### MCP Tools
Demonstrates how to list and call MCP (Model Context Protocol) tools available in a session.

<<< ./mcp_tools.py

