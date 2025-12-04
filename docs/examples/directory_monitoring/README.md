# Directory Monitoring Examples

This directory demonstrates how to watch for file changes in the remote session.

## Overview

Directory monitoring allows you to react to file system events (create, modify, delete) happening inside the session. This is useful for:
- Triggering downloads when a long-running job finishes writing a file.
- Debugging file operations.
- Building reactive workflows.

## Examples

### Basic Monitoring (`main.py`)
Starts a background process that creates files, and uses the `filesystem.watch` API to detect and report these changes.

<<< ./main.py
