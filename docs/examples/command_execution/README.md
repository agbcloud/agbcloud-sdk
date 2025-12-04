# Command Execution Examples

This directory demonstrates how to execute shell commands in the AGB environment.

## Overview

The Command Execution API allows you to run shell commands (bash) directly in the cloud environment. This is useful for:
- Installing system dependencies (apt-get, pip)
- Managing files and directories
- Running background processes
- System diagnostics

## Examples

### Basic Command Execution (`main.py`)
Shows how to run simple commands, handle long-running processes, and inspect exit codes/output.

<<< ./main.py

## Notes

- **Root Access**: You generally have sudo/root access in the container.
- **Persistence**: Changes to the filesystem (e.g., `mkdir`, `apt-get install`) persist for the duration of the session.
- **State**: Environment variables set in one command (e.g., `export VAR=1`) do **not** persist to the next command unless you chain them (e.g., `export VAR=1 && echo $VAR`) or write them to `.bashrc` (depending on the shell initialization).
