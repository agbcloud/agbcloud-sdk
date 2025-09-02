# OSS Integration Tutorial

## Overview

This tutorial teaches you how to integrate Object Storage Service (OSS) with the AGB cloud environment. You'll learn to upload and download files, manage cloud storage, and build data processing pipelines that leverage cloud storage capabilities.

## Quick Reference (1 minute)

```python
from agb import AGB

agb = AGB()
session = agb.create().session

# Initialize OSS
session.oss.env_init(
    endpoint="https://oss.example.com",
    access_key_id="your_access_key_id",
    access_key_secret="your_access_key_secret",
    bucket_name="my-bucket"
)

# Upload file
session.oss.upload("my-bucket", "path/file.txt", "/tmp/local_file.txt")

# Download file
session.oss.download("my-bucket", "path/file.txt", "/tmp/downloaded_file.txt")

agb.delete(session)
```

## Step-by-Step Tutorial (15 minutes)

### Step 1: OSS Environment Setup

```python
from agb import AGB
import os

def setup_oss_environment():
    agb = AGB()
    session = agb.create().session
    
    try:
        # OSS configuration (use environment variables in production)
        oss_config = {
            "endpoint": "https://oss.example.com",
            "access_key_id": "your_access_key_id",  # Use env var: os.getenv("OSS_ACCESS_KEY_ID")
            "access_key_secret": "your_access_key_secret",  # Use env var: os.getenv("OSS_ACCESS_KEY_SECRET")
            "bucket_name": "tutorial-bucket"
        }
        
        # Initialize OSS environment
        init_result = session.oss.env_init(
            endpoint=oss_config["endpoint"],
            access_key_id=oss_config["access_key_id"],
            access_key_secret=oss_config["access_key_secret"],
            bucket_name=oss_config["bucket_name"]
        )
        
        if init_result.success:
            print("✅ OSS environment initialized successfully")
            print("Client configuration:")
            for key, value in init_result.client_config.items():
                # Don't print sensitive information
                if "secret" in key.lower():
                    print(f"  {key}: [HIDDEN]")
                else:
                    print(f"  {key}: {value}")
            return True
        else:
            print("❌ OSS initialization failed:", init_result.error_message)
            return False
    
    finally:
        agb.delete(session)

# Test OSS setup
setup_oss_environment()
```

### Step 2: Basic File Upload and Download

```python
def basic_file_operations():
    agb = AGB()
    session = agb.create().session
    
    try:
        # Initialize OSS (replace with your credentials)
        init_result = session.oss.env_init(
            endpoint="https://oss.example.com",
            access_key_id="your_access_key_id",
            access_key_secret="your_access_key_secret",
            bucket_name="tutorial-bucket"
        )
        
        if not init_result.success:
            print("❌ OSS initialization failed")
            return
        
        # Step 1: Create a test file
        test_content = """Hello OSS!
This is a test file for upload.
Created at: 2023-12-01 10:30:00
Content: Sample data for OSS tutorial"""
        
        local_file_path = "/tmp/test_upload.txt"
        write_result = session.file_system.write_file(local_file_path, test_content)
        
        if write_result.success:
            print("✅ Test file created locally")
            
            # Step 2: Upload file to OSS
            upload_result = session.oss.upload(
                bucket="tutorial-bucket",
                object="tutorial/test_file.txt",
                path=local_file_path
            )
            
            if upload_result.success:
                print("✅ File uploaded to OSS successfully")
                print("Upload result:", upload_result.content)
                
                # Step 3: Download file from OSS
                download_path = "/tmp/test_download.txt"
                download_result = session.oss.download(
                    bucket="tutorial-bucket",
                    object="tutorial/test_file.txt",
                    path=download_path
                )
                
                if download_result.success:
                    print("✅ File downloaded from OSS successfully")
                    
                    # Step 4: Verify content integrity
                    downloaded_content = session.file_system.read_file(download_path)
                    if downloaded_content.success:
                        if downloaded_content.content == test_content:
                            print("✅ Content verification successful")
                            print("File integrity maintained through upload/download cycle")
                        else:
                            print("❌ Content verification failed")
                            print("Original length:", len(test_content))
                            print("Downloaded length:", len(downloaded_content.content))
                    else:
                        print("❌ Failed to read downloaded file")
                else:
                    print("❌ Download failed:", download_result.error_message)
            else:
                print("❌ Upload failed:", upload_result.error_message)
        else:
            print("❌ Failed to create test file")
    
    finally:
        agb.delete(session)

basic_file_operations()
```

### Step 3: Anonymous/Public File Operations

