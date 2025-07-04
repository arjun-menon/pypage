#!/usr/bin/env python3

import sys
target_dir = "target/debug"
if target_dir not in sys.path:
    sys.path.insert(0, target_dir)

import pypage

# Test the simplest possible conditional
test_cases = [
    "{% if True %}YES{% endif %}",
    "{% if False %}NO{% endif %}",
    "{{ True }}",
    "{{ False }}",
    "{% comment %}This is ignored{% endcomment %}AFTER",
    "BEFORE{# This is ignored #}AFTER",
    "{% if True %}TRUE{% else %}FALSE{% endif %}",
    "{% if False %}TRUE{% else %}FALSE{% endif %}",
]

for i, test in enumerate(test_cases):
    print(f"Test {i+1}: '{test}'")
    try:
        result = pypage.pypage_process(test, None)
        print(f"Result: '{result}'")
    except Exception as e:
        print(f"Error: {e}")
    print() 