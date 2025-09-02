#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGB session creation test code (simplified version)
"""

import sys
import os
import time

# Add project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Direct import, completely bypass __init__.py
import importlib.util
from agb.agb import AGB
from agb.session_params import CreateSessionParams


def get_api_key():
    """Get API Key from environment variables"""
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        raise ValueError(
            "AGB_API_KEY environment variable not set. Please set the environment variable:\n"
        )

    return api_key

def test_create_session():
    """Test creating AGB session"""

    # API key
    api_key = get_api_key()
    print(f"Using API Key: {api_key}")

    try:
        print("Initializing AGB client...")

        # Create AGB instance
        agb = AGB(api_key=api_key)
        print(f"✅ AGB client initialized successfully")
        print(f"   Endpoint: {agb.endpoint}")
        print(f"   Timeout: {agb.timeout_ms}ms")

        print("\nCreating session...")

        # Create session with specific image_id for code execution
        # Record session creation start time
        create_start_time = time.time()

        params = CreateSessionParams(image_id="agb-code-space-2")
        result = agb.create(params)

        # Record session creation end time
        create_end_time = time.time()
        create_duration = create_end_time - create_start_time

        print(f"⏱️  Session creation took: {create_duration:.3f} seconds")

        # Check result
        if result.success:
            print("✅ Session created successfully!")
            print(f"   Request ID: {result.request_id}")
            print(f"   Session ID: {result.session.session_id}")
            if hasattr(result.session, 'resource_url') and result.session.resource_url:
                print(f"   Resource URL: {result.session.resource_url}")
            if hasattr(result.session, 'image_id') and result.session.image_id:
                print(f"   Image ID: {result.session.image_id}")
        else:
            print("❌ Session creation failed!")
            print(f"   Error message: {result.error_message}")
            if result.request_id:
                print(f"   Request ID: {result.request_id}")

        return result, agb, create_duration

    except Exception as e:
        print(f"❌ Error occurred during test: {e}")
        import traceback
        traceback.print_exc()
        return None, None, 0


def test_run_code(session):
    """Test code execution functionality"""
    print("\n" + "=" * 60)
    print("Testing Code Execution Functionality")
    print("=" * 60)

    try:
        # Test Python code execution
        print("1. Testing Python code execution...")
        python_code = """
import datetime
import platform
import random

print("=== Python Code Execution Test ===")
print(f"Current time: {datetime.datetime.now()}")
print(f"Python version: {platform.python_version()}")
print(f"System platform: {platform.platform()}")

# Generate random numbers
numbers = [random.randint(1, 100) for _ in range(5)]
print(f"Random numbers: {numbers}")
print(f"Maximum: {max(numbers)}")
print(f"Minimum: {min(numbers)}")
print(f"Average: {sum(numbers) / len(numbers):.2f}")

# Simple calculation
result = 2 ** 10
print(f"2 to the power of 10: {result}")

print("Python code execution completed!")
"""

        result = session.code.run_code(python_code, "python", timeout_s=60)
        if result.success:
            print("✅ Python code execution successful!")
            print(f"   Request ID: {result.request_id}")
            print(f"   Execution result:\n{result.result}")
        else:
            print("❌ Python code execution failed!")
            print(f"   Error message: {result.error_message}")
            if result.request_id:
                print(f"   Request ID: {result.request_id}")

        # Test JavaScript code execution
        print("\n2. Testing JavaScript code execution...")
        js_code = """
console.log("=== JavaScript Code Execution Test ===");

// Get current time
const now = new Date();
console.log(`Current time: ${now.toISOString()}`);

// Array operations
const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
console.log(`Original array: ${numbers}`);

const squares = numbers.map(x => x * x);
console.log(`Squared array: ${squares}`);

const evenNumbers = numbers.filter(x => x % 2 === 0);
console.log(`Even numbers: ${evenNumbers}`);

const sum = numbers.reduce((acc, x) => acc + x, 0);
console.log(`Sum: ${sum}`);

// String operations
const message = "Hello AGB!";
console.log(`Message: ${message}`);
console.log(`Length: ${message.length}`);
console.log(`Uppercase: ${message.toUpperCase()}`);

