#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGB filesystem test code
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

        params = CreateSessionParams(
            image_id="code_latest"
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


def test_filesystem_operations(session):
    """Test filesystem operation functionality"""
    print("\n" + "=" * 60)
    print("Testing Filesystem Operation Functionality")
    print("=" * 60)

    try:
        # Test directory operations
        print("1. Testing directory operations...")

        # Create test directory
        test_dir = "/tmp/"
        print(f"\nCreating directory: {test_dir}")
        result = session.file_system.create_directory(test_dir)
        if result.success:
            print("✅ Directory created successfully!")
            print(f"   Request ID: {result.request_id}")
        else:
            print("❌ Directory creation failed!")
            print(f"   Error message: {result.error_message}")
            if result.request_id:
                print(f"   Request ID: {result.request_id}")

        # List directory contents
        print(f"\nListing directory contents: {test_dir}")
        result = session.file_system.list_directory(test_dir)
        if result.success:
            print("✅ Directory listing successful!")
            print(f"   Request ID: {result.request_id}")
            if result.entries:
                print(f"   Directory contents:")
                for entry in result.entries:
                    print(f"     - {entry.get('name', 'Unknown')} ({entry.get('type', 'Unknown')})")
            else:
                print("   Directory is empty")
        else:
            print("❌ Directory listing failed!")
            print(f"   Error message: {result.error_message}")
            if result.request_id:
                print(f"   Request ID: {result.request_id}")

        # Test file operations
        print("\n2. Testing file operations...")

        # Write file
        test_file = f"{test_dir}/test.txt"
        test_content = "Hello AGB! This is a test file.\nCreated at: " + str(os.popen('date').read().strip())

        print(f"\nWriting file: {test_file}")
        result = session.file_system.write_file(test_file, test_content, mode="overwrite")
        if result.success:
            print("✅ File written successfully!")
            print(f"   Request ID: {result.request_id}")
        else:
            print("❌ File writing failed!")
            print(f"   Error message: {result.error_message}")
            if result.request_id:
                print(f"   Request ID: {result.request_id}")

        # Read file
        print(f"\nReading file: {test_file}")
        result = session.file_system.read_file(test_file)
        if result.success:
            print("✅ File read successfully!")
            print(f"   Request ID: {result.request_id}")
            print(f"   File content:\n{result.content}")
        else:
            print("❌ File reading failed!")
            print(f"   Error message: {result.error_message}")
            if result.request_id:
                print(f"   Request ID: {result.request_id}")

        # Get file info
        print(f"\nGetting file info: {test_file}")
        result = session.file_system.get_file_info(test_file)
        if result.success:
            print("✅ File info retrieved successfully!")
            print(f"   Request ID: {result.request_id}")
            if result.file_info:
                print(f"   File info:")
                for key, value in result.file_info.items():
                    print(f"     {key}: {value}")
        else:
            print("❌ File info retrieval failed!")
            print(f"   Error message: {result.error_message}")
            if result.request_id:
                print(f"   Request ID: {result.request_id}")

        # Test file editing
        print("\n3. Testing file editing...")

        edits = [
            {"action": "append", "content": "\nThis line was appended."},
            {"action": "prepend", "content": "This line was prepended.\n"},
        ]

        print(f"\nEditing file: {test_file}")
        result = session.file_system.edit_file(test_file, edits, dry_run=False)
        if result.success:
            print("✅ File edited successfully!")
            print(f"   Request ID: {result.request_id}")

            # Re-read file to see editing results
            print(f"\nRe-reading edited file: {test_file}")
            result = session.file_system.read_file(test_file)
            if result.success:
                print("✅ Edited file read successfully!")
                print(f"   File content:\n{result.content}")
            else:
                print("❌ Edited file reading failed!")
        else:
            print("❌ File editing failed!")
            print(f"   Error message: {result.error_message}")
            if result.request_id:
                print(f"   Request ID: {result.request_id}")

        # Test file search
        print("\n4. Testing file search...")

        search_pattern = "*.txt"
        print(f"\nSearching files in {test_dir} directory for {search_pattern}")
        result = session.file_system.search_files(test_dir, search_pattern)
        if result.success:
            print("✅ File search successful!")
            print(f"   Request ID: {result.request_id}")
            if result.matches:
                print(f"   Found files:")
                for match in result.matches:
                    print(f"     - {match}")
            else:
                print("   No matching files found")
        else:
            print("❌ File search failed!")
            print(f"   Error message: {result.error_message}")
            if result.request_id:
                print(f"   Request ID: {result.request_id}")

        # Test large file operations
        print("\n5. Testing large file operations...")

        large_file = f"{test_dir}/large_file.txt"
        large_content = "This is a large file content.\n" * 1000  # Approx 30KB

        print(f"\nCreating large file: {large_file}")
        result = session.file_system.write_file(large_file, large_content)
        if result.success:
            print("✅ Large file created successfully!")
            print(f"   Request ID: {result.request_id}")

            # Read large file
            print(f"\nReading large file: {large_file}")
            result = session.file_system.read_file(large_file)
            if result.success:
                print("✅ Large file read successfully!")
                print(f"   Request ID: {result.request_id}")
                print(f"   File size: {len(result.content)} characters")
                print(f"   First 100 characters: {result.content[:100]}...")
            else:
                print("❌ Large file reading failed!")
        else:
            print("❌ Large file creation failed!")
            print(f"   Error message: {result.error_message}")
            if result.request_id:
                print(f"   Request ID: {result.request_id}")

        # Test multiple file operations
        print("\n6. Testing multiple file operations...")

        # Create multiple test files
        test_files = [
            f"{test_dir}/file1.txt",
            f"{test_dir}/file2.txt",
            f"{test_dir}/file3.txt"
        ]

        for i, file_path in enumerate(test_files):
            content = f"This is test file {i+1}\nContent: {i+1} * {i+1} = {(i+1)**2}"
            result = session.file_system.write_file(file_path, content)
            if result.success:
                print(f"✅ File {file_path} created successfully")
            else:
                print(f"❌ File {file_path} creation failed: {result.error_message}")

        # Batch read multiple files
        print(f"\nBatch reading multiple files")
        result = session.file_system.read_multiple_files(test_files)
        if result.success:
            print("✅ Multiple file reading successful!")
            print(f"   Request ID: {result.request_id}")
            if result.contents:
                print(f"   Read files:")
                for file_path, content in result.contents.items():
                    print(f"     {file_path}: {content.strip()}")
            else:
                print("   No file contents read")
        else:
            print("❌ Multiple file reading failed!")
            print(f"   Error message: {result.error_message}")
            if result.request_id:
                print(f"   Request ID: {result.request_id}")

        # Test file move
        print("\n7. Testing file move...")

        source_file = f"{test_dir}/file1.txt"
        dest_file = f"{test_dir}/moved_file.txt"

        print(f"\nMoving file: {source_file} -> {dest_file}")
        result = session.file_system.move_file(source_file, dest_file)
        if result.success:
            print("✅ File moved successfully!")
            print(f"   Request ID: {result.request_id}")

            # Verify move result
            if session.file_system.read_file(dest_file).success:
                print("✅ Destination file exists and is readable")
            else:
                print("❌ Destination file does not exist or is not readable")
        else:
            print("❌ File move failed!")
            print(f"   Error message: {result.error_message}")
            if result.request_id:
                print(f"   Request ID: {result.request_id}")

        # Clean up test files
        print("\n8. Cleaning up test files...")

        cleanup_files = [
            f"{test_dir}/test.txt",
            f"{test_dir}/file2.txt",
            f"{test_dir}/file3.txt",
            f"{test_dir}/moved_file.txt",
            f"{test_dir}/large_file.txt"
        ]

        for file_path in cleanup_files:
            try:
                # Use command to delete file (as filesystem module does not have a delete method)
                session.command.execute_command(f"rm -f {file_path}", timeout_ms=5000)
                print(f"✅ Cleaning up file: {file_path}")
            except Exception as e:
                print(f"⚠️   Failed to clean up file: {file_path}, Error: {e}")

        # Delete test directory
        try:
            session.command.execute_command(f"rmdir {test_dir}", timeout_ms=5000)
            print(f"✅ Cleaning up directory: {test_dir}")
        except Exception as e:
            print(f"⚠️   Failed to clean up directory: {test_dir}, Error: {e}")

        return True

    except Exception as e:
        print(f"❌ Error occurred during filesystem test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    print("=" * 60)
    print("AGB Filesystem Test")
    print("=" * 60)

    # Test session creation
    result, agb = test_create_session()

    if result and result.success and agb:
        # Test filesystem operation functionality
        filesystem_test_success = test_filesystem_operations(result.session)

        # Optional: Test deleting session
        print("\n" + "=" * 60)
        print("Do you want to delete the recently created session? (y/n): ", end="")
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
