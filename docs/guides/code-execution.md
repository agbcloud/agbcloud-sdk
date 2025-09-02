# Code Execution Guide

## Overview

The AGB SDK provides powerful code execution capabilities in the cloud. You can run Python, JavaScript, Java, and R code in isolated, secure environments without needing to install language runtimes locally. This guide covers everything from basic code execution to advanced patterns and best practices.

## Quick Reference (1 minute)

```python
from agb import AGB

agb = AGB()
session = agb.create().session

# Execute Python code
result = session.code.run_code("print('Hello, World!')", "python")
print(result.result)

# Execute JavaScript code
result = session.code.run_code("console.log('Hello, World!')", "javascript")
print(result.result)

# Execute Java code
java_code = """
System.out.println("Hello, World!");
int x = 42;
System.out.println("The answer is: " + x);
"""
result = session.code.run_code(java_code, "java")
print(result.result)

# Execute R code
result = session.code.run_code("cat('Hello, World!\\n')", "r")
print(result.result)

agb.delete(session)
```

## Basic Usage (5 minutes)

### Simple Code Execution

```python
from agb import AGB

agb = AGB()
result = agb.create()
session = result.session

# Python example
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

agb.delete(session)
```

### JavaScript Execution

```python
# JavaScript example
javascript_code = """
const numbers = [1, 2, 3, 4, 5];
const sum = numbers.reduce((a, b) => a + b, 0);
console.log(`Sum of numbers: ${sum}`);
"""

code_result = session.code.run_code(javascript_code, "javascript")
if code_result.success:
    print("Output:", code_result.result)
else:
    print("Error:", code_result.error_message)
```

### Java Execution

Java code execution supports code snippets without requiring full class definitions or main methods. The system automatically wraps your code in the appropriate execution context.

```python
# Java example
java_code = """
int[] numbers = {10, 20, 30, 40, 50};
int sum = 0;

System.out.println("Numbers:");
for (int num : numbers) {
    System.out.print(num + " ");
    sum += num;
}

System.out.println("\nSum: " + sum);
System.out.println("Average: " + (sum / numbers.length));

// String manipulation
String text = "Java Code Execution";
System.out.println("Original: " + text);
System.out.println("Uppercase: " + text.toUpperCase());
System.out.println("Length: " + text.length());
"""

code_result = session.code.run_code(java_code, "java")
if code_result.success:
    print("Output:", code_result.result)
else:
    print("Error:", code_result.error_message)
```

### R Execution

```python
# R example
r_code = """
# Statistical analysis in R
data <- c(23, 45, 56, 78, 32, 67, 89, 12, 34, 56)
cat("Data:", data, "\n")

# Basic statistics
cat("Mean:", mean(data), "\n")
cat("Median:", median(data), "\n")
cat("Standard Deviation:", sd(data), "\n")

# Create a simple plot data
x <- 1:10
y <- x^2
cat("X values:", x, "\n")
cat("Y values (x^2):", y, "\n")
"""

code_result = session.code.run_code(r_code, "r")
if code_result.success:
    print("Output:", code_result.result)
else:
    print("Error:", code_result.error_message)

### Timeout Configuration

```python
# Long-running code with custom timeout
long_running_code = """
import time
print("Starting long operation...")
time.sleep(5)
print("Operation completed!")
"""

# Set timeout to 10 seconds (default is 300s)
code_result = session.code.run_code(long_running_code, "python", timeout_s=10)
```

### Error Handling

```python
# Code that will cause an error
error_code = """
print("This will work")
print(undefined_variable)  # This will cause an error
print("This won't be reached")
"""

code_result = session.code.run_code(error_code, "python")
if not code_result.success:
    print("Execution failed:")
    print("Error:", code_result.error_message)
    print("Partial output:", code_result.result)  # May contain output before error
```

## Advanced Usage (15 minutes)

### Multi-step Code Execution

```python
class CodeExecutor:
    def __init__(self):
        self.agb = AGB()
        self.session = None
        self.variables = {}

    def start_session(self):
        """Start a new code execution session"""
        result = self.agb.create()
        if result.success:
            self.session = result.session
            return True
        else:
            print(f"Failed to create session: {result.error_message}")
            return False

    def execute_step(self, code: str, language: str = "python", description: str = ""):
        """Execute a code step and track results"""
        if not self.session:
            raise Exception("No active session. Call start_session() first.")

        print(f"Executing: {description or 'Code step'}")
        result = self.session.code.run_code(code, language)

        if result.success:
            print(f"✅ Success: {result.result}")
            return result.result
        else:
            print(f"❌ Error: {result.error_message}")
            return None

    def cleanup(self):
        """Clean up the session"""
        if self.session:
            self.agb.delete(self.session)
            self.session = None

