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
    params = CreateSessionParams(image_id="agb-code-space-1")
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
        py_result = session.code.run(python_code, "python")
        if py_result.success:
            print("Output:")
            for stdout_item in py_result.logs.stdout:
                print(stdout_item)
        else:
            print(f"Error: {py_result.error_message}")

        # 4. JavaScript Execution
        print("\n=== Executing JavaScript Code ===")
        js_code = """
const numbers = [1, 2, 3, 4, 5];
const sum = numbers.reduce((a, b) => a + b, 0);
console.log(`Sum of [${numbers}] is ${sum}`);
console.log(`User Agent: ${navigator.userAgent}`);
"""
        js_result = session.code.run(js_code, "javascript")
        if js_result.success:
            print("Output:")
            for stdout_item in js_result.logs.stdout:
                print(stdout_item)
        else:
            print(f"Error: {js_result.error_message}")

        # 5. Java Execution
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
        java_result = session.code.run(java_code, "java")
        if java_result.success:
            print("Output:")
            for stdout_item in java_result.logs.stdout:
                print(stdout_item)
        else:
            print(f"Error: {java_result.error_message}")

        # 6. R Execution
        print("\n=== Executing R Code ===")
        r_code = """
data <- c(10, 20, 30, 40, 50)
cat("Data:", data, "\\n")
cat("Mean:", mean(data), "\\n")
cat("SD:", sd(data), "\\n")
"""
        r_result = session.code.run(r_code, "r")
        if r_result.success:
            print("Output:")
            for stdout_item in r_result.logs.stdout:
                print(stdout_item)
        else:
            print(f"Error: {r_result.error_message}")

    finally:
        # 7. Cleanup
        print("\nCleaning up...")
        agb.delete(session)
        print("Session deleted")


if __name__ == "__main__":
    main()
