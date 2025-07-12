#!/usr/bin/env python3
"""
Performance & Stress Test Suite - Tests performance with large templates, deep nesting, and edge cases.
"""

import sys
import os
import time

# Import the Rust module directly from the current directory
sys.path.insert(0, os.path.dirname(__file__))
import pypage

# Test counters
passed = 0
total = 0

def test_case(template, expected, description, max_time=5.0):
    """Helper function to run a test case with timing"""
    global passed, total
    total += 1
    
    try:
        start_time = time.time()
        result = pypage.pypage_process(template, {})
        end_time = time.time()
        duration = end_time - start_time
        
        if result == expected:
            time_status = f"({duration:.3f}s)" if duration < max_time else f"(SLOW: {duration:.3f}s)"
            print(f"✅ Test {total:2d}: PASS - {description} {time_status}")
            passed += 1
        else:
            print(f"❌ Test {total:2d}: FAIL - {description} ({duration:.3f}s)")
            print(f"    Expected length: {len(expected)}, Got length: {len(result)}")
            if len(expected) < 200 and len(result) < 200:
                print(f"    Expected: {repr(expected)}")
                print(f"    Got:      {repr(result)}")
    except Exception as e:
        print(f"❌ Test {total:2d}: ERROR - {description}")
        print(f"    Template length: {len(template)}")
        print(f"    Error:    {e}")

def test_large_text_blocks():
    """Test processing large text blocks"""
    print("\nTesting large text blocks...")
    print("=" * 60)
    
    # Large text block (10KB)
    large_text = "This is a test sentence. " * 400  # ~10KB
    test_case(
        large_text,
        large_text,
        "Large text block (10KB)"
    )
    
    # Large text with embedded code
    text_with_code = ("Start " + "text " * 100 + "{{ 'middle' }}" + " more " * 100 + " end")
    expected = "Start " + "text " * 100 + "middle" + " more " * 100 + " end"
    test_case(
        text_with_code,
        expected,
        "Large text with embedded code"
    )
    
    # Multiple large code blocks
    large_code = "{{ 'x' * 1000 }}" * 10
    expected_code = "x" * 10000
    test_case(
        large_code,
        expected_code,
        "Multiple large code blocks"
    )

def test_many_variables():
    """Test templates with many variables"""
    print("\nTesting many variables...")
    print("=" * 60)
    
    # Many variable definitions via capture
    many_vars = ""
    for i in range(100):
        many_vars += "{% capture var" + str(i) + " %}value" + str(i) + "{% endcapture %}"
    
    # Use all variables
    use_vars = ""
    expected = ""
    for i in range(100):
        use_vars += "{{ var" + str(i) + " }}"
        expected += f"value{i}"
    
    template = many_vars + use_vars
    test_case(
        template,
        expected,
        "Template with 100 variables"
    )
    
    # Variables in loops
    loop_vars = "{% for i in range(50) %}{% capture temp %}{{ i }}{% endcapture %}{{ temp }}{% endfor %}"
    expected_loop = "".join(str(i) for i in range(50))
    test_case(
        loop_vars,
        expected_loop,
        "Variables created in loops"
    )

def test_deep_nesting():
    """Test very deep nesting scenarios"""
    print("\nTesting deep nesting...")
    print("=" * 60)
    
    # Deep conditional nesting (50 levels)
    deep_if = "{% if True %}" * 50 + "deep" + "{% endif %}" * 50
    test_case(
        deep_if,
        "deep",
        "Deep conditional nesting (50 levels)"
    )
    
    # Deep loop nesting (10 levels)
    deep_loops = ""
    expected_deep = ""
    for i in range(10):
        deep_loops += "{% for i" + str(i) + " in range(1) %}"
        expected_deep = "X"
    deep_loops += "X"
    for i in range(10):
        deep_loops += "{% endfor %}"
    
    test_case(
        deep_loops,
        expected_deep,
        "Deep loop nesting (10 levels)"
    )
    
    # Mixed deep nesting
    mixed_deep = "{% if True %}" * 20 + "{% for i in range(1) %}" * 10 + "result" + "{% endfor %}" * 10 + "{% endif %}" * 20
    test_case(
        mixed_deep,
        "result",
        "Mixed deep nesting (conditionals + loops)"
    )

