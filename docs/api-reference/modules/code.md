# Code Module API Reference

The Code module provides code execution capabilities in the AGB cloud environment. It supports executing Python and JavaScript code with configurable timeouts and comprehensive error handling.

## Class Definition

```python
from agb.modules.code import Code, CodeExecutionResult

class Code(BaseService):
    def __init__(self, session)
```

## Methods

### `run_code(code, language, timeout_s=300)`

Execute code in the specified language with a timeout.

**Parameters:**
- `code` (str): The code to execute.
- `language` (str): The programming language of the code. Supported languages are: `'python'`, `'javascript'`, `'java'`, `'r'`.
- `timeout_s` (int, optional): The timeout for the code execution in seconds. Default is 300 seconds (5 minutes).

**Returns:**
- `CodeExecutionResult`: Result object containing success status, execution result, and error message if any.

**Supported Languages:**
- `"python"` - Python 3.x code execution
- `"javascript"` - JavaScript (Node.js) code execution
- `"java"` - Java code execution (code snippets only, no class definitions required)
- `"r"` - R language code execution

**Example:**
```python
# Python code execution
python_code = """
import math
result = math.sqrt(16)
print(f"Square root of 16 is: {result}")
"""

code_result = session.code.run_code(python_code, "python")
if code_result.success:
    print("Output:", code_result.result)
else:
    print("Error:", code_result.error_message)

# JavaScript code execution
javascript_code = """
const numbers = [1, 2, 3, 4, 5];
const sum = numbers.reduce((a, b) => a + b, 0);
console.log(`Sum: ${sum}`);
"""

js_result = session.code.run_code(javascript_code, "javascript")
if js_result.success:
    print("JS Output:", js_result.result)

# Java code execution
java_code = """
System.out.println("Hello from Java!");
int result = 5 + 3;
System.out.println("Result: " + result);

// Array operations
int[] numbers = {1, 2, 3, 4, 5};
int sum = 0;
for (int num : numbers) {
    sum += num;
}
System.out.println("Array sum: " + sum);
"""

java_result = session.code.run_code(java_code, "java")
if java_result.success:
    print("Java Output:", java_result.result)

# R code execution
r_code = """
# Basic R operations
numbers <- c(1, 2, 3, 4, 5)
print(paste("Numbers:", paste(numbers, collapse=", ")))
mean_value <- mean(numbers)
print(paste("Mean:", mean_value))
"""

r_result = session.code.run_code(r_code, "r")
if r_result.success:
    print("R Output:", r_result.result)
```

## Language-Specific Notes

### Java Code Execution

Java code execution supports **code snippets only**. You don't need to define classes or main methods - just write your Java statements directly:

```python
# ✅ Correct - Code snippet format
java_code = """
int x = 10;
int y = 20;
System.out.println("Sum: " + (x + y));
"""

# ❌ Incorrect - Full class definition (not supported)
java_code = """
public class MyClass {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
"""
```

## CodeExecutionResult Class

Result object returned by code execution operations.

For detailed information about the response object, see: **[CodeExecutionResult](../responses/code-result.md)**

### Usage Example

```python
code_result = session.code.run_code("print('Hello World')", "python")

print(f"Request ID: {code_result.request_id}")
print(f"Success: {code_result.success}")

if code_result.success:
    print(f"Output: {code_result.result}")
else:
    print(f"Error: {code_result.error_message}")
    # Partial output may still be available
    if code_result.result:
        print(f"Partial output: {code_result.result}")
```

## Language-Specific Features

### Python Execution

Python code runs in a Python 3.x environment with access to standard libraries and many popular packages.

#### Available Standard Libraries

```python
python_code = """
# Standard library access
import os, sys, json, datetime, math, random, re
import urllib.request, urllib.parse
from collections import defaultdict, Counter
from itertools import combinations, permutations

print(f"Python version: {sys.version}")
print(f"Available modules: {len(sys.modules)}")
"""

result = session.code.run_code(python_code, "python")
```

#### File System Access

```python
python_code = """
import tempfile
import os

# Create temporary file
with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    f.write("Hello from Python!")
    temp_file = f.name

print(f"Created file: {temp_file}")

# Read it back
with open(temp_file, 'r') as f:
    content = f.read()
    print(f"File content: {content}")

# Clean up
os.unlink(temp_file)
"""

result = session.code.run_code(python_code, "python")
```

#### Data Processing

