# Command Execution Tutorial

## Overview

This tutorial teaches you how to execute shell commands in the AGB cloud environment using the Command module. You'll learn to run system commands, process output, handle errors, and integrate command execution with other AGB modules.

## Quick Reference (1 minute)

```python
from agb import AGB

agb = AGB()
session = agb.create().session

# Basic command execution
result = session.command.execute_command("ls -la /tmp")
if result.success:
    print("Output:", result.output)
else:
    print("Error:", result.error_message)

# Command with timeout
result = session.command.execute_command("find / -name '*.txt'", timeout_ms=5000)

agb.delete(session)
```

## Step-by-Step Tutorial (10 minutes)

### Step 1: Basic Command Execution

```python
from agb import AGB

# Initialize AGB and create session
agb = AGB()
session = agb.create().session

try:
    # Execute a simple command
    result = session.command.execute_command("echo 'Hello from AGB!'")
    
    if result.success:
        print("Command succeeded!")
        print("Output:", result.output)
        print("Request ID:", result.request_id)
    else:
        print("Command failed!")
        print("Error:", result.error_message)

finally:
    agb.delete(session)
```

### Step 2: System Information Commands

```python
def get_system_info():
    agb = AGB()
    session = agb.create().session
    
    try:
        # System information commands
        commands = [
            ("whoami", "Current user"),
            ("pwd", "Current directory"),
            ("uname -a", "System information"),
            ("date", "Current date and time"),
            ("uptime", "System uptime")
        ]
        
        print("System Information Report")
        print("=" * 40)
        
        for cmd, description in commands:
            result = session.command.execute_command(cmd)
            
            print(f"\n{description}:")
            if result.success:
                print(result.output.strip())
            else:
                print(f"Error: {result.error_message}")
    
    finally:
        agb.delete(session)

get_system_info()
```

### Step 3: File System Operations

```python
def file_system_commands():
    agb = AGB()
    session = agb.create().session
    
    try:
        # Create a test directory
        result = session.command.execute_command("mkdir -p /tmp/command_test")
        if result.success:
            print("✅ Directory created")
        
        # Create test files
        commands = [
            "echo 'File 1 content' > /tmp/command_test/file1.txt",
            "echo 'File 2 content' > /tmp/command_test/file2.txt",
            "echo 'File 3 content' > /tmp/command_test/file3.txt"
        ]
        
        for cmd in commands:
            result = session.command.execute_command(cmd)
            if result.success:
                print(f"✅ Executed: {cmd}")
        
        # List directory contents
        result = session.command.execute_command("ls -la /tmp/command_test")
        if result.success:
            print("\n📁 Directory contents:")
            print(result.output)
        
        # Count files
        result = session.command.execute_command("ls /tmp/command_test | wc -l")
        if result.success:
            print(f"\n📊 Number of files: {result.output.strip()}")
        
        # Search in files
        result = session.command.execute_command("grep -r 'content' /tmp/command_test")
        if result.success:
            print("\n🔍 Search results:")
            print(result.output)
    
    finally:
        agb.delete(session)

file_system_commands()
```

### Step 4: Command Chaining and Pipes

```python
def advanced_commands():
    agb = AGB()
    session = agb.create().session
    
    try:
        # Create sample data
        sample_data = """apple
banana
cherry
apple
date
banana
elderberry"""
        
        # Write data to file using command
        write_cmd = f"cat > /tmp/fruits.txt << 'EOF'\n{sample_data}\nEOF"
        result = session.command.execute_command(write_cmd)
        
        if result.success:
            print("✅ Sample data created")
            
            # Command chaining examples
            pipe_commands = [
                ("cat /tmp/fruits.txt", "Show all fruits"),
                ("cat /tmp/fruits.txt | sort", "Sort fruits alphabetically"),
                ("cat /tmp/fruits.txt | sort | uniq", "Unique fruits only"),
                ("cat /tmp/fruits.txt | sort | uniq -c", "Count unique fruits"),
                ("cat /tmp/fruits.txt | grep 'a' | wc -l", "Count fruits with 'a'")
            ]
            
            print("\n🔗 Command Chaining Examples:")
            print("=" * 50)
            
            for cmd, description in pipe_commands:
                result = session.command.execute_command(cmd, timeout_ms=2000)
                
                print(f"\n{description}:")
                print(f"Command: {cmd}")
                if result.success:
                    print(f"Output: {result.output.strip()}")
                else:
                    print(f"Error: {result.error_message}")
    
    finally:
        agb.delete(session)

advanced_commands()
```

## Advanced Usage (20 minutes)

### Data Processing Pipeline

