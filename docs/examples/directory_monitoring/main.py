#!/usr/bin/env python3
"""
AGB watch_directory Simple Example

This example demonstrates how to use the AGB SDK's watch_directory functionality to monitor directory changes.
Run this file directly to see the complete demonstration without reading complex documentation.

Usage:
    export AGB_API_KEY="your-api-key"
    python main.py

The program will:
1. Create a test directory
2. Start directory monitoring
3. Automatically create some test files
4. Display detected file changes in real-time
5. Stop when Ctrl+C is pressed
"""

import os
import sys
import time
import threading
from datetime import datetime

# Add project root directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from agb import AGB
from agb.session_params import CreateSessionParams


def print_step(step, message):
    """Print message with step number"""
    print(f"\n📍 Step {step}: {message}")


def print_info(message, indent=1):
    """Print info message"""
    prefix = "   " * indent
    print(f"{prefix}ℹ️  {message}")


def print_success(message, indent=1):
    """Print success message"""
    prefix = "   " * indent
    print(f"{prefix}✅ {message}")


def print_event(message, indent=1):
    """Print event message"""
    prefix = "   " * indent
    print(f"{prefix}🔍 {message}")


# Global variable: record all events for final comparison analysis
detected_events = []

def file_change_callback(events):
    """
    File change callback function
    
    This is the core of watch_directory: this function is called when file changes are detected
    Note: Empty events are filtered at the API level, this callback only receives events with actual changes
    """
    global detected_events
    
    print_event(f"Detected {len(events)} file changes:")
    
    for event in events:
        event_type = event.event_type.upper()
        file_name = os.path.basename(event.path)
        
        # Record event for final analysis
        detected_events.append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'type': event_type,
            'file': file_name,
            'path': event.path,
            'description': f"{event_type}: {file_name}"
        })
        
        if event_type == "CREATE":
            print_event(f"📄 File created: {file_name}", indent=2)
        elif event_type == "MODIFY":
            print_event(f"✏️  File modified: {file_name}", indent=2)
        elif event_type == "DELETE":
            print_event(f"🗑️  File deleted: {file_name}", indent=2)
        else:
            print_event(f"❓ Unknown event: {event_type} - {file_name}", indent=2)


# Global variable: record all file operations for final comparison analysis
file_operations = []

def log_operation(operation_type, filename, description=""):
    """Record file operation"""
    global file_operations
    file_operations.append({
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'type': operation_type,
        'file': filename,
        'description': description or f"{operation_type}: {filename}"
    })