```python
python_code = """
import json
import csv
from io import StringIO

# JSON processing
data = {"name": "Alice", "age": 30, "city": "New York"}
json_str = json.dumps(data, indent=2)
print("JSON data:")
print(json_str)

# CSV processing
csv_data = "name,age\\nAlice,25\\nBob,30"
reader = csv.DictReader(StringIO(csv_data))
for row in reader:
    print(f"{row['name']} is {row['age']} years old")
"""

result = session.code.run_code(python_code, "python")
```

### JavaScript Execution

JavaScript code runs in a Node.js environment with access to built-in modules and modern JavaScript features.

#### Modern JavaScript Features

```javascript
javascript_code = """
// Modern JavaScript features
const data = [1, 2, 3, 4, 5];

// Arrow functions and array methods
const doubled = data.map(x => x * 2);
const sum = data.reduce((acc, val) => acc + val, 0);

console.log("Original:", data);
console.log("Doubled:", doubled);
console.log("Sum:", sum);

// Object destructuring
const person = { name: "Alice", age: 25, city: "New York" };
const { name, age } = person;
console.log(`${name} is ${age} years old`);

// Template literals
const message = `Hello, ${name}! Welcome to ${person.city}.`;
console.log(message);
"""

result = session.code.run_code(javascript_code, "javascript")
```

#### Async/Await Support

```javascript
javascript_code = """
// Async/await example
async function fetchData() {
    return new Promise(resolve => {
        setTimeout(() => resolve("Data fetched!"), 100);
    });
}

async function main() {
    try {
        const data = await fetchData();
        console.log(data);
    } catch (error) {
        console.error("Error:", error.message);
    }
}

main();
"""

result = session.code.run_code(javascript_code, "javascript")
```

## Usage Patterns

### Basic Code Execution

```python
from agb import AGB

def execute_simple_code():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        # Execute Python code
        result = session.code.run_code("""
        for i in range(5):
            print(f"Count: {i}")
        """, "python")

        if result.success:
            print("Python output:")
            print(result.result)

        # Execute JavaScript code
        result = session.code.run_code("""
        for (let i = 0; i < 5; i++) {
            console.log(`Count: ${i}`);
        }
        """, "javascript")

        if result.success:
            print("JavaScript output:")
            print(result.result)

    finally:
        agb.delete(session)

execute_simple_code()
```

### Multi-Step Code Execution

```python
def multi_step_execution():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        # Step 1: Setup data
        setup_result = session.code.run_code("""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        print(f"Data initialized: {data}")
        """, "python")

        if not setup_result.success:
            print("Setup failed:", setup_result.error_message)
            return

        # Step 2: Process data
        process_result = session.code.run_code("""
        # Data persists between executions in the same session
        filtered_data = [x for x in data if x % 2 == 0]
        squared_data = [x**2 for x in filtered_data]
        print(f"Filtered (even): {filtered_data}")
        print(f"Squared: {squared_data}")
        """, "python")

        if process_result.success:
            print("Processing output:")
            print(process_result.result)

        # Step 3: Calculate result
        final_result = session.code.run_code("""
        total = sum(squared_data)
        average = total / len(squared_data)
        print(f"Total: {total}")
        print(f"Average: {average}")
        """, "python")

        if final_result.success:
            print("Final output:")
            print(final_result.result)

    finally:
        agb.delete(session)

multi_step_execution()
```

### Code Execution with File Integration

```python
def code_with_files():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        # Create input file
        session.file_system.write_file("/tmp/input.txt", "Hello\nWorld\nFrom\nAGB")

        # Process file with code
        result = session.code.run_code("""
        # Read and process file
        with open('/tmp/input.txt', 'r') as f:
            lines = f.readlines()

        # Process lines
        processed_lines = [line.strip().upper() for line in lines]

        # Write processed data
        with open('/tmp/output.txt', 'w') as f:
            for line in processed_lines:
                f.write(f"Processed: {line}\\n")

        print(f"Processed {len(processed_lines)} lines")
        print("Processed lines:", processed_lines)
        """, "python")

        if result.success:
            print("Code output:")
            print(result.result)

            # Read result file
            output_result = session.file_system.read_file("/tmp/output.txt")
            if output_result.success:
                print("Output file content:")
                print(output_result.content)

    finally:
        agb.delete(session)

code_with_files()
```

### Error Handling and Debugging

