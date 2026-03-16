#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests for AGB.list() API functionality
"""

import os
import random
import sys
import time
import unittest

# Add project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from agb import AGB
from agb.session_params import CreateSessionParams

def get_test_api_key():
    """Get API key for testing"""
    api_key = os.environ.get("AGB_API_KEY")
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

class TestAGBList(unittest.TestCase):
    """Integration tests for AGB.list() API."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for the entire test class."""
        api_key = get_test_api_key()
        cls.agb = AGB(api_key=api_key)

        # Generate a unique identifier for this test run
        cls.unique_id = generate_unique_id()
        print(f"Using unique ID for test: {cls.unique_id}")

        # Create multiple sessions with different labels for testing
        cls.sessions = []

        # Session 1: project=list-test, environment=dev
        print("Creating session 1 with dev environment...")
        params1 = CreateSessionParams(
            image_id="agb-browser-use-1",
            labels={
                "project": f"list-test-{cls.unique_id}",
                "environment": "dev",
                "owner": f"test-{cls.unique_id}",
            }
        )
        result1 = cls.agb.create(params1)
        if result1.success:
            cls.sessions.append(result1.session)
            print(f"Session 1 created: {result1.session.session_id}")
            print(f"Request ID: {result1.request_id}")

        # Session 2: project=list-test, environment=staging
        print("Creating session 2 with staging environment...")
        params2 = CreateSessionParams(
            image_id="agb-browser-use-1",
            labels={
                "project": f"list-test-{cls.unique_id}",
                "environment": "staging",
                "owner": f"test-{cls.unique_id}",
            }
        )
        result2 = cls.agb.create(params2)
        if result2.success:
            cls.sessions.append(result2.session)
            print(f"Session 2 created: {result2.session.session_id}")
            print(f"Request ID: {result2.request_id}")

        # Session 3: project=list-test, environment=prod
        print("Creating session 3 with prod environment...")
        params3 = CreateSessionParams(
            image_id="agb-browser-use-1",
            labels={
                "project": f"list-test-{cls.unique_id}",
                "environment": "prod",
                "owner": f"test-{cls.unique_id}",
            }
        )
        # Retry logic for session 3 creation
        max_retries = 3
        for attempt in range(max_retries):
            result3 = cls.agb.create(params3)
            if result3.success:
                cls.sessions.append(result3.session)
                print(f"Session 3 created: {result3.session.session_id}")
                print(f"Request ID: {result3.request_id}")
                break
            else:
                print(f"Attempt {attempt + 1} failed to create session 3: {result3.error_message}")
                if attempt < max_retries - 1:
                    print("Waiting 15 seconds before retrying...")
                    time.sleep(15)

        # Verify all sessions were created
        if len(cls.sessions) != 3:
            raise RuntimeError(f"Failed to create all 3 test sessions. Only created {len(cls.sessions)} sessions.")

        # Wait a bit for sessions to be fully created and labels to propagate
        time.sleep(5)

    @classmethod
    def tearDownClass(cls):
        """Tear down test fixtures after all tests in the class have been run."""
        print("Cleaning up: Deleting all test sessions...")
        for session in cls.sessions:
            try:
                result = cls.agb.delete(session)
                print(
                    f"Session {session.session_id} deleted. Success: {result.success}, Request ID: {result.request_id}"
                )
            except Exception as e:
                print(f"Warning: Error deleting session {session.session_id}: {e}")

    def test_list_all_sessions(self):
        """Test listing all sessions without any label filter."""
        print("\n=== Testing list() without labels ===")

        result = self.agb.list()

        # Verify the result
        self.assertTrue(result.success, "list() should succeed")
        self.assertIsNotNone(result.request_id, "Request ID should be present")
        self.assertIsNotNone(result.session_ids, "Session IDs list should not be None")

        print(f"Total sessions found: {result.total_count}")
        print(f"Sessions in current page: {len(result.session_ids)}")
        print(f"Request ID: {result.request_id}")

    def test_list_with_single_label(self):
        """Test listing sessions with a single label filter."""
        print("\n=== Testing list() with single label ===")

        # List sessions with project label
        result = self.agb.list(labels={"project": f"list-test-{self.unique_id}"})

        # Verify the result
        self.assertTrue(result.success, "list() with single label should succeed")
        self.assertIsNotNone(result.request_id, "Request ID should be present")
        self.assertGreaterEqual(
            len(result.session_ids), 3, "Should find at least 3 sessions"
        )

        # Verify all returned sessions have the expected label
        session_ids = [s.session_id for s in self.sessions]
        found_count = 0
        for session_id in result.session_ids:
            if session_id in session_ids:
                found_count += 1

        self.assertEqual(
            found_count, 3, "Should find exactly 3 test sessions"
        )

        print(f"Found {found_count} test sessions")
        print(f"Total sessions with label: {len(result.session_ids)}")
        print(f"Request ID: {result.request_id}")

    def test_list_with_multiple_labels(self):
        """Test listing sessions with multiple label filters."""
        print("\n=== Testing list() with multiple labels ===")

        # List sessions with project and environment labels
        result = self.agb.list(
            labels={
                "project": f"list-test-{self.unique_id}",
                "environment": "dev",
            }
        )

        # Verify the result
        self.assertTrue(result.success, "list() with multiple labels should succeed")
        self.assertIsNotNone(result.request_id, "Request ID should be present")
        self.assertGreaterEqual(
            len(result.session_ids), 1, "Should find at least 1 session"
        )

        # Verify the dev session is in the results
        dev_session_id = self.sessions[0].session_id
        found = False
        for session_id in result.session_ids:
            if session_id == dev_session_id:
                found = True
                break

        self.assertTrue(found, "Dev session should be in the results")

        print(f"Found dev session: {found}")
        print(f"Total matching sessions: {len(result.session_ids)}")
        print(f"Request ID: {result.request_id}")

    def test_list_with_pagination(self):
        """Test listing sessions with pagination parameters."""
        print("\n=== Testing list() with pagination ===")

        # List first page with limit of 2
        result_page1 = self.agb.list(
            labels={"project": f"list-test-{self.unique_id}"}, page=1, limit=2
        )

        # Verify first page
        self.assertTrue(result_page1.success, "First page should succeed")
        self.assertIsNotNone(result_page1.request_id, "Request ID should be present")
        self.assertLessEqual(
            len(result_page1.session_ids), 2, "First page should have at most 2 sessions"
        )

        print(f"Page 1 - Found {len(result_page1.session_ids)} sessions")
        print(f"Request ID: {result_page1.request_id}")

        # If there are more results, test page 2
        if result_page1.next_token:
            result_page2 = self.agb.list(
                labels={"project": f"list-test-{self.unique_id}"}, page=2, limit=2
            )

            self.assertTrue(result_page2.success, "Second page should succeed")
            self.assertIsNotNone(
                result_page2.request_id, "Request ID should be present"
            )

            print(f"Page 2 - Found {len(result_page2.session_ids)} sessions")
            print(f"Request ID: {result_page2.request_id}")

    def test_list_with_non_matching_label(self):
        """Test listing sessions with a label that doesn't match any session."""
        print("\n=== Testing list() with non-matching label ===")

        # List sessions with a label that doesn't exist
        result = self.agb.list(
            labels={
                "project": f"list-test-{self.unique_id}",
                "environment": "nonexistent",
            }
        )

        # Verify the result
        self.assertTrue(result.success, "list() should succeed even with no matches")
        self.assertIsNotNone(result.request_id, "Request ID should be present")

        # Verify our test sessions are NOT in the results
        session_ids = [s.session_id for s in self.sessions]
        found_count = 0
        for session_id in result.session_ids:
            if session_id in session_ids:
                found_count += 1

        self.assertEqual(
            found_count, 0, "Should not find any test sessions with non-matching label"
        )

        print(f"Found {found_count} test sessions (expected 0)")
        print(f"Total sessions with non-matching label: {len(result.session_ids)}")
        print(f"Request ID: {result.request_id}")

    def test_list_pagination_loop(self):
        """Test retrieving all sessions across multiple pages."""
        print("\n=== Testing list() pagination loop ===")

        all_session_ids = []
        page = 1
        limit = 2

        while True:
            result = self.agb.list(labels={"owner": f"test-{self.unique_id}"}, page=page, limit=limit)

            if not result.success:
                self.fail(f"Error on page {page}: {result.error_message}")

            print(f"Page {page}: Found {len(result.session_ids)} session IDs")
            all_session_ids.extend(result.session_ids)

            # Break if no more pages
            if not result.next_token:
                break

            page += 1

        print(f"Retrieved {len(all_session_ids)} total session IDs across {page} pages")

        # Verify we found all our test sessions
        session_ids = [s.session_id for s in self.sessions]
        found_count = 0
        for session_id in all_session_ids:
            if session_id in session_ids:
                found_count += 1

        self.assertEqual(
            found_count, 3, "Should find all 3 test sessions across pages"
        )

    def test_list_error_handling(self):
        """Test error handling for list() method."""
        print("\n=== Testing list() error handling ===")

        # Test with invalid label values (if any validation exists)
        try:
            result = self.agb.list(labels={"": "invalid-empty-key"})
            # This might succeed or fail depending on API validation
            print(f"Empty key test - Success: {result.success}")
            if not result.success:
                print(f"Error message: {result.error_message}")
        except Exception as e:
            print(f"Exception with empty key: {e}")

        # Test with None labels (should work as no filter)
        try:
            result = self.agb.list(labels=None)
            self.assertTrue(result.success, "list() with None labels should succeed")
            print(f"None labels test - Success: {result.success}")
        except Exception as e:
            print(f"Exception with None labels: {e}")

if __name__ == "__main__":
    unittest.main()