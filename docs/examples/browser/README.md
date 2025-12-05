# Browser Automation Examples

This directory contains examples for controlling a headless browser within the AGB session.

## Examples

### Basic Navigation (`basic_navigation.py`)
Demonstrates how to start a browser, navigate to a URL, and take a screenshot.

<<< ./basic_navigation.py

### Browser Fingerprint Basic Usage (`browser_fingerprint_basic_usage.py`)
Demonstrates how to use browser fingerprint to avoid detection by anti-bot services. It generates a random, realistic browser fingerprint (e.g., Windows desktop) and verifies the user agent and navigator properties.

<<< ./browser_fingerprint_basic_usage.py

### Browser Fingerprint Construct (`browser_fingerprint_construct.py`)
Shows how to construct a custom `FingerprintFormat` from a JSON file and apply it to the remote browser. This allows you to fully control the browser fingerprint details.

<<< ./browser_fingerprint_construct.py

### Browser Fingerprint Local Sync (`browser_fingerprint_local_sync.py`)
Demonstrates how to sync your local Chrome browser's fingerprint to the remote browser using `BrowserFingerprintGenerator`. This makes the remote browser behave exactly like your local browser.

<<< ./browser_fingerprint_local_sync.py

### Browser Fingerprint Persistence (`browser_fingerprint_persistence.py`)
A more advanced example showing how to persist browser fingerprint across multiple sessions using `BrowserContext` and `BrowserFingerprintContext`. This is useful for maintaining a consistent browser identity over time.

<<< ./browser_fingerprint_persistence.py

### Browser Type Selection (`browser_type_example.py`)
Demonstrates how to select between Chrome and Chromium browsers when using computer use images. Shows browser type configuration, verification, and best practices for choosing the right browser.

<<< ./browser_type_example.py

### Browser Command Arguments (`browser_command_args.py`)
Shows how to launch the browser with custom command-line arguments and a default navigation URL. Useful for disabling specific Chrome features or starting the browser on a specific page.

<<< ./browser_command_args.py

### Natural Language Actions (`natural_language_actions.py`)
Demonstrates how to use natural language instructions (e.g., "Click the 'Sign Up' button") to interact with the page, which simplifies automation logic.

<<< ./natural_language_actions.py

### Data Extraction (`data_extraction.py`)
Shows how to extract structured data from web pages using the `extract` tool.

<<< ./data_extraction.py

### CAPTCHA Solving (`captcha_tongcheng.py`)
A more advanced example showing how the agent can handle complex interactions like CAPTCHA challenges on real-world sites.

<<< ./captcha_tongcheng.py

## Notes

- Browser sessions consume more memory than standard code execution sessions.
- Screenshots are returned as base64 encoded strings.