```python
def anonymous_file_operations():
    agb = AGB()
    session = agb.create().session
    
    try:
        print("🌐 Anonymous OSS Operations Tutorial")
        
        # Create test content for anonymous upload
        anonymous_content = """Anonymous Upload Test
This file was uploaded using a pre-signed URL.
Timestamp: 2023-12-01 11:00:00
Public access test content."""
        
        local_file = "/tmp/anonymous_test.txt"
        session.file_system.write_file(local_file, anonymous_content)
        
        print("✅ Test file created for anonymous upload")
        
        # Example of anonymous upload (requires pre-signed URL from your OSS service)
        # In practice, you would get this URL from your backend service
        presigned_upload_url = "https://your-bucket.oss-region.example.com/public/test.txt?signature=..."
        
        print("📤 Attempting anonymous upload...")
        upload_result = session.oss.upload_anonymous(
            url=presigned_upload_url,
            path=local_file
        )
        
        if upload_result.success:
            print("✅ Anonymous upload successful")
            print("Upload response:", upload_result.content)
        else:
            print("❌ Anonymous upload failed:", upload_result.error_message)
            print("Note: This requires a valid pre-signed URL from your OSS service")
        
        # Example of anonymous download (public file)
        # This would be a public URL or pre-signed download URL
        public_download_url = "https://your-bucket.oss-region.example.com/public/sample.txt"
        
        print("\n📥 Attempting anonymous download...")
        download_result = session.oss.download_anonymous(
            url=public_download_url,
            path="/tmp/public_download.txt"
        )
        
        if download_result.success:
            print("✅ Anonymous download successful")
            
            # Read downloaded content
            content_result = session.file_system.read_file("/tmp/public_download.txt")
            if content_result.success:
                print("📄 Downloaded content preview:")
                print(content_result.content[:200] + "..." if len(content_result.content) > 200 else content_result.content)
        else:
            print("❌ Anonymous download failed:", download_result.error_message)
            print("Note: This requires a valid public or pre-signed URL")
        
        # Demonstrate URL generation concept (pseudo-code)
        print("\n💡 URL Generation Concept:")
        print("For production use, implement URL generation on your backend:")
        print("""
# Backend service example (Python)
def generate_presigned_upload_url(bucket, object_key, expiration=3600):
    # Use your OSS SDK to generate pre-signed URL
    return oss_client.generate_presigned_url(
        'put_object',
        Params={'Bucket': bucket, 'Key': object_key},
        ExpiresIn=expiration
    )

# Then use the generated URL with AGB
upload_url = generate_presigned_upload_url('my-bucket', 'uploads/file.txt')
session.oss.upload_anonymous(upload_url, '/tmp/file.txt')
        """)
    
    finally:
        agb.delete(session)

anonymous_file_operations()
```

### Step 4: Batch File Operations

```python
def batch_file_operations():
    agb = AGB()
    session = agb.create().session
    
    try:
        print("📦 Batch OSS Operations Tutorial")
        
        # Initialize OSS
        init_result = session.oss.env_init(
            endpoint="https://oss.example.com",
            access_key_id="your_access_key_id",
            access_key_secret="your_access_key_secret",
            bucket_name="batch-tutorial-bucket"
        )
        
        if not init_result.success:
            print("❌ OSS initialization failed")
            return
        
        # Step 1: Create multiple test files
        test_files = {}
        file_types = ["data", "config", "log", "report", "backup"]
        
        for i, file_type in enumerate(file_types):
            filename = f"/tmp/batch_{file_type}_{i}.txt"
            content = f"""{file_type.upper()} File {i}
Type: {file_type}
Created: 2023-12-01 12:00:0{i}
Size: {len(file_type) * 100} bytes of sample data
{'Sample data line ' * 10}
End of {file_type} file."""
            
            write_result = session.file_system.write_file(filename, content)
            if write_result.success:
                test_files[filename] = f"batch-upload/{file_type}/file_{i}.txt"
                print(f"✅ Created {filename}")
        
        print(f"\n📄 Created {len(test_files)} test files")
        
        # Step 2: Batch upload files
        upload_results = []
        print("\n📤 Starting batch upload...")
        
        for local_path, remote_key in test_files.items():
            upload_result = session.oss.upload(
                bucket="batch-tutorial-bucket",
                object=remote_key,
                path=local_path
            )
            
            result_info = {
                "local_path": local_path,
                "remote_key": remote_key,
                "success": upload_result.success,
                "error": upload_result.error_message if not upload_result.success else None
            }
            upload_results.append(result_info)
            
            if upload_result.success:
                print(f"✅ Uploaded: {remote_key}")
            else:
                print(f"❌ Failed: {remote_key} - {upload_result.error_message}")
        
        # Step 3: Upload summary
        successful_uploads = [r for r in upload_results if r["success"]]
        failed_uploads = [r for r in upload_results if not r["success"]]
        
        print(f"\n📊 Upload Summary:")
        print(f"  ✅ Successful: {len(successful_uploads)}")
        print(f"  ❌ Failed: {len(failed_uploads)}")
        
        if failed_uploads:
            print("\n❌ Failed uploads:")
            for failure in failed_uploads:
                print(f"  - {failure['remote_key']}: {failure['error']}")
        
        # Step 4: Selective download and verification
        if successful_uploads:
            print(f"\n📥 Verifying uploads by downloading...")
            
            # Download first 3 successful uploads for verification
            verification_files = successful_uploads[:3]
            
            for file_info in verification_files:
                download_path = f"/tmp/verify_{file_info['remote_key'].split('/')[-1]}"
                
                download_result = session.oss.download(
                    bucket="batch-tutorial-bucket",
                    object=file_info["remote_key"],
                    path=download_path
                )
                
                if download_result.success:
                    # Compare with original
                    original_content = session.file_system.read_file(file_info["local_path"])
                    downloaded_content = session.file_system.read_file(download_path)
                    
                    if (original_content.success and downloaded_content.success and 
                        original_content.content == downloaded_content.content):
                        print(f"✅ Verified: {file_info['remote_key']}")
                    else:
                        print(f"❌ Verification failed: {file_info['remote_key']}")
                else:
                    print(f"❌ Download failed: {file_info['remote_key']}")
        
        # Step 5: Create batch operation report
        report_content = f"""Batch OSS Operations Report
Generated: 2023-12-01 12:30:00
========================================

Operation Summary:
- Total files processed: {len(test_files)}
- Successful uploads: {len(successful_uploads)}
- Failed uploads: {len(failed_uploads)}
- Success rate: {len(successful_uploads)/len(test_files)*100:.1f}%

File Details:
"""
        
        for result in upload_results:
            status = "SUCCESS" if result["success"] else "FAILED"
            report_content += f"- {result['remote_key']}: {status}\n"
            if not result["success"]:
                report_content += f"  Error: {result['error']}\n"
        
        # Save and upload report
        report_path = "/tmp/batch_operation_report.txt"
        session.file_system.write_file(report_path, report_content)
        
        report_upload = session.oss.upload(
            bucket="batch-tutorial-bucket",
            object="reports/batch_operation_report.txt",
            path=report_path
        )
        
        if report_upload.success:
            print("\n📋 Batch operation report uploaded to OSS")
        
    finally:
        agb.delete(session)

batch_file_operations()
```

