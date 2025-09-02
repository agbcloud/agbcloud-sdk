# Best Practices Guide

## Overview

This guide covers production-ready patterns, performance optimization, and best practices for using AGB SDK in real-world applications. Follow these recommendations to build robust, scalable, and maintainable applications.

## Quick Reference (1 minute)

```python
from agb import AGB
from agb.session_params import CreateSessionParams

# Production-ready pattern
class AGBManager:
    def __init__(self):
        self.agb = AGB()  # Uses environment variable
        
    def safe_execute(self, operation):
        result = self.agb.create()
        if not result.success:
            raise Exception(f"Session creation failed: {result.error_message}")
            
        session = result.session
        try:
            return operation(session)
        finally:
            self.agb.delete(session)

# Usage
manager = AGBManager()
result = manager.safe_execute(lambda s: s.code.run_code("print('Hello')", "python"))
```

## Production Deployment (5-10 minutes)

### Environment Configuration

```python
import os
from agb import AGB
from agb.config import Config

class ProductionAGBClient:
    def __init__(self):
        # Validate required environment variables
        api_key = os.getenv("AGB_API_KEY")
        if not api_key:
            raise ValueError("AGB_API_KEY environment variable is required")
        
        # Configure for production
        config = Config(
            endpoint="your-custom-endpoint.com",
            timeout_ms=30000,
        )
        
        self.agb = AGB(api_key=api_key, cfg=config)
        
    def health_check(self):
        """Verify AGB service connectivity"""
        try:
            result = self.agb.create()
            if result.success:
                self.agb.delete(result.session)
                return True, "Service healthy"
            else:
                return False, result.error_message
        except Exception as e:
            return False, str(e)

# Usage in production
client = ProductionAGBClient()
healthy, message = client.health_check()
if not healthy:
    # Handle service unavailability
    print(f"AGB service unavailable: {message}")
```

### Error Handling and Retry Logic

```python
import time
import random
from typing import Callable, Any, Optional

class RobustAGBClient:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.agb = AGB()
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def execute_with_retry(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with exponential backoff retry"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = self.agb.create()
                if not result.success:
                    raise Exception(f"Session creation failed: {result.error_message}")
                
                session = result.session
                try:
                    return operation(session, *args, **kwargs)
                finally:
                    self.agb.delete(session)
                    
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff with jitter
                    delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                else:
                    print(f"All {self.max_retries} attempts failed")
        
        raise last_error

# Usage
def risky_operation(session):
    # This might fail due to network issues, service unavailability, etc.
    return session.code.run_code("import requests; print('Success')", "python")

client = RobustAGBClient(max_retries=3)
try:
    result = client.execute_with_retry(risky_operation)
    print("Operation succeeded:", result.result)
except Exception as e:
    print(f"Operation failed permanently: {e}")
```

### Resource Management

