"""
This example demonstrates how to pause and resume sessions in AGB.

Session pause/resume is useful for:
- Cost optimization: Pause sessions during idle periods to save resources
- Resource management: Free up resources temporarily for other tasks
- Long-running workflows: Pause sessions overnight and resume the next day
- Scheduled maintenance: Pause sessions before maintenance windows
"""

import os
import time
import asyncio

from agb import AGB
from agb.session_params import CreateSessionParams


def basic_pause_resume_example() -> None:
    """Demonstrate basic pause and resume operations."""
    print("\n" + "="*60)
    print("Example 1: Basic Pause and Resume")
    print("="*60)

    # Initialize the AGB client
    api_key = os.environ.get("AGB_API_KEY", "")
    agb = AGB(api_key=api_key)

    # Create a session
    params = CreateSessionParams(
        image_id="agb-linux-test-5",
        labels={"purpose": "pause-resume-demo", "environment": "example"}
    )
    result = agb.create(params)

    if not result.success or not result.session:
        print(f"Failed to create session: {result.error_message}")
        return

    session = result.session
    print(f"✓ Session created: {session.session_id}")

    try:
        # Get initial session status
        get_result = agb.get_session(session.session_id)
        if get_result.success and hasattr(get_result.data, 'status'):
            print(f"  Initial status: {get_result.data.status}")

        # Pause the session
        print("\nPausing session...")
        pause_result = agb.pause(session)

        if pause_result.success:
            print(f"✓ Session paused successfully")
            print(f"  Request ID: {pause_result.request_id}")
            print(f"  Status: {pause_result.status}")
        else:
            print(f"✗ Failed to pause session: {pause_result.error_message}")
            return

        # Wait for pause to complete
        print("\nWaiting for session to fully pause...")
        time.sleep(3)

        # Verify session is paused
        get_result = agb.get_session(session.session_id)
        if get_result.success and hasattr(get_result.data, 'status'):
            print(f"✓ Current status: {get_result.data.status}")

        # Resume the session
        print("\nResuming session...")
        resume_result = agb.resume(session, timeout=120, poll_interval=3)

        if resume_result.success:
            print(f"✓ Session resumed successfully")
            print(f"  Request ID: {resume_result.request_id}")
            print(f"  Final status: {resume_result.status}")
        else:
            print(f"✗ Failed to resume session: {resume_result.error_message}")
            return

        # Verify session is running
        get_result = agb.get_session(session.session_id)
        if get_result.success and hasattr(get_result.data, 'status'):
            print(f"✓ Verified status: {get_result.data.status}")

    finally:
        # Clean up
        print("\nCleaning up...")
        delete_result = agb.delete(session)
        if delete_result.success:
            print(f"✓ Session deleted successfully")
        else:
            print(f"✗ Failed to delete session: {delete_result.error_message}")


def pause_resume_with_custom_parameters() -> None:
    """Demonstrate pause and resume with custom timeout and polling parameters."""
    print("\n" + "="*60)
    print("Example 2: Pause and Resume with Custom Parameters")
    print("="*60)

    # Initialize the AGB client
    api_key = os.environ.get("AGB_API_KEY", "")
    agb = AGB(api_key=api_key)

    # Create a session
    params = CreateSessionParams(
        image_id="agb-linux-test-5",
        labels={"purpose": "custom-params-demo"}
    )
    result = agb.create(params)

    if not result.success or not result.session:
        print(f"Failed to create session: {result.error_message}")
        return

    session = result.session
    print(f"✓ Session created: {session.session_id}")

    try:
        # Pause with custom parameters
        print("\nPausing session with custom parameters...")
        print("  - Timeout: 300 seconds")
        print("  - Poll interval: 5 seconds")

        pause_result = agb.pause(session, timeout=300, poll_interval=5.0)

        if pause_result.success:
            print(f"✓ Session paused successfully")
            print(f"  Request ID: {pause_result.request_id}")
        else:
            print(f"✗ Failed to pause: {pause_result.error_message}")
            return

        # Wait for pause to complete
        time.sleep(3)

        # Resume with custom parameters
        print("\nResuming session with custom parameters...")
        print("  - Timeout: 300 seconds")
        print("  - Poll interval: 5 seconds")

        resume_result = agb.resume(session, timeout=300, poll_interval=5.0)

        if resume_result.success:
            print(f"✓ Session resumed successfully")
            print(f"  Request ID: {resume_result.request_id}")
            print(f"  Final status: {resume_result.status}")
        else:
            print(f"✗ Failed to resume: {resume_result.error_message}")

    finally:
        # Clean up
        print("\nCleaning up...")
        delete_result = agb.delete(session)
        if delete_result.success:
            print(f"✓ Session deleted successfully")
        else:
            print(f"✗ Failed to delete session: {delete_result.error_message}")


