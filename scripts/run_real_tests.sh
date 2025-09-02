#!/usr/bin/env bash
"""
Script to run integration tests with real API credentials.
This script requires valid API credentials to run.

To run this script:
1. Set AGB_API_KEY environment variable with your actual API key
2. Run: ./scripts/run_real_tests.sh
"""

# Exit on any error
set -e

# Check if API key is set
if [ -z "$AGB_API_KEY" ]; then
    echo "ERROR: AGB_API_KEY environment variable is not set."
    echo "Please set it with your actual API key to run real tests."
    echo
    echo "Usage:"
    echo "  export AGB_API_KEY=your_actual_api_key"
    echo "  ./scripts/run_real_tests.sh"
    exit 1
fi

echo "Running integration tests with real API credentials..."
echo "API Key: ${AGB_API_KEY:0:8}...${AGB_API_KEY: -4}"

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Warning: No virtual environment found. Using system Python."
fi

# Run the real API integration test
echo "Running real API integration tests..."
python tests/integration/test_agb_command.py
python tests/integration/test_session_info.py
python tests/integration/test_list_mcp_tools.py
python tests/integration/test_agb_code.py
python tests/integration/test_agb_filesystem.py
python tests/integration/test_session_info.py

echo "Real API integration tests completed!"