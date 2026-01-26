"""
AGB Code Execution Caching Example

This example demonstrates how to implement client-side caching for code execution results.
Caching deterministic operations can significantly reduce latency and API costs.
"""

import hashlib
import os
from typing import Any, Dict

from agb import AGB
from agb.session_params import CreateSessionParams


class CachedAGBClient:
    """AGB client with result caching for expensive operations"""

    def __init__(self, api_key: str, cache_size: int = 100):
        self.agb = AGB(api_key=api_key)
        self.cache: Dict[str, Any] = {}
        self.cache_size = cache_size
        self.cache_order = []  # For LRU eviction

    def execute_with_cache(self, code: str, language: str = "python") -> Any:
        """Execute code with caching based on content hash"""
        # Create cache key from code content
        cache_key = self._get_cache_key(code, language)

        # Check cache first
        if cache_key in self.cache:
            print(f"⚡ Cache hit for operation: {language}")
            self._update_cache_order(cache_key)
            return self.cache[cache_key]

        print(f"🔄 Cache miss. Executing on cloud...")

        # Execute operation
        # In a real app, you might want to reuse a session instead of creating one every time
        params = CreateSessionParams(image_id="agb-code-space-1")
        result = self.agb.create(params)

        if not result.success:
            raise Exception(f"Session creation failed: {result.error_message}")

        session = result.session
        try:
            code_result = session.code.run(code, language)

            # Cache successful results
            if code_result.success:
                self._add_to_cache(cache_key, code_result)

            return code_result

        finally:
            self.agb.delete(session)

    def _get_cache_key(self, code: str, language: str) -> str:
        """Generate cache key from code content"""
        content = f"{language}:{code}"
        return hashlib.md5(content.encode()).hexdigest()

    def _add_to_cache(self, key: str, result: Any):
        """Add result to cache with LRU eviction"""
        # Remove oldest entry if cache is full
        if len(self.cache) >= self.cache_size and key not in self.cache:
            oldest_key = self.cache_order.pop(0)
            del self.cache[oldest_key]

        self.cache[key] = result
        self._update_cache_order(key)

    def _update_cache_order(self, key: str):
        """Update LRU order"""
        if key in self.cache_order:
            self.cache_order.remove(key)
        self.cache_order.append(key)


def main():
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        print("Error: AGB_API_KEY environment variable is not set")
        return

    client = CachedAGBClient(api_key=api_key)

    # Operation 1: Expensive calculation
    expensive_code = "import time; time.sleep(1); print('Calculation complete: 42')"

    print("--- First execution (slow) ---")
    result1 = client.execute_with_cache(expensive_code)
    if result1.success and result1.logs.stdout and result1.logs.stdout[0]:
        print(f"✅  execution result: {result1.logs.stdout[0]}")
    else:
        print(f"Execution failed: {result1.error_message}")

    print("\n--- Second execution (fast) ---")
    result2 = client.execute_with_cache(expensive_code)
    if result2.success and result2.logs.stdout and result2.logs.stdout[0]:
        print(f"✅  execution result: {result2.logs.stdout[0]}")
    else:
        print(f"Execution failed: {result2.error_message}")


if __name__ == "__main__":
    main()
