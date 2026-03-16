#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGB session get_metrics integration test
Tests session metrics retrieval functionality
"""

import os
import sys
import unittest
import pytest

# Add project root directory to Python path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from agb.agb import AGB
from agb.session_params import CreateSessionParams
from agb.logger import get_logger

logger = get_logger(__name__)


def get_test_api_key():
    """Get API Key from environment variables"""
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        return None
    return api_key


class TestSessionGetMetricsIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        api_key = get_test_api_key()
        if not api_key:
            raise unittest.SkipTest("AGB_API_KEY environment variable not set")
        cls.agb = AGB(api_key=api_key)
        
        # Create a shared session for all tests
        result = cls.agb.create(CreateSessionParams(image_id="agb-computer-use-ubuntu-2204"))
        if not result.success:
            raise unittest.SkipTest(f"Session creation failed: {result.error_message}")
        cls.session = result.session
        if cls.session is None:
            raise unittest.SkipTest("Session creation returned None")
    
    @classmethod
    def tearDownClass(cls):
        # Clean up the shared session
        if hasattr(cls, 'session') and cls.session:
            delete_result = cls.session.delete()
            if not delete_result.success:
                logger.warning(f"Failed to delete session: {delete_result.error_message}")

    @pytest.mark.integration
    def test_get_metrics_returns_structured_data(self):
        """Test that get_metrics returns structured metrics data"""
        # Use the shared session
        session = self.session

        # Call get_metrics
        metrics_result = session.get_metrics()
        self.assertTrue(
            metrics_result.success,
            f"get_metrics failed: {metrics_result.error_message}",
        )
        self.assertIsNotNone(metrics_result.metrics)

        # Validate metrics structure and values
        m = metrics_result.metrics
        self.assertGreaterEqual(m.cpu_count, 1, "CPU count should be at least 1")
        self.assertGreater(m.mem_total, 0, "Total memory should be greater than 0")
        self.assertGreater(m.disk_total, 0, "Total disk should be greater than 0")
        self.assertGreaterEqual(m.cpu_used_pct, 0.0, "CPU usage should be >= 0%")
        self.assertLessEqual(m.cpu_used_pct, 100.0, "CPU usage should be <= 100%")
        self.assertTrue(len(m.timestamp) > 0, "Timestamp should not be empty")
        # Log metrics for debugging
        logger.info(f"Session metrics retrieved successfully:")
        logger.info(f"  CPU Count: {m.cpu_count}")
        logger.info(f"  CPU Used: {m.cpu_used_pct}%")
        logger.info(f"  Memory Total: {m.mem_total}")
        logger.info(f"  Memory Used: {m.mem_used}")
        logger.info(f"  Disk Total: {m.disk_total}")
        logger.info(f"  Disk Used: {m.disk_used}")
        logger.info(f"  Timestamp: {m.timestamp}")

    @pytest.mark.integration
    def test_get_metrics_with_timeouts(self):
        """Test get_metrics with custom timeout parameters"""
        # Use the shared session
        session = self.session

        # Call get_metrics with custom timeouts
        metrics_result = session.get_metrics(
            read_timeout=30000,  # 30 seconds
            connect_timeout=10000  # 10 seconds
        )
        self.assertTrue(
            metrics_result.success,
            f"get_metrics with timeouts failed: {metrics_result.error_message}",
        )
        self.assertIsNotNone(metrics_result.metrics)

        # Basic validation
        m = metrics_result.metrics
        self.assertGreaterEqual(m.cpu_count, 1)
        self.assertGreater(m.mem_total, 0)


if __name__ == "__main__":
    unittest.main()