## Advanced Usage (30 minutes)

### Data Processing Pipeline with OSS

```python
def data_processing_pipeline():
    agb = AGB()
    session = agb.create().session
    
    try:
        print("🚀 Data Processing Pipeline with OSS")
        
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
        
        # Step 1: Create sample dataset
        print("📊 Step 1: Creating sample dataset...")
        
        sample_data = """timestamp,user_id,action,value,category
2023-12-01 09:00:00,user_001,login,1,authentication
2023-12-01 09:01:15,user_001,view_page,1,navigation
2023-12-01 09:02:30,user_002,login,1,authentication
2023-12-01 09:03:45,user_001,purchase,150.00,transaction
2023-12-01 09:05:00,user_003,login,1,authentication
2023-12-01 09:06:15,user_002,view_page,1,navigation
2023-12-01 09:07:30,user_003,purchase,75.50,transaction
2023-12-01 09:08:45,user_001,logout,1,authentication
2023-12-01 09:10:00,user_002,purchase,200.25,transaction
2023-12-01 09:11:15,user_003,view_page,1,navigation
2023-12-01 09:12:30,user_002,logout,1,authentication
2023-12-01 09:13:45,user_003,logout,1,authentication"""
        
        # Save raw data locally
        raw_data_path = "/tmp/raw_user_activity.csv"
        session.file_system.write_file(raw_data_path, sample_data)
        
        # Upload raw data to OSS
        raw_upload = session.oss.upload(
            bucket="data-pipeline-bucket",
            object="raw-data/user_activity.csv",
            path=raw_data_path
        )
        
        if raw_upload.success:
            print("✅ Raw data uploaded to OSS")
        else:
            print("❌ Failed to upload raw data")
            return
        
        # Step 2: Process data with code
        print("\n⚙️ Step 2: Processing data...")
        
        processing_code = """
import csv
from io import StringIO
from collections import defaultdict
from datetime import datetime

# Read the CSV data
with open('/tmp/raw_user_activity.csv', 'r') as f:
    csv_content = f.read()

# Parse CSV data
reader = csv.DictReader(StringIO(csv_content))
activities = list(reader)

print(f"Loaded {len(activities)} activity records")

# Data analysis
user_stats = defaultdict(lambda: {'logins': 0, 'purchases': 0, 'total_spent': 0.0, 'page_views': 0})
category_stats = defaultdict(int)
hourly_activity = defaultdict(int)

for activity in activities:
    user_id = activity['user_id']
    action = activity['action']
    value = float(activity['value'])
    category = activity['category']
    timestamp = activity['timestamp']
    
    # Update user statistics
    if action == 'login':
        user_stats[user_id]['logins'] += 1
    elif action == 'purchase':
        user_stats[user_id]['purchases'] += 1
        user_stats[user_id]['total_spent'] += value
    elif action == 'view_page':
        user_stats[user_id]['page_views'] += 1
    
    # Update category statistics
    category_stats[category] += 1
    
    # Update hourly activity
    hour = timestamp.split(' ')[1].split(':')[0]
    hourly_activity[hour] += 1

# Generate user summary report
user_report = "User Activity Summary\\n" + "=" * 25 + "\\n\\n"
for user_id, stats in user_stats.items():
    user_report += f"User: {user_id}\\n"
    user_report += f"  Logins: {stats['logins']}\\n"
    user_report += f"  Purchases: {stats['purchases']}\\n"
    user_report += f"  Total Spent: ${stats['total_spent']:.2f}\\n"
    user_report += f"  Page Views: {stats['page_views']}\\n\\n"

# Generate category summary
category_report = "Category Activity Summary\\n" + "=" * 28 + "\\n\\n"
for category, count in category_stats.items():
    category_report += f"{category.title()}: {count} activities\\n"

# Generate hourly summary
hourly_report = "Hourly Activity Summary\\n" + "=" * 26 + "\\n\\n"
for hour in sorted(hourly_activity.keys()):
    hourly_report += f"Hour {hour}:00: {hourly_activity[hour]} activities\\n"

# Save processed reports
with open('/tmp/user_summary.txt', 'w') as f:
    f.write(user_report)

with open('/tmp/category_summary.txt', 'w') as f:
    f.write(category_report)

with open('/tmp/hourly_summary.txt', 'w') as f:
    f.write(hourly_report)

# Create aggregated data CSV
aggregated_data = []
for user_id, stats in user_stats.items():
    aggregated_data.append([
        user_id,
        stats['logins'],
        stats['purchases'],
        stats['total_spent'],
        stats['page_views']
    ])

with open('/tmp/user_aggregated.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['user_id', 'logins', 'purchases', 'total_spent', 'page_views'])
    writer.writerows(aggregated_data)

print("Data processing completed successfully")
print(f"Generated reports for {len(user_stats)} users")
print(f"Processed {len(activities)} total activities")
"""
        
        code_result = session.code.run_code(processing_code, "python")
        if code_result.success:
            print("✅ Data processing completed")
            print(code_result.result)
        else:
            print("❌ Data processing failed:", code_result.error_message)
            return
        
        # Step 3: Upload processed results to OSS
        print("\n📤 Step 3: Uploading processed results...")
        
        processed_files = [
            ("/tmp/user_summary.txt", "processed-data/reports/user_summary.txt"),
            ("/tmp/category_summary.txt", "processed-data/reports/category_summary.txt"),
            ("/tmp/hourly_summary.txt", "processed-data/reports/hourly_summary.txt"),
            ("/tmp/user_aggregated.csv", "processed-data/aggregated/user_data.csv")
        ]
        
        upload_success_count = 0
        for local_path, remote_key in processed_files:
            upload_result = session.oss.upload(
                bucket="data-pipeline-bucket",
                object=remote_key,
                path=local_path
            )
            
            if upload_result.success:
                print(f"✅ Uploaded: {remote_key}")
                upload_success_count += 1
            else:
                print(f"❌ Failed to upload: {remote_key}")
        
        # Step 4: Create pipeline summary and upload
        print(f"\n📋 Step 4: Creating pipeline summary...")
        
        pipeline_summary = f"""Data Processing Pipeline Summary
Generated: {datetime.now().isoformat()}
==========================================

Pipeline Status: {'SUCCESS' if upload_success_count == len(processed_files) else 'PARTIAL_SUCCESS'}

Input Data:
- Source: raw-data/user_activity.csv
- Records processed: {len(sample_data.split('\\n')) - 1}

Processing Results:
- User summary report: {'✅' if upload_success_count > 0 else '❌'}
- Category analysis: {'✅' if upload_success_count > 1 else '❌'}
- Hourly activity report: {'✅' if upload_success_count > 2 else '❌'}
- Aggregated data: {'✅' if upload_success_count > 3 else '❌'}

Output Files:
- processed-data/reports/user_summary.txt
- processed-data/reports/category_summary.txt
- processed-data/reports/hourly_summary.txt
- processed-data/aggregated/user_data.csv

Pipeline completed at: {datetime.now().isoformat()}
Success rate: {upload_success_count}/{len(processed_files)} files uploaded
"""
        
        # Save and upload pipeline summary
        summary_path = "/tmp/pipeline_summary.txt"
        session.file_system.write_file(summary_path, pipeline_summary)
        
        summary_upload = session.oss.upload(
            bucket="data-pipeline-bucket",
            object="pipeline-logs/summary.txt",
            path=summary_path
        )
        
        if summary_upload.success:
            print("✅ Pipeline summary uploaded")
        
        # Step 5: Download and display one of the reports
        print("\n📥 Step 5: Downloading sample report for verification...")
        
        download_result = session.oss.download(
            bucket="data-pipeline-bucket",
            object="processed-data/reports/user_summary.txt",
            path="/tmp/downloaded_user_summary.txt"
        )
        
        if download_result.success:
            report_content = session.file_system.read_file("/tmp/downloaded_user_summary.txt")
            if report_content.success:
                print("\n📊 User Summary Report:")
                print("=" * 50)
                print(report_content.content)
        
        print(f"\n🎉 Data processing pipeline completed successfully!")
        print(f"   Processed files uploaded to OSS bucket: data-pipeline-bucket")
    
    finally:
        agb.delete(session)

data_processing_pipeline()
```

