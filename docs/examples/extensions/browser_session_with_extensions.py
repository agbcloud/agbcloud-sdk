#!/usr/bin/env python3
"""
Browser Session with Extensions Example

This example demonstrates how to create a browser session with extensions loaded:
1. Create and upload browser extensions
2. Configure a browser session with extensions
3. Initialize the browser with extensions
4. Verify that extensions are loaded

Requirements:
- AGB_API_KEY environment variable set
- Playwright installed for browser interaction (pip install playwright)
- Extension ZIP files (Chrome extensions in .zip format)
"""

import asyncio
import os
import tempfile
import zipfile
import json
from typing import Optional
from agb.agb import AGB
from agb.extension import ExtensionsService, ExtensionOption
from agb.session_params import CreateSessionParams, BrowserContext
from agb.modules.browser.browser import BrowserOption
from agb.session import BaseSession

# Optional Playwright import for verification
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    async_playwright = None
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not available. Extension verification will be skipped.")


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
        body { width: 300px; padding: 10px; font-family: Arial, sans-serif; }
        .extension-info { background: #e8f5e8; padding: 10px; margin: 10px 0; border-radius: 4px; }
    </style>
</head>
<body>
    <h2>Sample Extension</h2>
    <div class="extension-info">
        <p><strong>Name:</strong> Sample Extension</p>
        <p><strong>ID:</strong> <span id="extensionId">Loading...</span></p>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id) {
                document.getElementById('extensionId').textContent = chrome.runtime.id;
            } else {
                document.getElementById('extensionId').textContent = 'Not available';
            }
        });
    </script>
</body>
</html>"""
        zipf.writestr("popup.html", popup_html)

        # Add background.js
        background_js = """console.log('Background service worker started for Sample Extension');"""
        zipf.writestr("background.js", background_js)

    return zip_path


async def verify_extensions_loaded(session: BaseSession):
    """Verify that extensions are loaded in the browser using Playwright."""
    if not PLAYWRIGHT_AVAILABLE or async_playwright is None:
        print("   Playwright not available, skipping extension verification")
        return True

    try:
        # Get browser endpoint URL
        endpoint_url = session.browser.get_endpoint_url()
        print(f"   Browser endpoint: {endpoint_url}")

        # Connect to browser using Playwright
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            cdp_session = await browser.new_browser_cdp_session()

            # Get all targets to find loaded extensions
            targets = await cdp_session.send("Target.getTargets")

            extensions = []
            for info in targets["targetInfos"]:
                url = info.get("url", "")
                if url.startswith("chrome-extension://"):
                    extensions.append({
                        "id": url.split("/")[2],  # Extract extension ID from URL
                        "title": info.get("title"),
                        "url": url
                    })

            print(f"   Found {len(extensions)} loaded extensions:")
            for ext in extensions:
                print(f"     - ID: {ext['id']}, Title: {ext['title']}")

            await cdp_session.detach()
            await browser.close()

            return len(extensions) > 0

    except Exception as e:
        print(f"   Error verifying extensions: {e}")
        return False


async def main():
    # Get API key from environment
    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        print("Please set the AGB_API_KEY environment variable")
        return

    # Initialize AGB client
    agb = AGB(api_key)

    print("=== Browser Session with Extensions Example ===\n")

    # Create ExtensionsService
    extensions_service = ExtensionsService(agb, "browser_extensions_example")

    session: Optional[BaseSession] = None
    extension1 = None
    extension2 = None
    ext1_path = None
    ext2_path = None

    try:
        # 1. Create extensions
        print("1. Creating extensions...")
        ext1_path = create_sample_extension_zip("TestExtension1")
        ext2_path = create_sample_extension_zip("TestExtension2")

        extension1 = extensions_service.create(ext1_path)
        extension2 = extensions_service.create(ext2_path)
        print(f"   Created extension 1: {extension1.id}")
        print(f"   Created extension 2: {extension2.id}")

        # 2. Create extension option for browser integration
        print("\n2. Creating extension option...")
        ext_option = extensions_service.create_extension_option([extension1.id, extension2.id])
        print(f"   Extension option created with {len(ext_option.extension_ids)} extensions")

        # 3. Create browser context with extensions
        print("\n3. Creating browser context with extensions...")
        browser_context = BrowserContext(
            context_id="browser_session_with_extensions",
            auto_upload=True,
            extension_option=ext_option
        )

        # 4. Create session with browser context
        print("\n4. Creating session with extensions...")
        session_params = CreateSessionParams(
            labels={"type": "browser_with_extensions", "example": "extensions"},
            image_id="agb-browser-use-1",
            browser_context=browser_context
        )

        session_result = agb.create(session_params)
        if not session_result.success:
            raise Exception(f"Failed to create session: {session_result.error_message}")

        session = session_result.session
        if session is not None:
            print(f"   Session created: {session.session_id}")
        else:
            raise Exception("Session creation failed: session is None")

        # 5. Initialize browser with extensions
        print("\n5. Initializing browser with extensions...")
        browser_option = BrowserOption(
            extension_path="/tmp/extensions/"
        )

        if session is not None:
            init_success = await session.browser.initialize_async(browser_option)
            if not init_success:
                raise Exception("Failed to initialize browser")

        print("   Browser initialized successfully")

        # 6. Verify extensions are loaded
        print("\n6. Verifying extensions are loaded...")
        extensions_loaded = False
        if session is not None:
            extensions_loaded = await verify_extensions_loaded(session)
        if extensions_loaded:
            print("   ✅ Extensions loaded successfully")
        else:
            print("   ⚠️  Could not verify extensions (this may be normal in some environments)")

        print("\n=== Example completed successfully ===")

    except Exception as e:
        print(f"Error: {e}")
        raise

    finally:
        # Clean up
        if session is not None:
            try:
                session.delete(sync_context=True)
                print("\nSession deleted successfully")
            except Exception as e:
                print(f"Error deleting session: {e}")

        # Clean up extensions
        if extension1 is not None and extension2 is not None:
            try:
                extensions_service.delete(extension1.id)
                extensions_service.delete(extension2.id)
                print("Extensions deleted successfully")
            except Exception as e:
                print(f"Error deleting extensions: {e}")

        # Clean up temporary files
        try:
            for path in [ext1_path, ext2_path]:
                if path is not None and os.path.exists(path):
                    os.unlink(path)
                    os.rmdir(os.path.dirname(path))
        except Exception as e:
            print(f"Error cleaning up temporary files: {e}")


if __name__ == "__main__":
    asyncio.run(main())