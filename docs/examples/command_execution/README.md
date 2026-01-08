# Command Execution Examples

This directory demonstrates how to execute shell commands in the AGB environment.

## Overview

The Command Execution API allows you to run shell commands (bash) directly in the cloud environment. This is useful for:
- Installing system dependencies (apt-get, pip)
- Managing files and directories
- Running background processes
- System diagnostics

## New Features

The Command Execution API now supports:
- **Working Directory**: Use the `cwd` parameter to set the working directory for commands
- **Environment Variables**: Use the `envs` parameter to set environment variables for commands
- **Detailed Results**: Access `exit_code`, `stdout`, `stderr`, and `trace_id` fields for better error handling and output parsing

## Examples

### Basic Command Execution
Shows how to run simple commands, handle long-running processes, and inspect exit codes/output.

<<< ./main.py

## Notes

- **Root Access**: You generally have sudo/root access in the container.
- **Persistence**: Changes to the filesystem (e.g., `mkdir`, `apt-get install`) persist for the duration of the session.
- **State**: Environment variables set in one command (e.g., `export VAR=1`) do **not** persist to the next command. Use the `envs` parameter instead for better control.
- **Working Directory**: Use the `cwd` parameter to set the working directory instead of using `cd` commands.
- **Error Handling**: Check `exit_code` (0 means success) and use `stdout`/`stderr` separately for better output parsing.