### Backup and Archive System

```python
def backup_archive_system():
    agb = AGB()
    session = agb.create().session
    
    try:
        print("💾 Backup and Archive System with OSS")
        
        # Initialize OSS
        init_result = session.oss.env_init(
            endpoint="https://oss.example.com",
            access_key_id="your_access_key_id",
            access_key_secret="your_access_key_secret",
            bucket_name="backup-archive-bucket"
        )
        
        if not init_result.success:
            print("❌ OSS initialization failed")
            return
        
        # Step 1: Create sample application data
        print("📁 Step 1: Creating sample application data...")
        
        # Create directory structure
        directories = [
            "/tmp/app_data/configs",
            "/tmp/app_data/logs",
            "/tmp/app_data/user_data",
            "/tmp/app_data/temp"
        ]
        
        for directory in directories:
            session.command.execute_command(f"mkdir -p {directory}")
        
        # Create sample files
        sample_files = {
            "/tmp/app_data/configs/app.conf": """[database]
host=localhost
port=5432
name=myapp

[cache]
host=redis-server
port=6379

[logging]
level=INFO
file=/var/log/app.log""",
            
            "/tmp/app_data/configs/secrets.conf": """api_key=secret_key_12345
db_password=super_secret_password
jwt_secret=jwt_signing_secret""",
            
            "/tmp/app_data/logs/app.log": """2023-12-01 10:00:00 INFO Application started
2023-12-01 10:00:01 INFO Database connection established
2023-12-01 10:01:00 INFO User alice logged in
2023-12-01 10:02:00 WARNING High memory usage detected
2023-12-01 10:03:00 INFO User bob logged in
2023-12-01 10:04:00 ERROR Database connection lost
2023-12-01 10:04:01 INFO Database connection restored""",
            
            "/tmp/app_data/user_data/users.json": """{
  "users": [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
  ]
}""",
            
            "/tmp/app_data/temp/cache.tmp": "temporary cache data that should not be backed up"
        }
        
        for filepath, content in sample_files.items():
            session.file_system.write_file(filepath, content)
        
        print(f"✅ Created {len(sample_files)} sample files")
        
        # Step 2: Create selective backup (exclude temp files)
        print("\n💾 Step 2: Creating selective backup...")
        
        # Get list of files to backup (exclude temp directory)
        list_result = session.command.execute_command("find /tmp/app_data -type f ! -path '*/temp/*'")
        
        if list_result.success:
            backup_files = [f.strip() for f in list_result.output.strip().split('\n') if f.strip()]
            print(f"Found {len(backup_files)} files to backup")
            
            # Create backup manifest
            manifest_content = f"""Backup Manifest
Created: {datetime.now().isoformat()}
===============================

Files included in backup:
"""
            
            backup_results = []
            for local_file in backup_files:
                # Create relative path for OSS storage
                relative_path = local_file.replace('/tmp/app_data/', '')
                oss_key = f"backups/2023-12-01/{relative_path}"
                
                # Upload file
                upload_result = session.oss.upload(
                    bucket="backup-archive-bucket",
                    object=oss_key,
                    path=local_file
                )
                
                backup_results.append({
                    "local_path": local_file,
                    "oss_key": oss_key,
                    "success": upload_result.success,
                    "error": upload_result.error_message if not upload_result.success else None
                })
                
                if upload_result.success:
                    # Get file info for manifest
                    file_info = session.file_system.get_file_info(local_file)
                    if file_info.success:
                        size = file_info.file_info.get('size', 'unknown')
                        manifest_content += f"✅ {relative_path} ({size} bytes) -> {oss_key}\n"
                    else:
                        manifest_content += f"✅ {relative_path} -> {oss_key}\n"
                    print(f"✅ Backed up: {relative_path}")
                else:
                    manifest_content += f"❌ {relative_path} -> FAILED: {upload_result.error_message}\n"
                    print(f"❌ Failed: {relative_path}")
            
            # Upload backup manifest
            manifest_path = "/tmp/backup_manifest.txt"
            session.file_system.write_file(manifest_path, manifest_content)
            
            manifest_upload = session.oss.upload(
                bucket="backup-archive-bucket",
                object="backups/2023-12-01/manifest.txt",
                path=manifest_path
            )
            
            if manifest_upload.success:
                print("✅ Backup manifest uploaded")
        
        # Step 3: Create compressed archive
        print("\n📦 Step 3: Creating compressed archive...")
        
        # Create tar.gz archive of configs and user data
        archive_cmd = "cd /tmp && tar -czf app_backup_2023-12-01.tar.gz -C app_data configs user_data"
        archive_result = session.command.execute_command(archive_cmd)
        
        if archive_result.success:
            print("✅ Compressed archive created")
            
            # Upload compressed archive
            archive_upload = session.oss.upload(
                bucket="backup-archive-bucket",
                object="archives/app_backup_2023-12-01.tar.gz",
                path="/tmp/app_backup_2023-12-01.tar.gz"
            )
            
            if archive_upload.success:
                print("✅ Compressed archive uploaded to OSS")
                
                # Get archive size
                archive_info = session.command.execute_command("ls -lh /tmp/app_backup_2023-12-01.tar.gz")
                if archive_info.success:
                    print(f"Archive info: {archive_info.output.strip()}")
        
        # Step 4: Backup verification
        print("\n🔍 Step 4: Backup verification...")
        
        # Download and verify a sample file
        test_file_key = "backups/2023-12-01/configs/app.conf"
        verify_download_path = "/tmp/verify_app.conf"
        
        verify_download = session.oss.download(
            bucket="backup-archive-bucket",
            object=test_file_key,
            path=verify_download_path
        )
        
        if verify_download.success:
            # Compare with original
            original_content = session.file_system.read_file("/tmp/app_data/configs/app.conf")
            downloaded_content = session.file_system.read_file(verify_download_path)
            
            if (original_content.success and downloaded_content.success and 
                original_content.content == downloaded_content.content):
                print("✅ Backup verification successful")
            else:
                print("❌ Backup verification failed")
        
        # Step 5: Create backup summary report
        print("\n📋 Step 5: Creating backup summary...")
        
        successful_backups = [r for r in backup_results if r["success"]]
        failed_backups = [r for r in backup_results if not r["success"]]
        
        backup_summary = f"""Backup Operation Summary
Generated: {datetime.now().isoformat()}
================================

Backup Status: {'SUCCESS' if len(failed_backups) == 0 else 'PARTIAL_SUCCESS'}

Statistics:
- Total files processed: {len(backup_results)}
- Successful backups: {len(successful_backups)}
- Failed backups: {len(failed_backups)}
- Success rate: {len(successful_backups)/len(backup_results)*100:.1f}%

Backup Locations:
- Individual files: backups/2023-12-01/
- Compressed archive: archives/app_backup_2023-12-01.tar.gz
- Backup manifest: backups/2023-12-01/manifest.txt

Excluded from backup:
- /tmp/app_data/temp/ (temporary files)

Next backup recommended: 2023-12-02
"""
        
        if failed_backups:
            backup_summary += "\nFailed Backups:\n"
            for failure in failed_backups:
                backup_summary += f"- {failure['local_path']}: {failure['error']}\n"
        
        # Save and upload summary
        summary_path = "/tmp/backup_summary.txt"
        session.file_system.write_file(summary_path, backup_summary)
        
        summary_upload = session.oss.upload(
            bucket="backup-archive-bucket",
            object="backup-reports/summary_2023-12-01.txt",
            path=summary_path
        )
        
        if summary_upload.success:
            print("✅ Backup summary uploaded")
            
            # Display summary
            print("\n📊 Backup Summary:")
            print("=" * 50)
            print(backup_summary)
        
        print(f"\n🎉 Backup and archive system completed!")
        print(f"   All backups stored in OSS bucket: backup-archive-bucket")
    
    finally:
        agb.delete(session)

backup_archive_system()
```

