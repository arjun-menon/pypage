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
from sys import exit

class TestCase(object):
    def __init__(self, cmd, tests_dir, input_file_name):
        self.cmd = cmd
        self.tests_dir = tests_dir

        self.name = self.construct_test_name(input_file_name)
        self.input_file = path.join(tests_dir, input_file_name)
        self.output_file = path.join(tests_dir, self.construct_output_file_name(input_file_name))

    @staticmethod
    def construct_test_name(input_file_name):
        input_file_root, file_ext = path.splitext(input_file_name)
        file_root, in_ext = path.splitext(input_file_root)
        assert in_ext == '.in'

        return file_root.replace('-', ' ')

    @staticmethod
    def construct_output_file_name(input_file_name):
        input_file_root, file_ext = path.splitext(input_file_name)
        file_root, in_ext = path.splitext(input_file_root)
        assert in_ext == '.in'

        return file_root + '.out' + file_ext

    @staticmethod
    def read_file(file_name):
        with open(file_name) as f:
            content = f.read().decode()
        return content

    @staticmethod
    def run_cmd(cmd, input_text):
        process = Popen([cmd, '-'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        process_output = process.communicate(input=input_text)[0]
        process.wait()
        return process_output

    def test(self):
        test_input = self.read_file(self.input_file)
        expected_output = self.read_file(self.output_file)

        actual_output = self.run_cmd(self.cmd, test_input)
        return expected_output == actual_output


def is_input_file(name):
    name, first_ext = path.splitext(name)
    name, second_ext = path.splitext(name)

    if second_ext == '.in':
        return True
    return False

def get_test_cases(cmd, tests_dir):
    file_list = listdir(tests_dir)
    input_files = filter(lambda name: is_input_file(name), file_list)

    test_cases = list()
    for input_file_name in input_files:
        if not path.isfile(path.join(tests_dir, TestCase.construct_output_file_name(input_file_name))):
            print "The following input file has no output file: " + input_file_name
        else:
            test_cases.append(TestCase(cmd, tests_dir, input_file_name))

    return test_cases

def test_cmd(cmd, tests_dir):
    test_cases = get_test_cases(cmd, tests_dir)

    print "Running %i tests..." % len(test_cases)

    passed = 0
    for test_case in test_cases:
        print test_case.name + "...", 

        success = test_case.test()

        print "Success" if success else "Failure"
        if success:
            passed += 1

    if passed == len(test_cases):
        print "All tests passed."
        return True
    else:
        print "%d tests passed, %d tests failed." % (passed, len(test_cases) - passed)
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Light-weight Python templating engine.")
    parser.add_argument('cmd', type=str, help='path to the command to test')
    parser.add_argument('tests_dir', type=str, help='directory containing test cases')
    args = parser.parse_args()

    if not path.isfile(args.cmd):
        print "The command '%s' does not exist." % args.cmd
        exit(1)

    if not path.isdir(args.tests_dir):
        print "The directory '%s' does not exist." % args.cmd
        exit(1)

    exit(0 if test_cmd(args.cmd, args.tests_dir) else 1)

if __name__ == '__main__':
    main()
