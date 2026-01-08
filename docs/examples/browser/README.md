# Browser Automation Examples

This directory contains examples for controlling a headless browser within the AGB session.

## Examples

### Basic Navigation
Demonstrates how to start a browser, navigate to a URL, and retrieve page information.

<<< ./basic_navigation.py

### Browser Fingerprint Basic Usage
Demonstrates how to use browser fingerprint to avoid detection by anti-bot services. It generates a random, realistic browser fingerprint (e.g., Windows desktop) and verifies the user agent and navigator properties.

<<< ./browser_fingerprint_basic_usage.py

### Browser Fingerprint Construct
Shows how to construct a custom `FingerprintFormat` from a JSON file and apply it to the remote browser. This allows you to fully control the browser fingerprint details.

<<< ./browser_fingerprint_construct.py

### Browser Fingerprint Local Sync
Demonstrates how to sync your local Chrome browser's fingerprint to the remote browser using `BrowserFingerprintGenerator`. This makes the remote browser behave exactly like your local browser.

<<< ./browser_fingerprint_local_sync.py

### Browser Fingerprint Persistence
A more advanced example showing how to persist browser fingerprint across multiple sessions using `BrowserContext` and `BrowserFingerprintContext`. This is useful for maintaining a consistent browser identity over time.

<<< ./browser_fingerprint_persistence.py

### Browser Type Selection
Demonstrates how to select between Chrome and Chromium browsers when using computer use images. Shows browser type configuration, verification, and best practices for choosing the right browser.

<<< ./browser_type_example.py

### Browser Command Arguments
Shows how to launch the browser with custom command-line arguments and a default navigation URL. Useful for disabling specific Chrome features or starting the browser on a specific page.

<<< ./browser_command_args.py
### Screenshot Capture
Demonstrates comprehensive browser screenshot functionality including:
- Viewport screenshots (visible area only)
- Full-page screenshots (long screenshots for entire scrollable content)
- JPEG format with quality settings
- Custom timeout configuration
- Multiple page screenshot workflow
- Error handling best practices

<<< ./screenshot_capture.py

### Natural Language Actions
Demonstrates how to use natural language instructions (e.g., "Click the 'Sign Up' button") to interact with the page, which simplifies automation logic.

<<< ./natural_language_actions.py

### Data Extraction
Shows how to extract structured data from web pages using the `extract` tool.

<<< ./data_extraction.py

### CAPTCHA Solving
A more advanced example showing how the agent can handle complex interactions like CAPTCHA challenges on real-world sites.

<<< ./captcha_tongcheng.py

## Notes

- Browser sessions consume more memory than standard code execution sessions.
- Screenshots are returned as raw bytes from `session.browser.screenshot()`.
- For full-page (long) screenshots, use `full_page=True` parameter.
- JPEG format with quality setting produces smaller file sizes compared to PNG.
- Always initialize browser before taking screenshots to avoid BrowserError.
