#!/usr/bin/env python3

import os

from agb import AGB, ContextSync, SyncPolicy
from agb.exceptions import AGBError
from agb.session_params import CreateSessionParams

def main():
    # Initialize the AGB client
    # You can provide the API key as a parameter or set the AGB_API_KEY
    # environment variable
    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        api_key = "akm-xxx"  # Replace with your actual API key

    session = None
    try:
        agb = AGB(api_key=api_key)

        # Example 1: List all contexts
        print("\nExample 1: Listing all contexts...")
        try:
            result = agb.context.list()
            print(f"Request ID: {result.request_id}")
            if result.success:
                print(f"Found {len(result.contexts)} contexts:")
                for context in result.contexts:
                    print(
                        f"- {context.name} ({context.id}): created={context.created_at}, last_used={context.last_used_at}"
                    )
            else:
                print("Failed to list contexts")
        except AGBError as e:
            print(f"Error listing contexts: {e}")

        # Example 2: Get a context (create if it doesn't exist)
        print("\nExample 2: Getting a context (creating if it doesn't exist)...")
        context_name = "my-test-context"
        try:
            result = agb.context.get(context_name, create=True)
            print(f"Request ID: {result.request_id}")
            if result.success and result.context:
                context = result.context
                print(f"Got context: {context.name} ({context.id})")
            else:
                print("Context not found and could not be created")
                return
        except AGBError as e:
            print(f"Error getting context: {e}")
            return

        # Example 3: Create a session with the context
        print("\nExample 3: Creating a session with the context...")
        try:
            params = CreateSessionParams(
                image_id="agb-code-space-1",
                context_syncs=[ContextSync.new(
                    context.id,
                    "/tmp/shared",
                    SyncPolicy()
                )]
            )

            session_result = agb.create(params)
            if session_result.success and session_result.session:
                session = session_result.session
                print(f"Session created with ID: {session.session_id}")
                print(f"Request ID: {session_result.request_id}")
            else:
                print("Failed to create session")
                return
            print("Note: The create() method automatically monitored the context status")
            print("and only returned after all context operations were complete or reached maximum retries.")
        except AGBError as e:
            print(f"Error creating session: {e}")
            return

        # Example 4: Update the context
        print("\nExample 4: Updating the context...")
        try:
            context.name = "renamed-test-context"
            result = agb.context.update(context)
            print(f"Request ID: {result.request_id}")
            if not result.success:
                print(f"Context update was not successful: {result.error_message}")
            else:
                print(f"Context updated successfully to: {context.name}")
        except AGBError as e:
            print(f"Error updating context: {e}")

        # Clean up
        print("\nCleaning up...")

        # Delete the session with context synchronization
        try:
            if session:
                print("Deleting the session with context synchronization...")
                delete_result = agb.delete(session, sync_context=True)
                print(f"Session deletion request ID: {delete_result.request_id}")
                print(f"Session deletion success: {delete_result.success}")
                print("Note: The delete() method synchronized the context before session deletion")
                print("and monitored all context operations until completion.")
                session = None

                # Alternative method using session's delete method:
                # delete_result = session.delete(sync_context=True)
        except AGBError as e:
            print(f"Error deleting session: {e}")

        # Delete the context
        print("Deleting the context...")
        try:
            result = agb.context.delete(context)
            print(f"Context deletion request ID: {result.request_id}")
            if result.success:
                print("Context deleted successfully")
            else:
                print(f"Failed to delete context: {result.error_message}")
        except AGBError as e:
            print(f"Error deleting context: {e}")

    except Exception as e:
        print(f"Error initializing AGB: {e}")
        if session and hasattr(session, 'session_id'):
            try:
                agb.delete(session)  # type: ignore
                print("Session deleted during cleanup")
            except AGBError as delete_error:
                print(f"Error deleting session during cleanup: {delete_error}")

if __name__ == "__main__":
    main()
