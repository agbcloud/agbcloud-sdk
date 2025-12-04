# Code Execution Examples

This directory contains examples of executing code in various programming languages using the AGB SDK.

## Supported Languages

- **Python**: Full Python 3 environment with standard libraries.
- **JavaScript**: Node.js environment.
- **Java**: Java execution environment (supports snippets).
- **R**: R statistical computing environment.

## Examples

### Basic Execution (`main.py`)
Comprehensive example demonstrating execution in all supported languages.

<<< ./main.py

### Caching Results (`caching.py`)
Demonstrates how to implement client-side caching for deterministic code execution results to save costs and reduce latency.

<<< ./caching.py

### Concurrency (`concurrency.py`)
Demonstrates how to execute multiple code tasks in parallel using threading for high-throughput scenarios.

<<< ./concurrency.py

### Security Best Practices (`security.py`)
Demonstrates security best practices, including input validation and sanitization for untrusted code.

<<< ./security.py

## How to Run

1. **Set API Key**:
   ```bash
   export AGB_API_KEY="your_api_key"
   ```

2. **Run Script**:
   ```bash
   python docs/examples/code_execution/main.py
   ```
