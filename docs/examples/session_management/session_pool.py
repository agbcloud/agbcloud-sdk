"""
AGB Session Pool Example

This example demonstrates how to implement a thread-safe session pool.
Pooling sessions is critical for applications that need to execute many short-lived operations
without incurring the latency of creating a new session for every request.
"""

import os
import threading
import time
from contextlib import contextmanager
from typing import Dict, Optional

from agb import AGB
from agb.session_params import CreateSessionParams


class SessionPool:
    """Thread-safe session pool for high-throughput applications"""

    def __init__(self, api_key: str, max_sessions: int = 5, session_timeout: int = 300):
        self.agb = AGB(api_key=api_key)
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout
        self.sessions: Dict[str, dict] = {}
        self.lock = threading.Lock()
        print(f"🎱 Session Pool initialized (max={max_sessions})")

    @contextmanager
    def get_session(self):
        """Context manager to acquire and release a session"""
        session_info = self._acquire_session()
        try:
            print(f"🟢 Acquired session: {session_info['id']}")
            yield session_info["session"]
        finally:
            print(f"🟡 Released session: {session_info['id']}")
            self._release_session(session_info["id"])

    def _acquire_session(self):
        with self.lock:
            # 1. Cleanup expired sessions
            self._cleanup_expired_sessions()

            # 2. Try to reuse an idle session
            for session_id, info in self.sessions.items():
                if not info["in_use"]:
                    info["in_use"] = True
                    info["last_used"] = time.time()
                    return info

            # 3. Create new session if under limit
            if len(self.sessions) < self.max_sessions:
                print("✨ Creating new session for pool...")
                params = CreateSessionParams(image_id="agb-code-space-1")
                result = self.agb.create(params)

                if result.success:
                    session_info = {
                        "id": result.session.session_id,
                        "session": result.session,
                        "created": time.time(),
                        "last_used": time.time(),
                        "in_use": True,
                    }
                    self.sessions[session_info["id"]] = session_info
                    return session_info
                else:
                    raise Exception(f"Failed to create session: {result.error_message}")

            raise Exception("No sessions available and pool is at maximum capacity")

    def _release_session(self, session_id: str):
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id]["in_use"] = False

    def _cleanup_expired_sessions(self):
        current_time = time.time()
        expired_ids = []

        for session_id, info in self.sessions.items():
            # If idle for too long
            if (
                not info["in_use"]
                and (current_time - info["last_used"]) > self.session_timeout
            ):
                expired_ids.append(session_id)

        for session_id in expired_ids:
            print(f"⌛ Cleaning up expired session: {session_id}")
            session_info = self.sessions.pop(session_id)
            try:
                self.agb.delete(session_info["session"])
            except Exception as e:
                print(f"Error deleting session {session_id}: {e}")

    def destroy_all(self):
        """Clean up all sessions in the pool"""
        print("💥 Destroying pool...")
        with self.lock:
            for session_info in self.sessions.values():
                try:
                    self.agb.delete(session_info["session"])
                    print(f"Deleted {session_info['id']}")
                except Exception as e:
                    print(f"Error deleting session: {e}")
            self.sessions.clear()


def main():
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        print("Error: AGB_API_KEY environment variable is not set")
        return

    # 1. Initialize pool
    pool = SessionPool(api_key=api_key, max_sessions=2)

    try:
        # 2. Run tasks using the pool
        # We'll simulate 4 tasks with a pool of size 2
        # This means sessions will be reused

        def run_task(task_name):
            try:
                with pool.get_session() as session:
                    print(f"▶️  Running {task_name}...")
                    result = session.code.run_code(
                        f"print('Hello from {task_name}')", "python"
                    )
                    # Simulate work holding the session
                    time.sleep(1)
                    print(f"✅ {task_name} Result: {result.result.strip()}")
            except Exception as e:
                print(f"❌ {task_name} failed: {e}")

        threads = []
        for i in range(4):
            t = threading.Thread(target=run_task, args=(f"Task-{i}",))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

    finally:
        # 3. Cleanup
        pool.destroy_all()


if __name__ == "__main__":
    main()