## Best Practices

### 1. Secure Credential Management

```python
import os

# ✅ Good: Use environment variables for credentials
def secure_oss_setup(session):
    """Initialize OSS with secure credential management"""
    
    # Load credentials from environment variables
    oss_config = {
        "endpoint": os.getenv("OSS_ENDPOINT"),
        "access_key_id": os.getenv("OSS_ACCESS_KEY_ID"),
        "access_key_secret": os.getenv("OSS_ACCESS_KEY_SECRET"),
        "bucket_name": os.getenv("OSS_BUCKET_NAME")
    }
    
    # Validate all required credentials are present
    missing_vars = [key for key, value in oss_config.items() if not value]
    if missing_vars:
        return False, f"Missing environment variables: {', '.join(missing_vars)}"
    
    # Initialize OSS
    result = session.oss.env_init(**oss_config)
    return result.success, result.error_message if not result.success else "Initialized"

# ❌ Bad: Hardcoded credentials
def insecure_oss_setup(session):
    session.oss.env_init(
        endpoint="https://oss-region.example.com",
        access_key_id="hardcoded_key",  # Security risk!
        access_key_secret="hardcoded_secret",  # Security risk!
        bucket_name="my-bucket"
    )
```

### 2. Organized Object Key Structure

```python
# ✅ Good: Hierarchical and meaningful object keys
def upload_with_good_structure(session, file_type, content, metadata=None):
    """Upload file with organized object key structure"""
    
    from datetime import datetime
    
    # Create hierarchical structure
    date_prefix = datetime.now().strftime("%Y/%m/%d")
    timestamp = datetime.now().strftime("%H%M%S")
    
    object_key = f"{file_type}/{date_prefix}/{timestamp}_{metadata or 'file'}.txt"
    
    # Examples of good structure:
    # logs/2023/12/01/103000_application.log
    # data/2023/12/01/103000_user_activity.csv
    # reports/2023/12/01/103000_monthly_summary.pdf
    # backups/2023/12/01/103000_database_dump.sql
    
    return session.oss.upload("my-bucket", object_key, "/tmp/file.txt")

# ❌ Avoid: Flat structure without organization
def upload_with_poor_structure(session):
    # Poor examples:
    # file1.txt
    # data.csv
    # report.pdf
    # backup.sql
    pass
```

