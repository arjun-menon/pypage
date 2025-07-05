#!/usr/bin/env python3

import subprocess
import sys
import os

def build_and_test():
    """Build the Rust library and run tests"""
    try:
        # Build the library
        result = subprocess.run(['cargo', 'build', '--release'], 
                              capture_output=True, text=True, cwd='.')
        if result.returncode != 0:
            print("Build failed:", result.stderr)
            return False
        
        # Copy the built library
        import shutil
        shutil.copy('target/release/libpypage.dylib', 'pypage.so')
        return True
    except Exception as e:
        print(f"Build error: {e}")
        return False

def run_test(name, template, expected, env=None):
    """Run a single test"""
    try:
        import pypage
        result = pypage.pypage_process(template, env)
        if result == expected:
            print(f"✅ {name}")
            return True
        else:
            print(f"❌ {name}")
            print(f"   Expected: {repr(expected)}")
            print(f"   Got:      {repr(result)}")
            return False
    except Exception as e:
        print(f"❌ {name} - Exception: {e}")
        return False

def main():
    if not build_and_test():
        sys.exit(1)
    
    # Test results
    passed = 0
    total = 0
    
    # Comprehensive elif chain tests
    tests = [
        # Basic elif tests
        ("Simple elif - first condition", "{% if x == 1 %}ONE{% elif x == 2 %}TWO{% endif %}", "ONE", {"x": 1}),
        ("Simple elif - second condition", "{% if x == 1 %}ONE{% elif x == 2 %}TWO{% endif %}", "TWO", {"x": 2}),
        ("Simple elif - no match", "{% if x == 1 %}ONE{% elif x == 2 %}TWO{% endif %}", "", {"x": 3}),
        
        # Elif with else
        ("Elif with else - first", "{% if x == 1 %}ONE{% elif x == 2 %}TWO{% else %}OTHER{% endif %}", "ONE", {"x": 1}),
        ("Elif with else - second", "{% if x == 1 %}ONE{% elif x == 2 %}TWO{% else %}OTHER{% endif %}", "TWO", {"x": 2}),
        ("Elif with else - else", "{% if x == 1 %}ONE{% elif x == 2 %}TWO{% else %}OTHER{% endif %}", "OTHER", {"x": 3}),
        
        # Multiple elif chains
        ("Multiple elif - first", "{% if x == 1 %}A{% elif x == 2 %}B{% elif x == 3 %}C{% elif x == 4 %}D{% endif %}", "A", {"x": 1}),
        ("Multiple elif - second", "{% if x == 1 %}A{% elif x == 2 %}B{% elif x == 3 %}C{% elif x == 4 %}D{% endif %}", "B", {"x": 2}),
        ("Multiple elif - third", "{% if x == 1 %}A{% elif x == 2 %}B{% elif x == 3 %}C{% elif x == 4 %}D{% endif %}", "C", {"x": 3}),
        ("Multiple elif - fourth", "{% if x == 1 %}A{% elif x == 2 %}B{% elif x == 3 %}C{% elif x == 4 %}D{% endif %}", "D", {"x": 4}),
        ("Multiple elif - none", "{% if x == 1 %}A{% elif x == 2 %}B{% elif x == 3 %}C{% elif x == 4 %}D{% endif %}", "", {"x": 5}),
        
        # Multiple elif with else
        ("Multiple elif with else - first", "{% if x == 1 %}A{% elif x == 2 %}B{% elif x == 3 %}C{% else %}D{% endif %}", "A", {"x": 1}),
        ("Multiple elif with else - second", "{% if x == 1 %}A{% elif x == 2 %}B{% elif x == 3 %}C{% else %}D{% endif %}", "B", {"x": 2}),
        ("Multiple elif with else - third", "{% if x == 1 %}A{% elif x == 2 %}B{% elif x == 3 %}C{% else %}D{% endif %}", "C", {"x": 3}),
        ("Multiple elif with else - else", "{% if x == 1 %}A{% elif x == 2 %}B{% elif x == 3 %}C{% else %}D{% endif %}", "D", {"x": 4}),
        
        # Complex expressions in elif
        ("Elif with complex expr - first", "{% if x > 10 %}BIG{% elif x > 5 %}MEDIUM{% elif x > 0 %}SMALL{% else %}ZERO{% endif %}", "BIG", {"x": 15}),
        ("Elif with complex expr - second", "{% if x > 10 %}BIG{% elif x > 5 %}MEDIUM{% elif x > 0 %}SMALL{% else %}ZERO{% endif %}", "MEDIUM", {"x": 8}),
        ("Elif with complex expr - third", "{% if x > 10 %}BIG{% elif x > 5 %}MEDIUM{% elif x > 0 %}SMALL{% else %}ZERO{% endif %}", "SMALL", {"x": 3}),
        ("Elif with complex expr - else", "{% if x > 10 %}BIG{% elif x > 5 %}MEDIUM{% elif x > 0 %}SMALL{% else %}ZERO{% endif %}", "ZERO", {"x": 0}),
        
        # String-based elif chains
        ("String elif - first", "{% if name == 'Alice' %}Hello Alice{% elif name == 'Bob' %}Hello Bob{% else %}Hello Stranger{% endif %}", "Hello Alice", {"name": "Alice"}),
        ("String elif - second", "{% if name == 'Alice' %}Hello Alice{% elif name == 'Bob' %}Hello Bob{% else %}Hello Stranger{% endif %}", "Hello Bob", {"name": "Bob"}),
        ("String elif - else", "{% if name == 'Alice' %}Hello Alice{% elif name == 'Bob' %}Hello Bob{% else %}Hello Stranger{% endif %}", "Hello Stranger", {"name": "Charlie"}),
        
        # Boolean logic in elif
        ("Boolean elif - first", "{% if x and y %}BOTH{% elif x %}X_ONLY{% elif y %}Y_ONLY{% else %}NEITHER{% endif %}", "BOTH", {"x": True, "y": True}),
        ("Boolean elif - second", "{% if x and y %}BOTH{% elif x %}X_ONLY{% elif y %}Y_ONLY{% else %}NEITHER{% endif %}", "X_ONLY", {"x": True, "y": False}),
        ("Boolean elif - third", "{% if x and y %}BOTH{% elif x %}X_ONLY{% elif y %}Y_ONLY{% else %}NEITHER{% endif %}", "Y_ONLY", {"x": False, "y": True}),
        ("Boolean elif - else", "{% if x and y %}BOTH{% elif x %}X_ONLY{% elif y %}Y_ONLY{% else %}NEITHER{% endif %}", "NEITHER", {"x": False, "y": False}),
        
        # Nested elif structures
        ("Nested elif outer", "{% if x == 1 %}{% if y == 1 %}A{% elif y == 2 %}B{% else %}C{% endif %}{% elif x == 2 %}D{% endif %}", "A", {"x": 1, "y": 1}),
        ("Nested elif inner", "{% if x == 1 %}{% if y == 1 %}A{% elif y == 2 %}B{% else %}C{% endif %}{% elif x == 2 %}D{% endif %}", "B", {"x": 1, "y": 2}),
        ("Nested elif else", "{% if x == 1 %}{% if y == 1 %}A{% elif y == 2 %}B{% else %}C{% endif %}{% elif x == 2 %}D{% endif %}", "C", {"x": 1, "y": 3}),
        ("Nested elif outer second", "{% if x == 1 %}{% if y == 1 %}A{% elif y == 2 %}B{% else %}C{% endif %}{% elif x == 2 %}D{% endif %}", "D", {"x": 2, "y": 1}),
        
        # Complex edge cases
        ("Long elif chain", "{% if x == 1 %}1{% elif x == 2 %}2{% elif x == 3 %}3{% elif x == 4 %}4{% elif x == 5 %}5{% elif x == 6 %}6{% elif x == 7 %}7{% elif x == 8 %}8{% elif x == 9 %}9{% else %}10{% endif %}", "5", {"x": 5}),
        ("Long elif chain else", "{% if x == 1 %}1{% elif x == 2 %}2{% elif x == 3 %}3{% elif x == 4 %}4{% elif x == 5 %}5{% elif x == 6 %}6{% elif x == 7 %}7{% elif x == 8 %}8{% elif x == 9 %}9{% else %}10{% endif %}", "10", {"x": 15}),
        
        # Edge case with function calls
        ("Elif with function calls", "{% if len(items) == 0 %}EMPTY{% elif len(items) == 1 %}SINGLE{% else %}MULTIPLE{% endif %}", "SINGLE", {"items": [1]}),
        ("Elif with method calls", "{% if text.startswith('A') %}STARTS_A{% elif text.startswith('B') %}STARTS_B{% else %}OTHER{% endif %}", "STARTS_A", {"text": "Apple"}),
        
        # Mixed types in elif
        ("Mixed types elif", "{% if isinstance(val, str) %}STRING{% elif isinstance(val, int) %}INTEGER{% elif isinstance(val, bool) %}BOOLEAN{% else %}OTHER{% endif %}", "INTEGER", {"val": 42}),
    ]
    
    print(f"Running {len(tests)} elif chain tests...")
    print("=" * 50)
    
    for test_data in tests:
        if len(test_data) == 3:
            name, template, expected = test_data
            env = None
        else:
            name, template, expected, env = test_data
        
        if run_test(name, template, expected, env):
            passed += 1
        total += 1
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All elif tests passed!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 