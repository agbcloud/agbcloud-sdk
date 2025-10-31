#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test code for session labels functionality - setLabels method
"""

import os
import sys
import time
import random

# Add project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

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

def generate_unique_id():
    """Create a unique identifier for test labels to avoid conflicts with existing data"""
    timestamp = int(time.time() * 1000000)
    random_part = random.randint(0, 10000)
    return f"{timestamp}-{random_part}"

def test_session_set_labels():
    """Test session.set_labels method"""

    # API key
    api_key = get_api_key()
    print(f"Using API Key: {api_key[:10]}...{api_key[-4:]}")

    try:
        print("Initializing AGB client...")

        # Create AGB instance
        agb = AGB(api_key=api_key)
        print(f"✅ AGB client initialized successfully")

        print("\n" + "=" * 60)
        print("Testing session.set_labels method...")
        print("=" * 60)

        # Generate a unique identifier for this test run
        unique_id = generate_unique_id()
        print(f"Using unique ID for test labels: {unique_id}")

        # Create a session to test set_labels method
        print("\n0. Creating a test session...")
        try:
            print("\nCreating session...")

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
        time.sleep(5)

        # Test 1: Basic set_labels call with valid labels
        print("\n1. Testing basic set_labels call with valid labels:")
        try:
            test_labels = {
                "environment": f"testing-{unique_id}",
                "owner": f"test-team-{unique_id}",
                "project": f"labels-test-{unique_id}",
                "version": "1.0.0",
            }

            print(f"   Setting labels: {test_labels}")
            set_result = session.set_labels(test_labels)

            print(f"   ✅ session.set_labels() call completed!")
            print(f"   Result type: {type(set_result)}")
            print(f"   Success: {set_result.success}")
            print(f"   Request ID: {set_result.request_id}")

            if set_result.success:
                print("   ✅ Labels set successfully")
            else:
                print(f"   ❌ Failed to set labels: {set_result.error_message}")

        except Exception as e:
            print(f"   ❌ Error testing set_labels: {e}")
            import traceback
            traceback.print_exc()

        # Test 2: Test set_labels with updated labels
        print("\n2. Testing set_labels with updated labels:")
        try:
            updated_labels = {
                "environment": f"staging-{unique_id}",
                "owner": f"test-team-{unique_id}",
                "project": f"labels-test-updated-{unique_id}",
                "status": "active",
            }

            print(f"   Setting updated labels: {updated_labels}")
            update_result = session.set_labels(updated_labels)

            print(f"   ✅ session.set_labels() update call completed!")
            print(f"   Success: {update_result.success}")
            print(f"   Request ID: {update_result.request_id}")

            if update_result.success:
                print("   ✅ Labels updated successfully")
            else:
                print(f"   ❌ Failed to update labels: {update_result.error_message}")

        except Exception as e:
            print(f"   ❌ Error testing set_labels update: {e}")
            import traceback
            traceback.print_exc()

        # Test 3: Test set_labels error handling - empty labels
        print("\n3. Testing set_labels error handling - empty labels:")
        try:
            empty_labels = {}

            print("   Setting empty labels (should fail)...")
            empty_result = session.set_labels(empty_labels)

            print(f"   Result received (expected to fail)")
            print(f"   Success: {empty_result.success}")
            print(f"   Request ID: {empty_result.request_id}")

            if not empty_result.success:
                print("   ✅ Error handling working correctly for empty labels")
                print(f"   Error message: {empty_result.error_message}")
            else:
                print("   ⚠️  Unexpected success with empty labels")

        except Exception as e:
            print(f"   ❌ Error testing empty labels: {e}")
            import traceback
            traceback.print_exc()

        # Test 4: Test set_labels error handling - None labels
        print("\n4. Testing set_labels error handling - None labels:")
        try:
            print("   Setting None labels (should fail)...")
            none_result = session.set_labels(None)

            print(f"   Result received (expected to fail)")
            print(f"   Success: {none_result.success}")
            print(f"   Request ID: {none_result.request_id}")

            if not none_result.success:
                print("   ✅ Error handling working correctly for None labels")
                print(f"   Error message: {none_result.error_message}")
            else:
                print("   ⚠️  Unexpected success with None labels")

        except Exception as e:
            print(f"   ❌ Error testing None labels: {e}")
            import traceback
            traceback.print_exc()

        # Test 5: Test set_labels error handling - invalid label values
        print("\n5. Testing set_labels error handling - invalid label values:")
        try:
            invalid_labels = {
                "environment": f"testing-{unique_id}",
                "owner": "",  # Empty value should fail
                "project": f"labels-test-{unique_id}",
            }

            print(f"   Setting labels with empty value: {invalid_labels}")
            invalid_result = session.set_labels(invalid_labels)

            print(f"   Result received (expected to fail)")
            print(f"   Success: {invalid_result.success}")
            print(f"   Request ID: {invalid_result.request_id}")

            if not invalid_result.success:
                print("   ✅ Error handling working correctly for invalid label values")
                print(f"   Error message: {invalid_result.error_message}")
            else:
                print("   ⚠️  Unexpected success with invalid label values")

        except Exception as e:
            print(f"   ❌ Error testing invalid label values: {e}")
            import traceback
            traceback.print_exc()

        # Test 6: Test set_labels multiple times
        print("\n6. Testing set_labels multiple times:")
        try:
            print("   Calling session.set_labels() multiple times...")

            for i in range(3):
                print(f"     Call {i+1}:")
                test_labels_multi = {
                    "environment": f"multi-test-{unique_id}",
                    "iteration": str(i+1),
                    "timestamp": str(int(time.time())),
                }

                result = session.set_labels(test_labels_multi)
                print(f"       Success: {result.success}")
                print(f"       Request ID: {result.request_id}")

                if not result.success:
                    print(f"       Error: {result.error_message}")

                if i < 2:  # Don't sleep after last call
                    time.sleep(2)

            print("   ✅ Multiple calls completed successfully")

        except Exception as e:
            print(f"   ❌ Error testing multiple calls: {e}")
            import traceback
            traceback.print_exc()

        # Test 7: Test set_labels with different session object
        print("\n7. Testing set_labels with different session object:")
        try:
            # Create a new session object using the same session_id
            from agb.session import Session

            new_session = Session(agb, session_id)

            print("   Created new session object with same session_id")
            print(f"   New session ID: {new_session.get_session_id()}")

            # Set labels on the new session object
            new_session_labels = {
                "environment": f"new-session-{unique_id}",
                "test": "different-session-object",
            }

            print(f"   Setting labels on new session object: {new_session_labels}")
            new_session_result = new_session.set_labels(new_session_labels)

            print(f"   ✅ New session.set_labels() call completed!")
            print(f"   Success: {new_session_result.success}")
            print(f"   Request ID: {new_session_result.request_id}")

            if new_session_result.success:
                print("   ✅ New session object can also set labels")
            else:
                print(f"   ❌ New session object failed: {new_session_result.error_message}")

        except Exception as e:
            print(f"   ❌ Error testing new session object: {e}")
            import traceback
            traceback.print_exc()

        # Clean up: delete the test session
        print("\n8. Cleaning up - deleting test session...")
        try:
            delete_result = agb.delete(session)
            if delete_result.success:
                print(f"   ✅ Session deleted successfully: {session_id}")
            else:
                print(f"   ⚠️  Failed to delete session: {delete_result.error_message}")
        except Exception as e:
            print(f"   ⚠️  Error deleting session: {e}")

        # Test 8: Test get_labels method
        print("\n8. Testing get_labels method:")
        try:
            # First set some known labels
            known_labels = {
                "environment": f"get-test-{unique_id}",
                "owner": f"test-team-{unique_id}",
                "project": f"get-labels-test-{unique_id}",
                "version": "2.0.0",
            }

            print(f"   Setting known labels for get_labels test: {known_labels}")
            set_result = session.set_labels(known_labels)

            if set_result.success:
                print("   ✅ Labels set successfully for get_labels test")

                # Wait a moment for labels to be persisted
                time.sleep(2)

                # Now test get_labels
                print("   Getting labels using get_labels()...")
                get_result = session.get_labels()

                print(f"   ✅ session.get_labels() call completed!")
                print(f"   Result type: {type(get_result)}")
                print(f"   Success: {get_result.success}")
                print(f"   Request ID: {get_result.request_id}")

                if get_result.success:
                    retrieved_labels = get_result.data
                    print(f"   Retrieved labels: {retrieved_labels}")

                    # Verify that all expected labels are present with correct values
                    labels_match = True
                    for key, expected_value in known_labels.items():
                        if key not in retrieved_labels:
                            print(f"   ❌ Expected label '{key}' not found in retrieved labels")
                            labels_match = False
                        elif retrieved_labels[key] != expected_value:
                            print(f"   ❌ Label '{key}' value mismatch: expected '{expected_value}', got '{retrieved_labels[key]}'")
                            labels_match = False
                        else:
                            print(f"   ✅ Label '{key}': {retrieved_labels[key]} (matches)")

                    if labels_match:
                        print("   ✅ All labels retrieved successfully and match expected values")
                    else:
                        print("   ❌ Some labels don't match expected values")
                else:
                    print(f"   ❌ Failed to get labels: {get_result.error_message}")
            else:
                print(f"   ❌ Failed to set labels for get_labels test: {set_result.error_message}")

        except Exception as e:
            print(f"   ❌ Error testing get_labels: {e}")
            import traceback
            traceback.print_exc()

        # Test 9: Test get_labels after label updates
        print("\n9. Testing get_labels after label updates:")
        try:
            # Update labels
            updated_labels = {
                "environment": f"updated-get-test-{unique_id}",
                "owner": f"updated-team-{unique_id}",
                "project": f"updated-get-labels-test-{unique_id}",
                "status": "active",
                "new_field": "added"
            }

            print(f"   Updating labels: {updated_labels}")
            update_result = session.set_labels(updated_labels)

            if update_result.success:
                print("   ✅ Labels updated successfully")

                # Wait a moment for updates to be persisted
                time.sleep(2)

                # Get updated labels
                print("   Getting updated labels...")
                get_updated_result = session.get_labels()

                if get_updated_result.success:
                    retrieved_updated_labels = get_updated_result.data
                    print(f"   Retrieved updated labels: {retrieved_updated_labels}")

                    # Verify updated labels
                    updates_match = True
                    for key, expected_value in updated_labels.items():
                        if key not in retrieved_updated_labels:
                            print(f"   ❌ Expected updated label '{key}' not found")
                            updates_match = False
                        elif retrieved_updated_labels[key] != expected_value:
                            print(f"   ❌ Updated label '{key}' value mismatch: expected '{expected_value}', got '{retrieved_updated_labels[key]}'")
                            updates_match = False
                        else:
                            print(f"   ✅ Updated label '{key}': {retrieved_updated_labels[key]} (matches)")

                    # Verify that old labels that were removed are no longer present
                    if "version" in retrieved_updated_labels:
                        print("   ❌ Removed label 'version' still present in updated labels")
                        updates_match = False
                    else:
                        print("   ✅ Removed label 'version' no longer present (correct)")

                    if updates_match:
                        print("   ✅ All updated labels retrieved successfully and match expected values")
                    else:
                        print("   ❌ Some updated labels don't match expected values")
                else:
                    print(f"   ❌ Failed to get updated labels: {get_updated_result.error_message}")
            else:
                print(f"   ❌ Failed to update labels: {update_result.error_message}")

        except Exception as e:
            print(f"   ❌ Error testing get_labels after updates: {e}")
            import traceback
            traceback.print_exc()

        # Test 10: Test get_labels with empty labels
        print("\n10. Testing get_labels with empty labels:")
        try:
            # Set empty labels (this should fail, but let's test get_labels behavior)
            print("   Testing get_labels when no labels are set...")

            # First, try to clear labels by setting empty dict (this might fail)
            empty_labels = {}
            clear_result = session.set_labels(empty_labels)

            if not clear_result.success:
                print(f"   Expected: Setting empty labels failed: {clear_result.error_message}")

                # Since we can't clear labels, get_labels should still return the last set labels
                print("   Getting labels when empty labels couldn't be set...")
                get_empty_result = session.get_labels()

                if get_empty_result.success:
                    print(f"   ✅ get_labels() succeeded even when empty labels couldn't be set")
                    print(f"   Retrieved labels: {get_empty_result.data}")
                    print("   This is expected behavior - previous labels remain")
                else:
                    print(f"   ❌ get_labels() failed: {get_empty_result.error_message}")
            else:
                print("   Unexpected: Empty labels were set successfully")

                # If empty labels were somehow set, test get_labels
                get_empty_result = session.get_labels()
                if get_empty_result.success:
                    print(f"   Retrieved labels after clearing: {get_empty_result.data}")
                else:
                    print(f"   ❌ get_labels() failed after clearing: {get_empty_result.error_message}")

        except Exception as e:
            print(f"   ❌ Error testing get_labels with empty labels: {e}")
            import traceback
            traceback.print_exc()

        # Test 11: Test get_labels multiple times
        print("\n11. Testing get_labels multiple times:")
        try:
            print("   Calling session.get_labels() multiple times...")

            for i in range(3):
                print(f"     Call {i+1}:")
                result = session.get_labels()
                print(f"       Success: {result.success}")
                print(f"       Request ID: {result.request_id}")

                if result.success:
                    print(f"       Labels count: {len(result.data) if result.data else 0}")
                else:
                    print(f"       Error: {result.error_message}")

                if i < 2:  # Don't sleep after last call
                    time.sleep(1)

            print("   ✅ Multiple get_labels calls completed")

        except Exception as e:
            print(f"   ❌ Error testing multiple get_labels calls: {e}")
            import traceback
            traceback.print_exc()

        # Clean up: delete the test session
        print("\n12. Cleaning up - deleting test session...")
        try:
            delete_result = agb.delete(session)
            if delete_result.success:
                print(f"   ✅ Session deleted successfully: {session_id}")
            else:
                print(f"   ⚠️  Failed to delete session: {delete_result.error_message}")
        except Exception as e:
            print(f"   ⚠️  Error deleting session: {e}")

        print("\n" + "=" * 60)
        print("session.set_labels and get_labels methods test completed!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("AGB session.set_labels Method Test")
    print("=" * 50)

    try:
        success = test_session_set_labels()
        if success:
            print("\n✅ All setLabels tests completed successfully!")
        else:
            print("\n❌ Some setLabels tests failed!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()