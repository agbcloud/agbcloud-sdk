#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Java code execution test using the format from R test
"""

import sys
import os

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
    print("Java Code Execution Test (Using R test format)")
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
            print(f"❌ Session creation failed: {result.error_message}")
            return

        print(f"✅ Session created: {result.session.session_id}")

        # Test Java code execution using the format from R test
        print("\nTesting Java code execution using R test format...")
        java_code = """public class Test {
    public static void main(String[] args) {
        System.out.println("Java is supported");
    }
}"""
        
        print("Java code to execute:")
        print(java_code)
        
        # Run the Java code
        code_result = result.session.code.run_code(java_code, "java", timeout_s=30)
        
        if code_result.success:
            print("✅ Java code execution succeeded!")
            print(f"Output:\n{code_result.result}")
        else:
            print("❌ Java code execution failed!")
            print(f"Error: {code_result.error_message}")
            
        # Clean up - delete session
        print("\nDeleting session...")
        delete_result = agb.delete(result.session)
        if delete_result.success:
            print("✅ Session deleted successfully!")
        else:
            print(f"❌ Session deletion failed: {delete_result.error_message}")

    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()