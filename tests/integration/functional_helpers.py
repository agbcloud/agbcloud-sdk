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

def validate_cursor_position(cursor_result, expected_x: int, expected_y: int, tolerance: int = 5) -> bool:
    """
    Validate cursor position is within tolerance of expected position.

    Args:
        cursor_result: Result from get_position() or tuple (x, y) from mouse.get_position()
        expected_x: Expected X coordinate
        expected_y: Expected Y coordinate
        tolerance: Allowed pixel difference (default: 5)

    Returns:
        bool: True if position is within tolerance
    """
    try:
        # Handle tuple from mouse.get_position()
        if isinstance(cursor_result, tuple):
            actual_x, actual_y = cursor_result
        # Handle old OperationResult format
        elif hasattr(cursor_result, 'success') and hasattr(cursor_result, 'data'):
            if not cursor_result.success or not cursor_result.data:
                return False
            import json
            cursor_data = cursor_result.data
            if isinstance(cursor_data, str):
                cursor_data = json.loads(cursor_data)
            actual_x = cursor_data.get('x', 0)
            actual_y = cursor_data.get('y', 0)
        else:
            return False

        x_diff = abs(actual_x - expected_x)
        y_diff = abs(actual_y - expected_y)

        return x_diff <= tolerance and y_diff <= tolerance
    except Exception:
        return False

def get_screen_center(session):
    """
    Get the center coordinates of the screen.

    Args:
        session: The AGB session object

    Returns:
        tuple: (center_x, center_y) coordinates, or (400, 300) as fallback
    """
    try:
        size_result = session.computer.screen.get_size()
        if not size_result.success or not size_result.data:
            print("⚠️ Failed to get screen size, using fallback center (400, 300)")
            return 400, 300

        screen_data = size_result.data
        width = screen_data.get('width', 800)
        height = screen_data.get('height', 600)

        center_x = width // 2
        center_y = height // 2

        print(f"📐 Screen size: {width}x{height}, center: ({center_x}, {center_y})")
        return center_x, center_y

    except Exception as e:
        print(f"⚠️ Error getting screen center: {e}, using fallback center (400, 300)")
        return 400, 300


def main():
    """
    Main function for functional_helpers module.
    This is a helper module, not a test file.
    It should be imported by other test files, not run directly.
    """
    print("This is a helper module, not a test file.")
    print("It should be imported by other test files, not run directly.")
    return 0


if __name__ == "__main__":
    exit(main())
