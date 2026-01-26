# File System Operations Examples

This directory demonstrates direct file system manipulation using the Filesystem API.

## Overview

While the Context Manager handles bulk uploads/downloads, the **Filesystem API** gives you fine-grained control to:
- List directories (`list`).
- Read file contents (`read`).
- Write file contents (`write`).
- Create directories (`mkdir`).
- Get file information (`info`).
- Edit files (`edit`).
- Move files (`move`).
- Delete files (`remove`).
- Search files (`search`).
- Read multiple files (`read_batch`).
- Binary file operations (with `format="bytes"` parameter).

## Examples

### Comprehensive File Operations
Demonstrates a complete range of file system operations including:

- **Basic Operations**: Write, read, and append to files
- **Directory Management**: Create directories and list contents
- **File Information**: Get detailed file metadata
- **File Editing**: Modify existing files with text replacements
- **File Movement**: Move files between directories
- **File Deletion**: Delete files from the file system
- **File Search**: Search for content within files
- **Batch Operations**: Read multiple files simultaneously
- **Binary File Handling**: Work with binary data using `format="bytes"`
- **Large File Operations**: Handle large files (1MB+ examples) with performance timing

The example includes 19 different operations with comprehensive error handling.

<<< ./main.py
