"""
AGB Code Execution Example

This example demonstrates how to execute code in various languages (Python, JavaScript, Java, R)
using the AGB SDK.
"""

import os
import sys

from agb import AGB
from agb.session_params import CreateSessionParams


def main():
    # 1. Initialize AGB client
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        print("Error: AGB_API_KEY environment variable is not set")
        return

    agb = AGB(api_key=api_key)

    # 2. Create a session
    print("Creating session...")
    # Note: For code execution, we recommend using the 'agb-code-space-1' image
    params = CreateSessionParams(image_id="agb-code-space-2")
    result = agb.create(params)

    if not result.success:
        print(f"Failed to create session: {result.error_message}")
        return

    session = result.session
    print(f"Session created: {session.session_id}")

    try:
        # 3. Python Execution
        print("\n=== Executing Python Code ===")
        python_code = """
import datetime
import math

print(f"Current time: {datetime.datetime.now()}")
print(f"Pi is approximately: {math.pi:.4f}")
numbers = [x**2 for x in range(5)]
print(f"Squares: {numbers}")
"""
        py_result = session.code.run_code(python_code, "python")
        if py_result.success:
            print("Output:")
            # Display stdout logs
            for stderr_item in py_result.logs.stderr:
                print(f"   Execution result:\n{stderr_item}")
        else:
            if py_result.error:
                print(f"Error: {py_result.error.name}: {py_result.error.value}")
            else:
                print("Execution failed with unknown error")

        # 4. JavaScript Execution
        print("\n=== Executing JavaScript Code ===")
        js_code = """
const numbers = [1, 2, 3, 4, 5];
const sum = numbers.reduce((a, b) => a + b, 0);
console.log(`Sum of [${numbers}] is ${sum}`);
console.log(`User Agent: ${navigator.userAgent}`);
"""
        js_result = session.code.run_code(js_code, "javascript")
        if js_result.success:
            print("Output:")
            # Display stdout logs
            for stdout_line in js_result.logs.stdout:
                print(stdout_line)

        else:
            if js_result.error_message:
                print(f"Error: {js_result.error_message}")
            else:
                print("Execution failed with unknown error")

        # 6. Java Execution
        # Note: Java support allows running snippets without boilerplate class definitions
        print("\n=== Executing Java Code ===")
        java_code = """
String message = "Hello from Java!";
System.out.println(message);
System.out.println("String length: " + message.length());
int[] arr = {10, 20, 30};
int sum = 0;
for(int i : arr) sum += i;
System.out.println("Array sum: " + sum);
"""
        java_result = session.code.run_code(java_code, "java")
        if java_result.success:
            print("Output:")
            # Display stdout logs
            for stdout_line in java_result.logs.stdout:
                print(stdout_line)
        else:
            if java_result.error:
                print(f"Error: {java_result.error.name}: {java_result.error.value}")
            else:
                print("Execution failed with unknown error")

        # 7. R Execution
        print("\n=== Executing R Code ===")
        r_code = """
data <- c(10, 20, 30, 40, 50)
cat("Data:", data, "\\n")
cat("Mean:", mean(data), "\\n")
cat("SD:", sd(data), "\\n")
"""
        r_result = session.code.run_code(r_code, "r")
        if r_result.success:
            print("Output:")
            # Display stdout logs
            for stdout_line in r_result.logs.stdout:
                print(stdout_line)
        else:
            if r_result.error:
                print(f"Error: {r_result.error.name}: {r_result.error.value}")
            else:
                print("Execution failed with unknown error")

        # 8. Rich Media Output Example (Python with HTML/Images)
        print("\n=== Rich Media Output Example ===")
        rich_code = """
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import HTML, display

# Create a simple plot
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 4))
plt.plot(x, y, 'b-', linewidth=2)
plt.title('Sine Wave')
plt.xlabel('x')
plt.ylabel('sin(x)')
plt.grid(True)
plt.show()

# Display HTML content
html_content = '''
<div style="background-color: #f0f8ff; padding: 10px; border-radius: 5px;">
    <h3 style="color: #4169e1;">Rich HTML Output</h3>
    <p>This is an example of <strong>HTML content</strong> in code execution results.</p>
    <ul>
        <li>Supports <em>formatted text</em></li>
        <li>Can include <span style="color: red;">colored elements</span></li>
        <li>Tables, lists, and more!</li>
    </ul>
</div>
'''
display(HTML(html_content))

print("Rich media example completed!")
"""
        rich_result = session.code.run_code(rich_code, "python")
        if rich_result.success:
            print("Output:")
            # Display stdout logs
            for stdout_line in rich_result.logs.stdout:
                print(stdout_line)

            # Display different types of results
            for i, result in enumerate(rich_result.results):
                print(f"\n--- Result {i+1} ---")

                if result.text:
                    print(f"Text: {result.text}")

                if result.html:
                    print(f"HTML Content: {len(result.html)} characters")
                    print(
                        "HTML Preview:",
                        (
                            result.html[:200] + "..."
                            if len(result.html) > 200
                            else result.html
                        ),
                    )

                if result.png:
                    print(f"PNG Image: {len(result.png)} bytes (base64 encoded)")

                if result.jpeg:
                    print(f"JPEG Image: {len(result.jpeg)} bytes (base64 encoded)")

                if result.svg:
                    print(f"SVG Image: {len(result.svg)} characters")

                if result.chart:
                    print(f"Chart Data: {type(result.chart)}")

                if result.markdown:
                    print(f"Markdown: {result.markdown}")

                if result.latex:
                    print(f"LaTeX: {result.latex}")

                print(f"Is Main Result: {result.is_main_result}")

            # Display execution metadata
            print(f"\nExecution Metadata:")
            print(f"  Execution Count: {rich_result.execution_count}")
            print(f"  Execution Time: {rich_result.execution_time}s")
            print(f"  Request ID: {rich_result.request_id}")
        else:
            if rich_result.error:
                print(f"Error: {rich_result.error.name}: {rich_result.error.value}")
            else:
                print("Execution failed with unknown error")

    finally:
        # 9. Cleanup
        print("\nCleaning up...")
        agb.delete(session)
        print("Session deleted")


if __name__ == "__main__":
    main()