```python
def data_processing_pipeline():
    agb = AGB()
    session = agb.create().session
    
    try:
        print("🚀 Starting Data Processing Pipeline")
        
        # Step 1: Create sample CSV data
        csv_data = """name,age,city,salary
Alice,25,New York,50000
Bob,30,London,60000
Charlie,35,Paris,70000
Diana,28,Tokyo,55000
Eve,32,Berlin,65000
Frank,27,Sydney,52000"""
        
        # Write CSV data
        write_result = session.command.execute_command(f"""
cat > /tmp/employees.csv << 'EOF'
{csv_data}
EOF
        """)
        
        if not write_result.success:
            print("❌ Failed to create CSV data")
            return
        
        print("✅ Step 1: CSV data created")
        
        # Step 2: Basic data analysis using shell commands
        analysis_commands = [
            ("wc -l /tmp/employees.csv", "Count total lines"),
            ("head -1 /tmp/employees.csv", "Show header"),
            ("tail -n +2 /tmp/employees.csv | wc -l", "Count data rows"),
            ("cut -d',' -f1 /tmp/employees.csv | tail -n +2", "Extract names"),
            ("cut -d',' -f4 /tmp/employees.csv | tail -n +2 | sort -n", "Sort salaries")
        ]
        
        print("\n📊 Step 2: Data Analysis")
        for cmd, description in analysis_commands:
            result = session.command.execute_command(cmd)
            if result.success:
                print(f"{description}: {result.output.strip()}")
        
        # Step 3: Advanced processing with awk
        awk_commands = [
            ("awk -F',' 'NR>1 {sum+=$4; count++} END {print \"Average salary: $\" sum/count}' /tmp/employees.csv", "Calculate average salary"),
            ("awk -F',' 'NR>1 && $4>55000 {print $1 \": $\" $4}' /tmp/employees.csv", "High earners"),
            ("awk -F',' 'NR>1 {cities[$3]++} END {for(city in cities) print city \": \" cities[city]}' /tmp/employees.csv", "Count by city")
        ]
        
        print("\n🔍 Step 3: Advanced Analysis")
        for cmd, description in awk_commands:
            result = session.command.execute_command(cmd, timeout_ms=3000)
            if result.success:
                print(f"{description}:")
                print(result.output)
            else:
                print(f"Error in {description}: {result.error_message}")
        
        # Step 4: Create summary report
        report_cmd = """
awk -F',' '
BEGIN {
    print "Employee Data Analysis Report"
    print "============================="
}
NR>1 {
    total++
    sum+=$4
    if($4>55000) high_earners++
    cities[$3]++
    ages[int($2/10)*10]++
}
END {
    print "Total Employees: " total
    print "Average Salary: $" int(sum/total)
    print "High Earners (>$55k): " high_earners
    print ""
    print "Cities:"
    for(city in cities) print "  " city ": " cities[city]
    print ""
    print "Age Groups:"
    for(age in ages) print "  " age "s: " ages[age]
}' /tmp/employees.csv > /tmp/report.txt
        """
        
        result = session.command.execute_command(report_cmd)
        if result.success:
            print("✅ Step 4: Summary report generated")
            
            # Display the report
            display_result = session.command.execute_command("cat /tmp/report.txt")
            if display_result.success:
                print("\n📋 Final Report:")
                print("=" * 50)
                print(display_result.output)
        
    finally:
        agb.delete(session)

data_processing_pipeline()
```

### System Monitoring and Automation

```python
def system_monitoring():
    agb = AGB()
    session = agb.create().session
    
    try:
        print("🖥️ System Monitoring Dashboard")
        print("=" * 40)
        
        # System resource monitoring
        monitoring_commands = [
            ("free -h", "Memory Usage", "💾"),
            ("df -h", "Disk Usage", "💿"),
            ("ps aux | head -10", "Top Processes", "⚙️"),
            ("netstat -tuln | head -10", "Network Connections", "🌐"),
            ("env | grep -E '^(PATH|HOME|USER|SHELL)' | sort", "Environment", "🔧")
        ]
        
        for cmd, title, icon in monitoring_commands:
            result = session.command.execute_command(cmd, timeout_ms=3000)
            
            print(f"\n{icon} {title}:")
            print("-" * 30)
            if result.success:
                print(result.output)
            else:
                print(f"Error: {result.error_message}")
        
        # Create system health check
        health_check_script = """
#!/bin/bash
echo "System Health Check - $(date)"
echo "================================"

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "⚠️  WARNING: Disk usage is ${DISK_USAGE}%"
else
    echo "✅ Disk usage: ${DISK_USAGE}%"
fi

# Check memory
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEM_USAGE -gt 80 ]; then
    echo "⚠️  WARNING: Memory usage is ${MEM_USAGE}%"
else
    echo "✅ Memory usage: ${MEM_USAGE}%"
fi

# Check load average
LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
echo "📊 Load average: $LOAD"

echo "Health check completed at $(date)"
        """
        
        # Write and execute health check script
        write_result = session.command.execute_command(f"""
cat > /tmp/health_check.sh << 'EOF'
{health_check_script}
EOF
        """)
        
        if write_result.success:
            # Make script executable and run it
            chmod_result = session.command.execute_command("chmod +x /tmp/health_check.sh")
            if chmod_result.success:
                health_result = session.command.execute_command("/tmp/health_check.sh")
                if health_result.success:
                    print("\n🏥 System Health Check:")
                    print("=" * 40)
                    print(health_result.output)
    
    finally:
        agb.delete(session)

system_monitoring()
```