```python
def robust_code_execution():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        # Code that will cause an error
        error_code = """
        print("This will work")
        result = 10 / 0  # This will cause an error
        print("This won't be reached")
        """

        result = session.code.run_code(error_code, "python")

        print(f"Success: {result.success}")
        print(f"Request ID: {result.request_id}")

        if result.success:
            print("Output:", result.result)
        else:
            print("Error:", result.error_message)
            # Check if we got partial output
            if result.result:
                print("Partial output before error:")
                print(result.result)

        # Try to recover with corrected code
        corrected_code = """
        print("This will work")
        try:
            result = 10 / 0
        except ZeroDivisionError as e:
            print(f"Caught error: {e}")
            result = 10 / 2
        print(f"Result: {result}")
        """

        corrected_result = session.code.run_code(corrected_code, "python")
        if corrected_result.success:
            print("Corrected code output:")
            print(corrected_result.result)

    finally:
        agb.delete(session)

robust_code_execution()
```

### Timeout Handling

```python
def timeout_example():
    agb = AGB()
    params = CreateSessionParams(image_id="agb-code-space-1")
    session = agb.create(params).session

    try:
        # Long-running code with short timeout
        long_code = """
        import time
        print("Starting long operation...")
        time.sleep(10)  # This will exceed the timeout
        print("Operation completed!")
        """

        # Set timeout to 5 seconds
        result = session.code.run_code(long_code, "python", timeout_s=5)

        if not result.success:
            if "timeout" in result.error_message.lower():
                print("Code execution timed out")
                print("Partial output:", result.result)
            else:
                print("Other error:", result.error_message)

        # Shorter operation that will complete
        quick_code = """
        import time
        print("Starting quick operation...")
        time.sleep(1)
        print("Quick operation completed!")
        """

        quick_result = session.code.run_code(quick_code, "python", timeout_s=5)
        if quick_result.success:
            print("Quick operation output:")
            print(quick_result.result)

    finally:
        agb.delete(session)

timeout_example()
```

## Best Practices

### 1. Always Check Execution Results

```python
# ✅ Good: Always check success status
result = session.code.run_code(code, "python")
if result.success:
    print("Output:", result.result)
else:
    print("Error:", result.error_message)
    # Handle error appropriately

# ❌ Bad: Assuming execution always succeeds
result = session.code.run_code(code, "python")
print(result.result)  # May be empty if execution failed
```

### 2. Use Appropriate Timeouts

```python
# ✅ Good: Set reasonable timeouts based on expected execution time
quick_result = session.code.run_code(simple_code, "python", timeout_s=30)
long_result = session.code.run_code(complex_code, "python", timeout_s=600)

# ❌ Avoid: Using very long timeouts for simple operations
result = session.code.run_code("print('hello')", "python", timeout_s=3600)  # Unnecessary
```

### 3. Handle Partial Output

```python
# ✅ Good: Check for partial output even on failure
result = session.code.run_code(code, "python")
if not result.success:
    print(f"Execution failed: {result.error_message}")
    if result.result:
        print(f"Partial output: {result.result}")
```

### 4. Use Session State Effectively

```python
# ✅ Good: Leverage session state for multi-step operations
session.code.run_code("data = [1, 2, 3, 4, 5]", "python")
session.code.run_code("processed = [x*2 for x in data]", "python")
result = session.code.run_code("print(processed)", "python")

# ❌ Less efficient: Recreating data in each execution
session.code.run_code("data = [1, 2, 3, 4, 5]; processed = [x*2 for x in data]; print(processed)", "python")
```

### 5. Validate Input Code

```python
def safe_code_execution(session, code, language):
    """Execute code with basic validation"""

    # Basic validation
    if not code.strip():
        return {"success": False, "error": "Empty code"}

    if language not in ["python", "javascript"]:
        return {"success": False, "error": f"Unsupported language: {language}"}

    # Length check
    if len(code) > 100000:  # 100KB limit
        return {"success": False, "error": "Code too large"}

    # Execute code
    result = session.code.run_code(code, language)

    return {
        "success": result.success,
        "output": result.result,
        "error": result.error_message if not result.success else None,
        "request_id": result.request_id
    }
```


## Related Documentation

- **[Session API](../core/session.md)** - Session management and lifecycle
- **[Command Module](command.md)** - Shell command execution
- **[FileSystem Module](filesystem.md)** - File operations for code integration
- **[Code Execution Guide](../../guides/code-execution.md)** - User guide for code execution
- **[Best Practices](../../guides/best-practices.md)** - Production deployment patterns