```python
import threading
import time
from contextlib import contextmanager
from typing import Dict, Optional

class SessionPool:
    """Thread-safe session pool for high-throughput applications"""
    
    def __init__(self, max_sessions: int = 10, session_timeout: int = 300):
        self.agb = AGB()
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout
        self.sessions: Dict[str, dict] = {}
        self.lock = threading.Lock()
    
    @contextmanager
    def get_session(self):
        """Get a session from the pool"""
        session_info = self._acquire_session()
        try:
            yield session_info['session']
        finally:
            self._release_session(session_info['id'])
    
    def _acquire_session(self):
        with self.lock:
            # Clean up expired sessions
            self._cleanup_expired_sessions()
            
            # Try to reuse existing session
            for session_id, info in self.sessions.items():
                if not info['in_use']:
                    info['in_use'] = True
                    info['last_used'] = time.time()
                    return info
            
            # Create new session if under limit
            if len(self.sessions) < self.max_sessions:
                result = self.agb.create()
                if result.success:
                    session_info = {
                        'id': result.session.session_id,
                        'session': result.session,
                        'created': time.time(),
                        'last_used': time.time(),
                        'in_use': True
                    }
                    self.sessions[session_info['id']] = session_info
                    return session_info
            
            raise Exception("No sessions available and pool is at maximum capacity")
    
    def _release_session(self, session_id: str):
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id]['in_use'] = False
    
    def _cleanup_expired_sessions(self):
        current_time = time.time()
        expired_sessions = []
        
        for session_id, info in self.sessions.items():
            if not info['in_use'] and (current_time - info['last_used']) > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            session_info = self.sessions.pop(session_id)
            try:
                self.agb.delete(session_info['session'])
            except Exception as e:
                print(f"Error cleaning up session {session_id}: {e}")
    
    def cleanup_all(self):
        """Clean up all sessions in the pool"""
        with self.lock:
            for session_info in self.sessions.values():
                try:
                    self.agb.delete(session_info['session'])
                except Exception as e:
                    print(f"Error cleaning up session: {e}")
            self.sessions.clear()

# Usage
pool = SessionPool(max_sessions=5)

def process_task(task_data):
    with pool.get_session() as session:
        result = session.code.run_code(f"print('Processing: {task_data}')", "python")
        return result.result

# Process multiple tasks
tasks = ["task1", "task2", "task3"]
results = []

for task in tasks:
    try:
        result = process_task(task)
        results.append(result)
    except Exception as e:
        print(f"Task {task} failed: {e}")

# Cleanup when done
pool.cleanup_all()
```

## Performance Optimization (15+ minutes)

### Batch Operations

```python
def batch_code_execution(session, code_snippets, language="python"):
    """Execute multiple code snippets efficiently"""
    # Combine multiple operations into a single execution
    combined_code = []
    
    for i, code in enumerate(code_snippets):
        combined_code.append(f"# Task {i+1}")
        combined_code.append(code)
        combined_code.append(f"print(f'Task {i+1} completed')")
        combined_code.append("")  # Empty line for separation
    
    full_code = "\n".join(combined_code)
    
    result = session.code.run_code(full_code, language)
    return result

# Usage
agb = AGB()
session = agb.create().session

code_snippets = [
    "x = 10 + 5",
    "y = x * 2", 
    "z = y / 3",
    "print(f'Final result: {z}')"
]

result = batch_code_execution(session, code_snippets)
print("Batch execution result:")
print(result.result)

agb.delete(session)
```

### Concurrent Processing

```python
import concurrent.futures
import threading
from typing import List, Callable

class ConcurrentAGBProcessor:
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.agb = AGB()
        
    def process_tasks_concurrently(self, tasks: List[dict], processor: Callable):
        """Process multiple tasks concurrently"""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self._process_single_task, task, processor): task 
                for task in tasks
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append({
                        'task': task,
                        'success': True,
                        'result': result
                    })
                except Exception as e:
                    results.append({
                        'task': task,
                        'success': False,
                        'error': str(e)
                    })
        
        return results
    
    def _process_single_task(self, task: dict, processor: Callable):
        """Process a single task with its own session"""
        result = self.agb.create()
        if not result.success:
            raise Exception(f"Failed to create session: {result.error_message}")
        
        session = result.session
        try:
            return processor(session, task)
        finally:
            self.agb.delete(session)

# Usage example
def data_processing_task(session, task):
    """Process data using code execution"""
    data = task['data']
    operation = task['operation']
    
    code = f"""
import json
data = {json.dumps(data)}
result = []

for item in data:
    if '{operation}' == 'double':
        result.append(item * 2)
    elif '{operation}' == 'square':
        result.append(item ** 2)
    else:
        result.append(item)

print(json.dumps(result))
"""
    
    code_result = session.code.run_code(code, "python")
    if code_result.success:
        import json
        return json.loads(code_result.result.strip().split('\n')[-1])
    else:
        raise Exception(code_result.error_message)

# Process multiple data sets concurrently
processor = ConcurrentAGBProcessor(max_workers=3)

tasks = [
    {'data': [1, 2, 3, 4], 'operation': 'double'},
    {'data': [2, 4, 6, 8], 'operation': 'square'},
    {'data': [1, 3, 5, 7], 'operation': 'double'}
]

results = processor.process_tasks_concurrently(tasks, data_processing_task)

for result in results:
    if result['success']:
        print(f"Task completed: {result['result']}")
    else:
        print(f"Task failed: {result['error']}")
```