console.log("JavaScript code execution completed!");
"""

        result = session.code.run_code(js_code, "javascript", timeout_s=60)
        if result.success:
            print("✅ JavaScript code execution successful!")
            print(f"   Request ID: {result.request_id}")
            print(f"   Execution result:\n{result.result}")
        else:
            print("❌ JavaScript code execution failed!")
            print(f"   Error message: {result.error_message}")
            if result.request_id:
                print(f"   Request ID: {result.request_id}")

        # Test Java code execution
        print("\n3. Testing Java code execution...")
        java_code = """
System.out.println("=== Java Code Execution Test ===");
System.out.println("Hello from Java!");

// Basic calculations
int a = 10;
int b = 20;
int sum = a + b;
System.out.println("Sum of " + a + " and " + b + " is: " + sum);

// Array operations
int[] numbers = {1, 2, 3, 4, 5};
int total = 0;
for (int num : numbers) {
    total += num;
}
System.out.println("Array sum: " + total);

System.out.println("Java code execution completed!");
"""

        result = session.code.run_code(java_code, "java", timeout_s=60)
        if result.success:
            print("✅ Java code execution successful!")
            print(f"   Request ID: {result.request_id}")
            print(f"   Execution result:\n{result.result}")
        else:
            print("❌ Java code execution failed!")
            print(f"   Error message: {result.error_message}")
            if result.request_id:
                print(f"   Request ID: {result.request_id}")

        # Test R code execution - Basic operations
        print("\n4. Testing R code execution - Basic operations...")
        r_code = """
# R Statistical Analysis Test
cat("=== R Code Execution Test ===\\n")

