#!/usr/bin/env python3
"""
Complex Nesting Test Suite - Tests deep nesting scenarios and interactions between different block types.
"""

import sys
import os

# Import the Rust module directly from the current directory
sys.path.insert(0, os.path.dirname(__file__))
import pypage

# Test counters
passed = 0
total = 0

def test_case(template, expected, description):
    """Helper function to run a test case"""
    global passed, total
    total += 1
    
    try:
        result = pypage.pypage_process(template, {})
        if result == expected:
            print(f"✅ Test {total:2d}: PASS - {description}")
            passed += 1
        else:
            print(f"❌ Test {total:2d}: FAIL - {description}")
            print(f"    Template: {repr(template)}")
            print(f"    Expected: {repr(expected)}")
            print(f"    Got:      {repr(result)}")
    except Exception as e:
        print(f"❌ Test {total:2d}: ERROR - {description}")
        print(f"    Template: {repr(template)}")
        print(f"    Error:    {e}")

def test_nested_conditionals_in_loops():
    """Test conditionals nested inside loops"""
    print("\nTesting nested conditionals in loops...")
    print("=" * 60)
    
    # For loop with nested if/elif/else
    test_case(
        "{% for i in range(3) %}{% if i == 0 %}zero{% elif i == 1 %}one{% else %}two{% endif %}{% endfor %}",
        "zeroonetwoo",
        "For loop with nested if/elif/else"
    )
    
    # Nested for loops with conditionals
    test_case(
        "{% for i in range(2) %}{% for j in range(2) %}{% if i == j %}equal{% else %}diff{% endif %}{% endfor %}{% endfor %}",
        "equaldiffdifeequal",
        "Nested for loops with conditionals"
    )
    
    # While loop with nested conditionals
    test_case(
        "{% capture count %}0{% endcapture %}{% while int(count) < 3 %}{% if int(count) == 1 %}one{% else %}other{% endif %}{% capture count %}{{ int(count) + 1 }}{% endcapture %}{% endwhile %}",
        "otheroneonother",
        "While loop with nested conditionals"
    )

def test_loops_in_conditionals():
    """Test loops nested inside conditionals"""
    print("\nTesting loops in conditionals...")
    print("=" * 60)
    
    # If with nested for loop
    test_case(
        "{% if True %}{% for i in range(3) %}{{ i }}{% endfor %}{% endif %}",
        "012",
        "If with nested for loop"
    )
    
    # If/elif/else with different nested loops
    test_case(
        "{% if False %}none{% elif True %}{% for i in range(2) %}{{ i }}{% endfor %}{% else %}fallback{% endif %}",
        "01",
        "Elif with nested for loop"
    )
    
    # Conditional chain with nested while loops
    test_case(
        "{% if True %}{% capture x %}0{% endcapture %}{% while int(x) < 2 %}{{ x }}{% capture x %}{{ int(x) + 1 }}{% endcapture %}{% endwhile %}{% endif %}",
        "01",
        "If with nested while loop"
    )

def test_deeply_nested_structures():
    """Test very deep nesting scenarios"""
    print("\nTesting deeply nested structures...")
    print("=" * 60)
    
    # 4-level nesting: for -> if -> for -> if
    test_case(
        "{% for i in range(2) %}{% if i == 0 %}{% for j in range(2) %}{% if j == 1 %}X{% endif %}{% endfor %}{% endif %}{% endfor %}",
        "X",
        "4-level nesting: for->if->for->if"
    )
    
    # 5-level nesting with mixed block types
    test_case(
        "{% if True %}{% for i in range(2) %}{% if i == 1 %}{% capture temp %}{% for k in range(1) %}found{% endfor %}{% endcapture %}{{ temp }}{% endif %}{% endfor %}{% endif %}",
        "found",
        "5-level nesting with capture block"
    )
    
    # Very deep conditional nesting
    test_case(
        "{% if True %}{% if True %}{% if True %}{% if True %}deep{% endif %}{% endif %}{% endif %}{% endif %}",
        "deep",
        "Very deep conditional nesting"
    )

def test_complex_loop_combinations():
    """Test complex combinations of different loop types"""
    print("\nTesting complex loop combinations...")
    print("=" * 60)
    
    # For loop inside while loop
    test_case(
        "{% capture outer %}0{% endcapture %}{% while int(outer) < 2 %}[{% for i in range(2) %}{{ i }}{% endfor %}]{% capture outer %}{{ int(outer) + 1 }}{% endcapture %}{% endwhile %}",
        "[01][01]",
        "For loop inside while loop"
    )
    
    # While loop inside for loop
    test_case(
        "{% for i in range(2) %}{% capture inner %}0{% endcapture %}{% while int(inner) < 2 %}{{ inner }}{% capture inner %}{{ int(inner) + 1 }}{% endcapture %}{% endwhile %}{% endfor %}",
        "0101",
        "While loop inside for loop"
    )
    
    # Nested loops with shared variables
    test_case(
        "{% for i in range(2) %}{% for j in range(2) %}{{ i }}{{ j }}{% endfor %}{% endfor %}",
        "00011011",
        "Nested for loops with shared iteration"
    )

