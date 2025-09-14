# OSS Module API Reference

The OSS (Object Storage Service) module provides cloud storage capabilities in the AGB environment. It supports uploading and downloading files to/from cloud storage with both authenticated and anonymous access patterns.

## Class Definition

```python
from agb.modules.oss import Oss, OSSUploadResult, OSSDownloadResult, OSSClientResult

class Oss(BaseService):
    def __init__(self, session)
```

## Core Methods

### Environment Setup

#### `env_init(endpoint, access_key_id, access_key_secret, bucket_name)`

Initialize OSS environment with credentials and configuration.

**Parameters:**
- `endpoint` (str): OSS service endpoint URL.
- `access_key_id` (str): Access key ID for authentication.
- `access_key_secret` (str): Access key secret for authentication.
- `bucket_name` (str): Default bucket name to use.

**Returns:**
- `OSSClientResult`: Result containing client configuration and operation status.

**Example:**
```python
# Initialize OSS environment
result = session.oss.env_init(
    endpoint="https://oss.example.com",
    access_key_id="your_access_key_id",
    access_key_secret="your_access_key_secret",
    bucket_name="my-bucket"
)

if result.success:
    print("OSS environment initialized successfully")
    print("Client config:", result.client_config)
else:
    print("Initialization failed:", result.error_message)
```

### File Upload Operations

#### `upload(bucket, object, path)`

Upload a file to OSS with authentication.

**Parameters:**
- `bucket` (str): Name of the OSS bucket.
- `object` (str): Object key/name in the bucket.
- `path` (str): Local file path to upload.

**Returns:**
- `OSSUploadResult`: Result containing upload status and metadata.

**Example:**
```python
# Upload a file to OSS
result = session.oss.upload(
    bucket="my-bucket",
    object="documents/report.pdf",
    path="/tmp/local_report.pdf"
)

if result.success:
    print("File uploaded successfully")
    print("Upload result:", result.content)
else:
    print("Upload failed:", result.error_message)
```

#### `upload_anonymous(url, path)`

Upload a file using anonymous/pre-signed URL.

**Parameters:**
- `url` (str): Pre-signed upload URL.
- `path` (str): Local file path to upload.

**Returns:**
- `OSSUploadResult`: Result containing upload status and metadata.

**Example:**
```python
# Upload using pre-signed URL
presigned_url = "https://my-bucket.oss.example.com/upload?signature=..."
result = session.oss.upload_anonymous(presigned_url, "/tmp/file_to_upload.txt")

if result.success:
    print("Anonymous upload successful")
else:
    print("Anonymous upload failed:", result.error_message)
```

### File Download Operations

#### `download(bucket, object, path)`

Download a file from OSS with authentication.

**Parameters:**
- `bucket` (str): Name of the OSS bucket.
- `object` (str): Object key/name in the bucket.
- `path` (str): Local path where to save the downloaded file.

**Returns:**
- `OSSDownloadResult`: Result containing download status and metadata.

**Example:**
```python
# Download a file from OSS
result = session.oss.download(
    bucket="my-bucket",
    object="documents/report.pdf",
    path="/tmp/downloaded_report.pdf"
)

if result.success:
    print("File downloaded successfully")
    print("Download result:", result.content)
else:
    print("Download failed:", result.error_message)
```

#### `download_anonymous(url, path)`

Download a file using anonymous/pre-signed URL.

**Parameters:**
- `url` (str): Pre-signed download URL or public URL.
- `path` (str): Local path where to save the downloaded file.

**Returns:**
- `OSSDownloadResult`: Result containing download status and metadata.

**Example:**
```python
# Download using public URL
public_url = "https://my-bucket.oss.example.com/public/image.jpg"
result = session.oss.download_anonymous(public_url, "/tmp/downloaded_image.jpg")

if result.success:
    print("Anonymous download successful")
else:
    print("Anonymous download failed:", result.error_message)
```

## Response Types