# Basic data operations
numbers <- c(10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
cat("Numbers:", numbers, "\\n")

# Statistical calculations
mean_val <- mean(numbers)
median_val <- median(numbers)
sd_val <- sd(numbers)
min_val <- min(numbers)
max_val <- max(numbers)

cat("Mean:", mean_val, "\\n")
cat("Median:", median_val, "\\n")
cat("Standard Deviation:", sd_val, "\\n")
cat("Minimum:", min_val, "\\n")
cat("Maximum:", max_val, "\\n")

# Vector operations
squared <- numbers^2
cat("Squared values:", squared, "\\n")

# String operations
message <- "Hello from R!"
cat("Message:", message, "\\n")
cat("Message length:", nchar(message), "\\n")
cat("Uppercase:", toupper(message), "\\n")

# Data frame creation
df <- data.frame(
    x = 1:5,
    y = c(2, 4, 6, 8, 10),
    z = c("a", "b", "c", "d", "e")
)
cat("Data frame:\\n")
print(df)

cat("R code execution completed!\\n")
"""

        result = session.code.run_code(r_code, "r", timeout_s=60)
        if result.success:
            print("✅ R code execution successful!")
            print(f"   Request ID: {result.request_id}")
            print(f"   Execution result:\n{result.result}")
        else:
            print("❌ R code execution failed!")
            print(f"   Error message: {result.error_message}")
            if result.request_id:
                print(f"   Request ID: {result.request_id}")

        # Test R advanced operations
        print("\n4b. Testing R advanced operations...")
        r_advanced_code = """
# Advanced R operations
cat("=== Advanced R Operations ===\\n")

# Generate sample data
set.seed(123)  # For reproducible results
x <- 1:20
y <- x + rnorm(20, mean=0, sd=2)

cat("X values:", x, "\\n")
cat("Y values:", y, "\\n")

# Linear regression
model <- lm(y ~ x)
cat("Linear model summary:\\n")
print(summary(model))

# Correlation
correlation <- cor(x, y)
cat("Correlation coefficient:", correlation, "\\n")

# Matrix operations
matrix_a <- matrix(1:6, nrow=2, ncol=3)
matrix_b <- matrix(7:12, nrow=3, ncol=2)
cat("Matrix A:\\n")
print(matrix_a)
cat("Matrix B:\\n")
print(matrix_b)

# Matrix multiplication
result_matrix <- matrix_a %*% matrix_b
cat("Matrix multiplication result:\\n")
print(result_matrix)

cat("Advanced R operations completed!\\n")
"""

        result_advanced = session.code.run_code(r_advanced_code, "r", timeout_s=60)
        if result_advanced.success:
            print("✅ Advanced R code execution successful!")
            print(f"   Request ID: {result_advanced.request_id}")
            print(f"   Execution result:\n{result_advanced.result}")
        else:
            print("❌ Advanced R code execution failed!")
            print(f"   Error message: {result_advanced.error_message}")
            if result_advanced.request_id:
                print(f"   Request ID: {result_advanced.request_id}")

        # Test error handling
        print("\n5. Testing error handling...")
        error_code = """
print("Starting execution...")
# Intentionally create an error
undefined_variable + 1
print("This line won't execute")
"""

        result = session.code.run_code(error_code, "python", timeout_s=30)
        if result.success:
            print("⚠️  Error code unexpectedly executed successfully")
            print(f"   Result: {result.result}")
        else:
            print("✅ Expected: Python error code execution failed!")
            print(f"   Error message: {result.error_message}")
            if result.request_id:
                print(f"   Request ID: {result.request_id}")

        # Test case-insensitive language parameter
        print("\n6. Testing case-insensitive language parameter...")
        
        # Test various case combinations for different languages
        test_cases = [
            ('print("Hello from Python!")', "PYTHON", "Python uppercase"),
            ('print("Hello from Python!")', "Python", "Python title case"),
            ('print("Hello from Python!")', "PyThOn", "Python mixed case"),
            ('print("Hello from Python!")', "python", "Python lowercase"),
            ('console.log("Hello from JavaScript!");', "JAVASCRIPT", "JavaScript uppercase"),
            ('console.log("Hello from JavaScript!");', "JavaScript", "JavaScript title case"),
            ('console.log("Hello from JavaScript!");', "javascript", "JavaScript lowercase"),
            ('cat("Hello from R!\\n")', "R", "R uppercase"),
            ('cat("Hello from R!\\n")', "r", "R lowercase"),
            ('System.out.println("Hello from Java!");', "JAVA", "Java uppercase"),
            ('System.out.println("Hello from Java!");', "Java", "Java title case"),
            ('System.out.println("Hello from Java!");', "java", "Java lowercase")
        ]
        
        for code, language_param, description in test_cases:
            print(f"   Testing {description}: '{language_param}'")
            result = session.code.run_code(code, language_param, timeout_s=30)
            if result.success:
                print(f"   ✅ {description} accepted successfully!")
            else:
                print(f"   ❌ {description} failed: {result.error_message}")

        # Test unsupported language with different cases
        print("\n   Testing unsupported language with different cases...")
        unsupported_cases = [
            ("UNSUPPORTED", "uppercase unsupported"),
            ("Unsupported", "title case unsupported"),
            ("unsupported", "lowercase unsupported")
        ]
        
        for language_param, description in unsupported_cases:
            print(f"   Testing {description}: '{language_param}'")
            result = session.code.run_code('print("test")', language_param, timeout_s=30)
            if result.success:
                print(f"   ❌ Unexpected: {description} was accepted!")
            else:
                print(f"   ✅ Expected: {description} was rejected: {result.error_message}")

        return True

    except Exception as e:
        print(f"❌ Error occurred during code execution test: {e}")
        import traceback
        traceback.print_exc()
        return False



def main():
    """Main function"""
    print("=" * 60)
    print("AGB Session Creation Test (Simplified Version)")
    print("=" * 60)

    # Test session creation
    result, agb, create_duration = test_create_session()

    if result and result.success and agb:
        # Test code execution functionality
        code_test_success = test_run_code(result.session)

        # Optional: Test session deletion
        print("\n" + "=" * 60)
        print("Do you want to delete the created session? (y/n): ", end="")
        try:
            choice = input().strip().lower()
            if choice in ['y', 'yes']:
                print("Deleting session...")

                # Record session deletion start time
                delete_start_time = time.time()

                delete_result = agb.delete(result.session)

                # Record session deletion end time
                delete_end_time = time.time()
                delete_duration = delete_end_time - delete_start_time

                print(f"⏱️  Session deletion took: {delete_duration:.3f} seconds")

                print("delete_result =", delete_result)
                if delete_result.success:
                    print("✅ Session deleted successfully!")
                else:
                    print(f"❌ Session deletion failed: {delete_result.error_message}")

                # Print total time statistics
                print("\n" + "=" * 60)
                print("📊 PERFORMANCE SUMMARY")
                print("=" * 60)
                print(f"Session Creation: {create_duration:.3f} seconds")
                print(f"Session Deletion: {delete_duration:.3f} seconds")
                print(f"Total API Time:  {create_duration + delete_duration:.3f} seconds")
                print("=" * 60)

        except KeyboardInterrupt:
            print("\nUser cancelled deletion operation")

    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)


if __name__ == "__main__":
    main()