# Usage example
executor = CodeExecutor()
executor.start_session()

# Step 1: Setup data
executor.execute_step("""
import pandas as pd
import numpy as np

# Create sample data
data = {
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'age': [25, 30, 35, 28],
    'salary': [50000, 60000, 70000, 55000]
}
df = pd.DataFrame(data)
print("Data created:")
print(df)
""", description="Create sample dataset")

# Step 2: Analyze data
executor.execute_step("""
# Calculate statistics
avg_age = df['age'].mean()
avg_salary = df['salary'].mean()
print(f"Average age: {avg_age}")
print(f"Average salary: ${avg_salary:,.2f}")
""", description="Calculate statistics")

# Step 3: Filter data
executor.execute_step("""
# Filter high earners
high_earners = df[df['salary'] > 55000]
print("High earners:")
print(high_earners)
""", description="Filter high earners")

executor.cleanup()
```

### Code Execution with File Integration

```python
def execute_code_with_files(agb: AGB, code: str, input_files: dict = None, output_files: list = None):
    """Execute code with file input/output handling"""
    result = agb.create()
    if not result.success:
        return {"success": False, "error": result.error_message}

    session = result.session

    try:
        # Upload input files if provided
        if input_files:
            for filename, content in input_files.items():
                write_result = session.file_system.write_file(filename, content)
                if not write_result.success:
                    return {"success": False, "error": f"Failed to write {filename}: {write_result.error_message}"}

        # Execute the code
        code_result = session.code.run_code(code, "python")
        if not code_result.success:
            return {"success": False, "error": code_result.error_message, "output": code_result.result}

        # Read output files if specified
        output_data = {}
        if output_files:
            for filename in output_files:
                read_result = session.file_system.read_file(filename)
                if read_result.success:
                    output_data[filename] = read_result.content

        return {
            "success": True,
            "output": code_result.result,
            "files": output_data
        }

    finally:
        agb.delete(session)

# Usage example
agb = AGB()

# Input data
input_files = {
    "/tmp/data.csv": "name,age,salary\nAlice,25,50000\nBob,30,60000\nCharlie,35,70000"
}

# Code to process the data
processing_code = """
import pandas as pd

# Read the input file
df = pd.read_csv('/tmp/data.csv')
print("Original data:")
print(df)

# Process the data
df['salary_category'] = df['salary'].apply(lambda x: 'High' if x > 55000 else 'Low')
print("\\nProcessed data:")
print(df)

# Save processed data
df.to_csv('/tmp/processed_data.csv', index=False)
print("\\nData saved to /tmp/processed_data.csv")
"""

# Execute with file handling
result = execute_code_with_files(
    agb,
    processing_code,
    input_files=input_files,
    output_files=["/tmp/processed_data.csv"]
)

if result["success"]:
    print("Execution Output:")
    print(result["output"])
    print("\nOutput Files:")
    for filename, content in result["files"].items():
        print(f"{filename}:")
        print(content)
else:
    print("Execution failed:", result["error"])
```

### Concurrent Code Execution

```python
import concurrent.futures
from typing import List, Dict

def execute_code_task(agb: AGB, task: Dict):
    """Execute a single code task"""
    result = agb.create()
    if not result.success:
        return {"task_id": task["id"], "success": False, "error": result.error_message}

    session = result.session

    try:
        code_result = session.code.run_code(task["code"], task.get("language", "python"))
        return {
            "task_id": task["id"],
            "success": code_result.success,
            "output": code_result.result,
            "error": code_result.error_message if not code_result.success else None
        }
    finally:
        agb.delete(session)

def execute_parallel_tasks(tasks: List[Dict], max_workers: int = 3):
    """Execute multiple code tasks in parallel"""
    agb = AGB()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = [executor.submit(execute_code_task, agb, task) for task in tasks]

        # Collect results
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({"success": False, "error": str(e)})

    return results

# Usage example
tasks = [
    {
        "id": "math_task",
        "code": """
import math
result = math.factorial(10)
print(f"10! = {result}")
""",
        "language": "python"
    },
    {
        "id": "string_task",
        "code": """
text = "Hello, World!"
print(f"Reversed: {text[::-1]}")
print(f"Length: {len(text)}")
""",
        "language": "python"
    },
    {
        "id": "js_task",
        "code": """
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);
console.log("Doubled:", doubled);
""",
        "language": "javascript"
    }
]

