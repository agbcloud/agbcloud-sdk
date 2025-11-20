#!/usr/bin/env python3
"""
Response types configuration for API documentation generation.
This file is automatically updated when generate_api_docs.py is run.
"""

from typing import Dict, Any, Type
from pathlib import Path
import sys
import re
import importlib

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def get_response_types() -> Dict[str, Dict[str, Any]]:
    """
    Get the response types configuration.
    
    Returns:
        Dict containing response type configurations with class objects, modules, and descriptions.
    """
    # Import response classes
    try:
        from agb.model.response import (
            ApiResponse, SessionResult, DeleteResult, OperationResult, 
            BoolResult, GetSessionResult, SessionListResult, GetSessionData
        )
        from agb.modules.file_system import (
            FileInfoResult, FileContentResult, MultipleFileContentResult,
            DirectoryListResult, FileSearchResult, FileChangeResult
        )
    except ImportError as e:
        print(f"Warning: Could not import response classes: {e}")
        return {}
    
    # Response types to document
    response_types = {
        'ApiResponse': {
            'class': ApiResponse,
            'module': 'agb.model.response',
            'description': 'Base class for all API responses, containing RequestID'
        },
        'SessionResult': {
            'class': SessionResult,
            'module': 'agb.model.response',
            'description': 'Result of operations returning a single Session'
        },
        'DeleteResult': {
            'class': DeleteResult,
            'module': 'agb.model.response',
            'description': 'Result of delete operations'
        },
        'OperationResult': {
            'class': OperationResult,
            'module': 'agb.model.response',
            'description': 'Result of general operations'
        },
        'BoolResult': {
            'class': BoolResult,
            'module': 'agb.model.response',
            'description': 'Result of operations returning a boolean value'
        },
        'GetSessionResult': {
            'class': GetSessionResult,
            'module': 'agb.model.response',
            'description': 'Result of GetSession operations'
        },
        'SessionListResult': {
            'class': SessionListResult,
            'module': 'agb.model.response',
            'description': 'Result of operations returning a list of Sessions'
        },
        'GetSessionData': {
            'class': GetSessionData,
            'module': 'agb.model.response',
            'description': 'Data returned by GetSession API'
        },
        'FileInfoResult': {
            'class': FileInfoResult,
            'module': 'agb.modules.file_system',
            'description': 'Result of file info operations'
        },
        'FileContentResult': {
            'class': FileContentResult,
            'module': 'agb.modules.file_system',
            'description': 'Result of file read operations'
        },
        'MultipleFileContentResult': {
            'class': MultipleFileContentResult,
            'module': 'agb.modules.file_system',
            'description': 'Result of multiple file read operations'
        },
        'DirectoryListResult': {
            'class': DirectoryListResult,
            'module': 'agb.modules.file_system',
            'description': 'Result of directory listing operations'
        },
        'FileSearchResult': {
            'class': FileSearchResult,
            'module': 'agb.modules.file_system',
            'description': 'Result of file search operations'
        },
        'FileChangeResult': {
            'class': FileChangeResult,
            'module': 'agb.modules.file_system',
            'description': 'Result of file change detection operations'
        }
    }
    
    return response_types

def update_response_types_config():
    """
    Update this configuration file by scanning the codebase for response types.
    This function automatically discovers new response types and updates the configuration.
    """
    import os
    import re
    import importlib.util
    from datetime import datetime
    
    print("Updating response types configuration...")
    
    # Scan for response classes in the codebase
    discovered_types = discover_response_types()
    
    if discovered_types:
        print(f"Discovered {len(discovered_types)} response types")
        # Update the configuration file with discovered types
        update_config_file(discovered_types)
    else:
        print("No new response types discovered")

def discover_response_types():
    """
    Automatically discover response types by scanning the codebase.
    
    Returns:
        Dict containing discovered response types
    """
    discovered = {}
    
    # Define search paths for response classes
    search_paths = [
        PROJECT_ROOT / "agb" / "model",
        PROJECT_ROOT / "agb" / "modules",
    ]
    
    for search_path in search_paths:
        if search_path.exists():
            for py_file in search_path.rglob("*.py"):
                if py_file.name.startswith('__'):
                    continue
                    
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for class definitions that end with "Result" or inherit from ApiResponse
                    class_pattern = r'class\s+(\w*(?:Result|Response))\s*\([^)]*\):'
                    matches = re.findall(class_pattern, content)
                    
                    for class_name in matches:
                        if class_name and class_name not in ['ApiResponse']:  # Skip base class
                            # Try to import and get the class
                            try:
                                module_path = str(py_file.relative_to(PROJECT_ROOT)).replace('/', '.').replace('\\', '.').replace('.py', '')
                                
                                # Import the module dynamically
                                spec = importlib.util.spec_from_file_location(module_path, py_file)
                                if spec and spec.loader:
                                    module = importlib.util.module_from_spec(spec)
                                    spec.loader.exec_module(module)
                                    
                                    if hasattr(module, class_name):
                                        class_obj = getattr(module, class_name)
                                        
                                        # Generate description based on class name and docstring
                                        description = generate_description(class_name, class_obj)
                                        
                                        discovered[class_name] = {
                                            'class': class_obj,
                                            'module': module_path,
                                            'description': description
                                        }
                                        
                            except Exception as e:
                                print(f"Warning: Could not import {class_name} from {py_file}: {e}")
                                continue
                                
                except Exception as e:
                    print(f"Warning: Could not scan file {py_file}: {e}")
                    continue
    
    return discovered

def generate_description(class_name: str, class_obj) -> str:
    """
    Generate a description for a response type based on its name and docstring.
    
    Args:
        class_name: Name of the class
        class_obj: The class object
        
    Returns:
        Generated description string
    """
    # Try to get description from docstring
    if hasattr(class_obj, '__doc__') and class_obj.__doc__:
        doc = class_obj.__doc__.strip()
        if doc:
            # Use first line of docstring
            first_line = doc.split('\n')[0].strip()
            if first_line and not first_line.startswith('class '):
                return first_line
    
    # Generate description based on class name patterns
    if class_name.endswith('Result'):
        base_name = class_name[:-6]  # Remove 'Result'
        if base_name:
            # Convert CamelCase to readable format
            readable_name = re.sub(r'([A-Z])', r' \1', base_name).strip().lower()
            return f"Result of {readable_name} operations"
    
    elif class_name.endswith('Response'):
        base_name = class_name[:-8]  # Remove 'Response'
        if base_name:
            readable_name = re.sub(r'([A-Z])', r' \1', base_name).strip().lower()
            return f"Response from {readable_name} operations"
    
    # Default description
    return f"Response type for {class_name}"

def update_config_file(discovered_types):
    """
    Update the configuration file with discovered response types.
    
    Args:
        discovered_types: Dictionary of discovered response types
    """
    # For now, we'll just print what was discovered
    # In a more advanced implementation, this could rewrite the configuration
    print("Discovered response types:")
    for name, config in discovered_types.items():
        print(f"  - {name}: {config['description']}")
    
    # Note: Automatic file rewriting is complex and could break existing code
    # For safety, we'll keep the manual configuration approach

if __name__ == "__main__":
    # When run directly, print available response types
    response_types = get_response_types()
    print("Available Response Types:")
    for name, config in response_types.items():
        print(f"  - {name}: {config['description']}")
