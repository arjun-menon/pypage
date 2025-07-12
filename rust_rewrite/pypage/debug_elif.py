#!/usr/bin/env python3

import subprocess
import sys
import os

# Global test counters
passed = 0
total = 0

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

def debug_test(name, template, expected, env=None):
    """Debug a single test with detailed output"""
    global passed, total
    total += 1
    
    try:
        import pypage
        print(f"\n🔍 DEBUG: {name}")
        print(f"Template: {repr(template)}")
        print(f"Expected: {repr(expected)}")
        print(f"Environment: {env}")
        
        result = pypage.pypage_process(template, env)
        print(f"Got:      {repr(result)}")
        
        if result == expected:
            print("✅ PASS")
            passed += 1
            return True
        else:
            print("❌ FAIL")
            print(f"   Difference: Expected {repr(expected)}, got {repr(result)}")
            return False
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if not build_and_test():
        sys.exit(1)
    
    # Debug specific elif issues
    print("🔬 DEBUGGING ELIF FUNCTIONALITY")
    print("=" * 60)
    
    # Test 1: Basic elif chain
    print("\n1. Testing basic elif chain...")
    debug_test("Basic elif first", "{% if x == 1 %}ONE{% elif x == 2 %}TWO{% endif %}", "ONE", {"x": 1})
    debug_test("Basic elif second", "{% if x == 1 %}ONE{% elif x == 2 %}TWO{% endif %}", "TWO", {"x": 2})
    debug_test("Basic elif none", "{% if x == 1 %}ONE{% elif x == 2 %}TWO{% endif %}", "", {"x": 3})
    
    # Test 2: Elif with else
    print("\n2. Testing elif with else...")
    debug_test("Elif else first", "{% if x == 1 %}ONE{% elif x == 2 %}TWO{% else %}OTHER{% endif %}", "ONE", {"x": 1})
    debug_test("Elif else second", "{% if x == 1 %}ONE{% elif x == 2 %}TWO{% else %}OTHER{% endif %}", "TWO", {"x": 2})
    debug_test("Elif else fallback", "{% if x == 1 %}ONE{% elif x == 2 %}TWO{% else %}OTHER{% endif %}", "OTHER", {"x": 3})
    
    # Test 3: Multiple elif chain
    print("\n3. Testing multiple elif...")
    debug_test("Multiple elif A", "{% if x == 1 %}A{% elif x == 2 %}B{% elif x == 3 %}C{% elif x == 4 %}D{% endif %}", "A", {"x": 1})
    debug_test("Multiple elif B", "{% if x == 1 %}A{% elif x == 2 %}B{% elif x == 3 %}C{% elif x == 4 %}D{% endif %}", "B", {"x": 2})
    debug_test("Multiple elif C", "{% if x == 1 %}A{% elif x == 2 %}B{% elif x == 3 %}C{% elif x == 4 %}D{% endif %}", "C", {"x": 3})
    debug_test("Multiple elif D", "{% if x == 1 %}A{% elif x == 2 %}B{% elif x == 3 %}C{% elif x == 4 %}D{% endif %}", "D", {"x": 4})
    debug_test("Multiple elif none", "{% if x == 1 %}A{% elif x == 2 %}B{% elif x == 3 %}C{% elif x == 4 %}D{% endif %}", "", {"x": 5})
    
    # Test 4: Complex expressions in elif
    print("\n4. Testing complex expressions...")
    debug_test("Complex expr 1", "{% if x > 10 %}BIG{% elif x > 5 %}MEDIUM{% elif x > 0 %}SMALL{% else %}ZERO{% endif %}", "BIG", {"x": 15})
    debug_test("Complex expr 2", "{% if x > 10 %}BIG{% elif x > 5 %}MEDIUM{% elif x > 0 %}SMALL{% else %}ZERO{% endif %}", "MEDIUM", {"x": 8})
    debug_test("Complex expr 3", "{% if x > 10 %}BIG{% elif x > 5 %}MEDIUM{% elif x > 0 %}SMALL{% else %}ZERO{% endif %}", "SMALL", {"x": 3})
    debug_test("Complex expr 4", "{% if x > 10 %}BIG{% elif x > 5 %}MEDIUM{% elif x > 0 %}SMALL{% else %}ZERO{% endif %}", "ZERO", {"x": 0})
    
    # Test 5: Boolean logic
    print("\n5. Testing boolean logic...")
    debug_test("Boolean and", "{% if x and y %}BOTH{% elif x %}X_ONLY{% elif y %}Y_ONLY{% else %}NEITHER{% endif %}", "BOTH", {"x": True, "y": True})
    debug_test("Boolean x only", "{% if x and y %}BOTH{% elif x %}X_ONLY{% elif y %}Y_ONLY{% else %}NEITHER{% endif %}", "X_ONLY", {"x": True, "y": False})
    debug_test("Boolean y only", "{% if x and y %}BOTH{% elif x %}X_ONLY{% elif y %}Y_ONLY{% else %}NEITHER{% endif %}", "Y_ONLY", {"x": False, "y": True})
    debug_test("Boolean neither", "{% if x and y %}BOTH{% elif x %}X_ONLY{% elif y %}Y_ONLY{% else %}NEITHER{% endif %}", "NEITHER", {"x": False, "y": False})
    
    # Test 6: String comparisons
    print("\n6. Testing string comparisons...")
    debug_test("String Alice", "{% if name == 'Alice' %}ALICE{% elif name == 'Bob' %}BOB{% else %}OTHER{% endif %}", "ALICE", {"name": "Alice"})
    debug_test("String Bob", "{% if name == 'Alice' %}ALICE{% elif name == 'Bob' %}BOB{% else %}OTHER{% endif %}", "BOB", {"name": "Bob"})
    debug_test("String other", "{% if name == 'Alice' %}ALICE{% elif name == 'Bob' %}BOB{% else %}OTHER{% endif %}", "OTHER", {"name": "Charlie"})
    
    # Test 7: Nested elif (problematic case)
    print("\n7. Testing nested elif...")
    debug_test("Nested elif", "{% if True %}{% if x == 1 %}A{% elif x == 2 %}B{% else %}C{% endif %}{% endif %}", "A", {"x": 1})
    debug_test("Nested elif 2", "{% if True %}{% if x == 1 %}A{% elif x == 2 %}B{% else %}C{% endif %}{% endif %}", "B", {"x": 2})
    debug_test("Nested elif 3", "{% if True %}{% if x == 1 %}A{% elif x == 2 %}B{% else %}C{% endif %}{% endif %}", "C", {"x": 3})
    
    # Test 8: Edge case - empty conditions
    print("\n8. Testing edge cases...")
    debug_test("Empty elif", "{% if False %}{% elif True %}YES{% endif %}", "YES")
    debug_test("Empty else", "{% if False %}{% elif False %}{% else %}YES{% endif %}", "YES")
    
    # Test 9: Function calls in elif
    print("\n9. Testing function calls...")
    debug_test("Function in elif", "{% if len(items) == 0 %}EMPTY{% elif len(items) == 1 %}SINGLE{% else %}MULTIPLE{% endif %}", "SINGLE", {"items": [1]})
    debug_test("Method in elif", "{% if text.startswith('A') %}STARTS_A{% elif text.startswith('B') %}STARTS_B{% else %}OTHER{% endif %}", "STARTS_A", {"text": "Apple"})
    
    # Test 10: Very long elif chain
    print("\n10. Testing long elif chain...")
    debug_test("Long elif chain", 
               "{% if x == 1 %}1{% elif x == 2 %}2{% elif x == 3 %}3{% elif x == 4 %}4{% elif x == 5 %}5{% elif x == 6 %}6{% elif x == 7 %}7{% elif x == 8 %}8{% elif x == 9 %}9{% else %}10{% endif %}", 
               "5", {"x": 5})
    debug_test("Long elif chain else", 
               "{% if x == 1 %}1{% elif x == 2 %}2{% elif x == 3 %}3{% elif x == 4 %}4{% elif x == 5 %}5{% elif x == 6 %}6{% elif x == 7 %}7{% elif x == 8 %}8{% elif x == 9 %}9{% else %}10{% endif %}", 
               "10", {"x": 15})
    
    print("\n" + "=" * 60)
    print("🔬 Debug session completed.")
    print(f"Results: {passed}/{total} tests passed")
    if passed == total:
        print("🎉 All elif tests passed!")
    else:
        print(f"⚠️  {total - passed} tests failed or had errors")
        print("If any tests failed, examine the detailed output above.")

if __name__ == "__main__":
    main() 