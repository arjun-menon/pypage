#!/usr/bin/env python3

import sys
import os

# Add the target directory to Python path to import the built module
target_dir = "target/debug"
if target_dir not in sys.path:
    sys.path.insert(0, target_dir)

# Global test counters
passed = 0
total = 0

def run_test(name, template, env=None, expected=None):
    """Run a single test and track results"""
    global passed, total
    total += 1
    
    print(f"Test {total}: {name}")
    try:
        result = pypage.pypage_process(template, env)
        print(f"Result: '{result}'")
        
        if expected is not None:
            if result == expected:
                print("✅ PASS")
                passed += 1
            else:
                print(f"❌ FAIL - Expected: '{expected}'")
        else:
            print("✅ PASS (no expected result specified)")
            passed += 1
        print()
        return True
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print()
        return False

try:
    import pypage
    
    print(f"pypage version: {pypage.pypage_version()}")
    print("=" * 50)
    
    # Test 1: Basic expression
    run_test("Basic expression", "Hello {{ 2 + 2 }}", None, "Hello 4")
    
    # Test 2: Simple conditional
    run_test("Simple conditional", "{% if True %}This is true{% endif %}", None, "This is true")
    
    # Test 3: False conditional
    run_test("False conditional", "{% if False %}This won't show{% endif %}", None, "")
    
    # Test 4: If-else
    run_test("If-else", "{% if False %}Won't show{% else %}This will show{% endif %}", None, "This will show")
    
    # Test 5: Variables with seed environment
    seed_env = {"name": "World", "value": "42"}
    run_test("Variables with seed environment", "Hello {{ name }}! The answer is {{ value }}.", seed_env, "Hello World! The answer is 42.")
    
    # Test 6: Comments (should be ignored)
    run_test("Comments", "Before {# This is a comment #} After", None, "Before  After")
    
    print("All tests completed!")
    print(f"Results: {passed}/{total} tests passed")
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {total - passed} tests failed or had errors")
    
except ImportError as e:
    print(f"Could not import pypage module: {e}")
    print("Make sure the Rust library is built with 'cargo build'")
except Exception as e:
    print(f"Error testing pypage: {e}")
    import traceback
    traceback.print_exc() 