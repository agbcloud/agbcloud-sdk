"""
AGB Secure Code Execution Example

This example demonstrates how to validate and sanitize user-provided code before execution.
While the AGB sandbox is secure, preventing malicious code execution saves resources and time.
"""

import os
import re
from agb import AGB
from agb.session_params import CreateSessionParams


class SecureAGBClient:
    """AGB client with security validations"""

    DANGEROUS_PATTERNS = [
        r"import\s+os",
        r"import\s+subprocess",
        r"__import__",
        r"eval\s*\(",
        r"exec\s*\(",
        r"open\s*\(",
        r"file\s*\(",
    ]

    def __init__(self, api_key: str):
        self.agb = AGB(api_key=api_key)

    def safe_execute_code(self, code: str, language: str = "python"):
        """Execute code with security validations"""
        # Validate input
        if not self._validate_code_safety(code):
            raise ValueError("Code contains potentially dangerous operations")

        if len(code) > 10000:  # 10KB limit
            raise ValueError("Code too large - potential DoS attempt")

        # Execute with timeout
        params = CreateSessionParams(image_id="agb-code-space-1")
        result = self.agb.create(params)

        if not result.success:
            raise Exception(f"Session creation failed: {result.error_message}")

        session = result.session
        try:
            # Use shorter timeout for security
            print("🔒 Executing validated code...")
            code_result = session.code.run_code(code, language, timeout_s=30)
            return code_result
        finally:
            self.agb.delete(session)

    def _validate_code_safety(self, code: str) -> bool:
        """Check code for dangerous patterns"""
        code_lower = code.lower()

        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, code_lower):
                print(f"⚠️  Dangerous pattern detected: {pattern}")
                return False

        return True

    def execute_trusted_code(self, code: str, language: str = "python"):
        """Execute code from trusted sources without validation"""
        params = CreateSessionParams(image_id="agb-code-space-1")
        result = self.agb.create(params)

        if not result.success:
            raise Exception(f"Session creation failed: {result.error_message}")

        session = result.session
        try:
            return session.code.run_code(code, language)
        finally:
            self.agb.delete(session)


def main():
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        print("Error: AGB_API_KEY environment variable is not set")
        return

    secure_client = SecureAGBClient(api_key=api_key)

    # 1. Safe code
    safe_code = """
x = 10
y = 20
result = x + y
print(f"Result: {result}")
"""
    try:
        result = secure_client.safe_execute_code(safe_code)
        if result.success and result.logs.stdout and result.logs.stdout[0]:
            print(f"✅ Safe execution result: {result.logs.stdout[0]}")
        else:
            print(f"Execution failed: {result.error_message}")
    except Exception as e:
        print(f"Execution failed: {e}")

    # 2. Dangerous code (will be rejected)
    dangerous_code = """
import os
os.system("rm -rf /")
"""
    print("\nAttempting to run dangerous code...")
    try:
        secure_client.safe_execute_code(dangerous_code)
    except ValueError as e:
        print(f"🛡️  Security validation passed: {e}")


if __name__ == "__main__":
    main()
