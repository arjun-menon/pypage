#!/usr/bin/env python3
"""
Unicode & Special Characters Test Suite - Tests Unicode handling and special character edge cases.
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

def test_basic_unicode():
    """Test basic Unicode characters"""
    print("\nTesting basic Unicode characters...")
    print("=" * 60)
    
    # Basic Unicode text
    test_case(
        "Hello 世界!",
        "Hello 世界!",
        "Basic Unicode text"
    )
    
    # Unicode in code blocks
    test_case(
        "{{ 'Hola España' }}",
        "Hola España",
        "Unicode in code blocks"
    )
    
    # Unicode variables
    test_case(
        "{% capture español %}¡Hola!{% endcapture %}{{ español }}",
        "¡Hola!",
        "Unicode variable names"
    )
    
    # Mixed ASCII and Unicode
    test_case(
        "Start {{ 'μέσον' }} End",
        "Start μέσον End",
        "Mixed ASCII and Unicode"
    )

def test_emoji_characters():
    """Test emoji and symbol characters"""
    print("\nTesting emoji and symbol characters...")
    print("=" * 60)
    
    # Basic emojis
    test_case(
        "Hello 🌍 World 🚀",
        "Hello 🌍 World 🚀",
        "Basic emoji characters"
    )
    
    # Emojis in expressions
    test_case(
        "{{ '🎉' + ' Party! ' + '🎈' }}",
        "🎉 Party! 🎈",
        "Emojis in expressions"
    )
    
    # Complex emoji sequences
    test_case(
        "{{ '👨‍👩‍👧‍👦' }}",  # Family emoji with ZWJ sequences
        "👨‍👩‍👧‍👦",
        "Complex emoji sequences (family)"
    )
    
    # Skin tone modifiers
    test_case(
        "{{ '👋🏽' }}",  # Waving hand with medium skin tone
        "👋🏽",
        "Emoji with skin tone modifiers"
    )
    
    # Multiple emoji types
    test_case(
        "{% for emoji in ['🔥', '💫', '⭐', '🌟'] %}{{ emoji }}{% endfor %}",
        "🔥💫⭐🌟",
        "Multiple emoji types in loop"
    )

def test_special_symbols():
    """Test special symbols and mathematical characters"""
    print("\nTesting special symbols...")
    print("=" * 60)
    
    # Mathematical symbols
    test_case(
        "{{ '∑∞∂∇±×÷≈≠≤≥' }}",
        "∑∞∂∇±×÷≈≠≤≥",
        "Mathematical symbols"
    )
    
    # Currency symbols
    test_case(
        "{% for currency in ['$', '€', '£', '¥', '₽', '₹'] %}{{ currency }}{% endfor %}",
        "$€£¥₽₹",
        "Currency symbols"
    )
    
    # Arrows and geometric shapes
    test_case(
        "{{ '←↑→↓↔↕⇄⇅' }}",
        "←↑→↓↔↕⇄⇅",
        "Arrow symbols"
    )
    
    # Box drawing characters
    test_case(
        "{{ '┌─┬─┐│┤├┴┘' }}",
        "┌─┬─┐│┤├┴┘",
        "Box drawing characters"
    )

def test_unicode_in_conditionals():
    """Test Unicode characters in conditional statements"""
    print("\nTesting Unicode in conditionals...")
    print("=" * 60)
    
    # Unicode in if conditions
    test_case(
        "{% if 'café' == 'café' %}Match!{% endif %}",
        "Match!",
        "Unicode string comparison in if"
    )
    
    # Unicode in variables and conditions
    test_case(
        "{% capture ciudad %}Madrid{% endcapture %}{% if ciudad == 'Madrid' %}¡Bienvenido!{% else %}No match{% endif %}",
        "¡Bienvenido!",
        "Unicode in conditional with variables"
    )
    
    # Unicode with elif chains
    test_case(
        "{% capture lang %}Français{% endcapture %}{% if lang == 'English' %}Hello{% elif lang == 'Français' %}Bonjour{% else %}Unknown{% endif %}",
        "Bonjour",
        "Unicode in elif chains"
    )
    
    # Emoji in conditionals
    test_case(
        "{% if '🌞' == '🌞' %}Sun{% else %}Not sun{% endif %}",
        "Sun",
        "Emoji comparison in conditionals"
    )

def test_unicode_in_loops():
    """Test Unicode characters in loop constructs"""
    print("\nTesting Unicode in loops...")
    print("=" * 60)
    
    # Unicode in for loops
    test_case(
        "{% for char in ['α', 'β', 'γ', 'δ'] %}{{ char }}{% endfor %}",
        "αβγδ",
        "Unicode characters in for loop"
    )
    
    # Unicode loop variables
    test_case(
        "{% for número in range(3) %}{{ número }}{% endfor %}",
        "012",
        "Unicode loop variable names"
    )
    
    # Unicode in while loops
    test_case(
        "{% capture índice %}0{% endcapture %}{% while int(índice) < 3 %}{{ '★' }}{% capture índice %}{{ int(índice) + 1 }}{% endcapture %}{% endwhile %}",
        "★★★",
        "Unicode in while loops"
    )
    
    # Complex Unicode iteration
    test_case(
        "{% for país in ['🇺🇸', '🇫🇷', '🇩🇪', '🇯🇵'] %}{{ país }}{% endfor %}",
        "🇺🇸🇫🇷🇩🇪🇯🇵",
        "Flag emojis in for loop"
    )

def test_unicode_functions():
    """Test Unicode in function definitions and calls"""
    print("\nTesting Unicode in functions...")
    print("=" * 60)
    
    # Unicode function names
    test_case(
        "{% def saludar nombre %}¡Hola {{ nombre }}!{% enddef %}{{ saludar('María') }}",
        "¡Hola María!",
        "Unicode function names"
    )
    
    # Unicode argument names
    test_case(
        "{% def greet prénom %}Hello {{ prénom }}{% enddef %}{{ greet('François') }}",
        "Hello François",
        "Unicode argument names"
    )
    
    # Unicode in function body
    test_case(
        "{% def emoji_greet %}👋 Hello! 🌟{% enddef %}{{ emoji_greet() }}",
        "👋 Hello! 🌟",
        "Unicode in function body"
    )
    
    # Function with Unicode return
    test_case(
        "{% def get_symbol %}{{ '∞' }}{% enddef %}Symbol: {{ get_symbol() }}",
        "Symbol: ∞",
        "Function returning Unicode"
    )

def test_unicode_edge_cases():
    """Test Unicode edge cases and boundary conditions"""
    print("\nTesting Unicode edge cases...")
    print("=" * 60)
    
    # Zero-width characters
    test_case(
        "{{ 'a' + '\u200b' + 'b' }}",  # Zero-width space
        "a\u200bb",
        "Zero-width space handling"
    )
    
    # Combining characters
    test_case(
        "{{ 'e' + '\u0301' }}",  # e + combining acute accent = é
        "é",
        "Combining characters"
    )
    
    # Right-to-left text
    test_case(
        "{{ 'Hello עברית World' }}",
        "Hello עברית World",
        "Mixed LTR and RTL text"
    )
    
    # Surrogate pairs (4-byte UTF-8)
    test_case(
        "{{ '𝐇𝐞𝐥𝐥𝐨' }}",  # Mathematical bold letters
        "𝐇𝐞𝐥𝐥𝐨",
        "Surrogate pairs (4-byte UTF-8)"
    )
    
    # Unicode normalization cases
    test_case(
        "{{ 'café' == 'café' }}",  # Different compositions of é
        "True",
        "Unicode normalization"
    )

def test_special_whitespace():
    """Test special whitespace characters"""
    print("\nTesting special whitespace characters...")
    print("=" * 60)
    
    # Non-breaking space
    test_case(
        "{{ 'Hello' + '\u00a0' + 'World' }}",
        "Hello\u00a0World",
        "Non-breaking space"
    )
    
    # Various Unicode spaces
    test_case(
        "{{ 'A' + '\u2003' + 'B' }}",  # Em space
        "A\u2003B",
        "Em space character"
    )
    
    # Tab and special characters
    test_case(
        "{{ 'Line1\\nLine2\\tTabbed' }}",
        "Line1\nLine2\tTabbed",
        "Tab and newline characters"
    )
    
    # Invisible characters
    test_case(
        "{{ 'Before' + '\u2060' + 'After' }}",  # Word joiner
        "Before\u2060After",
        "Word joiner character"
    )

def test_unicode_capture_blocks():
    """Test Unicode in capture blocks"""
    print("\nTesting Unicode in capture blocks...")
    print("=" * 60)
    
    # Capture Unicode content
    test_case(
        "{% capture mensaje %}¡Hola mundo! 🌎{% endcapture %}{{ mensaje }}",
        "¡Hola mundo! 🌎",
        "Capturing Unicode content"
    )
    
    # Unicode capture variable names
    test_case(
        "{% capture résultat %}Success ✅{% endcapture %}{{ résultat }}",
        "Success ✅",
        "Unicode capture variable names"
    )
    
    # Complex Unicode capture
    test_case(
        "{% capture 結果 %}{% for i in range(3) %}{{ '★' }}{% endfor %}{% endcapture %}{{ 結果 }}",
        "★★★",
        "Complex Unicode capture with loops"
    )
    
    # Multiple Unicode captures
    test_case(
        "{% capture français %}Bonjour{% endcapture %}{% capture español %}Hola{% endcapture %}{{ français }} & {{ español }}",
        "Bonjour & Hola",
        "Multiple Unicode captures"
    )

def test_unicode_comments():
    """Test Unicode in comments"""
    print("\nTesting Unicode in comments...")
    print("=" * 60)
    
    # Unicode in comments (should be ignored)
    test_case(
        "Start{# This is a comment with Unicode: 你好 🌟 #}End",
        "StartEnd",
        "Unicode in comments"
    )
    
    # Complex Unicode comments
    test_case(
        "{% if True %}{# Comentario en español: ñáéíóú #}Result{% endif %}",
        "Result",
        "Unicode in block comments"
    )
    
    # Emoji in comments
    test_case(
        "Before{# 🚀 Rocket comment 🌟 #}After",
        "BeforeAfter",
        "Emoji in comments"
    )

def test_unicode_performance():
    """Test Unicode performance with large content"""
    print("\nTesting Unicode performance...")
    print("=" * 60)
    
    # Large Unicode text
    unicode_text = "Unicón: ñáéíóú 🌟 " * 100
    test_case(
        unicode_text,
        unicode_text,
        "Large Unicode text block"
    )
    
    # Unicode in large loop
    large_unicode = "{% for i in range(50) %}{{ '测试' + str(i) + '🔥' }}{% endfor %}"
    expected_large = "".join(f"测试{i}🔥" for i in range(50))
    test_case(
        large_unicode,
        expected_large,
        "Unicode in large loop"
    )
    
    # Mixed Unicode performance
    mixed_large = "{% for char in ['α', 'β', 'γ'] * 20 %}{{ char }}{% endfor %}"
    expected_mixed = "αβγ" * 20
    test_case(
        mixed_large,
        expected_mixed,
        "Mixed Unicode performance test"
    )

def main():
    """Run all Unicode and special character tests"""
    print("🧪 Unicode & Special Characters Test Suite")
    print("=" * 60)
    
    test_basic_unicode()
    test_emoji_characters()
    test_special_symbols()
    test_unicode_in_conditionals()
    test_unicode_in_loops()
    test_unicode_functions()
    test_unicode_edge_cases()
    test_special_whitespace()
    test_unicode_capture_blocks()
    test_unicode_comments()
    test_unicode_performance()
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Unicode and special character tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 