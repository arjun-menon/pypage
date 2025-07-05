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

def run_test(name, template, expected, env=None, should_error=False):
    """Run a single test"""
    try:
        import pypage
        result = pypage.pypage_process(template, env)
        if should_error:
            print(f"❌ {name} - Expected error but got: {repr(result)}")
            return False
        elif result == expected:
            print(f"✅ {name}")
            return True
        else:
            print(f"❌ {name}")
            print(f"   Expected: {repr(expected)}")
            print(f"   Got:      {repr(result)}")
            return False
    except Exception as e:
        if should_error:
            print(f"✅ {name} - Expected error: {e}")
            return True
        else:
            print(f"❌ {name} - Unexpected exception: {e}")
            return False

def main():
    if not build_and_test():
        sys.exit(1)
    
    # Test results
    passed = 0
    total = 0
    
    # Error handling and edge case tests
    tests = [
        # Edge cases that should work
        ("Empty template", "", ""),
        ("Only whitespace", "   ", "   "),
        ("Only newlines", "\n\n\n", "\n\n\n"),
        ("Empty expression", "{{ }}", "", None, True),  # Should error
        ("Empty block", "{% %}", "", None, True),  # Should error
        ("Empty comment", "{# #}", ""),
        
        # Boundary cases
        ("Single character", "a", "a"),
        ("Single expression", "{{ 1 }}", "1"),
        ("Single comment", "{# x #}", ""),
        
        # Unicode and special characters
        ("Unicode text", "Hello 世界", "Hello 世界"),
        ("Unicode in expression", "{{ 'Hello 世界' }}", "Hello 世界"),
        ("Special characters", "!@#$%^&*()_+-=[]{}|;':\",./<>?", "!@#$%^&*()_+-=[]{}|;':\",./<>?"),
        
        # Large content
        ("Large text", "x" * 1000, "x" * 1000),
        ("Large expression", "{{ 'x' * 100 }}", "x" * 100),
        
        # Nested delimiters (should be handled gracefully)
        ("Text with delimiters", "Use {{ and }} for code", "Use {{ and }} for code"),
        ("Escaped delimiters", "Use \\{{ and \\}} for literal", "Use \\{{ and \\}} for literal"),
        
        # Variable edge cases
        ("Undefined variable", "{{ undefined_var }}", "", None, True),  # Should error
        ("None variable", "{{ none_var }}", "", {"none_var": None}),
        ("Empty string variable", "{{ empty_str }}", "", {"empty_str": ""}),
        ("Zero value", "{{ zero }}", "0", {"zero": 0}),
        ("False value", "{{ false_val }}", "False", {"false_val": False}),
        ("Empty list", "{{ empty_list }}", "[]", {"empty_list": []}),
        ("Empty dict", "{{ empty_dict }}", "{}", {"empty_dict": {}}),
        
        # Expression edge cases
        ("Division by zero protection", "{{ 1 if True else 1/0 }}", "1"),
        ("Short circuit AND", "{{ False and undefined_var }}", "False"),
        ("Short circuit OR", "{{ True or undefined_var }}", "True"),
        
        # For loop edge cases
        ("Empty for loop", "{% for i in [] %}{{ i }}{% endfor %}", ""),
        ("Single item for loop", "{% for i in [1] %}{{ i }}{% endfor %}", "1"),
        ("For loop with None", "{% for i in items %}{{ i }}{% endfor %}", "", {"items": None}, True),  # Should error
        
        # While loop edge cases
        ("While loop false condition", "{% while False %}{{ 'never' }}{% endwhile %}", ""),
        ("While loop with counter", "{% while x < 1 %}{{ x }}{% endwhile %}", "0", {"x": 0}),
        
        # Conditional edge cases
        ("If with None", "{% if none_val %}YES{% else %}NO{% endif %}", "NO", {"none_val": None}),
        ("If with empty string", "{% if empty_str %}YES{% else %}NO{% endif %}", "NO", {"empty_str": ""}),
        ("If with zero", "{% if zero %}YES{% else %}NO{% endif %}", "NO", {"zero": 0}),
        ("If with empty list", "{% if empty_list %}YES{% else %}NO{% endif %}", "NO", {"empty_list": []}),
        
        # Capture edge cases
        ("Capture empty", "{% capture empty %}{% endcapture %}{{ empty }}", ""),
        ("Capture whitespace", "{% capture ws %}   {% endcapture %}{{ ws }}", "   "),
        
        # Comment edge cases
        ("Comment with delimiters", "{# This has {{ and }} in it #}", ""),
        ("Comment with quotes", "{# This has 'quotes' and \"quotes\" #}", ""),
        ("Comment with newlines", "{# Line 1\nLine 2\nLine 3 #}", ""),
        
        # Mixed content edge cases
        ("Mixed empty blocks", "{% if True %}{% for i in [] %}{{ i }}{% endfor %}{% endif %}", ""),
        ("Mixed with comments", "A{# comment #}B{% if True %}C{% endif %}D", "ABCD"),
        
        # Error recovery tests
        ("Malformed expression recovery", "Before {{ 2 + 2 }} After", "Before 4 After"),
        ("Mixed valid/invalid", "{{ 1 + 1 }}{{ 2 + 2 }}", "24"),
        
        # Function definition edge cases
        ("Function with no args", "{% def greet %}Hello{% enddef %}", ""),
        ("Function with many args", "{% def func a b c d e f %}{{ a + b + c + d + e + f }}{% enddef %}", ""),
        
        # Complex nesting edge cases
        ("Deeply nested empty", "{% if True %}{% if True %}{% if True %}{% endif %}{% endif %}{% endif %}", ""),
        ("Alternating structures", "{% if True %}{% for i in [1] %}{% if i == 1 %}YES{% endif %}{% endfor %}{% endif %}", "YES"),
        
        # String handling edge cases
        ("String with quotes", "{{ \"It's a 'test'\" }}", "It's a 'test'"),
        ("String with backslashes", "{{ 'C:\\\\Users\\\\test' }}", "C:\\Users\\test"),
        ("Multiline string", "{{ '''Line 1\nLine 2''' }}", "Line 1\nLine 2"),
        
        # Arithmetic edge cases
        ("Large numbers", "{{ 999999999999999999999 }}", "999999999999999999999"),
        ("Float precision", "{{ 1.0 / 3.0 }}", "0.3333333333333333"),
        ("Negative numbers", "{{ -42 }}", "-42"),
        
        # Boolean edge cases
        ("Complex boolean", "{{ True and (False or True) }}", "True"),
        ("Boolean with variables", "{{ x and y or z }}", "True", {"x": False, "y": True, "z": True}),
        
        # List/Dict edge cases
        ("List with mixed types", "{{ [1, 'two', 3.0, True] }}", "[1, 'two', 3.0, True]"),
        ("Dict with mixed types", "{{ {'int': 1, 'str': 'two', 'float': 3.0} }}", "{'int': 1, 'str': 'two', 'float': 3.0}"),
        
        # Method call edge cases
        ("Method on empty string", "{{ ''.upper() }}", ""),
        ("Method chaining", "{{ 'hello world'.title().replace(' ', '_') }}", "Hello_World"),
        
        # Tuple unpacking edge cases
        ("Tuple unpacking single", "{% for a, in [(1,), (2,)] %}{{ a }}{% endfor %}", "12"),
        ("Tuple unpacking mismatch", "{% for a, b in [(1,)] %}{{ a }}{{ b }}{% endfor %}", "", None, True),  # Should error
        
        # Environment edge cases
        ("Environment with spaces", "{{ var_with_spaces }}", "value with spaces", {"var_with_spaces": "value with spaces"}),
        ("Environment with unicode", "{{ unicode_var }}", "🌟", {"unicode_var": "🌟"}),
        
        # Whitespace handling
        ("Leading whitespace", "   {{ 'test' }}", "   test"),
        ("Trailing whitespace", "{{ 'test' }}   ", "test   "),
        ("Mixed whitespace", "  {{ 'a' }}  {{ 'b' }}  ", "  a  b  "),
        
        # Performance edge cases
        ("Many small expressions", "".join(f"{{{{ {i} }}}}" for i in range(10)), "0123456789"),
        ("Nested loop performance", "{% for i in range(5) %}{% for j in range(5) %}{{ i }}{{ j }}{% endfor %}{% endfor %}", "".join(f"{i}{j}" for i in range(5) for j in range(5))),
        
        # Error boundary tests
        ("Recover from error", "Before{% if undefined %}ERROR{% endif %}After", "BeforeAfter", None, True),
        ("Multiple errors", "{{ undefined1 }}{{ undefined2 }}", "", None, True),
        
        # Memory usage edge cases
        ("Large string generation", "{{ 'x' * 1000 }}", "x" * 1000),
        ("Large iteration", "{% for i in range(100) %}{% if i == 99 %}DONE{% endif %}{% endfor %}", "DONE"),
    ]
    
    print(f"Running {len(tests)} error handling and edge case tests...")
    print("=" * 60)
    
    for test_data in tests:
        if len(test_data) == 3:
            name, template, expected = test_data
            env = None
            should_error = False
        elif len(test_data) == 4:
            name, template, expected, env = test_data
            should_error = False
        else:
            name, template, expected, env, should_error = test_data
        
        if run_test(name, template, expected, env, should_error):
            passed += 1
        total += 1
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All error handling tests passed!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 