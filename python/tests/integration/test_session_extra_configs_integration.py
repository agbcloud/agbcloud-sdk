#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration test cases for session creation with extra configurations using real API.
"""

import os
import sys
import unittest

# Add project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from agb.agb import AGB
from agb.session_params import CreateSessionParams

class TestSessionExtraConfigsIntegration(unittest.TestCase):
    """Integration test cases for session creation with extra configurations using real API."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment with real API key."""
        cls.api_key = os.getenv("AGB_API_KEY")
        if not cls.api_key:
            raise ValueError(
                "AGB_API_KEY environment variable not set. Please set it:\n"
                "export AGB_API_KEY=akm-xxx"
            )
        cls.agb = AGB(api_key=cls.api_key)

    def test_create_session_with_basic_config_integration(self):
        """Integration test for creating a session with basic configuration."""
        print("Testing session creation with basic configuration...")

        # Create session parameters with basic image
        params = CreateSessionParams(
            image_id="agb-browser-use-1",  # Specify basic image
            labels={
                "test_type": "basic_config_integration",
                "config_type": "basic",
                "created_by": "integration_test"
            }
        )

        # Create session
        result = self.__class__.agb.create(params)
        print(f"Session creation result: {result.success}")

        if result.success:
            self.assertIsNotNone(result.session)
            session = result.session
            if session is not None:
                print(f"Basic session created with ID: {session.session_id}")

                # Verify session properties
                self.assertIsNotNone(session.session_id)

                # Test session info
                try:
                    info_result = session.info()
                    if info_result.success:
                        print(f"Session info retrieved successfully")
                        print(f"Resource URL: {info_result.data.get('resource_url', 'N/A')}")
                    else:
                        print(f"Failed to get session info: {info_result.error_message}")
                except Exception as e:
                    print(f"Session info call failed: {e}")

                # Clean up
                try:
                    delete_result = self.__class__.agb.delete(session)
                    if delete_result.success:
                        print("Basic session deleted successfully")
                    else:
                        print(f"Failed to delete basic session: {delete_result.error_message}")

                    self.assertTrue(delete_result.success, "Session deletion should succeed")
                except Exception as e:
                    print(f"Session deletion failed: {e}")
        else:
            print(f"Failed to create basic session: {result.error_message}")
            # Fail the test if session creation fails in real environment
            self.fail(f"Basic session creation should succeed in real environment: {result.error_message}")

    def test_create_session_with_labels_verification_integration(self):
        """Integration test for creating a session with labels and verifying them."""
        print("Testing session creation with labels verification...")

        # Create session parameters with labels
        params = CreateSessionParams(
            image_id="agb-browser-use-1",  # Specify basic image
            labels={
                "test_type": "labels_verification_integration",
                "config_type": "labels_test",
                "security": "enabled",
                "created_by": "integration_test"
            }
        )

        # Create session
        result = self.__class__.agb.create(params)
        print(f"Labels verification session creation result: {result.success}")

        if result.success:
            self.assertIsNotNone(result.session)
            session = result.session
            if session is not None:
                print(f"Labels verification session created with ID: {session.session_id}")

                # Verify session properties
                self.assertIsNotNone(session.session_id)

                # Test session info to verify basic environment
                try:
                    info_result = session.info()
                    if info_result.success:
                        print(f"Session info retrieved successfully")
                        print(f"Resource URL: {info_result.data.get('resource_url', 'N/A')}")
                    else:
                        print(f"Failed to get session info: {info_result.error_message}")
                except Exception as e:
                    print(f"Session info call failed: {e}")

                # Verify labels were set
                try:
                    labels_result = session.get_labels()
                    if labels_result.success:
                        labels = labels_result.data
                        print(f"Session labels: {labels}")
                        self.assertEqual(labels.get("config_type"), "labels_test")
                        self.assertEqual(labels.get("security"), "enabled")
                    else:
                        print(f"Failed to get session labels: {labels_result.error_message}")
                except Exception as e:
                    print(f"Get labels call failed: {e}")

                # Clean up
                try:
                    delete_result = self.__class__.agb.delete(session)
                    if delete_result.success:
                        print("Labels verification session deleted successfully")
                    else:
                        print(f"Failed to delete labels verification session: {delete_result.error_message}")

                    self.assertTrue(delete_result.success, "Session deletion should succeed")
                except Exception as e:
                    print(f"Session deletion failed: {e}")
        else:
            print(f"Failed to create labels verification session: {result.error_message}")
            # Fail the test if session creation fails in real environment
            self.fail(f"Labels verification session creation should succeed in real environment: {result.error_message}")

if __name__ == "__main__":
    unittest.main()