### 3. Error Handling and Retry Logic

```python
def robust_oss_upload(session, bucket, object_key, local_path, max_retries=3):
    """Upload file with comprehensive error handling and retry logic"""
    
    import time
    
    for attempt in range(max_retries):
        try:
            # Check if local file exists
            file_info = session.file_system.get_file_info(local_path)
            if not file_info.success:
                return {"success": False, "error": "Local file not found", "retryable": False}
            
            # Attempt upload
            upload_result = session.oss.upload(bucket, object_key, local_path)
            
            if upload_result.success:
                return {
                    "success": True,
                    "object_key": object_key,
                    "attempts": attempt + 1,
                    "file_size": file_info.file_info.get('size', 'unknown')
                }
            else:
                error_msg = upload_result.error_message.lower()
                
                # Determine if error is retryable
                retryable_errors = ["timeout", "network", "temporary", "service unavailable"]
                non_retryable_errors = ["authentication", "permission", "bucket not found", "invalid"]
                
                is_retryable = any(err in error_msg for err in retryable_errors)
                is_non_retryable = any(err in error_msg for err in non_retryable_errors)
                
                if is_non_retryable:
                    return {
                        "success": False,
                        "error": upload_result.error_message,
                        "error_type": "non_retryable",
                        "attempts": attempt + 1
                    }
                
                if is_retryable and attempt < max_retries - 1:
                    wait_time = (2 ** attempt)  # Exponential backoff
                    print(f"Upload attempt {attempt + 1} failed, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                return {
                    "success": False,
                    "error": upload_result.error_message,
                    "error_type": "max_retries_exceeded",
                    "attempts": attempt + 1
                }
                
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Exception on attempt {attempt + 1}: {e}")
                time.sleep(2 ** attempt)
                continue
            else:
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "exception",
                    "attempts": attempt + 1
                }
    
    return {"success": False, "error": "Unexpected error", "attempts": max_retries}

# Usage
result = robust_oss_upload(session, "my-bucket", "data/file.txt", "/tmp/data.txt")
if result["success"]:
    print(f"✅ Upload successful after {result['attempts']} attempts")
else:
    print(f"❌ Upload failed: {result['error']} (Type: {result.get('error_type', 'unknown')})")
```

### 4. File Integrity Verification

```python
def upload_with_verification(session, bucket, object_key, local_path):
    """Upload file with integrity verification"""
    
    # Step 1: Read original file
    original_result = session.file_system.read_file(local_path)
    if not original_result.success:
        return {"success": False, "error": "Cannot read original file"}
    
    original_content = original_result.content
    original_size = len(original_content)
    
    # Step 2: Upload file
    upload_result = session.oss.upload(bucket, object_key, local_path)
    if not upload_result.success:
        return {"success": False, "error": f"Upload failed: {upload_result.error_message}"}
    
    # Step 3: Download for verification
    verify_path = f"/tmp/verify_{hash(object_key)}.tmp"
    download_result = session.oss.download(bucket, object_key, verify_path)
    
    if not download_result.success:
        return {"success": False, "error": f"Verification download failed: {download_result.error_message}"}
    
    # Step 4: Compare content
    verify_result = session.file_system.read_file(verify_path)
    if not verify_result.success:
        return {"success": False, "error": "Cannot read verification file"}
    
    downloaded_content = verify_result.content
    downloaded_size = len(downloaded_content)
    
    # Step 5: Verify integrity
    if original_content == downloaded_content:
        # Clean up verification file
        session.command.execute_command(f"rm -f {verify_path}")
        return {
            "success": True,
            "verified": True,
            "original_size": original_size,
            "downloaded_size": downloaded_size,
            "object_key": object_key
        }
    else:
        return {
            "success": False,
            "error": "Content verification failed",
            "original_size": original_size,
            "downloaded_size": downloaded_size
        }

# Usage
result = upload_with_verification(session, "my-bucket", "verified/data.txt", "/tmp/data.txt")
if result["success"] and result.get("verified"):
    print("✅ Upload verified successfully")
else:
    print("❌ Upload verification failed:", result.get("error"))
```

### 5. Batch Operations with Progress Tracking

