#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test code for list_mcp_tools interface
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
            "AGB_API_KEY environment variable not set. Please set it:\n"
            "export AGB_API_KEY=akm-xxx"
        )
    return api_key


def test_list_mcp_tools():
    """Test list_mcp_tools interface"""

    # API key
    api_key = get_api_key()
    print(f"Using API Key: {api_key[:10]}...{api_key[-4:]}")

    try:
        print("Initializing AGB client...")

        # Create AGB instance
        agb = AGB(api_key=api_key)
        print(f"✅ AGB client initialized successfully")

        print("\n" + "="*60)
        print("Testing list_mcp_tools interface...")
        print("="*60)

        try:
            # Import the client directly to test the interface
            from agb.api.client import Client
            from agb.config import Config

            # Create config
            cfg = Config(
                endpoint="sdk-api.agb.cloud",
                timeout_ms=60000
            )

            # Create client
            client = Client(cfg)

            # Create request
            from agb.api.models.list_mcp_tools_request import ListMcpToolsRequest
            request = ListMcpToolsRequest(
                authorization=f"Bearer {api_key}",
                image_id="agb-code-space-1"
            )

            # Call list_mcp_tools
            print("   Calling list_mcp_tools...")
            response = client.list_mcp_tools(request)

            print("   ✅ list_mcp_tools call successful!")

            # Check if response is successful
            if response.is_successful():
                print("   ✅ HTTP request successful")

                # Get tools list
                tools_list = response.get_tools_list()
                if tools_list:
                    print(f"   Tools list: {tools_list}")
                else:
                    print("   Tools list: None or empty")

                # Check for errors
                error_msg = response.get_error_message()
                if error_msg:
                    print(f"   ⚠️  Error message: {error_msg}")
                else:
                    print("   ✅ No error messages")

            else:
                print("   ❌ HTTP request failed")
                error_msg = response.get_error_message()
                if error_msg:
                    print(f"   Error: {error_msg}")

        except Exception as e:
            print(f"   ❌ Error testing list_mcp_tools: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    print("AGB list_mcp_tools Interface Test")
    print("=" * 50)

    try:
        test_list_mcp_tools()

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
