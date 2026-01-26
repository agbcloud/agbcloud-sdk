"""
Pytest configuration for integration tests.

This directory contains helper modules that are not test files. If CI runs pytest
with globs (e.g. `pytest tests/integration/*.py`), pytest may try to import these
helpers and they might show up in custom summaries. Explicitly ignore them here.

Note: This file should NOT be run directly as a test. It is a pytest configuration file.
"""

# Prevent pytest from collecting/importing helper modules as tests.
collect_ignore = [
    "functional_helpers.py",
    "conftest.py",  # Explicitly ignore conftest.py itself
]

# If this file is run directly, exit gracefully
if __name__ == "__main__":
    import sys
    print("conftest.py is a pytest configuration file and should not be run directly.")
    print("Run pytest on the test directory instead: pytest tests/integration/")
    sys.exit(0)

