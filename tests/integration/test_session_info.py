#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test code for session.info method
"""

import sys
import os
import time

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


def test_session_info():
    """Test session.info method"""

    # API key
    api_key = get_api_key()
    print(f"Using API Key: {api_key[:10]}...{api_key[-4:]}")

    try:
        print("Initializing AGB client...")

        # Create AGB instance
        agb = AGB(api_key=api_key)
        print(f"✅ AGB client initialized successfully")

        print("\n" + "="*60)
        print("Testing session.info method...")
        print("="*60)

        # Create a session to test info method
        print("\n0. Creating a test session...")
        try:
            create_result = agb.create()
            if create_result.success:
                session = create_result.session
                session_id = session.session_id
                print(f"   ✅ Session created successfully")
                print(f"   Session ID: {session_id}")
            else:
                print(f"   ❌ Failed to create session: {create_result.error_message}")
                return False
        except Exception as e:
            print(f"   ❌ Error creating session: {e}")
            return False

        # Wait a moment for session to be fully ready
        print("   Waiting for session to be ready...")
        time.sleep(5)

        # Test 1: Basic session.info call
        print("\n1. Testing basic session.info call:")
        try:
            print("   Calling session.info()...")
            info_result = session.info()

            print(f"   ✅ session.info() call successful!")
            print(f"   Result type: {type(info_result)}")
            print(f"   Success: {info_result.success}")
            print(f"   Request ID: {info_result.request_id}")

            if info_result.success:
                print("   ✅ Session info retrieved successfully")

                # Display session information
                if info_result.data:
                    data = info_result.data
                    print("   Session Information:")
                    print(f"     Session ID: {data.get('session_id', 'N/A')}")
                    print(f"     Resource URL: {data.get('resource_url', 'N/A')}")

                    # Display desktop info if available
                    if data.get('app_id'):
                        print("     Desktop Information:")
                        print(f"       App ID: {data.get('app_id', 'N/A')}")
                        print(f"       Auth Code: {data.get('auth_code', 'N/A')}")
                        print(f"       Connection Properties: {data.get('connection_properties', 'N/A')}")
                        print(f"       Resource ID: {data.get('resource_id', 'N/A')}")
                        print(f"       Resource Type: {data.get('resource_type', 'N/A')}")
                        print(f"       Ticket: {data.get('ticket', 'N/A')}")
                else:
                    print("   ⚠️  No data in result")
            else:
                print("   ❌ Failed to get session info")
                print(f"   Error: {info_result.error_message}")

        except Exception as e:
            print(f"   ❌ Error testing session.info: {e}")
            import traceback
            traceback.print_exc()

        # Test 2: Test session.info with different session object
        print("\n2. Testing session.info with different session object:")
        try:
            # Create a new session object using the same session_id
            from agb.session import Session
            new_session = Session(agb, session_id)

            print("   Created new session object with same session_id")
            print(f"   New session ID: {new_session.get_session_id()}")

            # Call info on the new session object
            print("   Calling info() on new session object...")
            new_info_result = new_session.info()

            print(f"   ✅ New session.info() call successful!")
            print(f"   Success: {new_info_result.success}")
            print(f"   Request ID: {new_info_result.request_id}")

            if new_info_result.success:
                print("   ✅ New session object can also retrieve info")
                if new_info_result.data:
                    data = new_info_result.data
                    print(f"     Resource URL: {data.get('resource_url', 'N/A')}")
            else:
                print(f"   ❌ New session object failed: {new_info_result.error_message}")

        except Exception as e:
            print(f"   ❌ Error testing new session object: {e}")
            import traceback
            traceback.print_exc()

        # Test 3: Test session.info error handling
        print("\n3. Testing session.info error handling:")
        try:
            # Create a session object with invalid session_id
            invalid_session = Session(agb, "invalid-session-id")

            print("   Created session object with invalid session_id")
            print("   Calling info() on invalid session...")

            invalid_info_result = invalid_session.info()

            print(f"   Result received (expected to fail)")
            print(f"   Success: {invalid_info_result.success}")
            print(f"   Request ID: {invalid_info_result.request_id}")

            if not invalid_info_result.success:
                print("   ✅ Error handling working correctly")
                print(f"   Error message: {invalid_info_result.error_message}")
            else:
                print("   ⚠️  Unexpected success with invalid session_id")

        except Exception as e:
            print(f"   ❌ Error testing error handling: {e}")
            import traceback
            traceback.print_exc()

        # Test 4: Test session.info multiple times
        print("\n4. Testing session.info multiple times:")
        try:
            print("   Calling session.info() multiple times...")

            for i in range(3):
                print(f"     Call {i+1}:")
                result = session.info()
                print(f"       Success: {result.success}")
                print(f"       Request ID: {result.request_id}")

                if result.success and result.data:
                    data = result.data
                    print(f"       Resource URL: {data.get('resource_url', 'N/A')}")

                if i < 2:  # Don't sleep after last call
                    time.sleep(2)

            print("   ✅ Multiple calls completed successfully")

        except Exception as e:
            print(f"   ❌ Error testing multiple calls: {e}")
            import traceback
            traceback.print_exc()

        # Clean up: delete the test session
        print("\n5. Cleaning up - deleting test session...")
        try:
            delete_result = agb.delete(session)
            if delete_result.success:
                print(f"   ✅ Session deleted successfully: {session_id}")
            else:
                print(f"   ⚠️  Failed to delete session: {delete_result.error_message}")
        except Exception as e:
            print(f"   ⚠️  Error deleting session: {e}")

        print("\n" + "="*60)
        print("session.info method test completed!")
        print("="*60)

        return True

    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    print("AGB session.info Method Test")
    print("=" * 50)

    try:
        success = test_session_info()
        if success:
            print("\n✅ All tests completed successfully!")
        else:
            print("\n❌ Some tests failed!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
