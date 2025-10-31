# Extensions Examples

This directory contains examples demonstrating how to use the Extensions API to manage and load browser extensions in AGB sessions.

## Overview

The Extensions API allows you to:
- Upload browser extensions from local ZIP files
- Manage extension lifecycle (create, list, update, delete)
- Load extensions in browser sessions for automated testing
- Integrate extensions with your browsing workflows

## Examples

1. [Basic Extension Management](basic_extension_management.py) - Demonstrates creating, listing, updating, and deleting extensions
2. [Browser Session with Extensions](browser_session_with_extensions.py) - Shows how to create a browser session with extensions loaded

## Prerequisites

To run these examples, you'll need:
- AGB Python SDK installed
- An API key for AGB services
- Browser extension ZIP files (Chrome extensions in .zip format)

## Usage

Set your API key as an environment variable:

```bash
export AGB_API_KEY=your_api_key_here
```

Then run any example:

```bash
python basic_extension_management.py
```