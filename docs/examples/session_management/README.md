# Session Management Examples

This directory contains examples demonstrating the complete lifecycle of AGB sessions.

<<<<<<< ours
## 📂 Examples

- **[create_session.py](create_session.py)**: Basic session creation, listing, and deletion.
- **[get_session.py](get_session.py)**: How to retrieve an existing session by ID (e.g., for reconnecting).

## 🚀 How to Run

1. **Set your API Key**:
   ```bash
   export AGB_API_KEY="your_api_key_here"
   ```

2. **Run Creation Example**:
   ```bash
   python docs/examples/session_management/create_session.py
   ```

3. **Run Retrieval Example**:
   ```bash
   python docs/examples/session_management/get_session.py
   ```

## 💡 Key Concepts
=======
## Key Concepts
>>>>>>> theirs

### Session Creation
- Use `CreateSessionParams` to configure your session (image, timeouts).
- Always check `result.success` before proceeding.

### Session Retrieval
- You can reconnect to any active session using `agb.get(session_id)`.
- This is useful for stateless applications (e.g., web servers) that need to resume control of a session.

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
   ```