def create_demo_files(session, watch_dir):
    """
    Create demo files
    
    This function will automatically create some files in the background to let users see the monitoring effect
    All files are created using touch command first, then content is added using write_file method if needed
    """
    print_step(4, "Starting to create demo files (starting in 3 seconds)")
    time.sleep(3)  # Wait for monitoring to start
    
    # Use touch command to create empty files
    touch_files = ["hello.txt", "config.ini"]
    
    for filename in touch_files:
        filepath = os.path.join(watch_dir, filename)
        
        print_info(f"Creating file using touch command: {filename}")
        log_operation("CREATE", filename, f"Create file using touch: {filename}")
        
        try:
            # Create file using touch command
            result = session.command.execute_command(f"touch {filepath}", timeout_ms=5000)
            if result.success:
                print_success(f"Touch creation successful: {filename}")
            else:
                print(f"   ❌ Touch creation failed: {result.error_message}")
        except Exception as e:
            print(f"   ❌ Error during touch creation: {e}")
        
        time.sleep(2)  # Wait 2 seconds before creating next file
    
    # Create files with content using touch command first, then add content
    content_files = [
        ("data.json", '{"name": "test data", "value": 123, "timestamp": "' + datetime.now().isoformat() + '"}'),
        ("readme.md", "# Test Document\n\nThis is a Markdown file used to demonstrate file monitoring functionality."),
    ]
    
    for filename, content in content_files:
        filepath = os.path.join(watch_dir, filename)
        
        # First create empty file using touch
        print_info(f"Creating file using touch command: {filename}")
        log_operation("CREATE", filename, f"Create file using touch: {filename}")
        
        try:
            result = session.command.execute_command(f"touch {filepath}", timeout_ms=5000)
            if result.success:
                print_success(f"Touch creation successful: {filename}")
            else:
                print(f"   ❌ Touch creation failed: {result.error_message}")
                continue
        except Exception as e:
            print(f"   ❌ Error during touch creation: {e}")
            continue
        
        time.sleep(1)  # Wait 1 second before adding content
        
        # Then add content using write_file
        print_info(f"Adding content to file: {filename}")
        log_operation("MODIFY", filename, f"Add content to file: {filename}")
        
        try:
            result = session.file_system.write_file(filepath, content)
            if result.success:
                print_success(f"Content addition successful: {filename}")
            else:
                print(f"   ❌ Content addition failed: {result.error_message}")
        except Exception as e:
            print(f"   ❌ Error during content addition: {e}")
        
        time.sleep(2)  # Wait 2 seconds before creating next file
    
    # Demonstrate file modification - add content to previously created empty file
    print_info("Waiting 3 seconds before demonstrating file modification...")
    time.sleep(3)
    
    modify_file = os.path.join(watch_dir, "hello.txt")
    new_content = f"Hello, AGB watch_directory!\nThis is the first content added to the empty file.\nModification time: {datetime.now().isoformat()}"
    
    print_info("Modifying file: hello.txt (adding content to empty file)")
    log_operation("MODIFY", "hello.txt", "Add content to empty file")
    try:
        result = session.file_system.write_file(modify_file, new_content)
        if result.success:
            print_success("File modification successful")
        else:
            print(f"   ❌ File modification failed: {result.error_message}")
    except Exception as e:
        print(f"   ❌ Error during file modification: {e}")
    
    # Demonstrate modifying the same file again
    print_info("Waiting 3 seconds before modifying the same file again...")
    time.sleep(3)
    
    new_content2 = f"Hello, AGB watch_directory!\nThis is the second modification content.\nModification time: {datetime.now().isoformat()}\nAdded more content lines.\nDemonstrating continuous modification detection."
    
    print_info("Modifying file again: hello.txt")
    log_operation("MODIFY", "hello.txt", "Second file content modification")
    try:
        result = session.file_system.write_file(modify_file, new_content2)
        if result.success:
            print_success("Second file modification successful")
        else:
            print(f"   ❌ File modification failed: {result.error_message}")
    except Exception as e:
        print(f"   ❌ Error during file modification: {e}")
    
    # Demonstrate file deletion - using rm command to delete file
    print_info("Waiting 3 seconds before demonstrating file deletion...")
    time.sleep(3)
    
    delete_file = os.path.join(watch_dir, "config.ini")
    print_info("Deleting file: config.ini (using rm command)")
    log_operation("DELETE", "config.ini", "Delete file using rm command")
    try:
        result = session.command.execute_command(f"rm {delete_file}", timeout_ms=5000)
        if result.success:
            print_success("File deletion successful")
        else:
            print(f"   ❌ File deletion failed: {result.error_message}")
    except Exception as e:
        print(f"   ❌ Error during file deletion: {e}")
    
    # Demonstrate creating new file
    print_info("Waiting 3 seconds before creating new file...")
    time.sleep(3)
    
    new_file = os.path.join(watch_dir, "summary.txt")
    summary_content = f"Demo Summary\n============\nCreation time: {datetime.now().isoformat()}\n\nThis demo included the following operations:\n- File creation\n- File modification\n- File deletion\n- New file creation"
    
    # First create empty file using touch
    print_info("Creating summary file using touch command: summary.txt")
    log_operation("CREATE", "summary.txt", "Create summary file using touch")
    try:
        result = session.command.execute_command(f"touch {new_file}", timeout_ms=5000)
        if result.success:
            print_success("Touch creation successful: summary.txt")
        else:
            print(f"   ❌ Touch creation failed: {result.error_message}")
    except Exception as e:
        print(f"   ❌ Error during touch creation: {e}")
    
    time.sleep(1)  # Wait 1 second before adding content
    
    # Then add content using write_file
    print_info("Adding content to summary file: summary.txt")
    log_operation("MODIFY", "summary.txt", "Add content to summary file")
    try:
        result = session.file_system.write_file(new_file, summary_content)
        if result.success:
            print_success("Summary file content addition successful")
        else:
            print(f"   ❌ Summary file content addition failed: {result.error_message}")
    except Exception as e:
        print(f"   ❌ Error during summary file content addition: {e}")
    
    print_info("Demo file operations completed, continuing monitoring...")


