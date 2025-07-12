#!/usr/bin/env python3
"""
Comprehensive test suite for testing escape sequence handling in the Rust pypage implementation.
Tests the unescape_str_cow function and related escape sequence processing.
"""

import sys
import os

# Import the Rust module directly from the current directory
sys.path.insert(0, os.path.dirname(__file__))
import pypage

# Test counters
passed = 0
total = 0

def test_unescape_function():
    """Test the unescape_str_cow function directly through template processing"""
    global passed, total
    
    test_cases = [
        # Basic empty and no-escape cases
        ("", "", "Empty string"),
        ("hello world", "hello world", "No escape sequences"),
        ("simple text", "simple text", "Simple text without escapes"),
        
        # Basic escape sequences
        ("\\{", "{", "Single escaped opening brace"),
        ("\\}", "}", "Single escaped closing brace"),
        ("\\{\\}", "{}", "Both escaped braces"),
        
        # Escape sequences at different positions
        ("\\{start", "{start", "Escaped brace at start"),
        ("end\\}", "end}", "Escaped brace at end"),
        ("mid\\{dle", "mid{dle", "Escaped brace in middle"),
        
        # Multiple escape sequences
        ("\\{first\\} and \\{second\\}", "{first} and {second}", "Multiple escape pairs"),
        ("\\{\\{\\}\\}", "{{}}", "Multiple consecutive escapes"),
        ("\\{a\\}\\{b\\}\\{c\\}", "{a}{b}{c}", "Multiple separate escape pairs"),
        
        # Mixed content
        ("Before \\{ middle \\} after", "Before { middle } after", "Mixed text with escapes"),
        ("Text with \\{ escape and normal { brace", "Text with { escape and normal { brace", "Mixed escaped and normal braces"),
        
        # Complex template-like content
        ("Hello \\{name\\}, your score is \\{score\\}!", "Hello {name}, your score is {score}!", "Template-like with escapes"),
        ("\\{% if condition %\\}content\\{% endif %\\}", "{% if condition %}content{% endif %}", "Template block with escapes"),
        
        # Edge cases with backslashes
        ("\\\\{", "\\{", "Backslash followed by brace (should not unescape)"),
        ("text\\\\{more", "text\\{more", "Backslash escape followed by brace"),
        ("\\{valid\\} and \\\\{invalid", "{valid} and \\{invalid", "Mix of valid and invalid escapes"),
        
        # Long strings
        ("\\{" * 100, "{" * 100, "Many escaped opening braces"),
        ("\\}" * 100, "}" * 100, "Many escaped closing braces"),
        ("\\{test\\}" * 50, "{test}" * 50, "Many escaped pairs"),
        
        # Real-world template examples
        ("Welcome \\{\\{ user.name \\}\\} to our site!", "Welcome {{ user.name }} to our site!", "Template with double braces"),
        ("\\{% for item in items %\\}\\{\\{ item \\}\\}\\{% endfor %\\}", "{% for item in items %}{{ item }}{% endfor %}", "Full template with escapes"),
        
        # No escapes but with braces (should be unchanged)
        ("{{ code }}", "{{ code }}", "Normal code braces"),
        ("{% block %}", "{% block %}", "Normal block braces"),
        ("{# comment #}", "{# comment #}", "Normal comment braces"),
        
        # Escape sequences with surrounding content
        ("prefix\\{content\\}suffix", "prefix{content}suffix", "Escaped content with prefix and suffix"),
        ("\\{\\{\\{ triple \\}\\}\\}", "{{{ triple }}}", "Triple braces with escapes"),
        
        # Unicode and special characters
        ("\\{unicode: ñáéíóú\\}", "{unicode: ñáéíóú}", "Escaped braces with unicode"),
        ("\\{symbols: @#$%^&*()\\}", "{symbols: @#$%^&*()}", "Escaped braces with symbols"),
        
        # Nested-like patterns
        ("\\{outer \\{inner\\} outer\\}", "{outer {inner} outer}", "Nested-like escaped braces"),
        ("\\{\\{nested\\}\\}", "{{nested}}", "Double nested escapes"),
    ]
    
    print("Testing escape sequence handling...")
    print("=" * 60)
    
    for i, (input_str, expected, description) in enumerate(test_cases, 1):
        total += 1
        
        # We test the unescape functionality by using it in a template context
        # where the escape sequences should be processed
        template = f"{{{{ '{input_str}' }}}}"
        
        try:
            result = pypage.pypage_process(template, {})
            
            if result == expected:
                print(f"✅ Test {i:2d}: PASS - {description}")
                passed += 1
            else:
                print(f"❌ Test {i:2d}: FAIL - {description}")
                print(f"    Input:    {repr(input_str)}")
                print(f"    Expected: {repr(expected)}")
                print(f"    Got:      {repr(result)}")
        except Exception as e:
            print(f"❌ Test {i:2d}: ERROR - {description}")
            print(f"    Input:    {repr(input_str)}")
            print(f"    Error:    {e}")