results = execute_parallel_tasks(tasks)

for result in results:
    print(f"Task {result['task_id']}: {'✅' if result['success'] else '❌'}")
    if result['success']:
        print(f"Output: {result['output']}")
    else:
        print(f"Error: {result['error']}")
    print("-" * 40)
```

### Code Execution with Environment Setup

```python
def setup_python_environment(session, packages: List[str]):
    """Setup Python environment with required packages"""
    if not packages:
        return True

    # Install packages
    install_code = f"""
import subprocess
import sys

packages = {packages}
for package in packages:
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print(f"✅ Installed {{package}}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {{package}}: {{e}}")
"""

    result = session.code.run_code(install_code, "python")
    return result.success

def execute_with_environment(agb: AGB, code: str, packages: List[str] = None):
    """Execute code with custom environment setup"""
    result = agb.create()
    if not result.success:
        return {"success": False, "error": result.error_message}

    session = result.session

    try:
        # Setup environment if packages specified
        if packages:
            print("Setting up environment...")
            if not setup_python_environment(session, packages):
                return {"success": False, "error": "Failed to setup environment"}

        # Execute the main code
        print("Executing code...")
        code_result = session.code.run_code(code, "python")

        return {
            "success": code_result.success,
            "output": code_result.result,
            "error": code_result.error_message if not code_result.success else None
        }

    finally:
        agb.delete(session)

# Usage example
agb = AGB()

# Code that requires specific packages
analysis_code = """
import requests
import matplotlib.pyplot as plt
import numpy as np

# Generate sample data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create a simple plot
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2)
plt.title('Sine Wave')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)

# Save the plot
plt.savefig('/tmp/sine_wave.png')
print("Plot saved to /tmp/sine_wave.png")

# Make a simple HTTP request
try:
    response = requests.get('https://httpbin.org/json')
    print(f"HTTP Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"HTTP request failed: {e}")
"""

result = execute_with_environment(
    agb,
    analysis_code,
    packages=["requests", "matplotlib", "numpy"]
)

if result["success"]:
    print("Execution completed successfully:")
    print(result["output"])
else:
    print("Execution failed:", result["error"])
```

## Language-Specific Features

### Python Features

```python
# Python-specific capabilities
python_features = """
# Standard library access
import os, sys, json, datetime, math, random
print(f"Python version: {sys.version}")
print(f"Available modules: {len(sys.modules)}")

# File system access
import tempfile
with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    f.write("Hello from Python!")
    temp_file = f.name

print(f"Created temporary file: {temp_file}")

# Data processing
import csv
from io import StringIO

csv_data = "name,age\\nAlice,25\\nBob,30"
reader = csv.DictReader(StringIO(csv_data))
for row in reader:
    print(f"{row['name']} is {row['age']} years old")

# Error handling
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Caught error: {e}")
"""

session.code.run_code(python_features, "python")
```

### JavaScript Features

```python
# JavaScript-specific capabilities
javascript_features = """
// Modern JavaScript features
const data = [1, 2, 3, 4, 5];

// Arrow functions and array methods
const doubled = data.map(x => x * 2);
const sum = data.reduce((acc, val) => acc + val, 0);

console.log("Original:", data);
console.log("Doubled:", doubled);
console.log("Sum:", sum);

// Async/await (if supported)
async function fetchData() {
    return new Promise(resolve => {
        setTimeout(() => resolve("Data fetched!"), 100);
    });
}

// Object destructuring
const person = { name: "Alice", age: 25, city: "New York" };
const { name, age } = person;
console.log(`${name} is ${age} years old`);

// Template literals
const message = `Hello, ${name}! Welcome to ${person.city}.`;
console.log(message);

// Error handling
try {
    throw new Error("Test error");
} catch (error) {
    console.log("Caught error:", error.message);
}
"""

