# Browser Fingerprint Guide

Browser fingerprinting is a crucial feature for web automation that helps avoid detection by anti-bot systems. AGB provides comprehensive fingerprint management capabilities including generation, customization, and persistence across sessions.

## Overview

AGB supports advanced browser fingerprint management with the following key capabilities:

- **Multiple Generation Methods**: Random generation, local browser sync, and custom construction
- **Fingerprint Persistence**: Maintain consistent fingerprints across multiple sessions
- **Context Management**: Persistent storage using browser and fingerprint contexts

## 1. Fingerprint Generation Methods

### 1.1 Random Fingerprint Generation

Generate random fingerprints based on specified criteria such as device type, operating system, and locale.

#### Features
- Automatic randomization of browser characteristics
- Configurable device types (desktop/mobile)
- Operating system selection (Windows, macOS, Linux, Android, iOS)
- Locale and language customization

#### Python Example

```python
import os
import asyncio

from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser.browser import BrowserOption, BrowserFingerprint

from playwright.async_api import async_playwright


async def random_fingerprint_example():
    """Main function demonstrating browser fingerprint basic usage."""
    # Get API key from environment variable
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        print("Error: AGB_API_KEY environment variable not set")
        return

    # Initialize AGB client
    print("Initializing AGB client...")
    agb = AGB(api_key=api_key)

    # Create a session
    print("Creating a new session...")
    params = CreateSessionParams(
        image_id="agb-browser-use-1",
    )
    session_result = agb.create(params)

    if session_result.success:
        session = session_result.session
        print(f"Session created with ID: {session.session_id}")

        # Create browser fingerprint option
        # - devices: desktop or mobile
        # - operating_systems: windows, macos, linux, android, ios
        # You can specify one or multiple values for each parameter.
        # But if you specify devices as desktop and operating_systems as android/ios,
        # the fingerprint feature will not work.
        browser_fingerprint = BrowserFingerprint(
            devices=["desktop"],
            operating_systems=["windows"],
            locales=["zh-CN", "zh"]
        )

        # Create browser option with stealth mode and fingerprint option limit.
        # This will help to avoid detection by anti-bot services. It will
        # generate a random, realistic browser fingerprint and make the browser
        # behave more like a real user.
        browser_option = BrowserOption(
            use_stealth=True,
            fingerprint=browser_fingerprint
        )

        if await session.browser.initialize_async(browser_option):
            endpoint_url = session.browser.get_endpoint_url()
            print("endpoint_url =", endpoint_url)

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                context = browser.contexts[0]
                page = await context.new_page()

                # Check user agent.
                print("\n--- Check User Agent ---")
                await page.goto("https://httpbin.org/user-agent", timeout=120000)

                response = await page.evaluate("() => JSON.parse(document.body.textContent)")
                user_agent = response.get("user-agent", "")
                print(f"User Agent: {user_agent}")

                # Check navigator properties.
                print("\n--- Check Navigator Properties ---")
                nav_info = await page.evaluate("""
                    () => ({
                        platform: navigator.platform,
                        language: navigator.language,
                        languages: navigator.languages,
                        webdriver: navigator.webdriver
                    })
                """)
                print(f"Platform: {nav_info.get('platform')}")
                print(f"Language: {nav_info.get('language')}")
                print(f"Languages: {nav_info.get('languages')}")
                print(f"WebDriver: {nav_info.get('webdriver')}")

                await page.wait_for_timeout(3000)
                await browser.close()

        # Clean up session
        agb.delete(session)

if __name__ == "__main__":
    asyncio.run(random_fingerprint_example())
```

### 1.2 Local Browser Fingerprint Sync

Capture fingerprint characteristics from your local Chrome browser and apply them to remote sessions for consistent behavior.

#### Features
- Extract fingerprint from local Chrome installation
- Preserve exact browser characteristics
- Maintain consistency between local and remote environments
- Support for both headless and visible mode extraction

#### Python Example

