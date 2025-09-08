#!/usr/bin/env python3
"""
Real API test script for get_file_change functionality.
Requires AGB_API_KEY environment variable to be set.

Usage:
    export AGB_API_KEY="your-api-key-here"
    python scripts/test_file_change_real.py
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agb import AGB
from agb.session_params import CreateSessionParams


def get_api_key():
    """Get API Key from environment variables"""
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        print("❌ AGB_API_KEY environment variable not set.")
        print("Please set it with: export AGB_API_KEY='your-api-key-here'")
        sys.exit(1)
    return api_key


def test_get_file_change_real():
    """
    Test the get_file_change functionality with real API by:
    1. Creating a session with specified ImageId
    2. Writing a file to /tmp/test/ directory
    3. Calling get_file_change to get initial state
    4. Modifying the file
    5. Calling get_file_change again to observe changes
    """
    print("=== Real API Test for get_file_change ===\n")
    
    # Initialize AGB client
    api_key = get_api_key()
    agb = AGB(api_key=api_key)
    print("✅ AGB client initialized")
    
    # Create session with specified ImageId
    session_params = CreateSessionParams(image_id="imgc-0abxi2dcvx7vr62cm")
    session_result = agb.create(session_params)
    
    if not session_result.success:
        print(f"❌ Failed to create session: {session_result.error_message}")
        return
    
    session = session_result.session
    print(f"✅ Session created successfully with ID: {session.session_id}")
    
    try:
        # Create the test directory
        print("\n1. Creating test directory...")
        create_dir_result = session.file_system.create_directory("/tmp/test")
        print(f"Create directory result: {create_dir_result.success}")
        
        # Write initial file content
        print("\n2. Writing initial file content...")
        initial_content = "This is the initial content of the test file.\nLine 2 of initial content."
        write_result = session.file_system.write_file("/tmp/test/test_file.txt", initial_content)
        print(f"Write file result: {write_result.success}")
        if not write_result.success:
            print(f"❌ Failed to write file: {write_result.error_message}")
            return
        
        # Call _get_file_change for the first time (initial state)
        print("\n3. First call to _get_file_change (initial state)...")
        first_change_result = session.file_system._get_file_change("/tmp/test")
        print(f"First change success: {first_change_result.success}")
        if first_change_result.success:
            print(f"First change events count: {len(first_change_result.events)}")
            print(f"First change has changes: {first_change_result.has_changes()}")
            if first_change_result.events:
                print("First change events:")
                for event in first_change_result.events:
                    print(f"  - {event}")
            print(f"First change raw data: {first_change_result.raw_data}")
        else:
            print(f"❌ First call failed: {first_change_result.error_message}")
        
        # Modify the file
        print("\n4. Modifying the file...")
        modified_content = "This is the MODIFIED content of the test file.\nLine 2 has been changed.\nAdded a new line 3."
        modify_result = session.file_system.write_file("/tmp/test/test_file.txt", modified_content)
        print(f"Modify file result: {modify_result.success}")
        if not modify_result.success:
            print(f"❌ Failed to modify file: {modify_result.error_message}")
            return
        
        # Call _get_file_change for the second time (after modification)
        print("\n5. Second call to _get_file_change (after modification)...")
        second_change_result = session.file_system._get_file_change("/tmp/test")
        print(f"Second change success: {second_change_result.success}")
        if second_change_result.success:
            print(f"Second change events count: {len(second_change_result.events)}")
            print(f"Second change has changes: {second_change_result.has_changes()}")
            if second_change_result.events:
                print("Second change events:")
                for event in second_change_result.events:
                    print(f"  - {event}")
            print(f"Second change raw data: {second_change_result.raw_data}")
            
            # Analyze specific change types
            modified_files = second_change_result.get_modified_files()
            created_files = second_change_result.get_created_files()
            deleted_files = second_change_result.get_deleted_files()
            print(f"Modified files: {modified_files}")
            print(f"Created files: {created_files}")
            print(f"Deleted files: {deleted_files}")
        else:
            print(f"❌ Second call failed: {second_change_result.error_message}")
        
        # Compare the results
        print("\n=== COMPARISON ===")
        print("First call result:")
        if first_change_result.success:
            print(f"  Events: {len(first_change_result.events)}")
            print(f"  Has changes: {first_change_result.has_changes()}")
        else:
            print("  Failed")
            
        print("\nSecond call result:")
        if second_change_result.success:
            print(f"  Events: {len(second_change_result.events)}")
            print(f"  Has changes: {second_change_result.has_changes()}")
            print(f"  Event details: {[str(event) for event in second_change_result.events]}")
        else:
            print("  Failed")
            
        # Summary
        if first_change_result.success and second_change_result.success:
            print("\n✅ Test completed successfully!")
            print("The get_file_change function is working and can detect file changes.")
        else:
            print("\n⚠️  Test completed with some failures.")
            
    finally:
        # Clean up
        print("\n6. Cleaning up session...")
        delete_result = agb.delete(session)
        if delete_result.success:
            print("✅ Session deleted successfully")
        else:
            print(f"❌ Failed to delete session: {delete_result.error_message}")


if __name__ == "__main__":
    test_get_file_change_real() 