### Log Analysis and Processing

```python
def log_analysis():
    agb = AGB()
    session = agb.create().session
    
    try:
        print("📊 Log Analysis Tutorial")
        
        # Create sample log data
        log_data = """2023-12-01 10:00:01 INFO User alice logged in from 192.168.1.100
2023-12-01 10:00:15 INFO User bob logged in from 192.168.1.101
2023-12-01 10:01:30 WARNING Failed login attempt for user charlie from 192.168.1.102
2023-12-01 10:02:45 INFO User alice accessed /dashboard
2023-12-01 10:03:12 ERROR Database connection failed
2023-12-01 10:03:30 INFO Database connection restored
2023-12-01 10:04:15 WARNING Failed login attempt for user charlie from 192.168.1.102
2023-12-01 10:05:00 INFO User bob accessed /reports
2023-12-01 10:05:30 INFO User alice logged out
2023-12-01 10:06:15 ERROR API timeout for endpoint /api/data
2023-12-01 10:07:00 WARNING Failed login attempt for user charlie from 192.168.1.102
2023-12-01 10:08:30 INFO User bob logged out"""
        
        # Write log data
        write_result = session.command.execute_command(f"""
cat > /tmp/app.log << 'EOF'
{log_data}
EOF
        """)
        
        if not write_result.success:
            print("❌ Failed to create log data")
            return
        
        print("✅ Sample log data created")
        
        # Log analysis commands
        analysis_commands = [
            ("wc -l /tmp/app.log", "Total log entries"),
            ("grep 'ERROR' /tmp/app.log | wc -l", "Error count"),
            ("grep 'WARNING' /tmp/app.log | wc -l", "Warning count"),
            ("grep 'INFO' /tmp/app.log | wc -l", "Info count"),
            ("grep 'logged in' /tmp/app.log | wc -l", "Login events"),
            ("grep 'Failed login' /tmp/app.log | wc -l", "Failed login attempts")
        ]
        
        print("\n📈 Log Statistics:")
        for cmd, description in analysis_commands:
            result = session.command.execute_command(cmd)
            if result.success:
                count = result.output.strip()
                print(f"{description}: {count}")
        
        # Advanced log analysis
        print("\n🔍 Detailed Analysis:")
        
        # Extract unique users
        users_cmd = "grep -o 'User [a-zA-Z]*' /tmp/app.log | sort | uniq -c | sort -nr"
        result = session.command.execute_command(users_cmd)
        if result.success:
            print("User activity:")
            print(result.output)
        
        # Extract IP addresses with failed logins
        failed_ips_cmd = "grep 'Failed login' /tmp/app.log | grep -o '[0-9]\\+\\.[0-9]\\+\\.[0-9]\\+\\.[0-9]\\+' | sort | uniq -c | sort -nr"
        result = session.command.execute_command(failed_ips_cmd)
        if result.success:
            print("Failed login IPs:")
            print(result.output)
        
        # Time-based analysis
        hourly_cmd = "awk '{print $2}' /tmp/app.log | cut -d':' -f1 | sort | uniq -c"
        result = session.command.execute_command(hourly_cmd)
        if result.success:
            print("Activity by hour:")
            print(result.output)
        
        # Generate security report
        security_report_cmd = """
awk '
BEGIN {
    print "Security Analysis Report"
    print "======================="
}
/Failed login/ {
    failed++
    match($0, /from ([0-9.]+)/, ip)
    if(ip[1]) failed_ips[ip[1]]++
}
/ERROR/ { errors++ }
/WARNING/ { warnings++ }
/logged in/ && !/Failed/ { logins++ }
END {
    print "Summary:"
    print "  Total logins: " logins
    print "  Failed attempts: " failed
    print "  Errors: " errors
    print "  Warnings: " warnings
    print ""
    if(failed > 0) {
        print "Suspicious IPs:"
        for(ip in failed_ips) {
            if(failed_ips[ip] > 1) {
                print "  " ip ": " failed_ips[ip] " attempts"
            }
        }
    }
}' /tmp/app.log > /tmp/security_report.txt
        """
        
        result = session.command.execute_command(security_report_cmd)
        if result.success:
            print("\n🛡️ Security Report Generated")
            
            # Display security report
            display_result = session.command.execute_command("cat /tmp/security_report.txt")
            if display_result.success:
                print("=" * 40)
                print(display_result.output)
    
    finally:
        agb.delete(session)

log_analysis()
```

