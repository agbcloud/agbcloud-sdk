#!/usr/bin/env python3
"""
Demonstrates scenarios where run returns multiple results.

Usage:
    python docs/examples/code_execution/multiple_results_demo.py
"""

import os
from dotenv import load_dotenv
from agb import AGB
from agb.session_params import CreateSessionParams

load_dotenv()

def demo_multiple_display():
    """Scenario 1: Multiple display() calls"""
    print("\n" + "="*60)
    print("Scenario 1: Multiple display() calls")
    print("="*60)

    code = """
from IPython.display import display, HTML, Markdown

# First display - HTML
display(HTML("<h1>Heading 1</h1>"))

# Second display - Markdown
display(Markdown("# Markdown Heading"))

# Third display - HTML
display(HTML("<p>This is a paragraph</p>"))

# Final return value
"Processing completed"
"""

    return code, "Expected 4 result items (3 displays + 1 return value)"


def demo_multiple_charts():
    """Scenario 2: Generate multiple charts"""
    print("\n" + "="*60)
    print("Scenario 2: Generate multiple charts")
    print("="*60)

    code = """
import matplotlib.pyplot as plt

# First chart
plt.figure(figsize=(6, 4))
plt.plot([1, 2, 3], [1, 2, 3])
plt.title("Line Chart")
plt.show()

# Second chart
plt.figure(figsize=(6, 4))
plt.bar([1, 2, 3], [3, 1, 4])
plt.title("Bar Chart")
plt.show()

"Chart generation completed"
"""

    return code, "Expected 3 result items (2 charts + 1 return value)"


def demo_mixed_output():
    """Scenario 3: Mixed output (data + chart + text)"""
    print("\n" + "="*60)
    print("Scenario 3: Mixed output (data + chart + text)")
    print("="*60)

    code = """
import pandas as pd
from IPython.display import display, HTML
import matplotlib.pyplot as plt

# 1. Display data table
df = pd.DataFrame({
    'Product': ['A', 'B', 'C'],
    'Sales': [100, 200, 150]
})
display(df)

# 2. Display descriptive text
display(HTML("<p><b>Data Analysis Results:</b></p>"))

# 3. Display visualization chart
plt.figure(figsize=(8, 5))
df.plot(x='Product', y='Sales', kind='bar', legend=False)
plt.title("Product Sales Comparison")
plt.show()

# 4. Return statistical result
f"Total Sales: {df['Sales'].sum()}"
"""

    return code, "Expected 4 result items (table + HTML text + chart + return value)"


def demo_single_result():
    """Scenario 4: Single result (comparison scenario)"""
    print("\n" + "="*60)
    print("Scenario 4: Single result (comparison scenario)")
    print("="*60)

    code = """
# Only print output and one return value
print("Starting calculation...")
result = 42 * 2
print(f"Calculation result: {result}")

# Final return
result
"""

    return code, "Expected 1 result item (return value), print in stdout"


def demo_only_prints():
    """Scenario 5: Only print, no return value"""
    print("\n" + "="*60)
    print("Scenario 5: Only print, no explicit return value")
    print("="*60)

    code = """
print("This is the first line of output")
print("This is the second line of output")
print("This is the third line of output")
# No explicit return value
"""

    return code, "Expected results may be empty or only None, output in stdout"


def analyze_results(result, description):
    """Analyze and display results"""
    print(f"\n📊 {description}")
    print("-" * 60)

    if not result.success:
        print(f"❌ Execution failed: {result.error_message}")
        return

    print(f"✅ Execution succeeded")
    print(f"⏱️  Execution time: {result.execution_time:.3f} seconds")

    # Analyze results
    print(f"\n📦 results list: {len(result.results)} result items")

    if result.results:
        for i, item in enumerate(result.results, 1):
            print(f"\n  Result {i}:")
            print(f"    is_main_result: {item.is_main_result}")

            # List contained formats
            formats = []
            if item.text:
                formats.append(f"text({len(item.text)} chars)")
            if item.html:
                formats.append(f"html({len(item.html)} chars)")
            if item.markdown:
                formats.append(f"markdown({len(item.markdown)} chars)")
            if item.png:
                formats.append(f"png({len(item.png)} bytes)")
            if item.jpeg:
                formats.append(f"jpeg({len(item.jpeg)} bytes)")
            if item.chart:
                formats.append(f"chart({type(item.chart).__name__})")

            print(f"    Formats: {', '.join(formats) if formats else 'None'}")

            # Display content preview
            if item.text and len(item.text) < 100:
                print(f"    Preview: {item.text}")
            elif item.text:
                print(f"    Preview: {item.text[:100]}...")
    else:
        print("  (empty list)")

    # Analyze logs
    print(f"\n📝 logs.stdout: {len(result.logs.stdout)} lines")
    if result.logs.stdout:
        for i, line in enumerate(result.logs.stdout[:3], 1):  # Show only first 3 lines
            print(f"    Line {i}: {line.strip()}")
        if len(result.logs.stdout) > 3:
            print(f"    ... {len(result.logs.stdout) - 3} more lines")

    print(f"\n📝 logs.stderr: {len(result.logs.stderr)} lines")
    if result.logs.stderr:
        for line in result.logs.stderr:
            print(f"    {line.strip()}")


def main():
    """Main function"""
    print("="*60)
    print("🚀 Multiple Results Scenarios Demo")
    print("="*60)

    # Initialize
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        print("❌ Error: Please set AGB_API_KEY environment variable")
        return

    agb = AGB(api_key=api_key)

    # Create session
    print("\n📍 Creating session...")
    params = CreateSessionParams(image_id="agb-code-space-1")
    session_result = agb.create(params)

    if not session_result.success:
        print(f"❌ Failed to create session: {session_result.error_message}")
        return

    session = session_result.session
    print(f"✅ Session created successfully: {session.session_id}")

    try:
        # Run demo scenarios
        scenarios = [
            demo_single_result,      # Start with simple scenario
            demo_only_prints,        # No return value scenario
            demo_multiple_display,   # Multiple display calls
            demo_multiple_charts,    # Multiple charts
            demo_mixed_output,       # Mixed output
        ]

        for scenario_func in scenarios:
            code, description = scenario_func()

            print(f"\n🔧 Executing code...")
            print("```python")
            print(code.strip())
            print("```")

            result = session.code.run(code, "python")
            analyze_results(result, description)

            input("\nPress Enter to continue to next scenario...")

        print("\n" + "="*60)
        print("✅ All demo scenarios completed")
        print("="*60)

    finally:
        # Cleanup session
        print("\n🧹 Cleaning up session...")
        delete_result = agb.delete(session)
        if delete_result.success:
            print("✅ Session deleted")
        else:
            print(f"⚠️  Failed to delete session: {delete_result.error_message}")


if __name__ == "__main__":
    main()
