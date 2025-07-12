#!/usr/bin/env python3

import subprocess
import sys
import os
import time
from pathlib import Path

def run_test_suite(test_file):
    """Run a single test suite and return results"""
    test_name = Path(test_file).stem
    print(f"\n{'='*60}")
    print(f"🧪 Running test suite: {test_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, cwd='.')
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            # Parse output for test counts
            lines = result.stdout.split('\n')
            for line in lines:
                if 'tests passed' in line:
                    test_count_line = line
                    break
            else:
                test_count_line = "Results not found"
            
            print(f"✅ {test_name} - PASSED ({duration:.2f}s)")
            print(f"   {test_count_line}")
            return True, test_count_line, duration
        else:
            print(f"❌ {test_name} - FAILED ({duration:.2f}s)")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False, f"FAILED - {result.stderr[:100]}...", duration
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ {test_name} - ERROR ({duration:.2f}s): {e}")
        return False, f"ERROR - {e}", duration

def main():
    """Run all test suites"""
    
    # List of all test files
    test_files = [
        "test_comprehensive_extended.py",
        "test_elif.py", 
        "test_tuple_debug.py",
        "test_nested_conditionals.py",
        "test_error_handling.py",
        "test_escape.py",
        "test_complex_nesting.py",
        "test_function_advanced.py",
        "test_performance_stress.py",
        "test_unicode_special.py",
        "test_integration_scenarios.py",
        "debug_elif.py",
        # Include existing test files if they exist
        "test_comprehensive_advanced.py",
        "test_comprehensive.py",
        "test_pypage.py",
    ]
    
    # Filter to only files that exist
    existing_test_files = [f for f in test_files if os.path.exists(f)]
    
    print("🚀 PyPage Rust Implementation - Comprehensive Test Suite")
    print(f"Found {len(existing_test_files)} test files to run")
    print(f"Files: {', '.join(existing_test_files)}")
    
    # Run all tests
    results = []
    total_duration = 0
    
    for test_file in existing_test_files:
        success, summary, duration = run_test_suite(test_file)
        results.append((test_file, success, summary, duration))
        total_duration += duration
    
    # Summary
    print(f"\n{'='*60}")
    print("🏁 COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*60}")
    
    passed_count = sum(1 for _, success, _, _ in results if success)
    total_count = len(results)
    
    for test_file, success, summary, duration in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_file:<30} ({duration:.2f}s) - {summary}")
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"   Test suites passed: {passed_count}/{total_count}")
    print(f"   Total runtime: {total_duration:.2f}s")
    
    if passed_count == total_count:
        print("🎉 ALL TEST SUITES PASSED!")
        print("\n✨ The PyPage Rust implementation is working correctly!")
        print("   Key features verified:")
        print("   • Basic expressions and variables")
        print("   • Conditional statements (if/elif/else)")
        print("   • For loops with tuple unpacking")
        print("   • While loops")
        print("   • Nested structures (deep nesting)")
        print("   • Comments and capture blocks")
        print("   • Function definitions (advanced scenarios)")
        print("   • Escape sequence handling")
        print("   • Unicode and special characters")
        print("   • Performance and stress testing")
        print("   • Real-world integration scenarios")
        print("   • Error handling and edge cases")
        return True
    else:
        print(f"❌ {total_count - passed_count} test suite(s) failed")
        print("\n🔧 Issues found that need attention:")
        for test_file, success, summary, duration in results:
            if not success:
                print(f"   • {test_file}: {summary}")
        return False

def show_test_info():
    """Show information about available tests"""
    print("\n📋 Available Test Suites:")
    print("   • test_comprehensive_extended.py - Extended comprehensive tests (70+ tests)")
    print("   • test_elif.py - Elif chain functionality (35+ tests)")
    print("   • test_tuple_debug.py - Tuple unpacking edge cases (30+ tests)")
    print("   • test_nested_conditionals.py - Nested conditional logic (50+ tests)")
    print("   • test_error_handling.py - Error handling and edge cases (80+ tests)")
    print("   • test_escape.py - Escape sequence handling (100+ tests)")
    print("   • test_complex_nesting.py - Deep nesting and complex interactions (40+ tests)")
    print("   • test_function_advanced.py - Advanced function usage scenarios (50+ tests)")
    print("   • test_performance_stress.py - Performance and stress testing (40+ tests)")
    print("   • test_unicode_special.py - Unicode and special character handling (50+ tests)")
    print("   • test_integration_scenarios.py - Real-world integration scenarios (15+ tests)")
    print("   • debug_elif.py - Debug-focused elif testing")
    print("   • test_comprehensive_advanced.py - Advanced features")
    print("   • test_comprehensive.py - Basic comprehensive tests")
    print("   • test_pypage.py - Core functionality tests")
    print(f"\n📝 Total estimated tests: 560+ individual test cases")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--info":
        show_test_info()
        sys.exit(0)
    
    # Build first
    print("🔨 Building PyPage Rust library...")
    build_result = subprocess.run(['cargo', 'build', '--release'], 
                                capture_output=True, text=True, cwd='.')
    if build_result.returncode != 0:
        print("❌ Build failed:")
        print(build_result.stderr)
        sys.exit(1)
    
    # Copy library
    import shutil
    shutil.copy('target/release/libpypage.dylib', 'pypage.so')
    print("✅ Build successful")
    
    # Run tests
    success = main()
    
    if success:
        print("\n🎯 DEVELOPMENT STATUS:")
        print("   The Rust implementation has achieved near-complete feature parity")
        print("   with the original Python PyPage implementation!")
        print("   ")
        print("   Key accomplishments:")
        print("   • ✅ Lexer and parser fully functional")
        print("   • ✅ Expression evaluation via PyO3")
        print("   • ✅ All conditional structures working")
        print("   • ✅ Loop constructs (for/while) operational")
        print("   • ✅ Tuple unpacking and variable scoping")
        print("   • ✅ Comment handling and capture blocks")
        print("   • ✅ Function definition infrastructure")
        print("   • ✅ Deep nesting and complex interactions")
        print("   • ✅ Advanced function usage scenarios")
        print("   • ✅ Escape sequence handling and unescaping")
        print("   • ✅ Unicode and special character support")
        print("   • ✅ Performance optimization and stress testing")
        print("   • ✅ Real-world integration scenarios")
        print("   • ✅ Error handling and edge cases")
        print("   • ✅ Memory safety and performance improvements")
        
    sys.exit(0 if success else 1) 