```python
def batch_upload_with_progress(session, bucket, file_mappings, progress_callback=None):
    """Batch upload with progress tracking and detailed reporting"""
    
    total_files = len(file_mappings)
    results = []
    
    print(f"🚀 Starting batch upload of {total_files} files...")
    
    for i, (local_path, object_key) in enumerate(file_mappings.items(), 1):
        # Progress callback
        if progress_callback:
            progress_callback(i, total_files, object_key)
        else:
            print(f"📤 [{i}/{total_files}] Uploading {object_key}...")
        
        # Upload file
        upload_result = session.oss.upload(bucket, object_key, local_path)
        
        result_info = {
            "local_path": local_path,
            "object_key": object_key,
            "success": upload_result.success,
            "error": upload_result.error_message if not upload_result.success else None,
            "index": i
        }
        results.append(result_info)
        
        if upload_result.success:
            print(f"✅ [{i}/{total_files}] Success: {object_key}")
        else:
            print(f"❌ [{i}/{total_files}] Failed: {object_key} - {upload_result.error_message}")
    
    # Generate summary
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    summary = {
        "total_files": total_files,
        "successful": len(successful),
        "failed": len(failed),
        "success_rate": len(successful) / total_files * 100,
        "results": results
    }
    
    print(f"\n📊 Batch Upload Summary:")
    print(f"   Total: {summary['total_files']}")
    print(f"   Success: {summary['successful']}")
    print(f"   Failed: {summary['failed']}")
    print(f"   Success Rate: {summary['success_rate']:.1f}%")
    
    return summary

# Custom progress callback
def progress_callback(current, total, filename):
    percentage = (current / total) * 100
    print(f"📊 Progress: {percentage:.1f}% ({current}/{total}) - {filename}")

# Usage
file_mappings = {
    "/tmp/file1.txt": "batch/file1.txt",
    "/tmp/file2.txt": "batch/file2.txt",
    "/tmp/file3.txt": "batch/file3.txt"
}

summary = batch_upload_with_progress(session, "my-bucket", file_mappings, progress_callback)
```

## Error Handling and Troubleshooting

### Common OSS Errors and Solutions

```python
def diagnose_oss_errors():
    """Comprehensive OSS error diagnosis and troubleshooting"""
    
    agb = AGB()
    session = agb.create().session
    
    try:
        print("🔍 OSS Error Diagnosis and Troubleshooting")
        
        # Test 1: Invalid credentials
        print("\n1. Testing invalid credentials...")
        invalid_init = session.oss.env_init(
            endpoint="https://oss.example.com",
            access_key_id="invalid_key",
            access_key_secret="invalid_secret",
            bucket_name="test-bucket"
        )
        
        if not invalid_init.success:
            error_msg = invalid_init.error_message.lower()
            if "authentication" in error_msg or "access" in error_msg:
                print("   ❌ Authentication Error - Check your access credentials")
                print("   💡 Solution: Verify OSS_ACCESS_KEY_ID and OSS_ACCESS_KEY_SECRET")
            else:
                print(f"   ❌ Unexpected error: {invalid_init.error_message}")
        
        # Test 2: Invalid endpoint
        print("\n2. Testing invalid endpoint...")
        invalid_endpoint = session.oss.env_init(
            endpoint="https://invalid-endpoint.com",
            access_key_id="test_key",
            access_key_secret="test_secret",
            bucket_name="test-bucket"
        )
        
        if not invalid_endpoint.success:
            error_msg = invalid_endpoint.error_message.lower()
            if "endpoint" in error_msg or "network" in error_msg or "dns" in error_msg:
                print("   ❌ Endpoint Error - Invalid or unreachable endpoint")
                print("   💡 Solution: Check OSS endpoint URL format and region")
            else:
                print(f"   ❌ Unexpected error: {invalid_endpoint.error_message}")
        
        # Test 3: File not found for upload
        print("\n3. Testing file not found...")
        # First initialize with valid credentials (mock)
        session.oss.env_init(
            endpoint="https://oss.example.com",
            access_key_id="valid_key",
            access_key_secret="valid_secret",
            bucket_name="test-bucket"
        )
        
        upload_result = session.oss.upload(
            bucket="test-bucket",
            object="test.txt",
            path="/nonexistent/file.txt"
        )
        
        if not upload_result.success:
            error_msg = upload_result.error_message.lower()
            if "not found" in error_msg or "no such file" in error_msg:
                print("   ❌ File Not Found - Local file doesn't exist")
                print("   💡 Solution: Check local file path and permissions")
            else:
                print(f"   ❌ Unexpected error: {upload_result.error_message}")
        
        # Test 4: Network timeout simulation
        print("\n4. Testing timeout scenarios...")
        print("   💡 Timeout Prevention Tips:")
        print("      - Use appropriate timeout values for file size")
        print("      - Implement retry logic for network issues")
        print("      - Consider chunked uploads for large files")
        print("      - Monitor network connectivity")
        
        # Test 5: Bucket permission issues
        print("\n5. Bucket Permission Issues:")
        print("   💡 Common Permission Problems:")
        print("      - Bucket doesn't exist: Check bucket name and region")
        print("      - No write permission: Verify IAM policies")
        print("      - Cross-region access: Ensure endpoint matches bucket region")
        print("      - Object key restrictions: Check naming conventions")
        
        # Error handling best practices
        print("\n🛠️ Error Handling Best Practices:")
        print("   1. Always check operation results before proceeding")
        print("   2. Implement exponential backoff for retries")
        print("   3. Log detailed error information for debugging")
        print("   4. Use environment variables for sensitive configuration")
        print("   5. Validate inputs before making OSS calls")
        print("   6. Monitor OSS service status and quotas")
        
    finally:
        agb.delete(session)

diagnose_oss_errors()
```

## Integration with Other Modules

### OSS + FileSystem + Code Integration

