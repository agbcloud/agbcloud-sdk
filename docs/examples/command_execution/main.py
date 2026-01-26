"""
AGB Command Execution Example

This example demonstrates how to execute shell commands in the cloud environment using the AGB SDK.
It covers:
1. Basic System Information
2. File Operations via Shell
3. Network Diagnostics
4. Advanced Data Processing Pipeline
5. System Monitoring Script
6. Using cwd and envs Parameters (New Features)
7. Accessing Detailed Command Results (exit_code, stdout, stderr)
"""

import os
import sys
import time

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
    params = CreateSessionParams(image_id="agb-code-space-1")
    result = agb.create(params)

    if not result.success:
        print(f"Failed to create session: {result.error_message}")
        return

    session = result.session
    print(f"Session created: {session.session_id}")

    try:
        # 3. System Information
        print("\n=== 1. System Information ===")
        commands = ["uname -a", "whoami", "date", "free -h"]

        for cmd in commands:
            print(f"> {cmd}")
            cmd_result = session.command.execute(cmd)
            if cmd_result.success:
                print(cmd_result.output.strip())
            else:
                print(f"Error: {cmd_result.error_message}")

        # 4. File Operations via Shell
        print("\n=== 2. File Operations (Shell) ===")

        # Create a file
        print("> echo 'Hello via Shell' > /tmp/shell_test.txt")
        session.command.execute("echo 'Hello via Shell' > /tmp/shell_test.txt")

        # Read it back
        print("> cat /tmp/shell_test.txt")
        read_result = session.command.execute("cat /tmp/shell_test.txt")
        print(read_result.output.strip())

        # List details
        print("> ls -l /tmp/shell_test.txt")
        ls_result = session.command.execute("ls -l /tmp/shell_test.txt")
        print(ls_result.output.strip())

        # 5. Network Diagnostics
        print("\n=== 3. Network Diagnostics ===")
        print("> curl -I https://www.google.com (Head Request)")
        curl_result = session.command.execute(
            "curl -I -s --connect-timeout 5 https://www.google.com"
        )
        if curl_result.success:
            # Print just the first few lines of headers
            print("\n".join(curl_result.output.splitlines()[:3]))
        else:
            print(f"Error: {curl_result.error_message}")

        # 6. Advanced Data Processing Pipeline (from Guide)
        print("\n=== 4. Data Processing Pipeline (Advanced) ===")

        # Step A: Create sample CSV data
        csv_data = """name,age,city,salary
Alice,25,New York,50000
Bob,30,London,60000
Charlie,35,Paris,70000
Diana,28,Tokyo,55000
Eve,32,Berlin,65000
Frank,27,Sydney,52000"""

        print("Creating CSV file...")
        session.command.execute(
            f"cat > /tmp/employees.csv << 'EOF'\n{csv_data}\nEOF"
        )

        # Step B: Analyze with awk
        print("Analyzing data with awk...")
        awk_cmd = "awk -F',' 'NR>1 {sum+=$4; count++} END {print \"Average salary: $\" sum/count}' /tmp/employees.csv"
        print(f"> {awk_cmd}")
        awk_result = session.command.execute(awk_cmd)
        print(awk_result.output.strip())

        # Step C: Filter high earners
        filter_cmd = (
            "awk -F',' 'NR>1 && $4>55000 {print $1 \": $\" $4}' /tmp/employees.csv"
        )
        print(f"> {filter_cmd}")
        filter_result = session.command.execute(filter_cmd)
        print("High earners:")
        print(filter_result.output.strip())

        # 7. System Monitoring Script (from Guide)
        print("\n=== 5. System Monitoring Script ===")
        health_check_script = """
#!/bin/bash
echo "System Health Check - $(date)"
echo "================================"
# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
echo "Disk usage: ${DISK_USAGE}%"
# Check memory
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
echo "Memory usage: ${MEM_USAGE}%"
echo "Health check completed"
"""
        # Write script
        print("Deploying health check script...")
        session.command.execute(
            f"cat > /tmp/health_check.sh << 'EOF'\n{health_check_script}\nEOF"
        )
        session.command.execute("chmod +x /tmp/health_check.sh")

        # Run script
        print("Running health check...")
        health_result = session.command.execute("/tmp/health_check.sh")
        if health_result.success:
            print(health_result.output.strip())
        else:
            print(f"Error: {health_result.error_message}")

        # 8. Using cwd and envs Parameters (New Features)
        print("\n=== 6. Using cwd and envs Parameters ===")

        # Example: Using cwd parameter
        print("\n6.1. Using cwd parameter to set working directory:")
        pwd_result = session.command.execute("pwd", cwd="/tmp")
        if pwd_result.success:
            print(f"   Current directory: {pwd_result.output.strip()}")
            if pwd_result.exit_code is not None:
                print(f"   Exit code: {pwd_result.exit_code}")

        # Example: Using envs parameter
        print("\n6.2. Using envs parameter to set environment variables:")
        env_result = session.command.execute(
            "echo $TEST_VAR $ANOTHER_VAR",
            envs={"TEST_VAR": "hello", "ANOTHER_VAR": "world"}
        )
        if env_result.success:
            print(f"   Output: {env_result.output.strip()}")

        # Example: Combining cwd and envs
        print("\n6.3. Combining cwd and envs parameters:")
        combined_result = session.command.execute(
            "pwd && echo $MY_VAR",
            cwd="/tmp",
            envs={"MY_VAR": "test_value"}
        )
        if combined_result.success:
            print(f"   Output:\n{combined_result.output.strip()}")

        # 9. Accessing Detailed Command Results
        print("\n=== 7. Accessing Detailed Command Results ===")

        # Example: Successful command with detailed fields
        print("\n7.1. Successful command:")
        success_result = session.command.execute("echo 'Hello World'")
        if success_result.success:
            print(f"   Success: {success_result.success}")
            print(f"   Exit code: {success_result.exit_code}")
            print(f"   Stdout: {success_result.stdout}")
            print(f"   Stderr: {success_result.stderr}")
            print(f"   Output (stdout + stderr): {success_result.output}")

        # Example: Failed command with detailed fields
        print("\n7.2. Failed command (non-existent file):")
        fail_result = session.command.execute("cat /nonexistent/file.txt")
        print(f"   Success: {fail_result.success}")
        if fail_result.exit_code is not None:
            print(f"   Exit code: {fail_result.exit_code}")
        print(f"   Stdout: {fail_result.stdout}")
        print(f"   Stderr: {fail_result.stderr}")
        if fail_result.trace_id:
            print(f"   Trace ID: {fail_result.trace_id}")
        print(f"   Error message: {fail_result.error_message}")

        # Example: Command with both stdout and stderr
        print("\n7.3. Command with both stdout and stderr:")
        mixed_result = session.command.execute(
            "echo 'This is stdout' && echo 'This is stderr' >&2"
        )
        if mixed_result.success:
            print(f"   Exit code: {mixed_result.exit_code}")
            print(f"   Stdout: {repr(mixed_result.stdout)}")
            print(f"   Stderr: {repr(mixed_result.stderr)}")
            print(f"   Combined output: {repr(mixed_result.output)}")

    finally:
        # 10. Cleanup
        print("\nCleaning up...")
        agb.delete(session)
        print("Session deleted")


if __name__ == "__main__":
    main()
