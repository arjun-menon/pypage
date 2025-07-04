#!/usr/bin/env python3

import sys
target_dir = "target/debug"
if target_dir not in sys.path:
    sys.path.insert(0, target_dir)

import pypage

def test_case(name, template, env=None, expected=None):
    """Test a single case and report results"""
    print(f"Testing: {name}")
    print(f"Template: {repr(template)}")
    try:
        result = pypage.pypage_process(template, env)
        print(f"Result: {repr(result)}")
        if expected is not None:
            if result == expected:
                print("✅ PASS")
            else:
                print(f"❌ FAIL - Expected: {repr(expected)}")
        print()
        return result
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print()
        return None

print("Advanced Comprehensive Tests for PyPage Rust Implementation")
print("=" * 60)

# Test 1: Complex nested for loops (multiple variables)
test_case(
    "Nested for loops with multiple variables",
    "{% for x in [1,2] for y in ['a','b'] %}{{ x }}{{ y }} {% endfor %}",
    None,
    "1a 1b 2a 2b "
)

# Test 2: For loop with filtering (using generator expression features)
test_case(
    "For loop with list comprehension style",
    "{% for x in [1,2,3,4,5] %}{% if x % 2 == 0 %}{{ x }} {% endif %}{% endfor %}",
    None,
    "2 4 "
)

# Test 3: Complex conditional chain with environment variable
test_case(
    "Complex if-elif-elif-else chain",
    "{% if int(grade) >= 90 %}A{% elif int(grade) >= 80 %}B{% elif int(grade) >= 70 %}C{% else %}F{% endif %}",
    {"grade": "85"},
    "B"
)

# Test 4: While loop with dofirst
test_case(
    "While dofirst loop",
    "{% while dofirst False %}Executed{% endwhile %} Done",
    None,
    "Executed Done"
)

# Test 5: Nested block structures
test_case(
    "Nested blocks (for inside if)",
    "{% if True %}{% for i in range(3) %}{{ i }}{% endfor %}{% endif %}",
    None,
    "012"
)

# Test 6: Function definition with arguments
test_case(
    "Function definition",
    "{% def greet name %}Hello {{ name }}!{% enddef %}Function defined",
    None,
    "Function defined"
)

# Test 7: Variable scoping with for loops (environment variable)
test_case(
    "Variable scoping in for loops",
    "Before: {{ x }} {% for x in ['loop'] %}Loop: {{ x }} {% endfor %}After: {{ x }}",
    {"x": "global"},
    "Before: global Loop: loop After: global"
)

# Test 8: Complex expression evaluation
test_case(
    "Complex expressions",
    "{{ [x*2 for x in range(3)] }}",
    None,
    "[0, 2, 4]"
)

# Test 9: Multiple variables in for loop (tuple unpacking)
test_case(
    "Tuple unpacking in for loops",
    "{% for name, age in [('Alice', 25), ('Bob', 30)] %}{{ name }} is {{ age }} years old. {% endfor %}",
    None,
    "Alice is 25 years old. Bob is 30 years old. "
)

# Test 10: Nested conditionals
test_case(
    "Nested if statements",
    "{% if True %}Outer{% if True %} Inner{% endif %} End{% endif %}",
    None,
    "Outer Inner End"
)

# Test 11: Complex while loop with counter (will timeout due to implementation)
test_case(
    "While loop with manual counter",
    "{% while int(count) < 3 %}{{ count }}{% endwhile %}",
    {"count": "0"},
    # This will timeout due to the 2-second limit since count doesn't get updated
    None
)

# Test 12: Multiple data types in for loop
test_case(
    "Mixed data types in for loop",
    "{% for item in [1, 'hello', 3.14, True] %}{{ item }} {% endfor %}",
    None,
    "1 hello 3.14 True "
)

# Test 13: Function with multiple arguments
test_case(
    "Function with multiple arguments",
    "{% def add a b c %}{{ a + b + c }}{% enddef %}Function created",
    None,
    "Function created"
)

# Test 14: Comment block functionality
test_case(
    "Comment block",
    "Before{% comment %}This is ignored{% endcomment %}After",
    None,
    "BeforeAfter"
)

# Test 15: Complex template with multiple features
complex_template = """{# This is a comment #}
{% for num in numbers %}
  {% if num % 2 == 0 %}
    <div>{{ num }} is even</div>
  {% else %}
    <div>{{ num }} is odd</div>
  {% endif %}
{% endfor %}"""

test_case(
    "Complex template with numbers",
    complex_template,
    {"numbers": [1, 2, 3, 4, 5]},
    None  # Complex expected result, just check it runs
)

# Test 16: Error handling - invalid syntax
test_case(
    "Error handling - unclosed tag",
    "{% if True %}Never closed",
    None,
    None  # Should error
)

# Test 17: Empty for loop
test_case(
    "Empty for loop",
    "Before{% for x in [] %}{{ x }}{% endfor %}After",
    None,
    "BeforeAfter"
)

# Test 18: While loop with environment variable
test_case(
    "While loop with environment variable",
    "{% while count_down == '3' %}Count: {{ count_down }}{% endwhile %}",
    {"count_down": "3"},
    None  # Will likely timeout since condition stays true
)

# Test 19: Nested for loops with different variables
test_case(
    "Independent nested for loops",
    "{% for i in range(2) %}Row {{ i }}: {% for j in range(3) %}{{ j }} {% endfor %}{% endfor %}",
    None,
    "Row 0: 0 1 2 Row 1: 0 1 2 "
)

# Test 20: Complex expression with conditionals
test_case(
    "Conditional expressions",
    "{{ 'Even' if 4 % 2 == 0 else 'Odd' }}",
    None,
    "Even"
)

print("Advanced tests completed!")
print("Note: Some tests may timeout or error due to current implementation limitations.") 