```python
import os
import asyncio

from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser.browser import BrowserOption
from agb.modules.browser.fingerprint import BrowserFingerprintGenerator

from playwright.async_api import async_playwright


async def local_sync_fingerprint_example():
    """Main function demonstrating browser fingerprint local sync."""
    # Get API key from environment variable
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        print("Error: AGB_API_KEY environment variable not set")
        return

    # Initialize AGB client
    print("Initializing AGB client...")
    agb = AGB(api_key=api_key)

    # Create a session
    print("Creating a new session...")
    params = CreateSessionParams(
        image_id="agb-browser-use-1",
    )
    session_result = agb.create(params)

    if session_result.success:
        session = session_result.session
        print(f"Session created with ID: {session.session_id}")

        # Generate fingerprint from local Chrome browser
        fingerprint_generator = BrowserFingerprintGenerator()
        fingerprint_format = await fingerprint_generator.generate_fingerprint()

        # Create browser option with fingerprint format.
        # Fingerprint format is dumped from local chrome browser by BrowserFingerprintGenerator
        # automatically, you can use it to sync to remote browser fingerprint.
        browser_option = BrowserOption(
            use_stealth=True,
            fingerprint_format=fingerprint_format
        )

        if await session.browser.initialize_async(browser_option):
            endpoint_url = session.browser.get_endpoint_url()
            print("endpoint_url =", endpoint_url)

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                context = browser.contexts[0]
                page = await context.new_page()

                # Check user agent.
                print("\n--- Check User Agent ---")
                await page.goto("https://httpbin.org/user-agent", timeout=120000)

                response = await page.evaluate("() => JSON.parse(document.body.textContent)")
                user_agent = response.get("user-agent", "")
                print(f"User Agent: {user_agent}")

                print("Please check if User Agent is synced correctly by visiting https://httpbin.org/user-agent in local chrome browser.")

                await page.wait_for_timeout(3000)
                await browser.close()

        # Clean up session
        agb.delete(session)


if __name__ == "__main__":
    asyncio.run(local_sync_fingerprint_example())
```

### 1.3 Custom Fingerprint Construction

Load and apply custom fingerprint data from JSON files or construct fingerprints programmatically.

#### Features
- Load fingerprint from JSON files
- Construct fingerprints programmatically
- Full control over all fingerprint characteristics
- Reusable fingerprint configurations

#### Python Example

```python
import os
import asyncio

from agb import AGB
from agb.session_params import CreateSessionParams
from agb.modules.browser.browser import BrowserOption
from agb.modules.browser.fingerprint import FingerprintFormat

from playwright.async_api import async_playwright


def generate_fingerprint_by_file() -> FingerprintFormat:
    """Generate fingerprint by file."""
    fingerprint_file = "path/to/custom_fingerprint.json"
    with open(fingerprint_file, "r") as f:
        fingerprint_format = FingerprintFormat.load(f.read())
    return fingerprint_format


async def custom_fingerprint_example():
    """Main function demonstrating custom fingerprint construction."""
    # Get API key from environment variable
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        print("Error: AGB_API_KEY environment variable not set")
        return

    # Initialize AGB client
    print("Initializing AGB client...")
    agb = AGB(api_key=api_key)

    # Create a session
    print("Creating a new session...")
    params = CreateSessionParams(
        image_id="agb-browser-use-1",
    )
    session_result = agb.create(params)

    if session_result.success:
        session = session_result.session
        print(f"Session created with ID: {session.session_id}")

        # You can generate fingerprint by file or construct FingerprintFormat by yourself totally.
        fingerprint_format = generate_fingerprint_by_file()

        # Create browser option with fingerprint format.
        # Fingerprint format is loaded from file by generate_fingerprint_by_file()
        browser_option = BrowserOption(
            use_stealth=True,
            fingerprint_format=fingerprint_format
        )

        if await session.browser.initialize_async(browser_option):
            endpoint_url = session.browser.get_endpoint_url()
            print("endpoint_url =", endpoint_url)

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                context = browser.contexts[0]
                page = await context.new_page()

                # Check user agent.
                print("\n--- Check User Agent ---")
                await page.goto("https://httpbin.org/user-agent", timeout=120000)

                response = await page.evaluate("() => JSON.parse(document.body.textContent)")
                user_agent = response.get("user-agent", "")
                print(f"User Agent: {user_agent}")
                
                # Verify that the user agent matches the fingerprint format
                if user_agent == fingerprint_format.fingerprint.navigator.userAgent:
                    print("User Agent constructed correctly")
                else:
                    print("User Agent mismatch")

                await page.wait_for_timeout(3000)
                await browser.close()

        # Clean up session
        agb.delete(session)


if __name__ == "__main__":
    asyncio.run(custom_fingerprint_example())
```

## 2. Fingerprint Persistence

Fingerprint persistence allows you to maintain consistent browser characteristics across multiple sessions by using browser contexts and fingerprint contexts.

### Features
- Persistent fingerprint storage across sessions
- Context-based fingerprint management
- Support for all fingerprint generation methods
- Automatic fingerprint loading and saving

### How It Works

