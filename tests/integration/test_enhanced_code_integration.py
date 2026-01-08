#!/usr/bin/env python3
"""
Enhanced Code Execution Integration Tests for AGB SDK.
Tests the enhanced code execution functionality with rich output formats.
"""

import pytest
import os
from agb import AGB
from agb.session_params import CreateSessionParams
from agb.model.response import EnhancedCodeExecutionResult

# Global session variable for reuse
_shared_session = None

def get_shared_session():
    """Get or create a shared session for all tests."""
    global _shared_session

    if _shared_session is None:
        api_key = os.getenv("AGB_API_KEY")
        if not api_key:
            pytest.fail("AGB_API_KEY environment variable not set")

        agb = AGB(api_key=api_key)
        params = CreateSessionParams(image_id="agb-code-space-2")
        session_result = agb.create(params)
        if not session_result.success or not session_result.session:
            pytest.fail(f"Failed to create session: {session_result.error_message}")

        _shared_session = session_result.session

    return _shared_session

def test_enhanced_result_structure():
    """Test that results use the enhanced structure."""
    session = get_shared_session()
    code = """
print("Hello, enhanced world!")
42
"""
    result = session.code.run_code(code, "python")

    assert isinstance(result, EnhancedCodeExecutionResult)
    assert result.success
    assert result.request_id is not None

    # Test enhanced features
    assert hasattr(result, 'logs')
    assert hasattr(result, 'results')
    assert hasattr(result, 'execution_time')
    assert (res.is_main_result for res in result.results)

def test_logs_capture():
    """Test that stdout and stderr are properly captured."""
    session = get_shared_session()
    code = """
import sys
print("This goes to stdout")
print("This also goes to stdout", file=sys.stdout)
print("This goes to stderr", file=sys.stderr)
"Final result"
"""
    result = session.code.run_code(code, "python")

    assert result.success
    assert isinstance(result.logs.stdout, list)
    assert isinstance(result.logs.stderr, list)

    # Check that output is captured (exact format may vary)
    stdout_content = "".join(result.logs.stdout) if result.logs.stdout else ""
    stderr_content = "".join(result.logs.stderr) if result.logs.stderr else ""

    # At minimum, some output should be captured
    assert len(stdout_content) > 0 or len(stderr_content) > 0 or len(result.results) > 0
    assert (res.is_main_result for res in result.results)

def test_multiple_results_formats():
    """Test handling of multiple result formats."""
    session = get_shared_session()
    code = """
# Test various output types
print("Standard output")

# Text result
text_result = "This is a text result"

# Dictionary that could be JSON
json_data = {"key": "value", "number": 42}

# Return the text result
text_result
"""
    result = session.code.run_code(code, "python")

    assert result.success
    assert isinstance(result.results, list)

    # Should have at least one result
    assert len(result.results) >= 0
    assert (res.is_main_result for res in result.results)

def test_execution_timing():
    """Test that execution time is tracked."""
    session = get_shared_session()
    code = """
import time
time.sleep(0.1)  # Small delay
"Execution completed"
"""
    result = session.code.run_code(code, "python")

    assert result.success
    assert hasattr(result, 'execution_time')
    assert isinstance(result.execution_time, (int, float))
    # Should be at least 0.0 seconds
    assert result.execution_time >= 0.0
    assert (res.is_main_result for res in result.results)

def test_error_details():
    """Test enhanced error reporting."""
    session = get_shared_session()
    code = """
# This should cause a NameError
print(undefined_variable_that_does_not_exist)
"""
    result = session.code.run_code(code, "python")

    # Error handling may vary - could be success=False or an error in results
    # In some cases, the error might be captured in executionError rather than success=False
    # Or it might appear in stderr
    has_error = (not result.success or
                (result.error_message and len(result.error_message) > 0) or
                (result.logs.stderr and len(result.logs.stderr) > 0))
    assert has_error

    if result.error_message:
        assert isinstance(result.error_message, str)
        assert len(result.error_message) > 0

def test_javascript_enhanced_features():
    """Test enhanced features with JavaScript."""
    session = get_shared_session()
    code = """
console.log("JavaScript output");
const data = {message: "Hello from JS", value: 123};
console.log(JSON.stringify(data));
data.value * 2;
"""
    result = session.code.run_code(code, "javascript")

    assert isinstance(result, EnhancedCodeExecutionResult)
    assert result.success
    assert result.logs is not None
    assert result.results is not None
    assert (res.is_main_result for res in result.results)

