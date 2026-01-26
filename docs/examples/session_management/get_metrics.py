"""
This example demonstrates how to retrieve session metrics in AGB using a shared session.

Session metrics provide real-time information about resource usage including:
- CPU usage and core count
- Memory usage (total and used)
- Disk usage (total and used)
- Network statistics (RX/TX rate and total usage)
- Timestamp of the metrics snapshot

This version uses a single shared session across all examples for better resource efficiency.
"""

import os
import time

from agb import AGB
from agb.session_params import CreateSessionParams

def get_basic_metrics(session) -> None:
    """Get basic session metrics."""
    print(f"Getting metrics for session: {session.session_id}")
    
    # Get session metrics
    metrics_result = session.get_metrics()
    
    if metrics_result.success and metrics_result.metrics:
        metrics = metrics_result.metrics
        print("\n=== Session Metrics ===")
        print(f"Request ID: {metrics_result.request_id}")
        
        # Display CPU information
        if hasattr(metrics, 'cpu_count') and hasattr(metrics, 'cpu_used_pct'):
            print(f"\nCPU:")
            print(f"  CPU Count: {metrics.cpu_count}")
            print(f"  CPU Used: {metrics.cpu_used_pct:.2f}%")
        
        # Display Memory information
        if hasattr(metrics, 'mem_total') and hasattr(metrics, 'mem_used'):
            mem_total_gb = metrics.mem_total / (1024**3)  # Convert bytes to GB
            mem_used_gb = metrics.mem_used / (1024**3)
            mem_usage_pct = (metrics.mem_used / metrics.mem_total) * 100 if metrics.mem_total > 0 else 0
            print(f"\nMemory:")
            print(f"  Total: {mem_total_gb:.2f} GB")
            print(f"  Used: {mem_used_gb:.2f} GB")
            print(f"  Usage: {mem_usage_pct:.2f}%")
        
        # Display Disk information
        if hasattr(metrics, 'disk_total') and hasattr(metrics, 'disk_used'):
            disk_total_gb = metrics.disk_total / (1024**3)  # Convert bytes to GB
            disk_used_gb = metrics.disk_used / (1024**3)
            disk_usage_pct = (metrics.disk_used / metrics.disk_total) * 100 if metrics.disk_total > 0 else 0
            print(f"\nDisk:")
            print(f"  Total: {disk_total_gb:.2f} GB")
            print(f"  Used: {disk_used_gb:.2f} GB")
            print(f"  Usage: {disk_usage_pct:.2f}%")
        
        # Display Network information
        if hasattr(metrics, 'rx_rate_kbps') and hasattr(metrics, 'tx_rate_kbps'):
            print(f"\nNetwork:")
            print(f"  RX Rate: {metrics.rx_rate_kbps:.2f} KB/s")
            print(f"  TX Rate: {metrics.tx_rate_kbps:.2f} KB/s")
            
            if hasattr(metrics, 'rx_used_kb') and hasattr(metrics, 'tx_used_kb'):
                print(f"  RX Total: {metrics.rx_used_kb:.2f} KB")
                print(f"  TX Total: {metrics.tx_used_kb:.2f} KB")
        
        # Display timestamp
        if hasattr(metrics, 'timestamp'):
            print(f"\nTimestamp: {metrics.timestamp}")
    else:
        print(f"Failed to get session metrics: {metrics_result.error_message}")

def monitor_metrics_over_time(session) -> None:
    """Monitor session metrics over time using the shared session."""
    print(f"Monitoring metrics for session: {session.session_id}")
    print("Monitoring metrics over time (5 snapshots, 10 seconds apart)...")
    
    for i in range(5):
        print(f"\n--- Snapshot {i + 1} ---")
        
        # Get session metrics
        metrics_result = session.get_metrics()
        
        if metrics_result.success and metrics_result.metrics:
            metrics = metrics_result.metrics
            
            # Display key metrics
            if hasattr(metrics, 'cpu_used_pct'):
                print(f"CPU Usage: {metrics.cpu_used_pct:.2f}%")
            
            if hasattr(metrics, 'mem_used') and hasattr(metrics, 'mem_total'):
                mem_usage_pct = (metrics.mem_used / metrics.mem_total) * 100 if metrics.mem_total > 0 else 0
                print(f"Memory Usage: {mem_usage_pct:.2f}%")
            
            if hasattr(metrics, 'rx_rate_kbps') and hasattr(metrics, 'tx_rate_kbps'):
                print(f"Network: RX {metrics.rx_rate_kbps:.2f} KB/s, TX {metrics.tx_rate_kbps:.2f} KB/s")
            
            if hasattr(metrics, 'timestamp'):
                print(f"Time: {metrics.timestamp}")
        else:
            print(f"Failed to get metrics: {metrics_result.error_message}")
        
        # Wait before next snapshot (except for the last one)
        if i < 4:
            time.sleep(10)

def main() -> None:
    """Run all metrics examples using a shared session."""
    # Initialize the AGB client
    api_key = os.environ.get("AGB_API_KEY", "")
    if not api_key:
        raise ValueError("AGB_API_KEY environment variable is not set")
    
    agb = AGB(api_key=api_key)
    session = None
    
    try:
        # Create a single shared session
        print("Creating shared session...")
        params = CreateSessionParams(image_id="agb-computer-use-ubuntu-2204")
        result = agb.create(params)
        
        if not result.success or not result.session:
            raise RuntimeError(f"Failed to create session: {result.error_message}")
        
        session = result.session
        print(f"Shared session created successfully with ID: {session.session_id}")
        
        
        # Run all examples using the shared session
        print("\n" + "="*60)
        print("1. Getting basic session metrics...")
        get_basic_metrics(session)
        
        print("\n" + "="*60)
        print("2. Monitoring metrics over time...")
        monitor_metrics_over_time(session)
        
    except Exception as e:
        print(f"Error occurred: {e}")
    
    finally:
        # Clean up: Delete the shared session when done
        if session:
            print("\n" + "="*60)
            print("Cleaning up shared session...")
            delete_result = agb.delete(session)
            if delete_result.success:
                print(f"Shared session {session.session_id} deleted successfully")
            else:
                print(f"Failed to delete session: {delete_result.error_message}")

if __name__ == "__main__":
    main()