async def async_pause_resume_example() -> None:
    """Demonstrate asynchronous pause and resume operations."""
    print("\n" + "="*60)
    print("Example 3: Async Pause and Resume")
    print("="*60)

    # Initialize the AGB client
    api_key = os.environ.get("AGB_API_KEY", "")
    agb = AGB(api_key=api_key)

    # Create a session
    params = CreateSessionParams(
        image_id="agb-linux-test-5",
        labels={"purpose": "async-demo"}
    )
    result = agb.create(params)

    if not result.success or not result.session:
        print(f"Failed to create session: {result.error_message}")
        return

    session = result.session
    print(f"✓ Session created: {session.session_id}")

    try:
        # Async pause
        print("\nPausing session asynchronously...")
        pause_result = await agb.pause_async(session, timeout=300, poll_interval=3.0)

        if pause_result.success:
            print(f"✓ Session paused successfully")
            print(f"  Request ID: {pause_result.request_id}")
        else:
            print(f"✗ Failed to pause: {pause_result.error_message}")
            return

        # Wait for pause to complete
        print("\nWaiting for session to fully pause...")
        await asyncio.sleep(3)

        # Async resume
        print("\nResuming session asynchronously...")
        resume_result = await agb.resume_async(session, timeout=300, poll_interval=3.0)

        if resume_result.success:
            print(f"✓ Session resumed successfully")
            print(f"  Request ID: {resume_result.request_id}")
            print(f"  Final status: {resume_result.status}")
        else:
            print(f"✗ Failed to resume: {resume_result.error_message}")

    finally:
        # Clean up
        print("\nCleaning up...")
        delete_result = agb.delete(session)
        if delete_result.success:
            print(f"✓ Session deleted successfully")
        else:
            print(f"✗ Failed to delete session: {delete_result.error_message}")


def multiple_pause_resume_cycles() -> None:
    """Demonstrate multiple pause/resume cycles on the same session."""
    print("\n" + "="*60)
    print("Example 4: Multiple Pause/Resume Cycles")
    print("="*60)

    # Initialize the AGB client
    api_key = os.environ.get("AGB_API_KEY", "")
    agb = AGB(api_key=api_key)

    # Create a session
    params = CreateSessionParams(
        image_id="agb-linux-test-5",
        labels={"purpose": "multi-cycle-demo"}
    )
    result = agb.create(params)

    if not result.success or not result.session:
        print(f"Failed to create session: {result.error_message}")
        return

    session = result.session
    print(f"✓ Session created: {session.session_id}")

    try:
        num_cycles = 2
        print(f"\nPerforming {num_cycles} pause/resume cycles...")

        for i in range(num_cycles):
            print(f"\n--- Cycle {i+1}/{num_cycles} ---")

            # Pause
            print("  Pausing...")
            pause_result = agb.pause(session, timeout=300, poll_interval=3)
            if pause_result.success:
                print(f"  ✓ Paused (Request ID: {pause_result.request_id})")
            else:
                print(f"  ✗ Pause failed: {pause_result.error_message}")
                break

            # Wait
            time.sleep(2)

            # Resume
            print("  Resuming...")
            resume_result = agb.resume(session, timeout=300, poll_interval=3)
            if resume_result.success:
                print(f"  ✓ Resumed (Status: {resume_result.status})")
            else:
                print(f"  ✗ Resume failed: {resume_result.error_message}")
                break

            # Wait before next cycle
            if i < num_cycles - 1:
                time.sleep(1)

        print(f"\n✓ Completed {num_cycles} pause/resume cycles successfully")

    finally:
        # Clean up
        print("\nCleaning up...")
        delete_result = agb.delete(session)
        if delete_result.success:
            print(f"✓ Session deleted successfully")
        else:
            print(f"✗ Failed to delete session: {delete_result.error_message}")


        # Clean up
        print("\nCleaning up...")
        delete_result = agb.delete(session)
        if delete_result.success:
            print(f"✓ Session deleted successfully")
        else:
            print(f"✗ Failed to delete session: {delete_result.error_message}")


def main() -> None:
    """Run all examples."""
    print("\n" + "="*70)
    print("AGB Session Pause/Resume Examples")
    print("="*70)
    print("\nThese examples demonstrate session lifecycle management:")
    print("- Creating sessions")
    print("- Pausing sessions (putting them in dormant state)")
    print("- Resuming sessions (restoring them to active state)")
    print("- Deleting sessions")
    print("\nBenefits of pause/resume:")
    print("- 💰 Cost optimization: Reduce costs during idle periods")
    print("- 🔄 Resource management: Free up resources temporarily")
    print("- 🕐 Long-running workflows: Pause overnight, resume next day")
    print("- 🛠️  Maintenance: Safely pause before system maintenance")

    # Run synchronous examples
    basic_pause_resume_example()
    pause_resume_with_custom_parameters()
    multiple_pause_resume_cycles()

    # Run async example
    print("\nRunning async example...")
    asyncio.run(async_pause_resume_example())

    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70)


if __name__ == "__main__":
    main()
