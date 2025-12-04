# Best Practices Guide

## Overview

This guide outlines the recommended patterns for building robust, secure, and efficient applications with the AGB SDK.

## 1. Resource Management

### Always Clean Up Sessions
Sessions are billing units. Leaking sessions (forgetting to delete them) leads to unnecessary costs.
- **Pattern**: Use `try...finally` blocks or context managers.
- **Anti-pattern**: relying on script exit to clean up.

### Use Session Pooling for High Concurrency
Creating a session takes time (cold start). If you have high traffic, do not create a session per request.
- **Recommendation**: Maintain a pool of "warm" sessions.
- **Example**: [Session Pool Example](../examples/session_management/session_pool.py)

## 2. Code Execution

### Cache Deterministic Results
If your code execution is deterministic (same input = same output), cache the result locally to save time and money.
- **Example**: [Caching Example](../examples/code_execution/caching.py)

### Handle Concurrency Correctly
Use threading or asyncio to run multiple tasks in parallel. The SDK is thread-safe.
- **Example**: [Concurrency Example](../examples/code_execution/concurrency.py)

### Security First
Never `exec()` unchecked user input. Validate code before sending it to the cloud.
- **Example**: [Security Example](../examples/code_execution/security.py)

## 3. Reliability

### Implement Retries
Network glitches happen. Wrap your API calls in a retry loop with exponential backoff.

### Check Return Values
The SDK uses a "Result Object" pattern instead of throwing exceptions for API errors.
- **Always check**: `if result.success:`
- **Never assume**: `session = result.session` (it might be None if failed)

## 4. File Operations

### Batch Operations
When uploading/downloading multiple files, do it in parallel or batch requests if the API supports it, rather than sequential loops.

### Use Absolute Paths
Always use absolute paths (e.g., `/tmp/myfile.txt`) in the remote environment to avoid ambiguity.
