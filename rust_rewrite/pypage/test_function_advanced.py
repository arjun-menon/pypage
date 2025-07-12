#!/usr/bin/env python3
"""
Advanced Function Usage Test Suite - Tests complex function scenarios and edge cases.
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

def test_function_with_multiple_arguments():
    """Test functions with multiple arguments"""
    print("\nTesting functions with multiple arguments...")
    print("=" * 60)
    
    # Function with 2 arguments
    test_case(
        "{% def add x y %}{{ x + y }}{% enddef %}{{ add(3, 5) }}",
        "8",
        "Function with 2 arguments"
    )
    
    # Function with 3 arguments
    test_case(
        "{% def triple_sum a b c %}{{ a + b + c }}{% enddef %}{{ triple_sum(1, 2, 3) }}",
        "6",
        "Function with 3 arguments"
    )
    
    # Function with 5 arguments
    test_case(
        "{% def five_args a b c d e %}{{ a }}-{{ b }}-{{ c }}-{{ d }}-{{ e }}{% enddef %}{{ five_args(1, 2, 3, 4, 5) }}",
        "1-2-3-4-5",
        "Function with 5 arguments"
    )
    
    # Function with string arguments
    test_case(
        "{% def greet first last %}Hello {{ first }} {{ last }}!{% enddef %}{{ greet('John', 'Doe') }}",
        "Hello John Doe!",
        "Function with string arguments"
    )

def test_function_complex_bodies():
    """Test functions with complex bodies"""
    print("\nTesting functions with complex bodies...")
    print("=" * 60)
    
    # Function with conditional
    test_case(
        "{% def describe n %}{% if n > 0 %}positive{% elif n < 0 %}negative{% else %}zero{% endif %}{% enddef %}{{ describe(-5) }}",
        "negative",
        "Function with conditional logic"
    )
    
    # Function with loop
    test_case(
        "{% def repeat text n %}{% for i in range(n) %}{{ text }}{% endfor %}{% enddef %}{{ repeat('hi', 3) }}",
        "hihihi",
        "Function with loop"
    )
    
    # Function with nested conditionals and loops
    test_case(
        "{% def complex n %}{% for i in range(n) %}{% if i % 2 == 0 %}even{% else %}odd{% endif %}{% endfor %}{% enddef %}{{ complex(4) }}",
        "evenoddeenodd",
        "Function with nested conditionals and loops"
    )
    
    # Function with capture block
    test_case(
        "{% def build_list items %}{% capture result %}{% for item in items %}[{{ item }}]{% endfor %}{% endcapture %}{{ result }}{% enddef %}{{ build_list([1, 2, 3]) }}",
        "[1][2][3]",
        "Function with capture block"
    )

def test_function_scoping():
    """Test function variable scoping"""
    print("\nTesting function variable scoping...")
    print("=" * 60)
    
    # Function arguments don't leak
    test_case(
        "{% def test x %}{{ x * 2 }}{% enddef %}{{ test(5) }}{% if exists('x') %}leaked{% else %}clean{% endif %}",
        "10clean",
        "Function arguments don't leak to global scope"
    )
    
    # Function can access global variables
    test_case(
        "{% capture global_var %}42{% endcapture %}{% def use_global %}{{ global_var }}{% enddef %}{{ use_global() }}",
        "42",
        "Function can access global variables"
    )
    
    # Function argument shadows global
    test_case(
        "{% capture x %}global{% endcapture %}{% def shadow x %}local:{{ x }}{% enddef %}{{ shadow('arg') }} global:{{ x }}",
        "local:arg global:global",
        "Function argument shadows global variable"
    )
    
    # Multiple functions with same argument names
    test_case(
        "{% def func1 x %}f1:{{ x }}{% enddef %}{% def func2 x %}f2:{{ x }}{% enddef %}{{ func1('a') }}{{ func2('b') }}",
        "f1:af2:b",
        "Multiple functions with same argument names"
    )

def test_function_calling_functions():
    """Test functions calling other functions"""
    print("\nTesting functions calling other functions...")
    print("=" * 60)
    
    # Simple function calling another
    test_case(
        "{% def double x %}{{ x * 2 }}{% enddef %}{% def quad x %}{{ double(double(x)) }}{% enddef %}{{ quad(3) }}",
        "12",
        "Function calling another function"
    )
    
    # Chain of function calls
    test_case(
        "{% def add1 x %}{{ x + 1 }}{% enddef %}{% def add2 x %}{{ add1(add1(x)) }}{% enddef %}{% def add4 x %}{{ add2(add2(x)) }}{% enddef %}{{ add4(5) }}",
        "9",
        "Chain of function calls"
    )
    
    # Function calling multiple other functions
    test_case(
        "{% def add x y %}{{ x + y }}{% enddef %}{% def mul x y %}{{ x * y }}{% enddef %}{% def complex a b %}{{ add(mul(a, 2), mul(b, 3)) }}{% enddef %}{{ complex(4, 5) }}",
        "23",
        "Function calling multiple other functions"
    )
    
    # Recursive-like behavior (with limits)
    test_case(
        "{% def countdown n %}{% if n > 0 %}{{ n }}{% if n > 1 %}-{{ countdown(n - 1) }}{% endif %}{% endif %}{% enddef %}{{ countdown(3) }}",
        "3-2-1",
        "Recursive-like function calls"
    )

def test_function_with_complex_arguments():
    """Test functions with complex argument expressions"""
    print("\nTesting functions with complex arguments...")
    print("=" * 60)
    
    # Function called with expressions
    test_case(
        "{% def show x %}[{{ x }}]{% enddef %}{{ show(3 + 4) }}",
        "[7]",
        "Function called with expression argument"
    )
    
    # Function called with function result
    test_case(
        "{% def double x %}{{ x * 2 }}{% enddef %}{% def show x %}[{{ x }}]{% enddef %}{{ show(double(5)) }}",
        "[10]",
        "Function called with function result"
    )
    
    # Function with list arguments
    test_case(
        "{% def sum_list items %}{{ sum(items) }}{% enddef %}{{ sum_list([1, 2, 3, 4]) }}",
        "10",
        "Function with list argument"
    )
    
    # Function with string operations
    test_case(
        "{% def process text %}{{ text.upper() }}{% enddef %}{{ process('hello world') }}",
        "HELLO WORLD",
        "Function with string method calls"
    )

def test_function_edge_cases():
    """Test function edge cases and error conditions"""
    print("\nTesting function edge cases...")
    print("=" * 60)
    
    # Function with no arguments
    test_case(
        "{% def no_args %}constant{% enddef %}{{ no_args() }}",
        "constant",
        "Function with no arguments"
    )
    
    # Function that returns empty string
    test_case(
        "{% def empty %}{% enddef %}[{{ empty() }}]",
        "[]",
        "Function that returns empty string"
    )
    
    # Function with whitespace-only body
    test_case(
        "{% def whitespace %}   {% enddef %}[{{ whitespace() }}]",
        "[   ]",
        "Function with whitespace-only body"
    )
    
    # Function redefinition (last one wins)
    test_case(
        "{% def test %}first{% enddef %}{% def test %}second{% enddef %}{{ test() }}",
        "second",
        "Function redefinition"
    )

def test_function_in_complex_expressions():
    """Test functions used in complex expressions"""
    print("\nTesting functions in complex expressions...")
    print("=" * 60)
    
    # Function result in arithmetic
    test_case(
        "{% def get_num %}5{% enddef %}{{ get_num() + 3 }}",
        "8",
        "Function result in arithmetic"
    )
    
    # Function result in comparison
    test_case(
        "{% def get_val %}10{% enddef %}{% if get_val() > 5 %}big{% else %}small{% endif %}",
        "big",
        "Function result in comparison"
    )
    
    # Function result in string operations
    test_case(
        "{% def get_name %}World{% enddef %}{{ 'Hello ' + get_name() + '!' }}",
        "Hello World!",
        "Function result in string operations"
    )
    
    # Multiple function calls in expression
    test_case(
        "{% def x %}3{% enddef %}{% def y %}4{% enddef %}{{ x() * x() + y() * y() }}",
        "25",
        "Multiple function calls in expression"
    )

def test_function_with_loops_and_conditionals():
    """Test functions that contain loops and conditionals"""
    print("\nTesting functions with loops and conditionals...")
    print("=" * 60)
    
    # Function with for loop and conditional
    test_case(
        "{% def filter_odds nums %}{% for n in nums %}{% if n % 2 == 1 %}{{ n }}{% endif %}{% endfor %}{% enddef %}{{ filter_odds([1, 2, 3, 4, 5]) }}",
        "135",
        "Function with for loop and conditional"
    )
    
    # Function with while loop
    test_case(
        "{% def count_down start %}{% capture n %}{{ start }}{% endcapture %}{% while int(n) > 0 %}{{ n }}{% capture n %}{{ int(n) - 1 }}{% endcapture %}{% endwhile %}{% enddef %}{{ count_down(3) }}",
        "321",
        "Function with while loop"
    )
    
    # Function with nested loops
    test_case(
        "{% def matrix rows cols %}{% for i in range(rows) %}{% for j in range(cols) %}{{ i }}{{ j }}{% endfor %}|{% endfor %}{% enddef %}{{ matrix(2, 2) }}",
        "0001|1011|",
        "Function with nested loops"
    )
    
    # Function with complex control flow
    test_case(
        "{% def process_list items %}{% for item in items %}{% if item < 0 %}neg{% elif item == 0 %}zero{% else %}pos{% endif %}{% endfor %}{% enddef %}{{ process_list([-1, 0, 1]) }}",
        "negzeropos",
        "Function with complex control flow"
    )

def test_function_variable_capture():
    """Test functions that interact with capture blocks"""
    print("\nTesting functions with capture blocks...")
    print("=" * 60)
    
    # Function that uses capture internally
    test_case(
        "{% def accumulate items %}{% capture result %}{% for item in items %}{{ item }}{% endfor %}{% endcapture %}{{ result }}{% enddef %}{{ accumulate(['a', 'b', 'c']) }}",
        "abc",
        "Function using capture internally"
    )
    
    # Function result captured
    test_case(
        "{% def get_data %}important{% enddef %}{% capture saved %}{{ get_data() }}{% endcapture %}{{ saved }}",
        "important",
        "Function result captured"
    )
    
    # Function modifying global via capture
    test_case(
        "{% def set_global val %}{% capture global_state %}{{ val }}{% endcapture %}{% enddef %}{{ set_global('test') }}{{ global_state }}",
        "test",
        "Function modifying global via capture"
    )

def main():
    """Run all advanced function tests"""
    print("🧪 Advanced Function Usage Test Suite")
    print("=" * 60)
    
    test_function_with_multiple_arguments()
    test_function_complex_bodies()
    test_function_scoping()
    test_function_calling_functions()
    test_function_with_complex_arguments()
    test_function_edge_cases()
    test_function_in_complex_expressions()
    test_function_with_loops_and_conditionals()
    test_function_variable_capture()
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All advanced function tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 