def test_escape_in_text_nodes():
    """Test escape sequences in text nodes (outside of code/block tags)"""
    global passed, total
    
    print("\nTesting escape sequences in text nodes...")
    print("=" * 60)
    
    test_cases = [
        ("Simple text with \\{ escape", "Simple text with { escape", "Text node with escaped brace"),
        ("Multiple \\{ and \\} in text", "Multiple { and } in text", "Text node with multiple escapes"),
        ("Before\\{middle\\}after", "Before{middle}after", "Text node without spaces"),
        ("\\{start of text", "{start of text", "Text node escape at start"),
        ("end of text\\}", "end of text}", "Text node escape at end"),
        ("\\{\\{double\\}\\}", "{{double}}", "Text node with double escapes"),
        ("Mixed {{ code }} and \\{ escaped \\}", "Mixed {{ code }} and { escaped }", "Text with code and escapes"),
        ("Line 1\\{esc\\}\nLine 2\\{esc\\}", "Line 1{esc}\nLine 2{esc}", "Multiline text with escapes"),
    ]
    
    for i, (template, expected, description) in enumerate(test_cases, 1):
        total += 1
        
        try:
            result = pypage.pypage_process(template, {})
            
            if result == expected:
                print(f"✅ Test {i:2d}: PASS - {description}")
                passed += 1
            else:
                print(f"❌ Test {i:2d}: FAIL - {description}")
                print(f"    Template: {repr(template)}")
                print(f"    Expected: {repr(expected)}")
                print(f"    Got:      {repr(result)}")
        except Exception as e:
            print(f"❌ Test {i:2d}: ERROR - {description}")
            print(f"    Template: {repr(template)}")
            print(f"    Error:    {e}")

def test_escape_in_code_blocks():
    """Test escape sequences in code and block tags"""
    global passed, total
    
    print("\nTesting escape sequences in code and block tags...")
    print("=" * 60)
    
    test_cases = [
        # Code tag escapes
        ("{{ 'hello \\{ world \\}' }}", "hello { world }", "String with escapes in code"),
        ("{{ 'prefix\\{test\\}suffix' }}", "prefix{test}suffix", "Escaped braces in string literal"),
        
        # Block tag escapes (these should be processed during parsing)
        ("{% if True %}Text with \\{ escape{% endif %}", "Text with { escape", "Block content with escapes"),
        ("{% if True %}\\{start{% endif %}", "{start", "Block content escape at start"),
        ("{% if True %}end\\}{% endif %}", "end}", "Block content escape at end"),
        
        # Complex combinations
        ("{% if True %}Before \\{ middle \\} after{% endif %}", "Before { middle } after", "Block with multiple escapes"),
        ("{{ 'code \\{ test \\}' }}Text \\{ escape", "code { test }Text { escape", "Code and text escapes"),
        
        # Nested scenarios
        ("{% if True %}\\{{% endif %}{{ 'test' }}{% if True %}\\}{% endif %}", "{test}", "Escapes around code"),
    ]
    
    for i, (template, expected, description) in enumerate(test_cases, 1):
        total += 1
        
        try:
            result = pypage.pypage_process(template, {})
            
            if result == expected:
                print(f"✅ Test {i:2d}: PASS - {description}")
                passed += 1
            else:
                print(f"❌ Test {i:2d}: FAIL - {description}")
                print(f"    Template: {repr(template)}")
                print(f"    Expected: {repr(expected)}")
                print(f"    Got:      {repr(result)}")
        except Exception as e:
            print(f"❌ Test {i:2d}: ERROR - {description}")
            print(f"    Template: {repr(template)}")
            print(f"    Error:    {e}")

