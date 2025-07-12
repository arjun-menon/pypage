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
    
    # Comprehensive nested conditionals tests
    tests = [
        # Basic nested if statements
        ("Simple nested if", "{% if True %}{% if True %}YES{% endif %}{% endif %}", "YES"),
        ("Nested if false outer", "{% if False %}{% if True %}YES{% endif %}{% endif %}", ""),
        ("Nested if false inner", "{% if True %}{% if False %}YES{% endif %}{% endif %}", ""),
        
        # Nested if-else combinations
        ("Nested if-else both true", "{% if True %}{% if True %}A{% else %}B{% endif %}{% endif %}", "A"),
        ("Nested if-else outer true inner false", "{% if True %}{% if False %}A{% else %}B{% endif %}{% endif %}", "B"),
        ("Nested if-else outer false", "{% if False %}{% if True %}A{% else %}B{% endif %}{% endif %}", ""),
        
        # Complex nested structures
        ("Nested if-else-if", "{% if True %}{% if x == 1 %}ONE{% elif x == 2 %}TWO{% else %}OTHER{% endif %}{% endif %}", "ONE", {"x": 1}),
        ("Nested elif chains", "{% if True %}{% if x == 1 %}ONE{% elif x == 2 %}TWO{% else %}OTHER{% endif %}{% endif %}", "TWO", {"x": 2}),
        ("Nested elif else", "{% if True %}{% if x == 1 %}ONE{% elif x == 2 %}TWO{% else %}OTHER{% endif %}{% endif %}", "OTHER", {"x": 3}),
        
        # Nested conditionals in for loops
        ("If in for loop", "{% for i in range(3) %}{% if i % 2 == 0 %}{{ i }}{% endif %}{% endfor %}", "02"),
        ("If-else in for loop", "{% for i in range(3) %}{% if i % 2 == 0 %}EVEN{% else %}ODD{% endif %}{% endfor %}", "EVENODDEVEN"),
        ("Complex if in for", "{% for i in range(4) %}{% if i == 0 %}ZERO{% elif i == 1 %}ONE{% elif i == 2 %}TWO{% else %}OTHER{% endif %}{% endfor %}", "ZEROONETWOOTHER"),
        
        # For loops in conditionals
        ("For in if true", "{% if True %}{% for i in range(3) %}{{ i }}{% endfor %}{% endif %}", "012"),
        ("For in if false", "{% if False %}{% for i in range(3) %}{{ i }}{% endfor %}{% endif %}", ""),
        ("For in if-else true", "{% if True %}{% for i in range(2) %}{{ i }}{% endfor %}{% else %}NO{% endif %}", "01"),
        ("For in if-else false", "{% if False %}{% for i in range(2) %}{{ i }}{% endfor %}{% else %}NO{% endif %}", "NO"),
        
        # Deeply nested structures
        ("Triple nested if", "{% if True %}{% if True %}{% if True %}DEEP{% endif %}{% endif %}{% endif %}", "DEEP"),
        ("Triple nested mixed", "{% if True %}{% if x > 0 %}{% if x < 10 %}SMALL{% else %}BIG{% endif %}{% else %}NEGATIVE{% endif %}{% endif %}", "SMALL", {"x": 5}),
        ("Triple nested else path", "{% if True %}{% if x > 0 %}{% if x < 10 %}SMALL{% else %}BIG{% endif %}{% else %}NEGATIVE{% endif %}{% endif %}", "BIG", {"x": 15}),
        
        # Nested conditionals with variables
        ("Nested with variables", "{% if x > 0 %}{% if y > 0 %}BOTH_POS{% else %}X_POS{% endif %}{% else %}X_NEG{% endif %}", "BOTH_POS", {"x": 5, "y": 3}),
        ("Nested variables mixed", "{% if x > 0 %}{% if y > 0 %}BOTH_POS{% else %}X_POS{% endif %}{% else %}X_NEG{% endif %}", "X_POS", {"x": 5, "y": -3}),
        ("Nested variables negative", "{% if x > 0 %}{% if y > 0 %}BOTH_POS{% else %}X_POS{% endif %}{% else %}X_NEG{% endif %}", "X_NEG", {"x": -5, "y": 3}),
        
        # Nested with complex expressions
        ("Nested complex expr", "{% if len(items) > 0 %}{% if items[0] == 'first' %}FIRST{% else %}OTHER{% endif %}{% endif %}", "FIRST", {"items": ["first", "second"]}),
        ("Nested method calls", "{% if name %}{% if name.startswith('A') %}STARTS_A{% else %}OTHER{% endif %}{% endif %}", "STARTS_A", {"name": "Alice"}),
        
        # Nested loops with conditionals
        ("Nested for loops with if", "{% for i in range(2) %}{% for j in range(2) %}{% if i == j %}{{ i }}{{ j }}{% endif %}{% endfor %}{% endfor %}", "0011"),
        ("Nested for with complex if", "{% for i in range(3) %}{% for j in range(3) %}{% if i + j == 2 %}({{ i }},{{ j }}){% endif %}{% endfor %}{% endfor %}", "(0,2)(1,1)(2,0)"),
        
        # Conditional chains in nested structures
        ("Nested elif chains", "{% if True %}{% if x == 1 %}A{% elif x == 2 %}B{% elif x == 3 %}C{% else %}D{% endif %}{% else %}OUTER_FALSE{% endif %}", "B", {"x": 2}),
        ("Nested outer elif", "{% if x == 1 %}{% if y == 1 %}A{% else %}B{% endif %}{% elif x == 2 %}{% if y == 1 %}C{% else %}D{% endif %}{% else %}E{% endif %}", "C", {"x": 2, "y": 1}),
        ("Nested outer elif else", "{% if x == 1 %}{% if y == 1 %}A{% else %}B{% endif %}{% elif x == 2 %}{% if y == 1 %}C{% else %}D{% endif %}{% else %}E{% endif %}", "D", {"x": 2, "y": 2}),
        
        # Mixed loop types in conditionals - commented out due to auto-increment expectation
        # ("While in if", "{% if True %}{% while x < 3 %}{{ x }}{% endwhile %}{% endif %}", "012", {"x": 0}),
        # ("If in while", "{% while x < 3 %}{% if x % 2 == 0 %}{{ x }}{% endif %}{% endwhile %}", "02", {"x": 0}),
        
        # Edge cases with empty conditions
        ("Nested empty if", "{% if True %}{% if True %}{% endif %}{% endif %}", ""),
        ("Nested one empty", "{% if True %}{% if True %}A{% endif %}{% if False %}B{% endif %}{% endif %}", "A"),
        
        # Boolean logic in nested conditions
        ("Nested boolean and", "{% if x and y %}{% if x > y %}X_BIGGER{% else %}Y_BIGGER{% endif %}{% endif %}", "X_BIGGER", {"x": 5, "y": 3}),
        ("Nested boolean or", "{% if x or y %}{% if x %}X_TRUE{% else %}Y_TRUE{% endif %}{% endif %}", "X_TRUE", {"x": True, "y": False}),
        
        # String operations in nested conditions
        ("Nested string conditions", "{% if name %}{% if len(name) > 5 %}LONG{% else %}SHORT{% endif %}{% endif %}", "SHORT", {"name": "Alice"}),
        ("Nested string methods", "{% if text %}{% if text.upper() == 'HELLO' %}GREETING{% else %}OTHER{% endif %}{% endif %}", "GREETING", {"text": "hello"}),
        
        # Nested with capture blocks
        ("Nested capture", "{% if True %}{% capture result %}{% if x > 0 %}POS{% else %}NEG{% endif %}{% endcapture %}{{ result }}{% endif %}", "POS", {"x": 5}),
        
        # Complex real-world scenarios
        ("User permissions", "{% if user %}{% if user['is_admin'] %}ADMIN{% elif user['is_moderator'] %}MOD{% else %}USER{% endif %}{% else %}GUEST{% endif %}", "ADMIN", {"user": {"is_admin": True, "is_moderator": False}}),
        ("Shopping cart", "{% if cart %}{% if len(cart) == 0 %}EMPTY{% elif len(cart) == 1 %}SINGLE{% else %}MULTIPLE{% endif %}{% else %}NO_CART{% endif %}", "MULTIPLE", {"cart": [1, 2, 3]}),
        ("Grade calculation", "{% if score %}{% if score >= 90 %}A{% elif score >= 80 %}B{% elif score >= 70 %}C{% elif score >= 60 %}D{% else %}F{% endif %}{% else %}NO_SCORE{% endif %}", "B", {"score": 85}),
        
        # Nested function definitions (if supported) - commented out until function calls are implemented
        # ("Nested with function", "{% def greet name %}Hello {{ name }}{% enddef %}{% if True %}{% if name %}{{ greet(name) }}{% endif %}{% endif %}", "Hello Alice", {"name": "Alice"}),
        
        # Error handling scenarios
        ("Nested with try-like", "{% if data %}{% if 'key' in data %}{{ data['key'] }}{% else %}NO_KEY{% endif %}{% else %}NO_DATA{% endif %}", "value", {"data": {"key": "value"}}),
        ("Nested missing key", "{% if data %}{% if 'key' in data %}{{ data['key'] }}{% else %}NO_KEY{% endif %}{% else %}NO_DATA{% endif %}", "NO_KEY", {"data": {"other": "value"}}),
        
        # Extremely deep nesting
        ("Deep nesting", "{% if True %}{% if True %}{% if True %}{% if True %}{% if True %}VERY_DEEP{% endif %}{% endif %}{% endif %}{% endif %}{% endif %}", "VERY_DEEP"),
        
        # Mixed structures
        ("If-for-if pattern", "{% if True %}{% for i in range(2) %}{% if i == 1 %}ONE{% endif %}{% endfor %}{% endif %}", "ONE"),
        ("For-if-for pattern", "{% for i in range(2) %}{% if i == 0 %}{% for j in range(2) %}{{ j }}{% endfor %}{% endif %}{% endfor %}", "01"),
        
        # Complex variable interactions
        ("Nested variable modification", "{% if x > 0 %}{% capture result %}{% if x > 10 %}BIG{% else %}SMALL{% endif %}{% endcapture %}{{ result }}:{{ x }}{% endif %}", "SMALL:5", {"x": 5}),
    ]
    
    print(f"Running {len(tests)} nested conditionals tests...")
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
        print("🎉 All nested conditionals tests passed!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 