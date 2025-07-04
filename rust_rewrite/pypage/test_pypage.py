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
    
    # Test basic template processing
    test_template = "Hello {{ 2 + 2 }}"
    
    result = pypage.pypage_process(test_template, None)
    print("Test result:")
    print(result)
    
except ImportError as e:
    print(f"Could not import pypage module: {e}")
    print("Make sure the Rust library is built with 'cargo build'")
except Exception as e:
    print(f"Error testing pypage: {e}") 