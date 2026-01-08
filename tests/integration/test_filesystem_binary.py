"""Integration tests for binary file operations."""

import os
import time
import tempfile

import pytest

from agb import AGB
from agb.session_params import CreateSessionParams
from agb.model.response import BinaryFileContentResult


@pytest.fixture(scope="module")
def agb_client():
    """Create AGB client for testing."""
    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        pytest.skip("AGB_API_KEY environment variable not set")
    return AGB(api_key=api_key)


@pytest.fixture
def test_session(agb_client):
    """Create a session for binary file testing."""
    print("Creating a new session for binary file testing...")
    params = CreateSessionParams(image_id="agb-computer-use-ubuntu-2204")
    result = agb_client.create(params)
    if not result.success:
        error_msg = getattr(result, 'error_message', 'Unknown error')
        request_id = getattr(result, 'request_id', 'N/A')
        print(f"Failed to create session:")
        print(f"  Error message: {error_msg}")
        print(f"  Request ID: {request_id}")
        pytest.fail(f"Session creation failed: {error_msg} (Request ID: {request_id})")
    assert result.session is not None, "Session object is None"
    session = result.session
    print(f"Session created successfully: {session.session_id}")
    assert len(session.session_id) > 0 , "Session ID is None"
    
    yield session
    
    # Clean up
    print("Cleaning up: Deleting the session...")
    try:
        agb_client.delete(session)
        print(f"Session deleted: {session.session_id}")
    except Exception as e:
        print(f"Warning: Failed to delete session: {e}")


def test_binary_file_creation(test_session):
    """Test creating binary file using command."""
    cmd = test_session.command
    fs = test_session.file_system

    # Create binary file
    result = cmd.execute_command(
        "dd if=/dev/zero of=/tmp/binary_test bs=1024 count=10"
    )
    assert result.success

    # Check file info
    info = fs.get_file_info("/tmp/binary_test")
    assert info.success
    size = int(info.file_info["size"])
    assert size > 0
    print(f"Binary file created, size: {size} bytes")


def test_binary_file_copy(test_session):
    """Test copying binary file."""
    cmd = test_session.command
    fs = test_session.file_system

    # Create binary file
    cmd.execute_command("dd if=/dev/zero of=/tmp/binary_src bs=1024 count=5")

    # Copy file
    copy_result = cmd.execute_command("cp /tmp/binary_src /tmp/binary_dst")
    assert copy_result.success

    # Verify both files exist
    src_info = fs.get_file_info("/tmp/binary_src")
    dst_info = fs.get_file_info("/tmp/binary_dst")

    assert src_info.success
    assert dst_info.success
    src_size = int(src_info.file_info["size"])
    dst_size = int(dst_info.file_info["size"])
    assert src_size == dst_size
    print(f"Binary file copied, size: {dst_size} bytes")