def test_function_definitions_in_blocks():
    """Test function definitions inside various block types"""
    print("\nTesting function definitions in blocks...")
    print("=" * 60)
    
    # Function defined in conditional
    test_case(
        "{% if True %}{% def greet name %}Hello {{ name }}{% enddef %}{% endif %}{{ greet('World') }}",
        "Hello World",
        "Function defined in conditional block"
    )
    
    # Function defined in loop (should be accessible after)
    test_case(
        "{% for i in range(1) %}{% def multiply x y %}{{ x * y }}{% enddef %}{% endfor %}{{ multiply(3, 4) }}",
        "12",
        "Function defined in loop"
    )
    
    # Multiple functions defined in nested blocks
    test_case(
        "{% if True %}{% def add x y %}{{ x + y }}{% enddef %}{% if True %}{% def sub x y %}{{ x - y }}{% enddef %}{% endif %}{% endif %}{{ add(5, 3) }}-{{ sub(5, 3) }}",
        "8-2",
        "Multiple functions in nested conditionals"
    )

def test_capture_blocks_complex():
    """Test complex capture block scenarios"""
    print("\nTesting complex capture block scenarios...")
    print("=" * 60)
    
    # Capture block with nested loops
    test_case(
        "{% capture result %}{% for i in range(3) %}{{ i }}{% endfor %}{% endcapture %}Result: {{ result }}",
        "Result: 012",
        "Capture block with nested for loop"
    )
    
    # Nested capture blocks
    test_case(
        "{% capture outer %}{% capture inner %}nested{% endcapture %}[{{ inner }}]{% endcapture %}{{ outer }}",
        "[nested]",
        "Nested capture blocks"
    )
    
    # Capture block in conditional with function call
    test_case(
        "{% def format_num n %}Number: {{ n }}{% enddef %}{% if True %}{% capture formatted %}{{ format_num(42) }}{% endcapture %}{% endif %}{{ formatted }}",
        "Number: 42",
        "Capture with function call in conditional"
    )

def test_variable_scoping_complex():
    """Test complex variable scoping scenarios"""
    print("\nTesting complex variable scoping...")
    print("=" * 60)
    
    # Variable shadowing in nested loops
    test_case(
        "{% for i in range(2) %}outer:{{ i }}{% for i in range(1) %}inner:{{ i }}{% endfor %}after:{{ i }}{% endfor %}",
        "outer:0inner:0after:0outer:1inner:0after:1",
        "Variable shadowing in nested loops"
    )
    
    # Variable persistence across blocks
    test_case(
        "{% for i in range(1) %}{% capture saved %}{{ i }}{% endcapture %}{% endfor %}{{ saved }}",
        "0",
        "Variable persistence from loop to capture"
    )
    
    # Complex scoping with functions
    test_case(
        "{% def test x %}{% for i in range(x) %}{{ i }}{% endfor %}{% enddef %}{% for j in range(2) %}{{ test(j + 1) }}{% endfor %}",
        "101",
        "Function calls with loop variables"
    )

def test_error_conditions_complex():
    """Test error conditions in complex nesting"""
    print("\nTesting error conditions in complex scenarios...")
    print("=" * 60)
    
    # These should work (not error)
    test_case(
        "{% for i in range(1) %}{% if True %}{% capture temp %}ok{% endcapture %}{% endif %}{% endfor %}{{ temp }}",
        "ok",
        "Complex nesting should work correctly"
    )
    
    test_case(
        "{% if True %}{% for i in range(1) %}{% def test %}works{% enddef %}{% endfor %}{% endif %}{{ test() }}",
        "works",
        "Function definition in nested blocks"
    )

def test_mixed_content_nesting():
    """Test nesting with mixed content types"""
    print("\nTesting mixed content nesting...")
    print("=" * 60)
    
    # Text, code, and blocks mixed in nesting
    test_case(
        "Start{% if True %} middle {{ 'code' }} {% for i in range(1) %}loop{{ i }}{% endfor %}{% endif %} end",
        "Start middle code loop0 end",
        "Mixed text, code, and blocks in nesting"
    )
    
    # Comments in nested structures
    test_case(
        "{% if True %}{# comment #}{% for i in range(2) %}{# another comment #}{{ i }}{% endfor %}{% endif %}",
        "01",
        "Comments in nested structures"
    )
    
    # Complex template with all features
    test_case(
        "{% def process items %}{% for item in items %}{% if item > 5 %}big:{{ item }}{% else %}small:{{ item }}{% endif %}{% endfor %}{% enddef %}{% capture numbers %}[1, 6, 3, 8]{% endcapture %}Result: {{ process(eval(numbers)) }}",
        "Result: small:1big:6small:3big:8",
        "Complex template with all features combined"
    )

def main():
    """Run all complex nesting tests"""
    print("🧪 Complex Nesting Test Suite")
    print("=" * 60)
    
    test_nested_conditionals_in_loops()
    test_loops_in_conditionals()
    test_deeply_nested_structures()
    test_complex_loop_combinations()
    test_function_definitions_in_blocks()
    test_capture_blocks_complex()
    test_variable_scoping_complex()
    test_error_conditions_complex()
    test_mixed_content_nesting()
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All complex nesting tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 