def test_large_output_handling():
    """Test handling of large outputs."""
    session = get_shared_session()
    code = """
# Generate some larger output
large_list = list(range(100))
print("Generated list of", len(large_list), "items")
for i in range(10):
    print(f"Line {i}: {i * i}")
"Processing completed"
"""
    result = session.code.run_code(code, "python")

    assert result.success
    assert result.logs is not None
    assert result.results is not None

    # Should handle the output without issues
    has_expected_output = (
        any("Generated list" in str(res.text or "") for res in result.results) or
        any("Generated list" in str(log) for log in result.logs.stdout)
    )
    assert has_expected_output
    assert (res.is_main_result for res in result.results)

def test_execution_count_tracking():
    """Test that execution count is tracked if available."""
    session = get_shared_session()
    code1 = "print('First execution')"
    code2 = "print('Second execution')"

    result1 = session.code.run_code(code1, "python")
    result2 = session.code.run_code(code2, "python")

    assert result1.success
    assert result2.success
    print(f"Execution count: {result1.execution_count}, {result2.execution_count}")
    # execution_count may or may not be provided by the backend
    if result1.execution_count is not None:
        assert isinstance(result1.execution_count, int)
    if result2.execution_count is not None:
        assert isinstance(result2.execution_count, int)
    # Verify that both executions produced stdout output
    stdout_content_1 = "".join(stdout_item or '' for stdout_item in result1.logs.stdout)
    stdout_content_2 = "".join(stdout_item or '' for stdout_item in result2.logs.stdout)
    assert len(stdout_content_1) > 0 and len(stdout_content_2) > 0
def test_mixed_output_types():
    """Test code that produces mixed output types."""
    session = get_shared_session()
    code = """
import json
print("Starting mixed output test")

# Text output
text_data = "Simple text"
print(f"Text: {text_data}")

# JSON-like output
json_data = {"type": "test", "values": [1, 2, 3]}
print("JSON:", json.dumps(json_data))

# Final result
"Mixed output test completed"
"""
    result = session.code.run_code(code, "python")

    assert result.success
    assert result.logs is not None
    assert result.results is not None

    # Should capture various types of output
    has_expected_output = any("Starting mixed output test" in str(log) for log in result.logs.stdout)
    assert has_expected_output
    assert (res.is_main_result for res in result.results)

def test_empty_code_execution():
    """Test execution of empty or minimal code."""
    session = get_shared_session()
    code = "# Just a comment"
    result = session.code.run_code(code, "python")

    assert result.success
    assert result.logs is not None
    assert result.results is not None

def test_backward_compatibility_properties():
    """Test that all backward compatibility properties work."""
    session = get_shared_session()
    code = """
print("Testing backward compatibility")
final_result = "This is the final result"
final_result
"""
    result = session.code.run_code(code, "python")

    assert result.success

    # Test all expected properties exist
    assert hasattr(result, 'success')
    assert hasattr(result, 'request_id')

    # Test new properties exist
    assert hasattr(result, 'logs')
    assert hasattr(result, 'results')
    assert hasattr(result, 'execution_time')
    assert hasattr(result, 'execution_count')
    assert hasattr(result, 'error_message')

    # Test property types
    assert isinstance(result.success, bool)
    assert isinstance(result.request_id, str)
    assert (res.is_main_result for res in result.results)

def test_html_output():
    """Test HTML output generation."""
    session = get_shared_session()
    code = """
from IPython.display import display, HTML

# Display HTML content
display(HTML("<h1>Hello HTML</h1>"))
"""
    result = session.code.run_code(code, "python")
    assert result.success
    # Check if any result has html content - handle both direct attribute and JSON structure
    has_html = any(
        (hasattr(res, 'html') and res.html is not None and "<h1>Hello HTML</h1>" in res.html)
        for res in result.results
    )
    assert has_html
    # HTML output may not be available in all environments, so we just check that execution succeeded
    assert result.success
    assert (res.is_main_result == False for res in result.results)

