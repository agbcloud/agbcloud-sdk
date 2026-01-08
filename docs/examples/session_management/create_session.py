"""
This example demonstrates how to create a session in AGB.
"""

import os
import time
from typing import Dict, Optional

from agb import AGB
from agb.session_params import CreateSessionParams


def create_session_with_default_params() -> None:
    """Create a session with default parameters."""
    # Initialize the AGB client
    api_key = os.environ.get("AGB_API_KEY", "")
    agb = AGB(api_key=api_key)

    # Create a session with default parameters
    params = CreateSessionParams(image_id="agb-code-space-1")
    result = agb.create(params)

    if result.success and result.session:
        session = result.session
        print(f"Session created successfully with ID: {session.session_id}")
        print(f"Request ID: {result.request_id}")

        # Clean up
        delete_result = agb.delete(session)
        if delete_result.success:
            print("Session deleted successfully")
        else:
            print(f"Failed to delete session: {delete_result.error_message}")
    else:
        print(f"Failed to create session: {result.error_message}")


def create_session_with_custom_image() -> None:
    """Create a session with custom image."""
    # Initialize the AGB client
    api_key = os.environ.get("AGB_API_KEY", "")
    agb = AGB(api_key=api_key)

    # Create session parameters with custom image
    params = CreateSessionParams(image_id="agb-code-space-1")

    # Create a session with the parameters
    result = agb.create(params)

    if result.success and result.session:
        session = result.session
        print(
            f"Session with custom image created successfully with ID: {session.session_id}"
        )
        print(f"Request ID: {result.request_id}")

        # Clean up
        delete_result = agb.delete(session)
        if delete_result.success:
            print("Session deleted successfully")
        else:
            print(f"Failed to delete session: {delete_result.error_message}")
    else:
        print(f"Failed to create session with custom image: {result.error_message}")


def create_session_with_labels() -> None:
    """Create a session with labels."""
    # Initialize the AGB client
    api_key = os.environ.get("AGB_API_KEY", "")
    agb = AGB(api_key=api_key)

    # Define labels
    labels: Dict[str, str] = {
        "environment": "development",
        "project": "example",
        "owner": "user123",
        "team": "backend",
        "version": "v1.0.0",
    }

    # Create session parameters with labels
    params = CreateSessionParams(image_id="agb-browser-use-1", labels=labels)

    # Create a session with the parameters
    result = agb.create(params)

    if result.success and result.session:
        session = result.session
        print(f"Session with labels created successfully with ID: {session.session_id}")
        print(f"Request ID: {result.request_id}")

        # Verify the labels were set
        label_result = session.get_labels()
        if label_result.success:
            retrieved_labels = label_result.data
            print("Retrieved labels:")
            for key, value in retrieved_labels.items():
                print(f"  {key}: {value}")
        else:
            print(f"Failed to get labels: {label_result.error_message}")

        # Update labels during session lifecycle
        updated_labels = {
            **labels,
            "status": "active",
            "last_updated": str(int(time.time())),
        }

        update_result = session.set_labels(updated_labels)
        if update_result.success:
            print("Labels updated successfully")

            # Get updated labels
            final_label_result = session.get_labels()
            if final_label_result.success:
                final_labels = final_label_result.data
                print("Final labels:")
                for key, value in final_labels.items():
                    print(f"  {key}: {value}")
        else:
            print(f"Failed to update labels: {update_result.error_message}")

        # Clean up
        delete_result = agb.delete(session)
        if delete_result.success:
            print("Session deleted successfully")
        else:
            print(f"Failed to delete session: {delete_result.error_message}")
    else:
        print(f"Failed to create session with labels: {result.error_message}")


def main() -> None:
    """Run all examples."""
    print("1. Creating session with default parameters...")
    create_session_with_default_params()
    print("\n2. Creating session with custom image...")
    create_session_with_custom_image()
    print("\n3. Creating session with labels...")
    create_session_with_labels()


if __name__ == "__main__":
    main()
