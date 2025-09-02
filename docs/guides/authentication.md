# Authentication

This guide explains how to authenticate with the AGB SDK.

## Overview

Authentication with the AGB SDK is done using an API key. This key is used to authenticate all requests to the AGB cloud environment.

## Authentication Methods

There are two main ways to provide your API key:

1. **Direct Initialization**: Provide the API key directly when initializing the AGB client.
2. **Environment Variable**: Set the `AGB_API_KEY` environment variable, and the SDK will use it automatically.

## Examples

### Python

```python
# Method 1: Direct initialization with API key
api_key = "your_api_key_here"
agb = AGB(api_key=api_key)

# Method 2: Using environment variable
# First, set the environment variable:
# export AGB_API_KEY=your_api_key_here
agb = AGB()
```

## Best Practices

1. **Environment Variables**: For production applications, it's recommended to use environment variables rather than hardcoding API keys in your code.

2. **Secure Storage**: Store your API keys securely and never commit them to version control systems.

3. **Key Rotation**: Periodically rotate your API keys to enhance security.

4. **Least Privilege**: Use API keys with the minimum required permissions for your application.

## Related Resources

- [Sessions](../api-reference/core/session.md)
- [Best Practices](best-practices.md)