def main():
    """Main function"""
    print("🎬 AGB watch_directory Simple Example")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv("AGB_API_KEY")
    if not api_key:
        print("❌ Please set AGB_API_KEY environment variable")
        print("   export AGB_API_KEY='your-api-key'")
        return 1
    
    print_step(1, "Initialize AGB client")
    try:
        # Create AGB client
        agb = AGB(api_key=api_key)
        print_success("AGB client created successfully")
        
        # Create session
        print_info("Creating AGB session...")
        session_params = CreateSessionParams(image_id="agb-code-space-2")
        session_result = agb.create(session_params)
        
        if not session_result.success:
            print(f"❌ Session creation failed: {session_result.error_message}")
            return 1
        
        session = session_result.session
        print_success(f"Session created successfully: {session.session_id}")
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return 1
    
    # Set up monitoring directory
    watch_dir = "/tmp/agb_watch_demo"
    
    print_step(2, f"Prepare monitoring directory: {watch_dir}")
    try:
        # Create monitoring directory
        result = session.file_system.create_directory(watch_dir)
        if result.success:
            print_success("Monitoring directory created successfully")
        else:
            print_info("Directory may already exist, continuing execution")
    except Exception as e:
        print(f"❌ Directory creation failed: {e}")
        return 1
    
    print_step(3, "Start directory monitoring")
    print_info("Calling session.file_system.watch_directory() to start monitoring")
    print_info("Monitoring interval: 1 second")
    print_info("Callback function: file_change_callback")
    
    try:
        # Create stop event
        stop_event = threading.Event()
        
        # Start directory monitoring - this is the core API call
        monitor_thread = session.file_system.watch_directory(
            path=watch_dir,                    # Directory path to monitor
            callback=file_change_callback,     # Callback function when changes detected                    # Polling interval (seconds)
            stop_event=stop_event              # Stop signal
        )
        
        monitor_thread.start()
        print_success("Directory monitoring started")
        print_info("Monitoring thread running in background...")
        
        # Start demo file creation (in background thread)
        demo_thread = threading.Thread(
            target=create_demo_files, 
            args=(session, watch_dir),
            daemon=True
        )
        demo_thread.start()
        
        print_step(5, "Monitoring running (press Ctrl+C to stop)")
        print_info("Program will continuously monitor directory changes and display detection results in real-time")
        print_info("You can also manually add/modify/delete files in the directory to test")
        
        # Main loop: wait for user interruption
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Received stop signal, gracefully exiting...")
            
        # Stop monitoring
        print_info("Stopping directory monitoring...")
        stop_event.set()
        monitor_thread.join(timeout=5)
        print_success("Monitoring stopped")
        
    except Exception as e:
        print(f"❌ Error during monitoring: {e}")
        return 1
    
    finally:
        # Clean up session
        print_step(6, "Clean up resources")
        try:
            delete_result = agb.delete(session)
            if delete_result.success:
                print_success("Session cleaned up")
            else:
                print(f"⚠️  Session cleanup failed: {delete_result.error_message}")
        except Exception as e:
            print(f"⚠️  Error during cleanup: {e}")
    
    print("\n🎉 Example execution completed!")
    
    # Display operation and event comparison analysis
    print_analysis_report()
    
    print("\n📚 API Usage Summary:")
    print("   1. Use AGB() to create client")
    print("   2. Use agb.create() to create session")
    print("   3. Use session.file_system.watch_directory() to monitor directory")
    print("   4. Handle file change events in callback function")
    print("   5. Use stop_event to gracefully stop monitoring")
    print("   6. Use agb.delete() to clean up session")
    
    return 0