1. **First Session**: Generate or apply a fingerprint with `fingerprint_persistent=True`
2. **Context Sync**: Save the session with `sync_context=True` to persist the fingerprint
3. **Subsequent Sessions**: Create new sessions with the same contexts to reuse the fingerprint

### Python Example (Random Fingerprint Persistence)

```python
import asyncio
import os
import time

from agb import AGB
from agb.session_params import CreateSessionParams, BrowserContext
from agb.modules.browser.browser import BrowserOption, BrowserFingerprint, BrowserFingerprintContext
from playwright.async_api import async_playwright

# Global variables for persistent context and fingerprint context
persistent_context = None
persistent_fingerprint_context = None


def is_windows_user_agent(user_agent: str) -> bool:
    if not user_agent:
        return False
    user_agent_lower = user_agent.lower()
    windows_indicators = [
        'windows nt',
        'win32',
        'win64',
        'windows',
        'wow64'
    ]
    return any(indicator in user_agent_lower for indicator in windows_indicators)


def run_as_first_time():
    """Run as first time - generate and persist fingerprint"""
    print("="*20)
    print("Run as first time")
    print("="*20)
    global persistent_context, persistent_fingerprint_context
    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        print("Error: AGB_API_KEY environment variable not set")
        return

    agb = AGB(api_key)

    # Create a browser context for first time
    session_context_name = f"test-browser-context-{int(time.time())}"
    context_result = agb.context.get(session_context_name, True)
    if not context_result.success or not context_result.context:
        print("Failed to create browser context")
        return

    persistent_context = context_result.context
    print(f"Created browser context: {persistent_context.name} (ID: {persistent_context.id})")

    # Create a browser fingerprint context for first time
    fingerprint_context_name = f"test-browser-fingerprint-{int(time.time())}"
    fingerprint_context_result = agb.context.get(fingerprint_context_name, True)
    if not fingerprint_context_result.success or not fingerprint_context_result.context:
        print("Failed to create fingerprint context")
        return

    persistent_fingerprint_context = fingerprint_context_result.context
    print(f"Created fingerprint context: {persistent_fingerprint_context.name} (ID: {persistent_fingerprint_context.id})")

    # Create session with BrowserContext and FingerprintContext
    print(f"Creating session with browser context ID: {persistent_context.id} "
            f"and fingerprint context ID: {persistent_fingerprint_context.id}")
    fingerprint_context = BrowserFingerprintContext(persistent_fingerprint_context.id)
    browser_context = BrowserContext(persistent_context.id, auto_upload=True, fingerprint_context=fingerprint_context)
    params = CreateSessionParams(
        image_id="agb-browser-use-1",
        browser_context=browser_context
    )

    session_result = agb.create(params)
    if not session_result.success or not session_result.session:
        print(f"Failed to create first session: {session_result.error_message}")
        return

    session = session_result.session
    print(f"First session created with ID: {session.session_id}")

    # Get browser object and generate fingerprint for persistence
    async def first_session_operations():
        # Initialize browser with fingerprint persistent enabled and set fingerprint generation options
        browser_option = BrowserOption(
            use_stealth=True,
            fingerprint_persistent=True,
            fingerprint=BrowserFingerprint(
                devices=["desktop"],
                operating_systems=["windows"],
                locales=["zh-CN"],
            ),
        )
        init_success = await session.browser.initialize_async(browser_option)
        if not init_success:
            print("Failed to initialize browser")
            return
        print("First session browser initialized successfully")

        # Get endpoint URL
        endpoint_url = session.browser.get_endpoint_url()
        if not endpoint_url:
            print("Failed to get browser endpoint URL")
            return
        print(f"First session browser endpoint URL: {endpoint_url}")

        # Connect with playwright, test first session fingerprint
        print("Opening https://httpbin.org/user-agent and test user agent...")
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            context = browser.contexts[0] if browser.contexts else await browser.new_context()

            page = await context.new_page()
            await page.goto("https://httpbin.org/user-agent", timeout=120000)
            response = await page.evaluate("() => JSON.parse(document.body.textContent)")
            user_agent = response["user-agent"]
            print("user_agent =", user_agent)
            is_windows = is_windows_user_agent(user_agent)
            if not is_windows:
                print("Failed to get windows user agent")
                return

            await context.close()
            print("First session browser fingerprint check completed")

    # Run first session operations
    asyncio.run(first_session_operations())

    # Delete first session with syncContext=True
    print("Deleting first session with syncContext=True...")
    delete_result = agb.delete(session, sync_context=True)
    print(f"First session deleted successfully (RequestID: {delete_result.request_id})")


def run_as_second_time():
    """Run as second time - reuse persisted fingerprint"""
    print("="*20)
    print("Run as second time")
    print("="*20)
    global persistent_context, persistent_fingerprint_context
    api_key = os.environ.get("AGB_API_KEY")
    if not api_key:
        print("Error: AGB_API_KEY environment variable not set")
        return

    agb = AGB(api_key)

    # Create second session with same browser context and fingerprint context
    print(f"Creating second session with same browser context ID: {persistent_context.id} "
            f"and fingerprint context ID: {persistent_fingerprint_context.id}")
    fingerprint_context = BrowserFingerprintContext(persistent_fingerprint_context.id)
    browser_context = BrowserContext(persistent_context.id, auto_upload=True, fingerprint_context=fingerprint_context)
    params = CreateSessionParams(
        image_id="agb-browser-use-1",
        browser_context=browser_context
    )
    session_result = agb.create(params)
    if not session_result.success or not session_result.session:
        print(f"Failed to create second session: {session_result.error_message}")
        return

    session = session_result.session
    print(f"Second session created with ID: {session.session_id}")

    # Get browser object and check if second session fingerprint is the same as first session
    async def second_session_operations():
        # Initialize browser with fingerprint persistent enabled but not specific fingerprint generation options
        browser_option = BrowserOption(
            use_stealth=True,
            fingerprint_persistent=True,
        )
        init_success = await session.browser.initialize_async(browser_option)
        if not init_success:
            print("Failed to initialize browser in second session")
            return
        print("Second session browser initialized successfully")

        # Get endpoint URL
        endpoint_url = session.browser.get_endpoint_url()
        if not endpoint_url:
            print("Failed to get browser endpoint URL in second session")
            return
        print(f"Second session browser endpoint URL: {endpoint_url}")

        # Connect with playwright and test second session fingerprint
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            context = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = await context.new_page()
            await page.goto("https://httpbin.org/user-agent", timeout=120000)
            response = await page.evaluate("() => JSON.parse(document.body.textContent)")
            user_agent = response["user-agent"]
            print("user_agent =", user_agent)
            is_windows = is_windows_user_agent(user_agent)
            if not is_windows:
                print("Failed to get windows user agent in second session")
                return
            print("SUCCESS: fingerprint persisted correctly!")

            await context.close()
            print("Second session browser fingerprint check completed")

    # Run second session operations
    asyncio.run(second_session_operations())

    # Delete second session with syncContext=True
    print("Deleting second session with syncContext=True...")
    delete_result = agb.delete(session, sync_context=True)
    print(f"Second session deleted successfully (RequestID: {delete_result.request_id})")


def fingerprint_persistence_example():
    """Test browser fingerprint persist across sessions with the same browser and fingerprint context."""
    run_as_first_time()
    time.sleep(3)
    run_as_second_time()


if __name__ == "__main__":
    fingerprint_persistence_example()
```

