#!/usr/bin/env python3
"""
File Archive Mode Demo

This example demonstrates how to use Archive upload mode for context synchronization.
It shows how to create files that will be automatically compressed into zip format
when uploaded to the context storage, and how to verify the archive behavior.
"""

import os
import time
import asyncio

from agb import AGB, ContextSync, SyncPolicy, UploadPolicy
from agb.context_sync import UploadMode
from agb.session_params import CreateSessionParams


async def demo_archive_mode(agb, context):
    """Demo Archive upload mode - files are automatically compressed into ZIP format."""
    print("\n🗜️ Archive Mode Demo")
    print("=" * 40)

    session = None

    try:
        # Configure Archive upload policy
        upload_policy = UploadPolicy(upload_mode=UploadMode.ARCHIVE)
        sync_policy = SyncPolicy(upload_policy=upload_policy)

        session_params = CreateSessionParams(image_id="agb-code-space-1")

        # Configure context synchronization with Archive mode
        sync_path = "/tmp/archive-mode-test"
        context_sync = ContextSync.new(context.id, sync_path, sync_policy)
        session_params.context_syncs = [context_sync]

        print("Creating session with Archive upload mode...")
        session_result = agb.create(session_params)
        if not session_result.success or not session_result.session:
            print("❌ Failed to create session")
            return False

        session = session_result.session
        print(f"✅ Session created: {session.session_id}")
        print(f"📦 Upload mode: {sync_policy.upload_policy.upload_mode.value}")

        # Wait for session to be ready
        print("⏳ Waiting for session to be ready...")
        await asyncio.sleep(5)

        # Create directory
        print(f"📁 Creating directory: {sync_path}")
        dir_result = session.file_system.create_directory(sync_path)
        if not dir_result.success:
            print(f"❌ Failed to create directory: {dir_result.error_message}")
            return False

        # Create test files
        print("📝 Creating test files...")

        # File : 5KB content
        content_size = 5 * 1024  # 5KB
        base_content = "Archive mode test successful! This is a test file created in the session path. "
        repeated_content = base_content * (content_size // len(base_content) + 1)
        file_content = repeated_content[:content_size]

        file_path = f"{sync_path}/archive-test-file-5kb.txt"
        print(f"Creating file: {file_path}")
        print(f"File content size: {len(file_content)} bytes")

        write_result = session.file_system.write_file(
            file_path, file_content, "overwrite"
        )
        if not write_result.success:
            print(f"❌ Failed to write file: {write_result.error_message}")
            return False

        print(f"✅ File write successful!")

        # Sync context data
        print("🔄 Syncing context data...")
        sync_result = await session.context.sync()
        if not sync_result.success:
            print(f"❌ Context sync failed")
            return False

        print("✅ Context sync completed")

        # List and verify files
        print("📋 Listing files in context sync directory...")

        list_result = agb.context.list_files(
            context.id, sync_path, page_number=1, page_size=10
        )

        if not list_result.success:
            print(
                f"❌ Failed to list files: {getattr(list_result, 'error_message', 'Unknown error')}"
            )
            return False

        print(
            f"✅ List files successful! Total files found: {len(list_result.entries)}"
        )

        if list_result.entries:
            print("Files in Archive mode:")
            for index, entry in enumerate(list_result.entries):
                print(f"  [{index}] FilePath: {entry.file_path}")
                print(f"      FileType: {entry.file_type}")
                print(f"      FileName: {entry.file_name}")

                # Verify that file name contains .zip extension for archive mode
                if entry.file_name.lower().endswith(".zip"):
                    print(f"      ✅ File correctly archived as ZIP format")
                else:
                    print(
                        f"      ⚠️ Unexpected file format: {entry.file_name} (expected: .zip extension)"
                    )

        print("🎉 Archive Mode demo completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Archive Mode demo failed with error: {e}")
        return False

    finally:
        # Cleanup session
        if session:
            try:
                agb.delete(session, sync_context=True)
                print("✅ Archive mode session deleted")
            except Exception as e:
                print(f"⚠️ Failed to delete archive mode session: {e}")


async def demo_file_mode(agb, context):
    """Demo File upload mode - files are uploaded in their original format."""
    print("\n📄 File Mode Demo")
    print("=" * 40)

    session = None

    try:
        # Configure File upload policy (default mode)
        upload_policy = UploadPolicy(upload_mode=UploadMode.FILE)
        sync_policy = SyncPolicy(upload_policy=upload_policy)

        session_params = CreateSessionParams(image_id="agb-code-space-1")

        # Configure context synchronization with File mode
        sync_path = "/tmp/file-mode-test"
        context_sync = ContextSync.new(context.id, sync_path, sync_policy)
        session_params.context_syncs = [context_sync]

        print("Creating session with File upload mode...")
        session_result = agb.create(session_params)
        if not session_result.success or not session_result.session:
            print("❌ Failed to create session")
            return False

        session = session_result.session
        print(f"✅ Session created: {session.session_id}")
        print(f"📦 Upload mode: {sync_policy.upload_policy.upload_mode.value}")

        # Wait for session to be ready
        print("⏳ Waiting for session to be ready...")
        await asyncio.sleep(5)

        # Create directory
        print(f"📁 Creating directory: {sync_path}")
        dir_result = session.file_system.create_directory(sync_path)
        if not dir_result.success:
            print(f"❌ Failed to create directory: {dir_result.error_message}")
            return False

        # Create test files
        print("📝 Creating test files...")

        # File 1: Text file
        text_content = "File mode test successful! This file is uploaded in its original format without compression."
        text_path = f"{sync_path}/file-mode-test.txt"
        print(f"Creating text file: {text_path}")

        write_result = session.file_system.write_file(
            text_path, text_content, "overwrite"
        )
        if not write_result.success:
            print(f"❌ Failed to write text file: {write_result.error_message}")
            return False

        print(f"✅ Text file write successful!")

        # Sync context data
        print("🔄 Syncing context data...")
        sync_result = await session.context.sync()
        if not sync_result.success:
            print(f"❌ Context sync failed")
            return False

        print("✅ Context sync completed")

        # List and verify files
        print("📋 Listing files in context sync directory...")

        list_result = agb.context.list_files(
            context.id, sync_path, page_number=1, page_size=10
        )

        if not list_result.success:
            print(
                f"❌ Failed to list files: {getattr(list_result, 'error_message', 'Unknown error')}"
            )
            return False

        print(
            f"✅ List files successful! Total files found: {len(list_result.entries)}"
        )

        if list_result.entries:
            print("Files in File mode:")
            for index, entry in enumerate(list_result.entries):
                print(f"  [{index}] FilePath: {entry.file_path}")
                print(f"      FileType: {entry.file_type}")
                print(f"      FileName: {entry.file_name}")

                # Verify that file name is not compressed (not .zip) for file mode
                if not entry.file_name.lower().endswith(".zip"):
                    print(
                        f"      ✅ File preserved in original format: {entry.file_name}"
                    )
                else:
                    print(
                        f"      ⚠️ Unexpected compression: {entry.file_name} (should not be .zip in File mode)"
                    )

        print("🎉 File Mode demo completed successfully!")
        return True

    except Exception as e:
        print(f"❌ File Mode demo failed with error: {e}")
        return False

    finally:
        # Cleanup session
        if session:
            try:
                agb.delete(session, sync_context=True)
                print("✅ File mode session deleted")
            except Exception as e:
                print(f"⚠️ Failed to delete file mode session: {e}")


async def main():
    """Main demo function - runs both Archive and File mode demonstrations."""
    # Initialize the AGB client
    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        api_key = "akm-xxx"  # Replace with your actual API key

    agb = AGB(api_key=api_key)
    context = None

    try:
        print("🚀 Upload Mode Comparison Demo")
        print("=" * 50)

        # Step 1: Create a context
        print("\n1️⃣ Creating a context...")
        context_name = f"upload-mode-demo-{int(time.time())}"
        context_result = agb.context.get(context_name, create=True)

        if not context_result.success or not context_result.context:
            print("❌ Failed to create context")
            return

        context = context_result.context
        print(f"✅ Context created: {context.name} (ID: {context.id})")

        # Step 2: Run Archive Mode Demo
        print("\n" + "=" * 60)
        archive_success = await demo_archive_mode(agb, context)

        # Step 3: Run File Mode Demo
        print("\n" + "=" * 60)
        file_success = await demo_file_mode(agb, context)

        # Step 4: Summary
        print("\n" + "=" * 60)
        print("📊 Demo Summary")
        print("=" * 20)
        print(f"Archive Mode: {'✅ Success' if archive_success else '❌ Failed'}")
        print(f"File Mode: {'✅ Success' if file_success else '❌ Failed'}")

        if archive_success and file_success:
            print("\n🎉 Both upload mode demos completed successfully!")
            print("\n📝 Key Differences:")
            print("- Archive Mode: Files are automatically compressed into ZIP format")
            print("- File Mode: Files are uploaded in their original format")
            print("- Archive Mode: Better for storage efficiency and batch operations")
            print(
                "- File Mode: Better for individual file access and format preservation"
            )
        else:
            print("\n⚠️ Some demos failed. Please check the logs above.")

    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Cleanup context
        print("\n🧹 Final cleanup...")
        if context:
            try:
                agb.context.delete(context)
                print("✅ Context deleted")
            except Exception as e:
                print(f"⚠️ Failed to delete context: {e}")


if __name__ == "__main__":
    asyncio.run(main())