def print_analysis_report():
    """Print operation and event comparison analysis report"""
    global file_operations, detected_events
    
    print("\n" + "="*80)
    print("📊 File Operations and Monitoring Events Comparison Analysis")
    print("="*80)
    
    print(f"\n📋 Executed File Operations (Total: {len(file_operations)}):")
    print("-" * 60)
    for i, op in enumerate(file_operations, 1):
        print(f"  {i:2d}. [{op['timestamp']}] {op['type']:6s} | {op['file']:15s} | {op['description']}")
    
    print(f"\n🔍 Detected Monitoring Events (Total: {len(detected_events)}):")
    print("-" * 60)
    for i, event in enumerate(detected_events, 1):
        print(f"  {i:2d}. [{event['timestamp']}] {event['type']:6s} | {event['file']:15s} | {event['description']}")
    
    # Analyze operation and event correspondence
    print(f"\n🔗 Operation and Event Correspondence Analysis:")
    print("-" * 60)
    
    # Count operations and events by type
    op_stats = {}
    event_stats = {}
    
    for op in file_operations:
        op_stats[op['type']] = op_stats.get(op['type'], 0) + 1
    
    for event in detected_events:
        event_stats[event['type']] = event_stats.get(event['type'], 0) + 1
    
    print("  Operation Type Statistics:")
    for op_type, count in op_stats.items():
        print(f"    {op_type:8s}: {count} times")
    
    print("  Event Type Statistics:")
    for event_type, count in event_stats.items():
        print(f"    {event_type:8s}: {count} times")
    
    # Analyze matching situation
    print(f"\n💡 Key Findings:")
    print("-" * 60)
    
    # Check CREATE operation and event matching
    create_ops = [op for op in file_operations if op['type'] == 'CREATE']
    create_events = [e for e in detected_events if e['type'] == 'CREATE']
    
    if len(create_ops) == len(create_events):
        print(f"  ✅ CREATE operations fully matched: {len(create_ops)} operations → {len(create_events)} events")
    else:
        print(f"  ⚠️  CREATE operations not fully matched: {len(create_ops)} operations → {len(create_events)} events")
    
    # Check MODIFY operation and event matching
    modify_ops = [op for op in file_operations if op['type'] == 'MODIFY']
    modify_events = [e for e in detected_events if e['type'] == 'MODIFY']
    
    if len(modify_ops) == len(modify_events):
        print(f"  ✅ MODIFY operations fully matched: {len(modify_ops)} operations → {len(modify_events)} events")
    else:
        print(f"  ⚠️  MODIFY operations not fully matched: {len(modify_ops)} operations → {len(modify_events)} events")
    
    # Check DELETE operation and DESTROY event matching
    delete_ops = [op for op in file_operations if op['type'] == 'DELETE']
    destroy_events = [e for e in detected_events if e['type'] == 'DESTROY']
    
    if len(delete_ops) == len(destroy_events):
        print(f"  ✅ DELETE operations fully matched: {len(delete_ops)} operations → {len(destroy_events)} DESTROY events")
    else:
        print(f"  ⚠️  DELETE operations not fully matched: {len(delete_ops)} operations → {len(destroy_events)} DESTROY events")
    
    # Empty events are filtered at API level, so there won't be empty events here
    # All detected events are valid file changes
    
    # Time delay analysis
    if file_operations and detected_events:
        first_op_time = file_operations[0]['timestamp']
        first_event_time = detected_events[0]['timestamp']
        print(f"  ⏱️  First operation time: {first_op_time}")
        print(f"  ⏱️  First event time: {first_event_time}")
    
    print(f"\n📖 Learning Points:")
    print("-" * 60)
    print("  • watch_directory detects file changes through polling mechanism")
    print("  • API automatically filters empty events, only passing events with actual changes")
    print("  • Event detection may have slight delay (depends on polling interval)")
    print("  • Using write_file to create files generates both CREATE and MODIFY events (as expected)")
    print("  • Deleting files generates DESTROY events (as expected)")
    print("  • touch creating empty files only generates CREATE events")
    print("  • Modifying existing file content generates MODIFY events")
    print("  • Callback function is only called when there are file changes")
    
    print("="*80)


if __name__ == "__main__":
    sys.exit(main()) 