# File System Operations Examples

This directory demonstrates direct file system manipulation using the Filesystem API.

## Overview

While the Context Manager handles bulk uploads/downloads, the **Filesystem API** gives you fine-grained control to:
- List directories (`list`).
- Read file contents (`read`).
- Write file contents (`write`).
- Create directories (`make_dir`).

## Examples

### Basic File Operations (`main.py`)
Perform a sequence of operations: create a directory, write a file, read it back, and list the directory contents.

<<< ./main.py