## Best Practices

### 1. Always Check Command Results

```python
# ✅ Good: Always verify command success
result = session.command.execute_command("ls /tmp")
if result.success:
    print("Files:", result.output)
else:
    print("Command failed:", result.error_message)

# ❌ Bad: Assuming commands always succeed
result = session.command.execute_command("ls /tmp")
print(result.output)  # May be empty if command failed
```

### 2. Use Appropriate Timeouts

```python
# ✅ Good: Set timeouts based on expected execution time
quick_cmd = session.command.execute_command("echo hello", timeout_ms=1000)
long_cmd = session.command.execute_command("find / -name '*.log'", timeout_ms=30000)

# ❌ Avoid: Using inappropriate timeouts
session.command.execute_command("find / -name '*.log'", timeout_ms=100)  # Too short
session.command.execute_command("echo hello", timeout_ms=60000)  # Too long
```

### 3. Handle Command Output Properly

```python
# ✅ Good: Process output line by line
result = session.command.execute_command("ps aux")
if result.success:
    lines = result.output.strip().split('\n')
    header = lines[0]
    processes = lines[1:]
    print(f"Found {len(processes)} processes")
    
    # Process each line
    for process_line in processes[:5]:  # Show first 5
        fields = process_line.split()
        if len(fields) >= 11:
            user, pid, cpu, mem = fields[0], fields[1], fields[2], fields[3]
            print(f"PID {pid}: {user} (CPU: {cpu}%, MEM: {mem}%)")
```

### 4. Use Safe Command Patterns

```python
# ✅ Good: Validate paths and use safe operations
def safe_file_operation(session, filepath):
    # Check if file exists first
    check_result = session.command.execute_command(f"test -f {filepath}")
    if check_result.success:
        # File exists, safe to operate
        return session.command.execute_command(f"cat {filepath}")
    else:
        print(f"File {filepath} does not exist")
        return None

# ✅ Good: Use absolute paths
session.command.execute_command("ls -la /tmp/myfile.txt")

# ❌ Avoid: Relative paths without context
session.command.execute_command("ls -la myfile.txt")
```

### 5. Combine Commands Effectively

```python
# ✅ Good: Use pipes for efficient processing
result = session.command.execute_command("ps aux | grep python | wc -l")
if result.success:
    python_processes = int(result.output.strip())
    print(f"Python processes running: {python_processes}")

# ✅ Good: Use command substitution
result = session.command.execute_command("echo 'Current time: $(date)'")
```

## Error Handling and Troubleshooting

### Common Command Errors

```python
def handle_common_errors():
    agb = AGB()
    session = agb.create().session
    
    try:
        # Test various error conditions
        error_tests = [
            ("nonexistent_command", "Command not found"),
            ("ls /nonexistent/directory", "Directory not found"),
            ("cat /etc/shadow", "Permission denied"),
            ("sleep 10", "Timeout (with short timeout)")
        ]
        
        for cmd, expected_error in error_tests:
            print(f"\nTesting: {expected_error}")
            print(f"Command: {cmd}")
            
            # Use short timeout for sleep command
            timeout = 500 if "sleep" in cmd else 2000
            result = session.command.execute_command(cmd, timeout_ms=timeout)
            
            if result.success:
                print("✅ Unexpected success:", result.output[:100])
            else:
                error_msg = result.error_message.lower()
                print("❌ Expected error:", result.error_message)
                
                # Categorize error types
                if "command not found" in error_msg:
                    print("   → Command doesn't exist")
                elif "no such file" in error_msg or "not found" in error_msg:
                    print("   → File/directory doesn't exist")
                elif "permission denied" in error_msg:
                    print("   → Insufficient permissions")
                elif "timeout" in error_msg:
                    print("   → Command timed out")
                else:
                    print("   → Other error type")
    
    finally:
        agb.delete(session)

handle_common_errors()
```

### Robust Command Execution

