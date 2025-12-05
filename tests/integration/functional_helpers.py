"""
Functional validation helpers for Computer and Mobile modules.
These helpers verify that operations actually work by checking their effects.
"""

import time
from typing import Optional, Tuple


class FunctionalTestResult:
    """Helper class to track test results and details."""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.success = False
        self.message = ""
        self.details = {}
        self.duration = 0.0
    
    def set_success(self, message: str):
        self.success = True
        self.message = message
    
    def set_failure(self, message: str):
        self.success = False
        self.message = message
    
    def add_detail(self, key: str, value):
        self.details[key] = value
    
    def __str__(self):
        status = "✅ PASS" if self.success else "❌ FAIL"
        return f"{status} {self.test_name}: {self.message} (Duration: {self.duration:.2f}s)"