```python
def complete_integration_example():
    """Complete example integrating OSS with FileSystem and Code modules"""
    
    agb = AGB()
    session = agb.create().session
    
    try:
        print("🔄 Complete OSS Integration Example")
        
        # Initialize OSS
        init_result = session.oss.env_init(
            endpoint="https://oss.example.com",
            access_key_id="your_access_key_id",
            access_key_secret="your_access_key_secret",
            bucket_name="integration-bucket"
        )
        
        if not init_result.success:
            print("❌ OSS initialization failed")
            return
        
        # Step 1: Create data with FileSystem
        print("\n📁 Step 1: Creating data with FileSystem...")
        
        raw_data = """product_id,product_name,price,category,stock
1,Laptop,999.99,Electronics,50
2,Mouse,29.99,Electronics,200
3,Keyboard,79.99,Electronics,150
4,Monitor,299.99,Electronics,75
5,Desk Chair,199.99,Furniture,30"""
        
        session.file_system.write_file("/tmp/products.csv", raw_data)
        print("✅ Raw data created with FileSystem")
        
        # Step 2: Upload to OSS
        print("\n☁️ Step 2: Uploading to OSS...")
        
        upload_result = session.oss.upload(
            bucket="integration-bucket",
            object="raw-data/products.csv",
            path="/tmp/products.csv"
        )
        
        if upload_result.success:
            print("✅ Data uploaded to OSS")
        else:
            print("❌ Upload failed")
            return
        
        # Step 3: Process data with Code
        print("\n⚙️ Step 3: Processing data with Code...")
        
        processing_code = """
import csv
from io import StringIO

# Read the CSV data
with open('/tmp/products.csv', 'r') as f:
    csv_content = f.read()

# Parse and analyze data
reader = csv.DictReader(StringIO(csv_content))
products = list(reader)

# Calculate statistics
total_products = len(products)
total_value = sum(float(p['price']) * int(p['stock']) for p in products)
avg_price = sum(float(p['price']) for p in products) / total_products

# Category analysis
categories = {}
for product in products:
    category = product['category']
    if category not in categories:
        categories[category] = {'count': 0, 'total_value': 0}
    categories[category]['count'] += 1
    categories[category]['total_value'] += float(product['price']) * int(product['stock'])

# Generate analysis report
report = f'''Product Analysis Report
Generated: 2023-12-01 15:00:00
========================

Summary:
- Total Products: {total_products}
- Average Price: ${avg_price:.2f}
- Total Inventory Value: ${total_value:.2f}

Category Breakdown:
'''

for category, stats in categories.items():
    report += f"- {category}: {stats['count']} products, ${stats['total_value']:.2f} value\\n"

report += "\\nTop 3 Most Expensive Products:\\n"
sorted_products = sorted(products, key=lambda x: float(x['price']), reverse=True)
for i, product in enumerate(sorted_products[:3], 1):
    report += f"{i}. {product['product_name']}: ${product['price']}\\n"

# Save processed report
with open('/tmp/analysis_report.txt', 'w') as f:
    f.write(report)

# Create summary JSON for API consumption
import json
summary_data = {
    "total_products": total_products,
    "average_price": round(avg_price, 2),
    "total_inventory_value": round(total_value, 2),
    "categories": categories,
    "generated_at": "2023-12-01T15:00:00Z"
}

with open('/tmp/summary.json', 'w') as f:
    json.dump(summary_data, f, indent=2)

print(f"Analysis completed: {total_products} products processed")
print(f"Total inventory value: ${total_value:.2f}")
"""
        
        code_result = session.code.run_code(processing_code, "python")
        if code_result.success:
            print("✅ Data processing completed")
            print(code_result.result)
        else:
            print("❌ Processing failed:", code_result.error_message)
            return
        
        # Step 4: Upload processed results to OSS
        print("\n📤 Step 4: Uploading processed results...")
        
        processed_files = [
            ("/tmp/analysis_report.txt", "processed-data/analysis_report.txt"),
            ("/tmp/summary.json", "processed-data/summary.json")
        ]
        
        for local_path, object_key in processed_files:
            upload_result = session.oss.upload(
                bucket="integration-bucket",
                object=object_key,
                path=local_path
            )
            
            if upload_result.success:
                print(f"✅ Uploaded: {object_key}")
            else:
                print(f"❌ Failed to upload: {object_key}")
        
        # Step 5: Download and verify with FileSystem
        print("\n📥 Step 5: Downloading and verifying...")
        
        download_result = session.oss.download(
            bucket="integration-bucket",
            object="processed-data/analysis_report.txt",
            path="/tmp/downloaded_report.txt"
        )
        
        if download_result.success:
            report_content = session.file_system.read_file("/tmp/downloaded_report.txt")
            if report_content.success:
                print("\n📊 Analysis Report:")
                print("=" * 50)
                print(report_content.content)
        
        # Step 6: Use Command module for cleanup
        print("\n🧹 Step 6: Cleanup with Command module...")
        
        cleanup_commands = [
            "ls -la /tmp/*.csv /tmp/*.txt /tmp/*.json",
            "rm -f /tmp/products.csv /tmp/analysis_report.txt /tmp/summary.json /tmp/downloaded_report.txt"
        ]
        
        for cmd in cleanup_commands:
            result = session.command.execute_command(cmd)
            if result.success and "ls" in cmd:
                print("Files before cleanup:")
                print(result.output)
            elif result.success:
                print("✅ Cleanup completed")
        
        print("\n🎉 Complete integration example finished!")
        print("   Data flow: FileSystem → OSS → Code → OSS → FileSystem → Command")
    
    finally:
        agb.delete(session)

complete_integration_example()
```

## Related Documentation

- **[OSS Module API](../api-reference/modules/oss.md)** - Complete OSS API reference
- **[FileSystem Module](../api-reference/modules/filesystem.md)** - File operations for OSS integration
- **[Code Execution Guide](../guides/code-execution.md)** - Processing OSS data with code
- **[Session Management Guide](../guides/session-management.md)** - Managing OSS sessions
- **[Best Practices](../guides/best-practices.md)** - Production deployment patterns 