```python
def robust_command_execution(session, command, max_retries=3, timeout_ms=5000):
    """Execute command with retry logic and comprehensive error handling"""
    
    for attempt in range(max_retries):
        try:
            result = session.command.execute_command(command, timeout_ms=timeout_ms)
            
            if result.success:
                return {
                    "success": True,
                    "output": result.output,
                    "request_id": result.request_id,
                    "attempts": attempt + 1
                }
            else:
                error_msg = result.error_message.lower()
                
                # Don't retry certain types of errors
                non_retryable_errors = [
                    "command not found",
                    "permission denied",
                    "no such file",
                    "syntax error"
                ]
                
                if any(error in error_msg for error in non_retryable_errors):
                    return {
                        "success": False,
                        "error": result.error_message,
                        "error_type": "non_retryable",
                        "attempts": attempt + 1
                    }
                
                # Retry for potentially temporary errors
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed, retrying: {result.error_message}")
                    continue
                else:
                    return {
                        "success": False,
                        "error": result.error_message,
                        "error_type": "max_retries_exceeded",
                        "attempts": attempt + 1
                    }
                    
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Exception on attempt {attempt + 1}: {e}")
                continue
            else:
                return {
                    "success": False,
                    "error": str(e),
                    "error_type": "exception",
                    "attempts": attempt + 1
                }
    
    return {
        "success": False,
        "error": "Unexpected error in retry loop",
        "error_type": "unknown",
        "attempts": max_retries
    }

# Usage example
def test_robust_execution():
    agb = AGB()
    session = agb.create().session
    
    try:
        commands_to_test = [
            "echo 'Hello World'",
            "ls -la /tmp",
            "nonexistent_command",
            "find /tmp -name '*.txt'"
        ]
        
        for cmd in commands_to_test:
            print(f"\nTesting command: {cmd}")
            result = robust_command_execution(session, cmd)
            
            if result["success"]:
                print(f"✅ Success after {result['attempts']} attempts")
                print(f"Output: {result['output'][:100]}...")
            else:
                print(f"❌ Failed after {result['attempts']} attempts")
                print(f"Error type: {result['error_type']}")
                print(f"Error: {result['error']}")
    
    finally:
        agb.delete(session)

test_robust_execution()
```

## Integration with Other Modules

### Command + Code Integration

```python
def command_code_integration():
    agb = AGB()
    session = agb.create().session
    
    try:
        # Use commands to set up environment
        setup_commands = [
            "mkdir -p /tmp/integration_test",
            "echo 'sample,data' > /tmp/integration_test/input.csv",
            "echo '1,100' >> /tmp/integration_test/input.csv",
            "echo '2,200' >> /tmp/integration_test/input.csv",
            "echo '3,300' >> /tmp/integration_test/input.csv"
        ]
        
        for cmd in setup_commands:
            result = session.command.execute_command(cmd)
            if not result.success:
                print(f"Setup failed: {cmd}")
                return
        
        print("✅ Environment set up with commands")
        
        # Process data with code
        processing_code = """
import csv

# Read CSV data
with open('/tmp/integration_test/input.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    data = [(int(row[0]), int(row[1])) for row in reader]

# Process data
total = sum(value for _, value in data)
average = total / len(data)
maximum = max(value for _, value in data)

# Create summary
summary = f'''Data Processing Summary
=====================
Records processed: {len(data)}
Total value: {total}
Average value: {average:.2f}
Maximum value: {maximum}
'''

# Write summary
with open('/tmp/integration_test/summary.txt', 'w') as f:
    f.write(summary)

print("Data processing completed")
print(f"Processed {len(data)} records")
"""
        
        code_result = session.code.run_code(processing_code, "python")
        if code_result.success:
            print("✅ Data processed with code")
            print(code_result.result)
            
            # Use commands to verify results
            verify_commands = [
                ("ls -la /tmp/integration_test/", "List files"),
                ("cat /tmp/integration_test/summary.txt", "Show summary"),
                ("wc -l /tmp/integration_test/input.csv", "Count input lines")
            ]
            
            print("\n🔍 Verification with commands:")
            for cmd, description in verify_commands:
                result = session.command.execute_command(cmd)
                if result.success:
                    print(f"{description}:")
                    print(result.output)
        
    finally:
        agb.delete(session)

command_code_integration()
```

## Related Documentation

- **[Command Module API](../api-reference/modules/command.md)** - Complete Command API reference
- **[Code Execution Guide](../guides/code-execution.md)** - Integrating commands with code
- **[File Operations Tutorial](file-operations.md)** - File management with commands
- **[Session Management Guide](../guides/session-management.md)** - Managing command execution sessions
- **[Best Practices](../guides/best-practices.md)** - Production deployment patterns 