#!/usr/bin/env python3

import sys
target_dir = "target/debug"
if target_dir not in sys.path:
    sys.path.insert(0, target_dir)

import pypage

# Test for loops
test_cases = [
    # Simple for loop
    ("Simple for loop", "{% for i in range(3) %}{{ i }}{% endfor %}", None),
    
    # For loop with multiple variables  
    ("For loop with tuples", "{% for i, j in [(1, 'a'), (2, 'b')] %}{{ i }}:{{ j }} {% endfor %}", None),
    
    # For loop with list
    ("For loop with list", "{% for item in ['apple', 'banana', 'cherry'] %}{{ item }} {% endfor %}", None),
    
    # Simple while loop (should not execute)
    ("While false", "{% while False %}This should not show{% endwhile %}", None),
    
    # While loop with counter (will be infinite, but time limit will stop it)
    ("While with counter", "{% while int(counter) < 3 %}{{ counter }}{% endwhile %}", {"counter": "0"}),
    
    # Dofirst while loop
    ("Dofirst while", "{% while dofirst False %}Executed once{% endwhile %}", None),
    
    # Function definition
    ("Function definition", "{% def greet name %}Hello {{ name }}!{% enddef %}", None),
    
    # Function definition with multiple arguments
    ("Function with args", "{% def add a b %}{{ a + b }}{% enddef %}", None),
]

print("Testing loops and functions:")
print("=" * 60)

for i, (description, test, env) in enumerate(test_cases):
    print(f"Test {i+1}: {description}")
    print(f"Template: '{test}'")
    try:
        result = pypage.pypage_process(test, env)
        print(f"Result: '{result}'")
    except Exception as e:
        print(f"Error: {e}")
    print()