### Caching and Optimization

```python
import hashlib
import json
from typing import Any, Optional

class CachedAGBClient:
    """AGB client with result caching for expensive operations"""
    
    def __init__(self, cache_size: int = 100):
        self.agb = AGB()
        self.cache = {}
        self.cache_size = cache_size
        self.cache_order = []  # For LRU eviction
    
    def execute_with_cache(self, code: str, language: str = "python") -> Any:
        """Execute code with caching based on content hash"""
        # Create cache key from code content
        cache_key = self._get_cache_key(code, language)
        
        # Check cache first
        if cache_key in self.cache:
            print(f"Cache hit for operation")
            self._update_cache_order(cache_key)
            return self.cache[cache_key]
        
        # Execute operation
        result = self.agb.create()
        if not result.success:
            raise Exception(f"Session creation failed: {result.error_message}")
        
        session = result.session
        try:
            code_result = session.code.run_code(code, language)
            
            # Cache successful results
            if code_result.success:
                self._add_to_cache(cache_key, code_result)
            
            return code_result
            
        finally:
            self.agb.delete(session)
    
    def _get_cache_key(self, code: str, language: str) -> str:
        """Generate cache key from code content"""
        content = f"{language}:{code}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _add_to_cache(self, key: str, result: Any):
        """Add result to cache with LRU eviction"""
        # Remove oldest entry if cache is full
        if len(self.cache) >= self.cache_size and key not in self.cache:
            oldest_key = self.cache_order.pop(0)
            del self.cache[oldest_key]
        
        self.cache[key] = result
        self._update_cache_order(key)
    
    def _update_cache_order(self, key: str):
        """Update LRU order"""
        if key in self.cache_order:
            self.cache_order.remove(key)
        self.cache_order.append(key)
    
    def clear_cache(self):
        """Clear all cached results"""
        self.cache.clear()
        self.cache_order.clear()

# Usage
cached_client = CachedAGBClient(cache_size=50)

# This will execute and cache the result
result1 = cached_client.execute_with_cache("print('Hello World')", "python")
print("First execution:", result1.result)

# This will use cached result
result2 = cached_client.execute_with_cache("print('Hello World')", "python")
print("Cached execution:", result2.result)
```

## Security Best Practices

### Input Validation and Sanitization

```python
import re
from typing import List

class SecureAGBClient:
    """AGB client with security validations"""
    
    DANGEROUS_PATTERNS = [
        r'import\s+os',
        r'import\s+subprocess',
        r'__import__',
        r'eval\s*\(',
        r'exec\s*\(',
        r'open\s*\(',
        r'file\s*\(',
    ]
    
    def __init__(self):
        self.agb = AGB()
    
    def safe_execute_code(self, code: str, language: str = "python") -> Any:
        """Execute code with security validations"""
        # Validate input
        if not self._validate_code_safety(code):
            raise ValueError("Code contains potentially dangerous operations")
        
        if len(code) > 10000:  # 10KB limit
            raise ValueError("Code too large - potential DoS attempt")
        
        # Execute with timeout
        result = self.agb.create()
        if not result.success:
            raise Exception(f"Session creation failed: {result.error_message}")
        
        session = result.session
        try:
            # Use shorter timeout for security
            code_result = session.code.run_code(code, language, timeout_s=30)
            return code_result
        finally:
            self.agb.delete(session)
    
    def _validate_code_safety(self, code: str) -> bool:
        """Check code for dangerous patterns"""
        code_lower = code.lower()
        
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, code_lower):
                print(f"Dangerous pattern detected: {pattern}")
                return False
        
        return True
    
    def execute_trusted_code(self, code: str, language: str = "python") -> Any:
        """Execute code from trusted sources without validation"""
        result = self.agb.create()
        if not result.success:
            raise Exception(f"Session creation failed: {result.error_message}")
        
        session = result.session
        try:
            return session.code.run_code(code, language)
        finally:
            self.agb.delete(session)

# Usage
secure_client = SecureAGBClient()

# Safe code
safe_code = """
x = 10
y = 20
result = x + y
print(f"Result: {result}")
"""

try:
    result = secure_client.safe_execute_code(safe_code)
    print("Safe execution:", result.result)
except ValueError as e:
    print(f"Security validation failed: {e}")

# Dangerous code (will be rejected)
dangerous_code = """
import os
os.system("rm -rf /")
"""

try:
    result = secure_client.safe_execute_code(dangerous_code)
except ValueError as e:
    print(f"Dangerous code rejected: {e}")
```

