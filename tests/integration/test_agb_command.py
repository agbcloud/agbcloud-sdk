#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGB command execution test code
"""

import sys
import os

# Add project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Direct import, completely bypass __init__.py
import importlib.util
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


def test_create_session():
    """Test creating AGB session"""

    # API key
    api_key = get_api_key()
    print(f"Using API Key: {api_key}")

    try:
        print("Initializing AGB client...")

        # Create AGB instance
        agb = AGB(api_key=api_key)
        print(f"✅ AGB client initialized successfully")
        print(f"   Endpoint: {agb.endpoint}")
        print(f"   Timeout: {agb.timeout_ms}ms")

        print("\nCreating session...")

        # Call create() method without passing any parameters
        params = CreateSessionParams(
            image_id="agb-code-space-1"
        )
        result = agb.create(params)

        # Check result
        if result.success:
            print("✅ Session created successfully!")
            print(f"   Request ID: {result.request_id}")
            print(f"   Session ID: {result.session.session_id}")
            if hasattr(result.session, 'resource_url') and result.session.resource_url:
                print(f"   Resource URL: {result.session.resource_url}")
            if hasattr(result.session, 'image_id') and result.session.image_id:
                print(f"   Image ID: {result.session.image_id}")
        else:
            print("❌ Session creation failed!")
            print(f"   Error message: {result.error_message}")
            if result.request_id:
                print(f"   Request ID: {result.request_id}")

        return result, agb

    except Exception as e:
        print(f"❌ Error occurred during test: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def test_command_execution(session):
    """Test command execution functionality"""
    print("\n" + "=" * 60)
    print("Testing Command Execution Functionality")
    print("=" * 60)

    try:
        # Test basic system information commands
        print("1. Testing system information commands...")
        commands = [
            "uname -a",  # System information
            "whoami",    # Current user
            "pwd",       # Current directory
            "ls -la",    # List files
            "date",      # Current time
        ]

        for cmd in commands:
            print(f"\nExecuting command: {cmd}")
            result = session.command.execute_command(cmd, timeout_ms=10000)
            if result.success:
                print("✅ Command executed successfully!")
                print(f"   Request ID: {result.request_id}")
                print(f"   Output:\n{result.output}")
            else:
                print("❌ Command execution failed!")
                print(f"   Error message: {result.error_message}")
                if result.request_id:
                    print(f"   Request ID: {result.request_id}")

        # Test file operation commands
        print("\n2. Testing file operation commands...")
        file_commands = [
            "echo 'Hello AGB!' > test_file.txt",
            "cat test_file.txt",
            "wc -l test_file.txt",
            "rm test_file.txt",
        ]

        for cmd in file_commands:
            print(f"\nExecuting command: {cmd}")
            result = session.command.execute_command(cmd, timeout_ms=10000)
            if result.success:
                print("✅ Command executed successfully!")
                print(f"   Request ID: {result.request_id}")
                if result.output.strip():
                    print(f"   Output:\n{result.output}")
            else:
                print("❌ Command execution failed!")
                print(f"   Error message: {result.error_message}")
                if result.request_id:
                    print(f"   Request ID: {result.request_id}")

        # Test network-related commands
        print("\n3. Testing network-related commands...")
        network_commands = [
            "curl -s --connect-timeout 5 http://httpbin.org/ip",
            "ping -c 3 8.8.8.8",
            "nslookup google.com",
        ]

        for cmd in network_commands:
            print(f"\nExecuting command: {cmd}")
            result = session.command.execute_command(cmd, timeout_ms=15000)
            if result.success:
                print("✅ Command executed successfully!")
                print(f"   Request ID: {result.request_id}")
                if result.output.strip():
                    print(f"   Output:\n{result.output}")
            else:
                print("❌ Command execution failed!")
                print(f"   Error message: {result.error_message}")
                if result.request_id:
                    print(f"   Request ID: {result.request_id}")

        # Test process management commands
        print("\n4. Testing process management commands...")
        process_commands = [
            "ps aux | head -10",
            "top -bn1 | head -20",
            "free -h",
        ]

        for cmd in process_commands:
            print(f"\nExecuting command: {cmd}")
            result = session.command.execute_command(cmd, timeout_ms=10000)
            if result.success:
                print("✅ Command executed successfully!")
                print(f"   Request ID: {result.request_id}")
                if result.output.strip():
                    print(f"   Output:\n{result.output}")
            else:
                print("❌ Command execution failed!")
                print(f"   Error message: {result.error_message}")
                if result.request_id:
                    print(f"   Request ID: {result.request_id}")

        # Test error handling
        print("\n5. Testing error handling...")
        error_commands = [
            "nonexistent_command",
            "ls /nonexistent/path",
            "cat /etc/shadow",  # Insufficient permissions
        ]

        for cmd in error_commands:
            print(f"\nExecuting command: {cmd}")
            result = session.command.execute_command(cmd, timeout_ms=10000)
            if result.success:
                print("⚠️  Error command unexpectedly executed successfully")
                print(f"   Output: {result.output}")
            else:
                print("❌ Command execution failed (expected result)!")
                print(f"   Error message: {result.error_message}")
                if result.request_id:
                    print(f"   Request ID: {result.request_id}")

        return True

    except Exception as e:
        print(f"❌ Error occurred during command execution test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    print("=" * 60)
    print("AGB Command Execution Test")
    print("=" * 60)

    # Test session creation
    result, agb = test_create_session()

    if result and result.success and agb:
        # Test command execution functionality
        command_test_success = test_command_execution(result.session)

        # Optional: Test session deletion
        print("\n" + "=" * 60)
        print("Do you want to delete the created session? (y/n): ", end="")
        try:
            choice = input().strip().lower()
            if choice in ['y', 'yes']:
                print("Deleting session...")
                delete_result = agb.delete(result.session)
                print("delete_result =", delete_result)
                if delete_result.success:
                    print("✅ Session deleted successfully!")
                else:
                    print(f"❌ Session deletion failed: {delete_result.error_message}")
        except KeyboardInterrupt:
            print("\nUser cancelled deletion operation")

    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