def test_escape_edge_cases():
    """Test edge cases and error conditions"""
    global passed, total
    
    print("\nTesting escape sequence edge cases...")
    print("=" * 60)
    
    test_cases = [
        # Edge cases that should NOT be unescaped
        ("\\\\{", "\\{", "Double backslash should not unescape"),
        ("\\\\}", "\\}", "Double backslash should not unescape brace"),
        ("normal\\text", "normal\\text", "Backslash without brace should be unchanged"),
        ("\\{incomplete", "{incomplete", "Incomplete escape (missing closing)"),
        ("incomplete\\}", "incomplete}", "Incomplete escape (missing opening)"),
        
        # Complex mixed scenarios
        ("\\{valid\\} \\\\{invalid\\} \\{valid\\}", "{valid} \\{invalid} {valid}", "Mix of valid and invalid"),
        ("\\{\\\\{\\}\\\\}", "{\\{}\\}", "Complex escape combinations"),
        
        # Empty and whitespace
        ("\\{\\}", "{}", "Empty escaped braces"),
        ("\\{ \\}", "{ }", "Escaped braces with space"),
        ("\\{\t\\}", "{\t}", "Escaped braces with tab"),
        ("\\{\n\\}", "{\n}", "Escaped braces with newline"),
        
        # Long escape sequences
        ("\\{" + "a" * 1000 + "\\}", "{" + "a" * 1000 + "}", "Long content between escapes"),
        ("\\{\\}" * 1000, "{}" * 1000, "Many consecutive escape pairs"),
        
        # Unicode edge cases
        ("\\{café\\}", "{café}", "Unicode content in escapes"),
        ("\\{🌟\\}", "{🌟}", "Emoji in escapes"),
        ("\\{测试\\}", "{测试}", "Chinese characters in escapes"),
    ]
    
    for i, (template, expected, description) in enumerate(test_cases, 1):
        total += 1
        
        try:
            result = pypage.pypage_process(template, {})
            
            if result == expected:
                print(f"✅ Test {i:2d}: PASS - {description}")
                passed += 1
            else:
                print(f"❌ Test {i:2d}: FAIL - {description}")
                print(f"    Template: {repr(template)}")
                print(f"    Expected: {repr(expected)}")
                print(f"    Got:      {repr(result)}")
        except Exception as e:
            print(f"❌ Test {i:2d}: ERROR - {description}")
            print(f"    Template: {repr(template)}")
            print(f"    Error:    {e}")

def test_escape_performance():
    """Test performance characteristics of escape handling"""
    global passed, total
    
    print("\nTesting escape sequence performance characteristics...")
    print("=" * 60)
    
    # Test that strings without escapes are handled efficiently (should return Cow::Borrowed)
    test_cases = [
        ("no escapes here", "no escapes here", "String without escapes should be efficient"),
        ("{ normal } braces", "{ normal } braces", "Normal braces should be efficient"),
        ("lots of { normal } braces { here }", "lots of { normal } braces { here }", "Many normal braces"),
        ("very " + "long " * 100 + "string", "very " + "long " * 100 + "string", "Long string without escapes"),
    ]
    
    for i, (template, expected, description) in enumerate(test_cases, 1):
        total += 1
        
        try:
            result = pypage.pypage_process(template, {})
            
            if result == expected:
                print(f"✅ Test {i:2d}: PASS - {description}")
                passed += 1
            else:
                print(f"❌ Test {i:2d}: FAIL - {description}")
                print(f"    Template: {repr(template)}")
                print(f"    Expected: {repr(expected)}")
                print(f"    Got:      {repr(result)}")
        except Exception as e:
            print(f"❌ Test {i:2d}: ERROR - {description}")
            print(f"    Template: {repr(template)}")
            print(f"    Error:    {e}")

def main():
    """Run all escape sequence tests"""
    print("🧪 Comprehensive Escape Sequence Tests")
    print("=" * 60)
    
    test_unescape_function()
    test_escape_in_text_nodes()
    test_escape_in_code_blocks()
    test_escape_edge_cases()
    test_escape_performance()
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All escape sequence tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 