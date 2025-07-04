#!/usr/bin/env python3

import sys
import os

# Add the target directory to Python path to import the built module
target_dir = "target/debug"
if target_dir not in sys.path:
    sys.path.insert(0, target_dir)

try:
    import pypage
    
    print(f"pypage version: {pypage.pypage_version()}")
    print("=" * 50)
    
    # Test 1: Basic expression
    print("Test 1: Basic expression")
    result = pypage.pypage_process("Hello {{ 2 + 2 }}", None)
    print(f"Result: '{result}'")
    print()
    
    # Test 2: Simple conditional
    print("Test 2: Simple conditional")
    result = pypage.pypage_process("{% if True %}This is true{% endif %}", None)
    print(f"Result: '{result}'")
    print()
    
    # Test 3: False conditional
    print("Test 3: False conditional")
    result = pypage.pypage_process("{% if False %}This won't show{% endif %}", None)
    print(f"Result: '{result}'")
    print()
    
    # Test 4: If-else
    print("Test 4: If-else")
    result = pypage.pypage_process("{% if False %}Won't show{% else %}This will show{% endif %}", None)
    print(f"Result: '{result}'")
    print()
    
    # Test 5: Variables with seed environment
    print("Test 5: Variables with seed environment")
    seed_env = {"name": "World", "value": "42"}
    result = pypage.pypage_process("Hello {{ name }}! The answer is {{ value }}.", seed_env)
    print(f"Result: '{result}'")
    print()
    
    # Test 6: Comments (should be ignored)
    print("Test 6: Comments")
    result = pypage.pypage_process("Before {# This is a comment #} After", None)
    print(f"Result: '{result}'")
    print()
    
    print("All tests completed successfully!")
    
except ImportError as e:
    print(f"Could not import pypage module: {e}")
    print("Make sure the Rust library is built with 'cargo build'")
except Exception as e:
    print(f"Error testing pypage: {e}")
    import traceback
    traceback.print_exc() 