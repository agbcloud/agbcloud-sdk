#!/usr/bin/env python3
"""
Basic Extension Management Example

This example demonstrates how to use the Extensions API to manage browser extensions:
1. Create extensions from local ZIP files
2. List all available extensions
3. Update an existing extension
4. Delete extensions

Requirements:
- AGB_API_KEY environment variable set
- Extension ZIP files (Chrome extensions in .zip format)
"""

import os
import tempfile
import zipfile
import json
from agb.agb import AGB
from agb.extension import ExtensionsService


def create_sample_extension_zip(name: str) -> str:
    """Create a sample extension ZIP file for testing purposes."""
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"{name}.zip")

    manifest = {
        "manifest_version": 3,
        "name": f"Sample {name}",
        "version": "1.0.0",
        "description": "A sample extension for testing",
        "permissions": ["activeTab", "storage"],
        "action": {
            "default_popup": "popup.html",
            "default_title": f"Sample {name}"
        },
        "background": {
            "service_worker": "background.js"
        }
    }

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # Add manifest.json
        zipf.writestr("manifest.json", json.dumps(manifest, indent=2))

        # Add popup.html
        popup_html = """<!DOCTYPE html>
<html>
<head>
    <title>Sample Extension</title>
    <style>
        body { width: 300px; padding: 10px; }
    </style>
</head>
<body>
    <h2>Sample Extension</h2>
    <p>This is a sample extension for testing.</p>
</body>
</html>"""
        zipf.writestr("popup.html", popup_html)

        # Add background.js
        background_js = """console.log('Background service worker started');"""
        zipf.writestr("background.js", background_js)

    return zip_path


def main():
    # Get API key from environment
    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        print("Please set the AGB_API_KEY environment variable")
        return

    # Initialize AGB client
    agb = AGB(api_key)

    # Create ExtensionsService
    extensions_service = ExtensionsService(agb, "my_extensions_example")

    print("=== Extension Management Example ===\n")

    try:
        # 1. Create extensions
        print("1. Creating extensions...")

        # Create sample extension files (in real usage, you would use your own extension ZIP files)
        ext1_path = create_sample_extension_zip("Extension1")
        ext2_path = create_sample_extension_zip("Extension2")

        # Upload extensions
        extension1 = extensions_service.create(ext1_path)
        extension2 = extensions_service.create(ext2_path)

        print(f"   Created extension 1: {extension1.id}")
        print(f"   Created extension 2: {extension2.id}")

        # 2. List extensions
        print("\n2. Listing extensions...")
        extensions = extensions_service.list()
        for ext in extensions:
            print(f"   ID: {ext.id}, Name: {ext.name}")

        # 3. Update an extension
        print("\n3. Updating extension...")
        # Create a new version of the extension
        updated_ext_path = create_sample_extension_zip("UpdatedExtension1")
        updated_extension = extensions_service.update(extension1.id, updated_ext_path)
        print(f"   Updated extension: {updated_extension.id}")

        # 4. List extensions again to see the update
        print("\n4. Listing extensions after update...")
        extensions = extensions_service.list()
        for ext in extensions:
            print(f"   ID: {ext.id}, Name: {ext.name}")

        # 5. Clean up - delete extensions
        print("\n5. Cleaning up...")
        extensions_service.delete(extension1.id)
        extensions_service.delete(extension2.id)
        print("   Extensions deleted successfully")

        # Clean up temporary files
        os.unlink(ext1_path)
        os.unlink(ext2_path)
        os.unlink(updated_ext_path)
        os.rmdir(os.path.dirname(ext1_path))
        os.rmdir(os.path.dirname(ext2_path))
        os.rmdir(os.path.dirname(updated_ext_path))

        print("\n=== Example completed successfully ===")

    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()