def test_large_loops():
    """Test loops with large iteration counts"""
    print("\nTesting large loops...")
    print("=" * 60)
    
    # Large for loop (1000 iterations)
    large_for = "{% for i in range(1000) %}{{ i % 10 }}{% endfor %}"
    expected_for = "".join(str(i % 10) for i in range(1000))
    test_case(
        large_for,
        expected_for,
        "Large for loop (1000 iterations)"
    )
    
    # Nested loops with moderate size
    nested_moderate = "{% for i in range(20) %}{% for j in range(20) %}{{ (i + j) % 10 }}{% endfor %}{% endfor %}"
    expected_nested = ""
    for i in range(20):
        for j in range(20):
            expected_nested += str((i + j) % 10)
    test_case(
        nested_moderate,
        expected_nested,
        "Nested loops (20x20)"
    )
    
    # Large while loop (with safety limit)
    large_while = "{% capture count %}0{% endcapture %}{% while int(count) < 500 %}{{ count }}{% capture count %}{{ int(count) + 1 }}{% endcapture %}{% endwhile %}"
    expected_while = "".join(str(i) for i in range(500))
    test_case(
        large_while,
        expected_while,
        "Large while loop (500 iterations)",
        max_time=10.0
    )

def test_many_function_calls():
    """Test templates with many function calls"""
    print("\nTesting many function calls...")
    print("=" * 60)
    
    # Many function definitions
    many_funcs = ""
    for i in range(50):
        many_funcs += "{% def func" + str(i) + " %}result" + str(i) + "{% enddef %}"
    
    # Call all functions
    call_funcs = ""
    expected_calls = ""
    for i in range(50):
        call_funcs += "{{ func" + str(i) + "() }}"
        expected_calls += f"result{i}"
    
    template = many_funcs + call_funcs
    test_case(
        template,
        expected_calls,
        "Template with 50 functions"
    )
    
    # Recursive-like function calls
    recursive_setup = "{% def countdown n %}{% if n > 0 %}{{ n }}{% if n > 1 %}{{ countdown(n - 1) }}{% endif %}{% endif %}{% enddef %}"
    recursive_call = "{{ countdown(20) }}"
    expected_recursive = "".join(str(i) for i in range(20, 0, -1))
    test_case(
        recursive_setup + recursive_call,
        expected_recursive,
        "Recursive-like function calls (depth 20)"
    )

def test_complex_expressions():
    """Test complex expressions and computations"""
    print("\nTesting complex expressions...")
    print("=" * 60)
    
    # Complex arithmetic
    complex_math = "{{ " + " + ".join(f"({i} * {i})" for i in range(1, 51)) + " }}"
    expected_math = str(sum(i * i for i in range(1, 51)))
    test_case(
        complex_math,
        expected_math,
        "Complex arithmetic expression"
    )
    
    # Large string concatenation
    string_concat = "{{ " + " + ".join(f"'part{i}'" for i in range(100)) + " }}"
    expected_concat = "".join(f"part{i}" for i in range(100))
    test_case(
        string_concat,
        expected_concat,
        "Large string concatenation"
    )
    
    # Complex list operations
    list_ops = "{% capture nums %}[" + ", ".join(str(i) for i in range(100)) + "]{% endcapture %}{{ sum(eval(nums)) }}"
    expected_sum = str(sum(range(100)))
    test_case(
        list_ops,
        expected_sum,
        "Complex list operations"
    )

