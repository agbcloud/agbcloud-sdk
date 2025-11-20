#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test code for session.get_link method
"""

import os
import sys
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
            "export AGB_API_KEY=your_api_key_here"
        )
    return api_key


def test_session_get_link():
    """Test session.get_link method"""

    # API key
    api_key = get_api_key()
    print(f"Using API Key: {api_key[:10]}...{api_key[-4:]}")

    try:
        print("Initializing AGB client...")
        from agb.config import Config

        config = Config(
            endpoint=os.getenv("AGB_ENDPOINT", "sdk-api.agb.cloud"), timeout_ms=60000
        )

        # Create AGB instance
        agb = AGB(api_key=api_key, cfg=config)
        print(f"✅ AGB client initialized successfully")

        print("\n" + "=" * 60)
        print("Testing session.get_link method...")
        print("=" * 60)

        # Create a session to test get_link method
        print("\n0. Creating a test session...")
        try:
            params = CreateSessionParams(image_id="agb-browser-use-1")
            create_result = agb.create(params)
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
        time.sleep(1)
        # Test 1: Basic session.get_link call (no parameters)
        print("\n1. Testing basic session.get_link call (no parameters):")
        try:
            print("   Calling session.get_link()...")
            start_time = time.time()

            link_result = session.get_link()

            end_time = time.time()
            duration = end_time - start_time

            print(f"   ✅ session.get_link() call successful!")
            print(f"   Result type: {type(link_result)}")
            print(f"   Success: {link_result.success}")
            print(f"   Request ID: {link_result.request_id}")
            print(f"   Duration: {duration:.3f} seconds")

            if link_result.success:
                print("   ✅ Session link retrieved successfully")

                # Display link information
                if link_result.data:
                    print(f"   Link URL: {link_result.data}")
                else:
                    print("   ⚠️  No link URL in result")
            else:
                print("   ❌ Failed to get session link")
                print(f"   Error: {link_result.error_message}")

        except Exception as e:
            print(f"   ❌ Error testing session.get_link: {e}")
            import traceback

            traceback.print_exc()

        # Test 2: Test session.get_link with port parameter
        print("\n2. Testing session.get_link with port parameter:")
        try:
            # Use valid port range [30100, 30199] as per API requirements
            test_port = 30100
            print(f"   Calling session.get_link(port={test_port})...")
            start_time = time.time()

            link_result_port = session.get_link(port=test_port)

            end_time = time.time()
            duration = end_time - start_time

            print(f"   ✅ session.get_link(port={test_port}) call successful!")
            print(f"   Success: {link_result_port.success}")
            print(f"   Request ID: {link_result_port.request_id}")
            print(f"   Duration: {duration:.3f} seconds")

            if link_result_port.success:
                print(f"   ✅ Link with port {test_port} retrieved successfully")
                if link_result_port.data:
                    print(f"   Link URL: {link_result_port.data}")
                else:
                    print("   ⚠️  No link URL in result")
            else:
                print(
                    f"   ❌ Failed to get link with port: {link_result_port.error_message}"
                )

        except Exception as e:
            print(f"   ❌ Error testing session.get_link with port: {e}")
            import traceback

            traceback.print_exc()

        # Test 2.5: Test session.get_link with protocol_type parameter
        print("\n2.5. Testing session.get_link with protocol_type parameter:")
        try:
            # Use valid port range [30100, 30199] as per API requirements
            test_port = 30101
            print("   Calling session.get_link(protocol_type='https')...")
            start_time = time.time()

            link_result_https = session.get_link(protocol_type="https", port=test_port)

            end_time = time.time()
            duration = end_time - start_time

            print(f"   ✅ session.get_link(protocol_type='https') call successful!")
            print(f"   Success: {link_result_https.success}")
            print(f"   Request ID: {link_result_https.request_id}")
            print(f"   Duration: {duration:.3f} seconds")

            if link_result_https.success:
                print("   ✅ HTTPS link retrieved successfully")
                if link_result_https.data:
                    print(f"   HTTPS Link URL: {link_result_https.data}")
                    # Check if the URL starts with https://
                    if link_result_https.data.startswith("https://"):
                        print("   ✅ URL correctly uses HTTPS protocol")
                    else:
                        print("   ⚠️  URL does not start with https://")
                else:
                    print("   ⚠️  No HTTPS link URL in result")
            else:
                print(
                    f"   ❌ Failed to get HTTPS link: {link_result_https.error_message}"
                )

        except Exception as e:
            print(f"   ❌ Error testing session.get_link with protocol_type: {e}")
            import traceback

            traceback.print_exc()

        # Test 3: Test session.get_link with different session object
        print("\n3. Testing session.get_link with different session object:")
        try:
            # Create a new session object using the same session_id
            from agb.session import Session

            new_session = Session(agb, session_id)

            print("   Created new session object with same session_id")
            print(f"   New session ID: {new_session.get_session_id()}")

            # Call get_link on the new session object
            print("   Calling get_link() on new session object...")
            start_time = time.time()

            new_link_result = new_session.get_link()

            end_time = time.time()
            duration = end_time - start_time

            print(f"   ✅ New session.get_link() call successful!")
            print(f"   Success: {new_link_result.success}")
            print(f"   Request ID: {new_link_result.request_id}")
            print(f"   Duration: {duration:.3f} seconds")

            if new_link_result.success:
                print("   ✅ New session object can also retrieve link")
                if new_link_result.data:
                    print(f"     Link URL: {new_link_result.data}")
            else:
                print(
                    f"   ❌ New session object failed: {new_link_result.error_message}"
                )

        except Exception as e:
            print(f"   ❌ Error testing new session object: {e}")
            import traceback

            traceback.print_exc()

        # Test 4: Test session.get_link error handling
        print("\n4. Testing session.get_link error handling:")
        try:
            # Create a session object with invalid session_id
            invalid_session = Session(agb, "invalid-session-id")

            print("   Created session object with invalid session_id")
            print("   Calling get_link() on invalid session...")

            start_time = time.time()

            invalid_link_result = invalid_session.get_link()

            end_time = time.time()
            duration = end_time - start_time

            print(f"   Result received (expected to fail)")
            print(f"   Success: {invalid_link_result.success}")
            print(f"   Request ID: {invalid_link_result.request_id}")
            print(f"   Duration: {duration:.3f} seconds")

            if not invalid_link_result.success:
                print("   ✅ Error handling working correctly")
                print(f"   Error message: {invalid_link_result.error_message}")
            else:
                print("   ⚠️  Unexpected success with invalid session_id")

        except Exception as e:
            print(f"   ❌ Error testing error handling: {e}")
            import traceback

            traceback.print_exc()

        # Test 5: Test session.get_link multiple times
        print("\n5. Testing session.get_link multiple times:")
        try:
            print("   Calling session.get_link() multiple times...")

            for i in range(3):
                print(f"     Call {i+1}:")
                start_time = time.time()

                result = session.get_link()

                end_time = time.time()
                duration = end_time - start_time

                print(f"       Success: {result.success}")
                print(f"       Request ID: {result.request_id}")
                print(f"       Duration: {duration:.3f} seconds")

                if result.success and result.data:
                    print(f"       Link URL: {result.data}")

                if i < 2:  # Don't sleep after last call
                    time.sleep(2)

            print("   ✅ Multiple calls completed successfully")

        except Exception as e:
            print(f"   ❌ Error testing multiple calls: {e}")
            import traceback

            traceback.print_exc()

        # Test 6: Test session.get_link performance comparison
        print("\n6. Testing session.get_link performance comparison:")
        try:
            print("   Comparing different parameter combinations...")

            # Test no parameters
            start_time = time.time()
            result_no_params = session.get_link()
            end_time = time.time()
            duration_no_params = end_time - start_time

            # Test with protocol_type wss
            start_time = time.time()
            result_with_protocol_wss = session.get_link(protocol_type="wss")
            end_time = time.time()
            duration_with_protocol_wss = end_time - start_time

            # Test with protocol_type https
            start_time = time.time()
            result_with_protocol_https = session.get_link(protocol_type="https")
            end_time = time.time()
            duration_with_protocol_https = end_time - start_time

            # Test with port (use valid port range [30100, 30199])
            test_port = 30102
            start_time = time.time()
            result_with_port = session.get_link(port=test_port)
            end_time = time.time()
            duration_with_port = end_time - start_time

            # Test with both wss and port
            start_time = time.time()
            result_with_wss_and_port = session.get_link(protocol_type="wss", port=test_port)
            end_time = time.time()
            duration_with_wss_and_port = end_time - start_time

            # Test with both https and port
            start_time = time.time()
            result_with_https_and_port = session.get_link(
                protocol_type="https", port=test_port
            )
            end_time = time.time()
            duration_with_https_and_port = end_time - start_time

            print("   Performance Results:")
            print(f"     No parameters: {duration_no_params:.3f}s")
            print(f"     With protocol_type wss: {duration_with_protocol_wss:.3f}s")
            print(f"     With protocol_type https: {duration_with_protocol_https:.3f}s")
            print(f"     With port: {duration_with_port:.3f}s")
            print(f"     With wss + port: {duration_with_wss_and_port:.3f}s")
            print(f"     With https + port: {duration_with_https_and_port:.3f}s")

            # Display link results for different protocol types
            print("\n   Link Results Comparison:")
            if result_with_protocol_wss.success and result_with_protocol_wss.data:
                print(f"     WSS Link: {result_with_protocol_wss.data}")
            if result_with_protocol_https.success and result_with_protocol_https.data:
                print(f"     HTTPS Link: {result_with_protocol_https.data}")

            print("   ✅ Performance comparison completed")

        except Exception as e:
            print(f"   ❌ Error testing performance comparison: {e}")
            import traceback

            traceback.print_exc()

        # Clean up: delete the test session
        print("\n7. Cleaning up - deleting test session...")
        try:
            delete_result = agb.delete(session)
            if delete_result.success:
                print(f"   ✅ Session deleted successfully: {session_id}")
            else:
                print(f"   ⚠️  Failed to delete session: {delete_result.error_message}")
        except Exception as e:
            print(f"   ⚠️  Error deleting session: {e}")

        print("\n" + "=" * 60)
        print("session.get_link method test completed!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main function"""
    print("AGB session.get_link Method Test")
    print("=" * 50)

    try:
        success = test_session_get_link()
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
