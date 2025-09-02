# OSS Management Example

This example demonstrates how to use the Object Storage Service (OSS) features of the AGB SDK for Python.

## Features Demonstrated

- Initializing OSS credentials in a session
- Uploading files to OSS buckets
- Downloading files from OSS buckets
- Anonymous uploads to OSS using URLs
- Anonymous downloads from OSS using URLs
- Handling OSS operations in a session environment

## Running the Example

1. Make sure you have installed the AGB SDK:

```bash
pip install agbcloud-sdk
```

2. Set your API key as an environment variable (recommended):

```bash
export AGB_API_KEY=your_api_key_here
```

3. Optionally, set OSS credentials as environment variables:

```bash
export OSS_ACCESS_KEY_ID=your_access_key_id
export OSS_ACCESS_KEY_SECRET=your_access_key_secret
export OSS_SECURITY_TOKEN=your_security_token
export OSS_ENDPOINT=https://oss.example.com
export OSS_REGION=oss-region
export OSS_TEST_BUCKET=your_test_bucket
```

4. Run the example:

```bash
python main.py
```

## Code Explanation

The example demonstrates OSS integration with AGB:

1. Create a new session
2. Initialize OSS environment with credentials
3. Create a test file in the session
4. Upload the file to an OSS bucket
5. Upload a file anonymously using a URL
6. Download a file from an OSS bucket
7. Download a file anonymously using a URL
8. Clean up by deleting the session

OSS integration allows you to:

- Transfer files between your local environment and the cloud session
- Store session artifacts in permanent storage
- Share files across multiple sessions
- Download resources from external sources
- Implement file backup and restore functionality

For more details on OSS integration, see the [OSS API Reference](../../api-reference/modules/oss.md).
