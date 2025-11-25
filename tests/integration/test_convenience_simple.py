#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for AGB create and delete interfaces
"""

import os
import sys

# Add project root directory to Python path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)
print(f"Added project root to Python path: {project_root}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")  # Show first 3 entries


def get_api_key():
    """Get API Key from environment variables"""
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        raise ValueError(
            "AGB_API_KEY environment variable not set. Please set the environment variable:\n"
            "export AGB_API_KEY='your_api_key_here'"
        )
    return api_key


def test_agb_create_and_delete():
    """Test AGB create and delete interfaces"""
    print("=== Testing AGB Create and Delete Interfaces ===")

    try:
        # Get API Key
        api_key = get_api_key()
        print(f"Using API Key: {api_key[:10]}...{api_key[-4:]}")

        # Import AGB client
        from agb import AGB
        from agb.session_params import CreateSessionParams

        # Initialize AGB client
        print("\n1. Initializing AGB client...")
        agb = AGB(api_key=api_key)
        print("✅ AGB client initialized successfully")

        # Test session creation
        print("\n2. Testing session creation...")
        try:
            params = CreateSessionParams(image_id="agb-code-space-2")

            result = agb.create(params)

            if result.success:
                print("✅ Session created successfully")
                session = result.session
                print(f"   Session ID: {session.session_id}")
                print(f"   Request ID: {result.request_id}")

                # Test session info
                print("\n3. Testing session info...")
                try:
                    info_result = session.info()
                    if info_result.success:
                        print("✅ Session info retrieved successfully")
                        if info_result.data:
                            session_data = info_result.data
                            print(
                                f"   Session ID: {session_data.get('session_id', 'N/A')}"
                            )
                            print(
                                f"   Resource URL: {session_data.get('resource_url', 'N/A')}"
                            )
                    else:
                        print(
                            f"⚠️ Failed to get session info: {info_result.error_message}"
                        )
                except Exception as e:
                    print(f"⚠️ Error getting session info: {e}")

                # Test session listing
                print("\n4. Testing session listing...")
                try:
                    sessions = agb.list()
                    print(f"✅ Found {len(sessions)} sessions in local cache")
                    for i, session in enumerate(sessions):
                        print(f"   Session {i+1}: {session.session_id}")
                except Exception as e:
                    print(f"⚠️ Error listing sessions: {e}")

                # Test session deletion
                print("\n5. Testing session deletion...")
                try:
                    # Ensure session is not None and is of correct type before deletion
                    if session is not None:
                        from agb.session import Session  # Ensure correct import
                        if not isinstance(session, Session):
                            session = Session(**session.__dict__)
                        delete_result = agb.delete(session)
                    else:
                        raise ValueError("Session is None, cannot delete.")

                    if delete_result.success:
                        print("✅ Session deleted successfully")
                        print(f"   Request ID: {delete_result.request_id}")
                    else:
                        print(
                            f"❌ Failed to delete session: {delete_result.error_message}"
                        )
                        print(f"   Request ID: {delete_result.request_id}")

                except Exception as e:
                    print(f"❌ Error deleting session: {e}")
                    import traceback

                    traceback.print_exc()

            else:
                print(f"❌ Session creation failed: {result.error_message}")
                print(f"   Request ID: {result.request_id}")

        except Exception as e:
            print(f"❌ Error creating session: {e}")
            import traceback

            traceback.print_exc()

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


def test_agb_with_custom_params():
    """Test AGB create with custom parameters"""
    print("\n=== Testing AGB Create with Custom Parameters ===")

    try:
        # Get API Key
        api_key = get_api_key()

        # Import AGB client and session params
        from agb import AGB
        from agb.session_params import CreateSessionParams

        # Initialize AGB client
        print("\n1. Initializing AGB client...")
        agb = AGB(api_key=api_key)
        print("✅ AGB client initialized successfully")

        # Create session with custom parameters
        print("\n2. Testing session creation with custom parameters...")
        try:
            params = CreateSessionParams(image_id="agb-code-space-2")

            result = agb.create(params)

            if result.success:
                print("✅ Custom session created successfully")
                session = result.session
                print(f"   Session ID: {session.session_id}")
                print(f"   Request ID: {result.request_id}")
                print(f"   Image ID: {session.image_id}")

                # Delete the custom session
                print("\n3. Deleting custom session...")
                delete_result = agb.delete(session)

                if delete_result.success:
                    print("✅ Custom session deleted successfully")
                    print(f"   Request ID: {delete_result.request_id}")
                else:
                    print(
                        f"❌ Failed to delete custom session: {delete_result.error_message}"
                    )

            else:
                print(f"❌ Custom session creation failed: {result.error_message}")

        except Exception as e:
            print(f"❌ Error creating custom session: {e}")
            import traceback

            traceback.print_exc()

    except Exception as e:
        print(f"❌ Custom parameters test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Run basic create and delete test
    test_agb_create_and_delete()

    # Run custom parameters test
    test_agb_with_custom_params()

    print("\n=== Test Summary ===")
    print("All tests completed. Check the output above for results.")