### Persistence with Other Fingerprint Types

The fingerprint persistence feature works with all three generation methods:

#### Local Sync Persistence
```python
# First session: Generate from local browser and persist
browser_option = BrowserOption(
    use_stealth=True,
    fingerprint_persistent=True,
    fingerprint_format=local_fingerprint_format  # From BrowserFingerprintGenerator
)
```

#### Custom Fingerprint Persistence
```python
# First session: Load custom fingerprint and persist
browser_option = BrowserOption(
    use_stealth=True,
    fingerprint_persistent=True,
    fingerprint_format=custom_fingerprint_format  # From JSON file or constructed
)
```

## Best Practices

### 1. Browser Context Usage

**💡 Important**: Always use the pre-created browser context provided by AGB SDK.

```python
# ✅ Correct - Use the existing context
browser = await p.chromium.connect_over_cdp(endpoint_url)
context = browser.contexts[0]  # Use the default context
page = await context.new_page()
```

```python
# ❌ Incorrect - Creating new context breaks stealth features
browser = await p.chromium.connect_over_cdp(endpoint_url)
context = await browser.new_context()  # Don't do this
page = await context.new_page()
```

### 2. Important Notice

All fingerprint generation methods require `use_stealth=True` configuration, otherwise fingerprint settings will not take effect. This is because fingerprint functionality depends on stealth mode to properly apply browser feature masking.

```python
# ✅ Correct - Always enable stealth mode for fingerprints
browser_option = BrowserOption(
    use_stealth=True,  # Required for fingerprint to work
    fingerprint=BrowserFingerprint(
        devices=["desktop"],
        operating_systems=["windows"],
        locales=["en-US"]
    )
)
```