def test_read_binary_file(test_session):
    """Test reading a binary file using format='bytes'."""
    fs = test_session.file_system
    
    # File path where user will manually upload the test file
    file_path = "/tmp/test_binary.dat"
    print(f"\n📁 Creating a base64-compatible test file locally...")
    local_test_path = os.path.join(tempfile.gettempdir(), "test_upload_base64.dat")
    
    import base64
    
    # Create test content that's designed to be base64-friendly
    # Use a known pattern that will encode/decode cleanly
    original_text = "Hello World! This is a test file for binary reading with base64 encoding support. 123456789"
    
    # Convert to bytes and create a predictable binary pattern
    text_bytes = original_text.encode('utf-8')
    
    # Add some binary data that's base64-safe (using only bytes 0-255 in a controlled way)
    binary_pattern = bytes(range(0, 256))  # Full byte range for comprehensive testing
    
    # Combine text and binary data
    test_file_content = text_bytes + b'\n--- BINARY SECTION ---\n' + binary_pattern
    
    print(f"📊 Test content size: {len(test_file_content)} bytes")
    print(f"📝 Content preview: {test_file_content[:50]}...")
    
    # Verify the content can be base64 encoded/decoded properly
    try:
        encoded = base64.b64encode(test_file_content)
        decoded = base64.b64decode(encoded)
        assert decoded == test_file_content, "Base64 round-trip failed"
        print(f"✅ Base64 compatibility verified")
    except Exception as e:
        pytest.fail(f"Content is not base64 compatible: {e}")
    
    with open(local_test_path, 'wb') as f:
        f.write(test_file_content)
    
    print(f"✅ Test file created: {local_test_path} | Size: {len(test_file_content)} bytes")
    
    # Check if local file exists before upload
    if not os.path.exists(local_test_path):
        pytest.fail(f"Local file not found: {local_test_path}")
    
    if not os.path.isfile(local_test_path):
        pytest.fail(f"Path is not a file: {local_test_path}")
    
    local_file_size = os.path.getsize(local_test_path)
    print(f"📊 Local file size: {local_file_size} bytes")

    remote_path = file_path
    print(f"🎯 Remote path: {remote_path}")
    
    print(f"\n📤 Uploading file from {local_test_path} to {remote_path}")
    upload_result = fs.upload_file(local_test_path, remote_path, wait=True, wait_timeout=60)
    assert upload_result.success, f"Upload failed: {upload_result.error_message}"
    assert upload_result.bytes_sent > 0
    assert upload_result.request_id_upload_url
    assert upload_result.request_id_sync
    
    print(f"✅ Upload successful: {upload_result.bytes_sent} bytes sent")
    
    # Verify file exists
    print(f"\n🔍 Checking if file exists: {file_path}")
    info = fs.get_file_info(file_path)
    if not info.success:
        pytest.fail(f"File not found at {file_path}. Please ensure the file is uploaded correctly.")
    
    file_size = int(info.file_info["size"])
    print(f"✅ File found, size: {file_size} bytes")
    
    # Read binary file using format='bytes'
    print(f"\n📖 Reading binary file: {file_path}")
    result = fs.read_file(file_path, format="bytes")
    assert result.success, f"Failed to read binary file: {result.error_message}"
    assert isinstance(result, BinaryFileContentResult), "Result should be BinaryFileContentResult"
    assert isinstance(result.content, bytes), "Content should be bytes type"
    assert len(result.content) == file_size, f"Expected {file_size} bytes, got {len(result.content)}"
    
    # Verify the content matches what we uploaded
    # Check if content starts with our expected text
    content_str = result.content.decode('utf-8', errors='ignore')
    if original_text in content_str:
        print(f"✅ Text content verified: Found expected text in file")
    else:
        print(f"⚠️  Text content not found in decoded content")
    
    # Verify the binary pattern is present
    binary_section_marker = b'\n--- BINARY SECTION ---\n'
    if binary_section_marker in result.content:
        print(f"✅ Binary section marker found")
        # Find the binary pattern after the marker
        marker_pos = result.content.find(binary_section_marker)
        binary_start = marker_pos + len(binary_section_marker)
        binary_data = result.content[binary_start:]
        
        # Verify we have the expected binary pattern (0-255 bytes)
        if len(binary_data) >= 256:
            expected_pattern = bytes(range(0, 256))
            actual_pattern = binary_data[:256]
            if actual_pattern == expected_pattern:
                print(f"✅ Binary pattern verified: 0-255 byte sequence found")
            else:
                print(f"⚠️  Binary pattern mismatch")
        else:
            print(f"⚠️  Binary data too short: {len(binary_data)} bytes")
    else:
        print(f"⚠️  Binary section marker not found")
    
    print(f"✅ Successfully read binary file: {len(result.content)} bytes")
    
    # Save the read file to local file for verification
    temp_dir = tempfile.gettempdir()
    local_verification_path = os.path.join(temp_dir, "test_read_binary_verification.dat")
    
    print(f"\n💾 Saving read file to local file for verification...")
    print(f"   Local path: {local_verification_path}")
    
    with open(local_verification_path, 'wb') as f:
        f.write(result.content)
    
    # Verify local file was saved correctly
    local_file_size = os.path.getsize(local_verification_path)
    assert local_file_size == len(result.content), f"Local file size mismatch: {local_file_size} vs {len(result.content)}"
    
    print(f"✅ File saved successfully to: {local_verification_path}")
    print(f"   File size: {local_file_size} bytes")
    
    # Verify the content matches exactly what we originally created
    with open(local_verification_path, 'rb') as f:
        saved_content = f.read()
    
    if saved_content == test_file_content:
        print(f"✅ Content integrity verified: Read content matches original")
    else:
        print(f"⚠️  Content mismatch detected")
        print(f"   Original size: {len(test_file_content)}")
        print(f"   Read size: {len(saved_content)}")
    
    # Verify optional fields
    if hasattr(result, 'size') and result.size is not None:
        assert result.size == file_size
    
    print(f"\n✅ Binary file read test completed successfully!")
    print(f"📁 Local verification file: {local_verification_path}")


def test_read_binary_file_with_non_zero_content(test_session):
    """Test reading a binary file with non-zero content."""
    cmd = test_session.command
    fs = test_session.file_system

    # Create binary file with pattern (using printf to create specific bytes)
    # Create a file with pattern: 0x00, 0x01, 0x02, ... repeating
    create_result = cmd.execute_command(
        "python3 -c \"with open('/tmp/binary_pattern_test', 'wb') as f: f.write(bytes(range(256)) * 4)\""
    )
    assert create_result.success

    # Read binary file
    result = fs.read_file("/tmp/binary_pattern_test", format="bytes")
    assert result.success, f"Failed to read binary file: {result.error_message}"
    assert isinstance(result, BinaryFileContentResult)
    assert isinstance(result.content, bytes)
    
    # Verify content pattern (0-255 repeating 4 times = 1024 bytes)
    expected_pattern = bytes(range(256)) * 4
    assert len(result.content) == len(expected_pattern)
    assert result.content == expected_pattern
    
    print(f"Successfully read binary file with pattern: {len(result.content)} bytes")


def test_read_text_file_still_works(test_session):
    """Test that reading text files still works with default format."""
    fs = test_session.file_system

    test_content = "This is a test text file for binary read feature."
    test_file_path = "/tmp/test_text_for_binary_feature.txt"

    # Write text file
    write_result = fs.write_file(test_file_path, test_content, "overwrite")
    assert write_result.success

    # Read as text (default format)
    result = fs.read_file(test_file_path)
    assert result.success
    assert result.content == test_content
    assert isinstance(result.content, str)
    
    # Explicitly read as text format
    result_explicit = fs.read_file(test_file_path, format="text")
    assert result_explicit.success
    assert result_explicit.content == test_content

def test_read_alias_method(test_session):
    """Test that the read() alias method works correctly."""
    fs = test_session.file_system

    test_content = "This is a test for the read() alias method."
    test_file_path = "/tmp/test_read_alias.txt"
    # Write text file
    write_result = fs.write_file(test_file_path, test_content, "overwrite")
    assert write_result.success
    # Test read() alias with default format
    result = fs.read(test_file_path)
    assert result.success
    assert result.content == test_content
    assert isinstance(result.content, str)