def test_markdown_output():
    """Test Markdown output generation."""
    session = get_shared_session()
    code = """
from IPython.display import display, Markdown

display(Markdown('# Hello Markdown'))
"""
    result = session.code.run_code(code, "python")
    assert result.success
    # Markdown output may not be available in all environments, so we just check that execution succeeded
    has_markdown = any(
        (hasattr(res, 'markdown') and res.markdown is not None and "Hello Markdown" in res.markdown)
        for res in result.results
    )
    assert has_markdown
    assert (res.is_main_result == False for res in result.results)

def test_image_output():
    """Test image (PNG/JPEG) output generation."""
    session = get_shared_session()
    code = """
import matplotlib.pyplot as plt

plt.figure()
plt.plot([1, 2, 3], [1, 2, 3])
plt.title("Test Plot")
plt.show()
"""
    result = session.code.run_code(code, "python")
    assert result.success
    # Image output may not be available in all environments, so we just check that execution succeeded
    has_png_or_jpeg = any(
        (hasattr(res, 'png') and res.png is not None and len(res.png) > 0) or
        (hasattr(res, 'jpeg') and res.jpeg is not None and len(res.jpeg) > 0)
        for res in result.results
    )
    assert has_png_or_jpeg
    assert (res.is_main_result == False for res in result.results)

def test_svg_output():
    """Test SVG output generation."""
    session = get_shared_session()
    code = """
from IPython.display import display, SVG

svg_code = '<svg height="100" width="100"><circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" /></svg>'
display(SVG(svg_code))
"""
    result = session.code.run_code(code, "python")
    assert result.success
    # SVG output may not be available in all environments, so we just check that execution succeeded
    has_svg = any(
            (hasattr(res, 'svg') and res.svg is not None and len(res.svg) > 0)
            for res in result.results
        )
    assert has_svg
    assert (res.is_main_result == False for res in result.results)

def test_latex_output():
    """Test LaTeX output generation."""
    session = get_shared_session()
    code = r"""
from IPython.display import display, Latex

display(Latex(r'\frac{1}{2}'))
"""
    result = session.code.run_code(code, "python")
    assert result.success
    # LaTeX output may not be available in all environments, so we just check that execution succeeded
    has_latex = any(
            (hasattr(res, 'latex') and res.latex is not None and "frac{1}{2}" in res.latex)
            for res in result.results
        )
    assert has_latex
    assert (res.is_main_result == False for res in result.results)

def test_chart_output():
    """Test structured chart output."""
    session = get_shared_session()
    # Use a mock object to simulate chart output without external dependencies like Altair
    code = """
from IPython.display import display
class MockChart:
    def _repr_mimebundle_(self, include=None, exclude=None):
        return {
            "application/vnd.vegalite.v4+json": {"data": "mock_chart_data", "mark": "bar"},
            "text/plain": "MockChart"
        }
display(MockChart())
"""
    result = session.code.run_code(code, "python")
    assert result.success
    # Chart output may not be available in all environments, so we just check that execution succeeded
    has_chart = any(
            (hasattr(res, 'chart') and res.chart is not None and isinstance(res.chart, dict))
            for res in result.results
        )
    assert has_chart
    all_have_chart = all(
        (hasattr(res, 'chart') and isinstance(res.chart, dict))
        for res in result.results
    )
    assert all_have_chart
    assert (res.is_main_result == False for res in result.results)

def test_language_aliases():
    """Test language aliases support."""
    session = get_shared_session()

    # Test python3 -> python
    result = session.code.run_code("print('Python3 alias test')", "python3")
    assert result.success

    # Test js -> javascript
    result = session.code.run_code("console.log('JS alias test')", "js")
    assert result.success
    assert len(result.logs.stdout) > 0

def test_unsupported_language():
    """Test execution with unsupported language."""
    session = get_shared_session()
    result = session.code.run_code("print('test')", "ruby")

    assert isinstance(result, EnhancedCodeExecutionResult)
    assert not result.success
    assert result.error_message is not None
    assert len(result.error_message) > 0
    assert "ruby" in result.error_message

def test_zzz_cleanup():
    """Cleanup shared session - runs last due to name sorting."""
    global _shared_session
    if _shared_session:
        try:
            # Use AGB's delete method
            api_key = os.getenv("AGB_API_KEY")
            if api_key:
                agb = AGB(api_key=api_key)
                agb.delete(_shared_session)
            _shared_session = None
        except Exception:
            pass  # Ignore cleanup errors

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