session.code.run_code(javascript_features, "javascript")
```

## Best Practices

### 1. Code Organization

```python
# ✅ Good: Break complex code into steps
def execute_data_pipeline(session):
    """Execute a data processing pipeline in steps"""

    # Step 1: Data loading
    load_code = """
import pandas as pd
data = pd.read_csv('/tmp/input.csv')
print(f"Loaded {len(data)} rows")
"""
    result1 = session.code.run_code(load_code, "python")
    if not result1.success:
        return False, "Data loading failed"

    # Step 2: Data processing
    process_code = """
# Clean and process data
data_cleaned = data.dropna()
data_processed = data_cleaned.groupby('category').sum()
print("Data processed successfully")
"""
    result2 = session.code.run_code(process_code, "python")
    if not result2.success:
        return False, "Data processing failed"

    # Step 3: Save results
    save_code = """
data_processed.to_csv('/tmp/output.csv')
print("Results saved")
"""
    result3 = session.code.run_code(save_code, "python")
    return result3.success, "Pipeline completed" if result3.success else "Save failed"
```

### 2. Error Recovery

```python
def robust_code_execution(session, code: str, language: str, max_retries: int = 3):
    """Execute code with retry logic"""
    for attempt in range(max_retries):
        try:
            result = session.code.run_code(code, language)
            if result.success:
                return result
            else:
                print(f"Attempt {attempt + 1} failed: {result.error_message}")
                if attempt < max_retries - 1:
                    print("Retrying...")
        except Exception as e:
            print(f"Attempt {attempt + 1} exception: {e}")
            if attempt < max_retries - 1:
                print("Retrying...")

    return None  # All attempts failed
```

### 3. Resource Management

```python
def execute_with_resource_monitoring(session, code: str, language: str):
    """Execute code with resource monitoring"""
    import time

    start_time = time.time()

    # Check initial session health
    initial_info = session.info()

    try:
        result = session.code.run_code(code, language)
        execution_time = time.time() - start_time

        print(f"Execution completed in {execution_time:.2f}s")

        # Check final session health
        final_info = session.info()
        if initial_info.success and final_info.success:
            print("Session remained healthy")

        return result

    except Exception as e:
        execution_time = time.time() - start_time
        print(f"Execution failed after {execution_time:.2f}s: {e}")
        return None
```

### 4. Code Validation

```python
def validate_and_execute(session, code: str, language: str):
    """Validate code before execution"""

    # Basic validation
    if not code.strip():
        return {"success": False, "error": "Empty code"}

    if language not in ["python", "javascript"]:
        return {"success": False, "error": f"Unsupported language: {language}"}

    # Language-specific validation
    if language == "python":
        # Check for dangerous operations
        dangerous_patterns = ["os.system", "subprocess.call", "exec(", "eval("]
        for pattern in dangerous_patterns:
            if pattern in code:
                print(f"Warning: Potentially dangerous operation detected: {pattern}")

    # Execute the code
    result = session.code.run_code(code, language)

    return {
        "success": result.success,
        "output": result.result,
        "error": result.error_message if not result.success else None
    }
```

## Troubleshooting

### Common Issues

**Timeout Errors**
```python
# Increase timeout for long-running code
result = session.code.run_code(long_code, "python", timeout_s=600)  # 10 minutes
```

**Memory Issues**
```python
# Break large operations into smaller chunks
large_data_code = """
# Instead of loading all data at once
# data = pd.read_csv('huge_file.csv')  # May cause memory issues

# Process in chunks
chunk_size = 10000
for chunk in pd.read_csv('huge_file.csv', chunksize=chunk_size):
    # Process each chunk
    processed_chunk = chunk.groupby('category').sum()
    print(f"Processed chunk with {len(chunk)} rows")
"""
```

**Import Errors**
```python
# Check available packages
check_packages = """
import sys
import pkg_resources

installed_packages = [d.project_name for d in pkg_resources.working_set]
print("Available packages:", sorted(installed_packages))
"""

session.code.run_code(check_packages, "python")
```

**Syntax Errors**
```python
# Validate syntax before execution
def validate_python_syntax(code: str) -> bool:
    try:
        compile(code, '<string>', 'exec')
        return True
    except SyntaxError as e:
        print(f"Syntax error: {e}")
        return False

# Usage
code_to_check = "print('Hello World')"
if validate_python_syntax(code_to_check):
    result = session.code.run_code(code_to_check, "python")
```

## Related Documentation

- **[Session Management Guide](session-management.md)** - Managing code execution sessions
- **[Command Execution Tutorial](../guides/command-execution.md)** - Running shell commands
- **[File Operations Tutorial](../guides/file-operations.md)** - Working with files in code
- **[API Reference](../api-reference/modules/code.md)** - Complete code execution API
- **[Examples](../examples/file_system/README.md)** - More code execution examples