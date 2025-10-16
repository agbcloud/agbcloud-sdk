#!/usr/bin/env python3
"""
Context Synchronization Demo

This example demonstrates how to use context synchronization for data persistence
across sessions. It shows how to create a context, sync it with a session,
perform operations, and then verify data persistence in a new session.
"""

import os
import time
import asyncio

from agb import AGB, ContextSync, SyncPolicy
from agb.session_params import CreateSessionParams


async def main():
    """Main demo function."""
    # Initialize the AGB client
    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        api_key = "akm-xxx"  # Replace with your actual API key

    agb = AGB(api_key=api_key)
    context = None
    session1 = None
    session2 = None

    try:
        print("🚀 Context Synchronization Demo")
        print("=" * 50)

        # Step 1: Create a context
        print("\n1️⃣ Creating a context...")
        context_name = f"demo-context-{int(time.time())}"
        context_result = agb.context.get(context_name, create=True)

        if not context_result.success or not context_result.context:
            print("❌ Failed to create context")
            return

        context = context_result.context
        print(f"✅ Context created: {context.name} (ID: {context.id})")

        # Step 2: Create first session with context sync
        print("\n2️⃣ Creating first session with context sync...")
        session_params = CreateSessionParams(
            image_id="agb-code-space-1"
        )

        # Configure context synchronization
        sync_path = "/home/wuying/demo-data"
        context_sync = ContextSync.new(
            context.id,
            sync_path,
            SyncPolicy()
        )
        session_params.context_syncs = [context_sync]

        session_result = agb.create(session_params)
        if not session_result.success or not session_result.session:
            print("❌ Failed to create first session")
            return

        session1 = session_result.session
        print(f"✅ First session created: {session1.session_id}")

        # Step 3: Perform operations in first session
        print("\n3️⃣ Performing operations in first session...")

        # Wait for session to be ready
        print("⏳ Waiting for session to be ready...")
        await asyncio.sleep(5)

        # Create some test data
        test_file_path = f"{sync_path}/test_data.txt"
        test_content = f"Hello from session 1! Created at {time.time()}"

        # Create directory and file
        print(f"📁 Creating directory: {sync_path}")
        dir_result = session1.file_system.create_directory(sync_path)
        if not dir_result.success:
            print(f"❌ Failed to create directory: {dir_result.error_message}")
            return

        print(f"📝 Creating test file: {test_file_path}")
        file_result = session1.file_system.write_file(test_file_path, test_content)
        if not file_result.success:
            print(f"❌ Failed to create file: {file_result.error_message}")
            return

        print("✅ Test data created successfully")

        # Step 4: Sync context data
        print("\n4️⃣ Syncing context data...")
        sync_result = await session1.context.sync()
        if not sync_result.success:
            print(f"❌ Context sync failed")
            return

        print("✅ Context sync completed")

        # Step 5: Release first session
        print("\n5️⃣ Releasing first session...")
        delete_result = agb.delete(session1, sync_context=True)
        if not delete_result.success:
            print(f"❌ Failed to delete first session: {delete_result.error_message}")
            return

        print("✅ First session released with context sync")
        session1 = None

        # Step 6: Create second session with same context
        print("\n6️⃣ Creating second session with same context...")
        session_params2 = CreateSessionParams(
            image_id="agb-code-space-1"
        )

        # Use the same context sync configuration
        context_sync2 = ContextSync.new(
            context.id,
            sync_path,
            SyncPolicy()
        )
        session_params2.context_syncs = [context_sync2]

        session_result2 = agb.create(session_params2)
        if not session_result2.success or not session_result2.session:
            print("❌ Failed to create second session")
            return

        session2 = session_result2.session
        print(f"✅ Second session created: {session2.session_id}")

        # Step 7: Verify data persistence
        print("\n7️⃣ Verifying data persistence...")

        # Wait for session to be ready and context to sync
        print("⏳ Waiting for context sync to complete...")
        await asyncio.sleep(10)

        # Read the file content
        read_result = session2.file_system.read_file(test_file_path)
        if read_result.success:
            print(f"📄 File content: {read_result.content}")
        else:
            print(f"❌ Failed to read file: {read_result.error_message}")

        # Step 8: Create additional data in second session
        print("\n8️⃣ Creating additional data in second session...")
        additional_file = f"{sync_path}/session2_data.txt"
        additional_content = f"Hello from session 2! Created at {time.time()}"

        file_result2 = session2.file_system.write_file(additional_file, additional_content)
        if not file_result2.success:
            print(f"❌ Failed to create additional file: {file_result2.error_message}")
        else:
            print("✅ Additional data created in second session")

        # Step 9: Final context sync
        print("\n9️⃣ Performing final context sync...")
        final_sync_result = await session2.context.sync()
        if not final_sync_result.success:
            print(f"❌ Final context sync failed")
        else:
            print("✅ Final context sync completed")

        print("\n🎉 Context synchronization demo completed successfully!")

    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")

        if session2:
            try:
                agb.delete(session2)
                print("✅ Second session deleted")
            except Exception as e:
                print(f"⚠️ Failed to delete second session: {e}")

        if session1:
            try:
                agb.delete(session1)
                print("✅ First session deleted")
            except Exception as e:
                print(f"⚠️ Failed to delete first session: {e}")

        if context:
            try:
                agb.context.delete(context)
                print("✅ Context deleted")
            except Exception as e:
                print(f"⚠️ Failed to delete context: {e}")


if __name__ == "__main__":
    asyncio.run(main())
