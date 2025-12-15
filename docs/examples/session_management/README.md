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

### Session Pause and Resume
- Sessions can be paused to save costs during idle periods or when resources are temporarily not needed.
- Paused sessions maintain their state and can be resumed later to continue work.
- This is ideal for long-running workflows, overnight processing, or cost optimization scenarios.
- Benefits include:
  - **Cost savings**: ~70% cost reduction during pause periods
  - **Resource management**: Free up resources for other tasks
  - **State preservation**: Session state is maintained across pause/resume cycles
  - **Flexible scheduling**: Pause during non-business hours, resume when needed

### Cleanup
- Always call `agb.delete(session)` in a `finally` block or when the session is no longer needed to avoid unnecessary charges.

## Examples

### Basic Session Lifecycle (`create_session.py`)
Basic session creation, listing, and deletion.

<<< ./create_session.py

### Reconnecting to Sessions (`get_session.py`)
How to retrieve an existing session by ID.

<<< ./get_session.py

### Session Pooling (`session_pool.py`)
Implementation of a thread-safe session pool for high-concurrency applications.

<<< ./session_pool.py

### Session Pause and Resume (`pause_resume_session.py`)
Comprehensive examples of pausing and resuming sessions for cost optimization and resource management.

<<< ./pause_resume_session.py

## How to Run

1. **Set your API Key**:
   ```bash
   export AGB_API_KEY="your_api_key_here"
   ```

2. **Run Examples**:
   ```bash
   python docs/examples/session_management/create_session.py
   python docs/examples/session_management/get_session.py
   python docs/examples/session_management/session_pool.py
   python docs/examples/session_management/pause_resume_session.py
   ```