def test_memory_intensive():
    """Test memory-intensive scenarios"""
    print("\nTesting memory-intensive scenarios...")
    print("=" * 60)
    
    # Large capture blocks
    large_capture = "{% capture big %}{% for i in range(1000) %}{{ 'data' * 10 }}{% endfor %}{% endcapture %}{{ len(big) }}"
    expected_len = str(1000 * 40)  # 1000 iterations * 40 chars each
    test_case(
        large_capture,
        expected_len,
        "Large capture block"
    )
    
    # Many small capture blocks
    many_captures = ""
    use_captures = ""
    expected_many = ""
    for i in range(200):
        many_captures += "{% capture small" + str(i) + " %}data" + str(i) + "{% endcapture %}"
        use_captures += "{{ small" + str(i) + " }}"
        expected_many += f"data{i}"
    
    test_case(
        many_captures + use_captures,
        expected_many,
        "Many small capture blocks (200)"
    )

def test_unicode_performance():
    """Test performance with Unicode content"""
    print("\nTesting Unicode performance...")
    print("=" * 60)
    
    # Large Unicode text
    unicode_text = "Hello 世界! 🌍 " * 1000
    test_case(
        unicode_text,
        unicode_text,
        "Large Unicode text block"
    )
    
    # Unicode in loops
    unicode_loop = "{% for i in range(100) %}{{ 'Unicode: 🎉 测试 ñáéíóú' }}{% endfor %}"
    expected_unicode_loop = "Unicode: 🎉 测试 ñáéíóú" * 100
    test_case(
        unicode_loop,
        expected_unicode_loop,
        "Unicode content in loops"
    )
    
    # Mixed Unicode and ASCII
    mixed_content = "{% for i in range(100) %}ASCII{{ i }}Unicode🔥{% endfor %}"
    expected_mixed = "".join(f"ASCII{i}Unicode🔥" for i in range(100))
    test_case(
        mixed_content,
        expected_mixed,
        "Mixed Unicode and ASCII content"
    )

def test_edge_case_performance():
    """Test edge case performance scenarios"""
    print("\nTesting edge case performance...")
    print("=" * 60)
    
    # Very long single line
    very_long_line = "{% if True %}" + "x" * 10000 + "{% endif %}"
    expected_long = "x" * 10000
    test_case(
        very_long_line,
        expected_long,
        "Very long single line"
    )
    
    # Many empty blocks
    empty_blocks = "{% if True %}{% endif %}" * 1000 + "end"
    test_case(
        empty_blocks,
        "end",
        "Many empty blocks (1000)"
    )
    
    # Alternating text and code
    alternating = ""
    expected_alt = ""
    for i in range(500):
        alternating += f"text{i}" + "{{ " + str(i) + " }}"
        expected_alt += f"text{i}{i}"
    
    test_case(
        alternating,
        expected_alt,
        "Alternating text and code (500 pairs)"
    )

def test_stress_combinations():
    """Test combinations of stress factors"""
    print("\nTesting stress combinations...")
    print("=" * 60)
    
    # Large template with all features
    stress_template = ""
    
    # Add functions
    for i in range(10):
        stress_template += "{% def func" + str(i) + " x %}{{ x * " + str(i+1) + " }}{% enddef %}"
    
    # Add loops with conditionals
    stress_template += "{% for i in range(100) %}"
    stress_template += "{% if i % 10 == 0 %}"
    stress_template += "{% for j in range(5) %}"
    stress_template += "{{ func" + str(0) + "(j) }}"
    stress_template += "{% endfor %}"
    stress_template += "{% endif %}"
    stress_template += "{% endfor %}"
    
    # Expected result
    expected_stress = ""
    for i in range(100):
        if i % 10 == 0:
            for j in range(5):
                expected_stress += str(j * 1)  # func0 multiplies by 1
    
    test_case(
        stress_template,
        expected_stress,
        "Stress test: functions + loops + conditionals",
        max_time=15.0
    )

def main():
    """Run all performance and stress tests"""
    print("🧪 Performance & Stress Test Suite")
    print("=" * 60)
    
    test_large_text_blocks()
    test_many_variables()
    test_deep_nesting()
    test_large_loops()
    test_many_function_calls()
    test_complex_expressions()
    test_memory_intensive()
    test_unicode_performance()
    test_edge_case_performance()
    test_stress_combinations()
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All performance and stress tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 