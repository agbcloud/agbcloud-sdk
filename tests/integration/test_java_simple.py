#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Java code execution test
"""

import os
import sys

# Add project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agb.agb import AGB
from agb.session_params import CreateSessionParams


def get_api_key():
    """Get API Key from environment variables"""
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        raise ValueError(
            "AGB_API_KEY environment variable not set. Please set the environment variable:\n"
        )
    return api_key


def main():
    """Main function"""
    print("=" * 60)
    print("Simple Java Code Execution Test")
    print("=" * 60)

    # API key
    api_key = get_api_key()
    print(f"Using API Key: {api_key[:8]}...{api_key[-4:]}")

    try:
        # Create AGB instance
        agb = AGB(api_key=api_key)
        print(f"✅ AGB client initialized successfully")

        # Create session
        print("\nCreating session...")
        params = CreateSessionParams(image_id="agb-code-space-2")
        result = agb.create(params)

        if not result.success:
            raise AssertionError(f"Session creation failed: {result.error_message}")

        print(f"✅ Session created: {result.session.session_id}")

        # Test simple Java code execution
        print("\nTesting simple Java code execution...")
        # The server wraps the code in a class and main method, so we only provide the body
        java_code = 'System.out.println("Java is supported");'

        print("Java code to execute:")
        print(java_code)

        # Run the Java code
        code_result = result.session.code.run_code(java_code, "java", timeout_s=30)

        if not code_result.success:
            raise AssertionError(f"Java code execution failed! Error: {code_result.error_message}")

        print("✅ Java code execution succeeded!")
        print(f"Output:\n{code_result.result}")

        # Clean up - delete session
        print("\nDeleting session...")
        delete_result = agb.delete(result.session)
        if not delete_result.success:
            raise AssertionError(f"Session deletion failed: {delete_result.error_message}")

        print("✅ Session deleted successfully!")

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