## Monitoring and Logging

```python
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class MonitoredAGBClient:
    """AGB client with comprehensive monitoring"""
    
    def __init__(self):
        self.agb = AGB()
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            'total_sessions': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'total_execution_time': 0
        }
    
    def execute_with_monitoring(self, operation_name: str, operation_func):
        """Execute operation with full monitoring"""
        start_time = time.time()
        operation_id = f"{operation_name}_{int(start_time)}"
        
        self.logger.info(f"Starting operation: {operation_id}")
        
        try:
            # Create session
            result = self.agb.create()
            if not result.success:
                self.logger.error(f"Session creation failed for {operation_id}: {result.error_message}")
                self.metrics['failed_operations'] += 1
                raise Exception(f"Session creation failed: {result.error_message}")
            
            self.metrics['total_sessions'] += 1
            session = result.session
            
            self.logger.info(f"Session created for {operation_id}: {session.session_id}")
            
            try:
                # Execute operation
                operation_result = operation_func(session)
                
                execution_time = time.time() - start_time
                self.metrics['successful_operations'] += 1
                self.metrics['total_execution_time'] += execution_time
                
                self.logger.info(f"Operation {operation_id} completed successfully in {execution_time:.2f}s")
                
                return operation_result
                
            finally:
                # Always clean up session
                delete_result = self.agb.delete(session)
                if delete_result.success:
                    self.logger.info(f"Session {session.session_id} cleaned up successfully")
                else:
                    self.logger.warning(f"Failed to clean up session {session.session_id}: {delete_result.error_message}")
                
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics['failed_operations'] += 1
            
            self.logger.error(f"Operation {operation_id} failed after {execution_time:.2f}s: {e}")
            raise
    
    def get_metrics(self):
        """Get current metrics"""
        avg_execution_time = (
            self.metrics['total_execution_time'] / max(self.metrics['successful_operations'], 1)
        )
        
        return {
            **self.metrics,
            'success_rate': self.metrics['successful_operations'] / max(self.metrics['total_sessions'], 1),
            'average_execution_time': avg_execution_time
        }

# Usage
monitored_client = MonitoredAGBClient()

def sample_operation(session):
    return session.code.run_code("print('Hello from monitored operation')", "python")

# Execute monitored operations
for i in range(3):
    try:
        result = monitored_client.execute_with_monitoring(f"sample_op_{i}", sample_operation)
        print(f"Operation {i} result: {result.result}")
    except Exception as e:
        print(f"Operation {i} failed: {e}")

# Check metrics
metrics = monitored_client.get_metrics()
print("\nMetrics:")
for key, value in metrics.items():
    print(f"  {key}: {value}")
```

## Related Documentation

- **[Session Management](session-management.md)** - Session lifecycle and management patterns
- **[Code Execution Guide](code-execution.md)** - Code execution best practices
- **[API Reference](../api-reference/README.md)** - Complete API documentation 