#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Command-line Testing Tool
#
# This is a good tool for testing function-like command-line tools.
# Test cases are input-output pairs; and if the tool being tested can 
# produce the output from the input, the test case passes.
#
# The tool looks for files that follow this naming pattern:
#
#   test-A.in.ext  ->  test-A.out.ext
#   test-B.in.ext  ->  test-B.out.ext
#   test-C.in.ext  ->  test-C.out.ext
#
# The extension ('ext' here) can be anything. 
# The content of a *.in.* file  is piped to the tool being tested, 
# and the output is compared against the *.out* file. 
# A match means the test passed.
#

#
# Copyright (C) 2014 Arjun G. Menon
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from json import loads
from collections import OrderedDict
from subprocess import Popen, PIPE, STDOUT
from os import path, listdir

def test_input_output(input_text, output_text):
    process = Popen(["../pypage.py", "-"], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    process_output = process.communicate(input=input_text)[0]
    process.wait()
    return process_output == output_text

def get_content(file_name):
    with open(file_name) as f:
        content = f.read().decode()
    return content

def is_input_file(name):
    name, first_ext = path.splitext(name)
    name, second_ext = path.splitext(name)

    if second_ext == '.in':
        return True
    return False

def construct_output_file_name(input_file_name):
    input_file_root, file_ext = path.splitext(input_file_name)
    file_root, in_ext = path.splitext(input_file_root)
    assert in_ext == '.in'

    return file_root + '.out' + file_ext

def construct_test_name(input_file_name):
    input_file_root, file_ext = path.splitext(input_file_name)
    file_root, in_ext = path.splitext(input_file_root)
    assert in_ext == '.in'

    return file_root.replace('-', ' ')

def get_test_cases(directory, file_list):
    input_files = filter(lambda name: is_input_file(name), file_list)
    return [ (construct_test_name(name), path.join(directory, name), path.join(directory, construct_output_file_name(name))) for 
            name in input_files if path.isfile(path.join(directory, construct_output_file_name(name))) ]

def run_all():
    tests_dir = '.'

    all_files = listdir(tests_dir)
    test_cases = [ (name, get_content(input_file), get_content(output_file)) for 
        name, input_file, output_file in get_test_cases(tests_dir, all_files) ]

    print "Running %i tests..." % len(test_cases)

    passed = 0
    for name, input_text, output_text in test_cases:
        print name + "...", 

        #input_text, output_text  = get_test_data(input_file_name)
        success = test_input_output(input_text, output_text)

        print "Success" if success else "Failure"
        if success:
            passed += 1

    if passed == len(test_cases):
        print "All tests passed."
    else:
        print "%d tests passed, %d tests failed." % (passed, len(tests) - passed)

if __name__ == '__main__':
    run_all()