For detailed information about response objects, see:
- **[OSSClientResult](../responses/oss-results.md#ossclientresult)** - OSS client initialization result
- **[OSSUploadResult](../responses/oss-results.md#ossuploadresult)** - OSS upload operation result
- **[OSSDownloadResult](../responses/oss-results.md#ossdownloadresult)** - OSS download operation result

## Usage Patterns

### Basic OSS Operations

```python
from agb import AGB

def basic_oss_operations():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        # Step 1: Initialize OSS environment
        init_result = session.oss.env_init(
            endpoint="https://oss.example.com",
            access_key_id="your_access_key_id",
            access_key_secret="your_access_key_secret",
            bucket_name="my-test-bucket"
        )

        if not init_result.success:
            print("❌ OSS initialization failed:", init_result.error_message)
            return

        print("✅ OSS environment initialized")

        # Step 2: Create a test file
        test_content = "Hello, OSS!\nThis is a test file for upload."
        session.file_system.write_file("/tmp/test_upload.txt", test_content)

        # Step 3: Upload the file
        upload_result = session.oss.upload(
            bucket="my-test-bucket",
            object="test-files/upload_test.txt",
            path="/tmp/test_upload.txt"
        )

        if upload_result.success:
            print("✅ File uploaded successfully")
            print("Upload info:", upload_result.content)

            # Step 4: Download the file to verify
            download_result = session.oss.download(
                bucket="my-test-bucket",
                object="test-files/upload_test.txt",
                path="/tmp/test_download.txt"
            )

            if download_result.success:
                print("✅ File downloaded successfully")

                # Verify content
                read_result = session.file_system.read_file("/tmp/test_download.txt")
                if read_result.success:
                    print("📄 Downloaded content:")
                    print(read_result.content)

                    if read_result.content == test_content:
                        print("✅ Content verification successful")
                    else:
                        print("❌ Content verification failed")
            else:
                print("❌ Download failed:", download_result.error_message)
        else:
            print("❌ Upload failed:", upload_result.error_message)

    finally:
        agb.delete(session)

basic_oss_operations()
```

### Anonymous OSS Operations

```python
def anonymous_oss_operations():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        # Create test content
        test_data = "Anonymous upload test\nTimestamp: 2023-12-01 10:30:00"
        session.file_system.write_file("/tmp/anonymous_test.txt", test_data)

        # Upload using pre-signed URL (example URL)
        presigned_upload_url = "https://example-bucket.oss-region.example.com/anonymous/test.txt?signature=..."

        upload_result = session.oss.upload_anonymous(
            url=presigned_upload_url,
            path="/tmp/anonymous_test.txt"
        )

        if upload_result.success:
            print("✅ Anonymous upload successful")

            # Download using public URL
            public_download_url = "https://example-bucket.oss-region.example.com/public/sample.txt"

            download_result = session.oss.download_anonymous(
                url=public_download_url,
                path="/tmp/public_download.txt"
            )

            if download_result.success:
                print("✅ Anonymous download successful")

                # Read downloaded content
                content_result = session.file_system.read_file("/tmp/public_download.txt")
                if content_result.success:
                    print("📄 Public file content:")
                    print(content_result.content)
            else:
                print("❌ Anonymous download failed:", download_result.error_message)
        else:
            print("❌ Anonymous upload failed:", upload_result.error_message)

    finally:
        agb.delete(session)

anonymous_oss_operations()
```

### Batch File Operations

```python
def batch_oss_operations():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        # Initialize OSS
        init_result = session.oss.env_init(
            endpoint="https://oss.example.com",
            access_key_id="your_access_key_id",
            access_key_secret="your_access_key_secret",
            bucket_name="batch-test-bucket"
        )

        if not init_result.success:
            print("❌ OSS initialization failed")
            return

        # Create multiple test files
        test_files = {}
        for i in range(5):
            filename = f"/tmp/batch_file_{i}.txt"
            content = f"Batch file {i}\nCreated for batch upload test\nFile number: {i}"
            session.file_system.write_file(filename, content)
            test_files[filename] = f"batch-uploads/file_{i}.txt"

        print(f"📄 Created {len(test_files)} test files")

        # Upload all files
        upload_results = []
        for local_path, remote_key in test_files.items():
            upload_result = session.oss.upload(
                bucket="batch-test-bucket",
                object=remote_key,
                path=local_path
            )

            upload_results.append({
                "local_path": local_path,
                "remote_key": remote_key,
                "success": upload_result.success,
                "error": upload_result.error_message if not upload_result.success else None
            })

        # Report upload results
        successful_uploads = [r for r in upload_results if r["success"]]
        failed_uploads = [r for r in upload_results if not r["success"]]

        print(f"✅ Successful uploads: {len(successful_uploads)}")
        print(f"❌ Failed uploads: {len(failed_uploads)}")

        if failed_uploads:
            print("Failed upload details:")
            for failure in failed_uploads:
                print(f"  - {failure['local_path']}: {failure['error']}")

        # Download and verify a few files
        verification_files = successful_uploads[:2]  # Verify first 2 successful uploads

        for file_info in verification_files:
            download_path = f"/tmp/verify_{file_info['remote_key'].split('/')[-1]}"

            download_result = session.oss.download(
                bucket="batch-test-bucket",
                object=file_info["remote_key"],
                path=download_path
            )

            if download_result.success:
                print(f"✅ Verified: {file_info['remote_key']}")
            else:
                print(f"❌ Verification failed for: {file_info['remote_key']}")

    finally:
        agb.delete(session)

batch_oss_operations()
```

### OSS with Data Processing Pipeline

```python
def oss_data_pipeline():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        # Initialize OSS
        init_result = session.oss.env_init(
            endpoint="https://oss.example.com",
            access_key_id="your_access_key_id",
            access_key_secret="your_access_key_secret",
            bucket_name="data-pipeline-bucket"
        )

        if not init_result.success:
            print("❌ OSS initialization failed")
            return

        # Step 1: Create sample data
        sample_data = """timestamp,temperature,humidity,pressure
2023-12-01 09:00:00,22.5,65,1013.2
2023-12-01 09:15:00,23.1,63,1013.5
2023-12-01 09:30:00,23.8,61,1013.1
2023-12-01 09:45:00,24.2,59,1012.8
2023-12-01 10:00:00,24.7,58,1012.5"""

        session.file_system.write_file("/tmp/sensor_data.csv", sample_data)

        # Step 2: Upload raw data to OSS
        upload_result = session.oss.upload(
            bucket="data-pipeline-bucket",
            object="raw-data/sensor_data.csv",
            path="/tmp/sensor_data.csv"
        )

        if not upload_result.success:
            print("❌ Failed to upload raw data")
            return

        print("✅ Raw data uploaded to OSS")

        # Step 3: Process data with code
        processing_code = """
import csv
from io import StringIO
from datetime import datetime

# Read the CSV data
with open('/tmp/sensor_data.csv', 'r') as f:
    csv_content = f.read()

# Parse and process data
reader = csv.DictReader(StringIO(csv_content))
data = list(reader)

# Calculate statistics
temperatures = [float(row['temperature']) for row in data]
avg_temp = sum(temperatures) / len(temperatures)
max_temp = max(temperatures)
min_temp = min(temperatures)

# Create summary report
report = f'''Sensor Data Analysis Report
Generated: {datetime.now().isoformat()}
================================

Data Points: {len(data)}
Temperature Statistics:
  - Average: {avg_temp:.2f}°C
  - Maximum: {max_temp:.2f}°C
  - Minimum: {min_temp:.2f}°C

Raw Data Summary:
'''

for i, row in enumerate(data, 1):
    report += f"  {i}. {row['timestamp']}: {row['temperature']}°C, {row['humidity']}%, {row['pressure']}hPa\\n"

# Save processed report
with open('/tmp/analysis_report.txt', 'w') as f:
    f.write(report)

print("Data analysis completed")
"""

        code_result = session.code.run_code(processing_code, "python")
        if not code_result.success:
            print("❌ Data processing failed:", code_result.error_message)
            return

        print("✅ Data processing completed")

        # Step 4: Upload processed report to OSS
        report_upload = session.oss.upload(
            bucket="data-pipeline-bucket",
            object="processed-data/analysis_report.txt",
            path="/tmp/analysis_report.txt"
        )

        if report_upload.success:
            print("✅ Analysis report uploaded to OSS")

            # Step 5: Download and display the report
            download_result = session.oss.download(
                bucket="data-pipeline-bucket",
                object="processed-data/analysis_report.txt",
                path="/tmp/downloaded_report.txt"
            )

            if download_result.success:
                report_content = session.file_system.read_file("/tmp/downloaded_report.txt")
                if report_content.success:
                    print("\n📊 Analysis Report:")
                    print("=" * 50)
                    print(report_content.content)
        else:
            print("❌ Failed to upload analysis report")

    finally:
        agb.delete(session)

oss_data_pipeline()
```

## Best Practices

### 1. Always Initialize OSS Environment

```python
# ✅ Good: Initialize OSS before operations
init_result = session.oss.env_init(endpoint, access_key_id, access_key_secret, bucket_name)
if init_result.success:
    # Proceed with OSS operations
    pass
else:
    # Handle initialization error
    print("OSS initialization failed:", init_result.error_message)

# ❌ Bad: Using OSS operations without initialization
upload_result = session.oss.upload(bucket, object, path)  # May fail
```

### 2. Use Meaningful Object Keys

```python
# ✅ Good: Organized object keys
session.oss.upload("my-bucket", "documents/2023/reports/monthly_report.pdf", local_path)
session.oss.upload("my-bucket", "images/thumbnails/product_123.jpg", local_path)
session.oss.upload("my-bucket", "data/processed/2023-12-01/sensor_data.csv", local_path)

# ❌ Avoid: Unclear or flat structure
session.oss.upload("my-bucket", "file1.pdf", local_path)
session.oss.upload("my-bucket", "img.jpg", local_path)
```

### 3. Handle Large Files Appropriately

```python
def upload_large_file(session, bucket, object_key, local_path):
    """Upload large file with proper error handling"""

    # Check file size first
    info_result = session.file_system.get_file_info(local_path)
    if info_result.success:
        file_size = info_result.file_info.get('size', 0)
        if file_size > 100 * 1024 * 1024:  # > 100MB
            print(f"Warning: Large file detected ({file_size} bytes)")

    # Upload with error handling
    upload_result = session.oss.upload(bucket, object_key, local_path)

    if upload_result.success:
        print(f"✅ Large file uploaded: {object_key}")
        return True
    else:
        print(f"❌ Large file upload failed: {upload_result.error_message}")
        return False
```

### 4. Verify Upload/Download Operations

```python
def verified_upload(session, bucket, object_key, local_path):
    """Upload file with verification"""

    # Read original content
    original_result = session.file_system.read_file(local_path)
    if not original_result.success:
        return False, "Cannot read original file"

    # Upload file
    upload_result = session.oss.upload(bucket, object_key, local_path)
    if not upload_result.success:
        return False, f"Upload failed: {upload_result.error_message}"

    # Download to verify
    verify_path = f"/tmp/verify_{hash(object_key)}.tmp"
    download_result = session.oss.download(bucket, object_key, verify_path)

    if download_result.success:
        # Compare content
        verify_result = session.file_system.read_file(verify_path)
        if verify_result.success and verify_result.content == original_result.content:
            # Clean up verification file
            session.command.execute_command(f"rm -f {verify_path}")
            return True, "Upload verified successfully"

    return False, "Upload verification failed"
```

### 5. Use Environment Variables for Credentials

```python
import os

def secure_oss_init(session):
    """Initialize OSS with environment variables"""

    endpoint = os.getenv("OSS_ENDPOINT")
    access_key_id = os.getenv("OSS_ACCESS_KEY_ID")
    access_key_secret = os.getenv("OSS_ACCESS_KEY_SECRET")
    bucket_name = os.getenv("OSS_BUCKET_NAME")

    if not all([endpoint, access_key_id, access_key_secret, bucket_name]):
        return False, "Missing OSS environment variables"

    result = session.oss.env_init(endpoint, access_key_id, access_key_secret, bucket_name)
    return result.success, result.error_message if not result.success else "Initialized"

# Usage
success, message = secure_oss_init(session)
if success:
    print("✅ OSS initialized securely")
else:
    print("❌ OSS initialization failed:", message)
```

## Error Handling

### Common Error Types

**Authentication Errors:**
```python
init_result = session.oss.env_init(endpoint, "invalid_key", "invalid_secret", bucket)
if not init_result.success:
    if "authentication" in init_result.error_message.lower():
        print("Check your access credentials")
```

**Network Errors:**
```python
upload_result = session.oss.upload(bucket, object_key, path)
if not upload_result.success:
    if "network" in upload_result.error_message.lower() or "timeout" in upload_result.error_message.lower():
        print("Network issue - retry upload")
```

**File Not Found:**
```python
upload_result = session.oss.upload(bucket, object_key, "/nonexistent/file.txt")
if not upload_result.success:
    if "not found" in upload_result.error_message.lower():
        print("Local file doesn't exist")
```

**Bucket/Object Errors:**
```python
download_result = session.oss.download("nonexistent-bucket", "object", "/tmp/file")
if not download_result.success:
    if "bucket" in download_result.error_message.lower():
        print("Bucket doesn't exist or no access")
    elif "object" in download_result.error_message.lower():
        print("Object not found in bucket")
```

### Robust OSS Operations

```python
def robust_oss_operation(session, operation_type, **kwargs):
    """Execute OSS operation with retry logic"""

    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            if operation_type == "upload":
                result = session.oss.upload(kwargs["bucket"], kwargs["object"], kwargs["path"])
            elif operation_type == "download":
                result = session.oss.download(kwargs["bucket"], kwargs["object"], kwargs["path"])
            elif operation_type == "upload_anonymous":
                result = session.oss.upload_anonymous(kwargs["url"], kwargs["path"])
            elif operation_type == "download_anonymous":
                result = session.oss.download_anonymous(kwargs["url"], kwargs["path"])
            else:
                return {"success": False, "error": "Unknown operation type"}

            if result.success:
                return {"success": True, "result": result}
            else:
                # Check if error is retryable
                error_msg = result.error_message.lower()
                if any(retryable in error_msg for retryable in ["timeout", "network", "temporary"]):
                    if attempt < max_retries - 1:
                        print(f"Attempt {attempt + 1} failed, retrying in {retry_delay}s...")
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue

                return {"success": False, "error": result.error_message}

        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Exception on attempt {attempt + 1}: {e}")
                import time
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                return {"success": False, "error": str(e)}

    return {"success": False, "error": "All retry attempts failed"}

# Usage
result = robust_oss_operation(session, "upload",
                             bucket="my-bucket",
                             object="test.txt",
                             path="/tmp/test.txt")
if result["success"]:
    print("✅ Operation succeeded")
else:
    print("❌ Operation failed:", result["error"])
```

## Integration with Other Modules

### OSS + FileSystem Integration

```python
# Create file with FileSystem
session.file_system.write_file("/tmp/data.json", '{"key": "value"}')

# Upload to OSS
session.oss.upload("my-bucket", "data/file.json", "/tmp/data.json")

# Download from OSS
session.oss.download("my-bucket", "data/file.json", "/tmp/downloaded.json")

# Read with FileSystem
result = session.file_system.read_file("/tmp/downloaded.json")
```

### OSS + Code Integration

```python
# Generate data with code
session.code.run_code("""
import json
data = {"processed": True, "timestamp": "2023-12-01", "values": [1,2,3]}
with open('/tmp/generated.json', 'w') as f:
    json.dump(data, f)
print("Data generated")
""", "python")

# Upload generated data
session.oss.upload("my-bucket", "generated/data.json", "/tmp/generated.json")
```

## Related Documentation

- **[Session API](../core/session.md)** - Session management and lifecycle
- **[FileSystem Module](filesystem.md)** - File operations for OSS integration
- **[Code Module](code.md)** - Code execution for data processing
- **[OSS Integration Guide](../../guides/oss-integration.md)** - User guide for OSS operations
- **[Best Practices](../../guides/best-practices.md)** - Production deployment patterns