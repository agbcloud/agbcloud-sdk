# Browser Automation Examples

This directory contains examples for controlling a headless browser within the AGB session.

## Examples

### Basic Navigation (`basic_navigation.py`)
Demonstrates how to start a browser, navigate to a URL, and take a screenshot.

<<< ./basic_navigation.py

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