```python
# ❌ Incorrect - Missing use_stealth=True
browser_option = BrowserOption(
    # use_stealth=True is missing!
    fingerprint=BrowserFingerprint(
        devices=["desktop"],
        operating_systems=["windows"],
        locales=["en-US"]
    )
)
# Fingerprint configuration will be ignored
```

### 3. Fingerprint Generation Strategy

#### Parameter Priority
When multiple fingerprint parameters are provided, the priority is:
1. `fingerprint_format` (customized generation)
2. `fingerprint` (random generation)

```python
# ✅ Correct - Use fingerprint_format for specific fingerprints
browser_option = BrowserOption(
    use_stealth=True,
    fingerprint_format=my_fingerprint_format
    # fingerprint parameter will be ignored
)
```

```python
# ❌ Avoid - user_agent disables fingerprint features
browser_option = BrowserOption(
    use_stealth=True,
    user_agent="Custom User Agent",
    fingerprint=BrowserFingerprint(...)  # Will be ignored
)
```

### 4. Fingerprint Persistence Behavior

When fingerprint persistence is enabled (`fingerprint_persistent=True`), the system behaves differently based on the fingerprint configuration type:

#### Using `fingerprint` Parameter
When configured with the `fingerprint` parameter, the system will **prioritize persisted fingerprints** over generating new random ones:

```python
# First run - generates and persists a random fingerprint
browser_option = BrowserOption(
    use_stealth=True,
    fingerprint_persistent=True,
    fingerprint=BrowserFingerprint(
        devices=["desktop"],
        operating_systems=["windows"],
        locales=["en-US"]
    )
)

# Subsequent runs - uses the same persisted fingerprint
# The fingerprint parameter serves as a template but won't generate new random values
```

#### Using `fingerprint_format` Parameter
When configured with the `fingerprint_format` parameter, the system will **override existing persisted fingerprints** because the user has explicitly configured the fingerprint parameters:

```python
# This will replace any existing persisted fingerprint
browser_option = BrowserOption(
    use_stealth=True,
    fingerprint_persistent=True,
    fingerprint_format=custom_fingerprint_format  # Overrides persisted data
)
```

#### Behavior Summary

| Configuration Type | Persistence Behavior |
|-------------------|---------------------|
| `fingerprint` | Uses persisted fingerprint if exists, otherwise generates and persists new random fingerprint |
| `fingerprint_format` | Always uses provided fingerprint and overwrites any existing persisted data |

```python
# ✅ Correct - Consistent fingerprint across sessions
browser_option = BrowserOption(
    use_stealth=True,
    fingerprint_persistent=True,
    fingerprint=BrowserFingerprint(devices=["desktop"])
)
# Will use the same fingerprint in all sessions

# ✅ Correct - Force update persisted fingerprint
browser_option = BrowserOption(
    use_stealth=True,
    fingerprint_persistent=True,
    fingerprint_format=new_fingerprint_data
)
# Will replace existing fingerprint with new data
```

### 5. Device and OS Compatibility

Ensure device types match operating systems:

```python
# ✅ Correct configurations
desktop_fingerprint = BrowserFingerprint(
    devices=["desktop"],
    operating_systems=["windows", "macos", "linux"]
)

mobile_fingerprint = BrowserFingerprint(
    devices=["mobile"],
    operating_systems=["android", "ios"]
)
```

```python
# ❌ Incorrect - mismatched device and OS
wrong_fingerprint = BrowserFingerprint(
    devices=["desktop"],
    operating_systems=["android", "ios"]  # Mobile OS with desktop device
)
```

### 6. Context Management for Persistence

- Create unique context names to avoid conflicts
- Use `sync_context=True` when deleting sessions to save fingerprints
- Clean up contexts after use to prevent resource leaks
- Wait for context sync to complete before creating new sessions

## Troubleshooting

### Common Issues

1. **Fingerprint Not Persisting**
   - Ensure `fingerprint_persistent=True` is set
   - Verify browser and fingerprint contexts are properly configured
   - Use `sync_context=True` when deleting sessions
   - Wait for context sync to complete

2. **Local Fingerprint Generation Fails**
   - Check if Chrome is installed and accessible
   - Try running with `headless=False` for debugging
   - Ensure sufficient permissions for browser automation

3. **Custom Fingerprint Loading Errors**
   - Verify JSON file format matches FingerprintFormat schema
   - Check file permissions and path accessibility
   - Validate fingerprint data completeness

## 📚 Related Guides

- [Browser Automation](browser-automation.md) - Complete browser automation features
- [Session Management](session-management.md) - Session lifecycle and configuration
