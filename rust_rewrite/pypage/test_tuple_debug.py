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
    
    # Comprehensive tuple unpacking tests
    tests = [
        # Basic tuple unpacking
        ("Simple tuple unpacking", "{% for a, b in [(1, 2), (3, 4)] %}{{ a }}-{{ b }} {% endfor %}", "1-2 3-4 "),
        ("Tuple with strings", "{% for name, age in [('Alice', 25), ('Bob', 30)] %}{{ name }}:{{ age }} {% endfor %}", "Alice:25 Bob:30 "),
        ("Mixed types", "{% for num, text in [(1, 'one'), (2, 'two')] %}{{ num }}={{ text }} {% endfor %}", "1=one 2=two "),
        
        # Triple unpacking
        ("Triple unpacking", "{% for a, b, c in [(1, 2, 3), (4, 5, 6)] %}{{ a }}-{{ b }}-{{ c }} {% endfor %}", "1-2-3 4-5-6 "),
        ("Triple with mixed types", "{% for x, y, z in [(1, 'a', True), (2, 'b', False)] %}{{ x }}{{ y }}{{ z }} {% endfor %}", "1aTrue 2bFalse "),
        
        # Quadruple and higher unpacking
        ("Quadruple unpacking", "{% for a, b, c, d in [(1, 2, 3, 4), (5, 6, 7, 8)] %}{{ a }}{{ b }}{{ c }}{{ d }} {% endfor %}", "1234 5678 "),
        ("Five element unpacking", "{% for a, b, c, d, e in [(1, 2, 3, 4, 5)] %}{{ a }}{{ b }}{{ c }}{{ d }}{{ e }}{% endfor %}", "12345"),
        
        # Edge cases with different data structures
        ("List of tuples", "{% for x, y in [(1, 10), (2, 20), (3, 30)] %}{{ x }}*{{ y }}={{ x*y }} {% endfor %}", "1*10=10 2*20=40 3*30=90 "),
        ("Nested tuples", "{% for a, b in [((1, 2), (3, 4)), ((5, 6), (7, 8))] %}{{ a }}+{{ b }} {% endfor %}", "(1, 2)+(3, 4) (5, 6)+(7, 8) "),
        
        # Using zip function
        ("Zip two lists", "{% for a, b in zip([1, 2, 3], ['a', 'b', 'c']) %}{{ a }}{{ b }} {% endfor %}", "1a 2b 3c "),
        ("Zip three lists", "{% for a, b, c in zip([1, 2], ['x', 'y'], [True, False]) %}{{ a }}{{ b }}{{ c }} {% endfor %}", "1xTrue 2yFalse "),
        ("Zip with range", "{% for i, letter in zip(range(3), ['a', 'b', 'c']) %}{{ i }}:{{ letter }} {% endfor %}", "0:a 1:b 2:c "),
        
        # Using enumerate
        ("Enumerate list", "{% for i, item in enumerate(['apple', 'banana', 'cherry']) %}{{ i }}.{{ item }} {% endfor %}", "0.apple 1.banana 2.cherry "),
        ("Enumerate with start", "{% for i, item in enumerate(['x', 'y', 'z'], 1) %}{{ i }}.{{ item }} {% endfor %}", "1.x 2.y 3.z "),
        
        # Dictionary items
        ("Dict items", "{% for key, value in {'a': 1, 'b': 2}.items() %}{{ key }}={{ value }} {% endfor %}", "a=1 b=2 "),
        ("Dict items complex", "{% for name, info in {'Alice': {'age': 25}, 'Bob': {'age': 30}}.items() %}{{ name }}:{{ info['age'] }} {% endfor %}", "Alice:25 Bob:30 "),
        
        # Complex expressions in unpacking
        ("Math in unpacking", "{% for x, y in [(1, 2), (3, 4)] %}{{ x + y }} {% endfor %}", "3 7 "),
        ("String operations", "{% for first, last in [('John', 'Doe'), ('Jane', 'Smith')] %}{{ first + ' ' + last }} {% endfor %}", "John Doe Jane Smith "),
        
        # Nested loops with unpacking
        ("Nested loop unpacking", "{% for i in range(2) %}{% for a, b in [(1, 2), (3, 4)] %}{{ i }}{{ a }}{{ b }} {% endfor %}{% endfor %}", "012 034 112 134 "),
        
        # Error handling and edge cases
        ("Empty tuple list", "{% for a, b in [] %}{{ a }}{{ b }}{% endfor %}", ""),
        ("Single element list", "{% for a, b in [(1, 2)] %}{{ a }}{{ b }}{% endfor %}", "12"),
        
        # Using list comprehensions
        ("List comprehension tuples", "{% for x, y in [(i, i*2) for i in range(3)] %}{{ x }}-{{ y }} {% endfor %}", "0-0 1-2 2-4 "),
        
        # Complex data structures
        ("Complex nested data", "{% for name, data in [('person1', {'age': 25, 'city': 'NYC'}), ('person2', {'age': 30, 'city': 'LA'})] %}{{ name }} is {{ data['age'] }} from {{ data['city'] }} {% endfor %}", "person1 is 25 from NYC person2 is 30 from LA "),
        
        # Real-world like scenarios  
        ("CSV-like data", "{% for name, age, city in [('Alice', 25, 'NYC'), ('Bob', 30, 'LA'), ('Charlie', 35, 'Chicago')] %}{{ name }} ({{ age }}) - {{ city }}{% endfor %}", "Alice (25) - NYCBob (30) - LACharlie (35) - Chicago"),
        ("Coordinate pairs", "{% for x, y in [(0, 0), (1, 1), (2, 4), (3, 9)] %}({{ x }}, {{ y }}) {% endfor %}", "(0, 0) (1, 1) (2, 4) (3, 9) "),
        
        # Using built-in functions
        ("Max/min pairs", "{% for a, b in [(1, 5), (3, 2), (8, 4)] %}max={{ max(a, b) }} min={{ min(a, b) }} {% endfor %}", "max=5 min=1 max=3 min=2 max=8 min=4 "),
        
        # String and number combinations
        ("String number pairs", "{% for letter, num in zip('abc', [1, 2, 3]) %}{{ letter }}{{ num }} {% endfor %}", "a1 b2 c3 "),
        
        # Boolean combinations
        ("Boolean pairs", "{% for a, b in [(True, False), (False, True), (True, True)] %}{{ a and b }} {% endfor %}", "False False True "),
        
        # List of lists (not tuples)
        ("List of lists", "{% for a, b in [[1, 2], [3, 4], [5, 6]] %}{{ a }}+{{ b }}={{ a+b }} {% endfor %}", "1+2=3 3+4=7 5+6=11 "),
        
        # Using itertools-like patterns
        ("Pairwise iteration", "{% for a, b in zip([1, 2, 3, 4], [2, 3, 4, 5]) %}{{ a }}-{{ b }} {% endfor %}", "1-2 2-3 3-4 4-5 "),
    ]
    
    print(f"Running {len(tests)} tuple unpacking tests...")
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
        print("🎉 All tuple unpacking tests passed!")
        return True
    else:
        print(f"❌ {total - passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 