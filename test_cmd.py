#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

#
#  Command-line Testing Tool
#  =========================
#  This is a simple tool for testing command-line tools.
#  Test cases are input-output pairs; and if the command being 
#  tested can produce the output from the input, the test passes.
#
#  This tool looks for files that follow this naming pattern:
#
#    test-A.in.ext  ->  test-A.out.ext
#    test-B.in.ext  ->  test-B.out.ext
#    test-C.in.ext  ->  test-C.out.ext
#
#  The extension ('ext' here) can be anything. The content 
#  of a *.in.* file is piped to the command being tested, 
#  and its STDOUT is compared against the *.out* file. 
#  A match means the test passed.
#
#  Usage
#  -----
#  This tool requires two command-line arguments:
#    1. The path to the command being tested.
#    2. The directory containing test cases.
#
#  You can specify command-line arguments for your test cases
#  by creating a special file named 'tests.json', and placing 
#  it in the directory containing your test cases. As a perk, 
#  if an arguments maps to a non-string value, that value is 
#  passed in as JSON.
#

from __future__ import print_function
from json import dumps, loads
from collections import OrderedDict
from subprocess import Popen, PIPE, STDOUT
from sys import exit, version_info
from os import path, listdir

class TestCase(object):
    def __init__(self, cmd, tests_dir, input_file_name):
        self.cmd = cmd
        self.tests_dir = tests_dir

        self.name = self.construct_test_name(input_file_name)
        self.input_file = path.join(tests_dir, input_file_name)
        self.stdout_file = path.join(tests_dir, self.construct_stdout_file_name(input_file_name))
        self.stderr_file = path.join(tests_dir, self.construct_stderr_file_name(input_file_name))

    @staticmethod
    def construct_test_name(input_file_name):
        input_file_root, file_ext = path.splitext(input_file_name)
        file_root, in_ext = path.splitext(input_file_root)
        assert in_ext == '.in'

        return file_root.replace('-', ' ')

    @staticmethod
    def get_file_root_and_ext(input_file_name):
        input_file_root, file_ext = path.splitext(input_file_name)
        file_root, in_ext = path.splitext(input_file_root)
        assert in_ext == '.in'
        return file_root, file_ext

    @staticmethod
    def construct_stdout_file_name(input_file_name):
        file_root, file_ext = TestCase.get_file_root_and_ext(input_file_name)
        return file_root + '.out' + file_ext

    @staticmethod
    def construct_stderr_file_name(input_file_name):
        file_root, file_ext = TestCase.get_file_root_and_ext(input_file_name)
        return file_root + '.err' + file_ext

    @staticmethod
    def read_file(file_name):
        with open(file_name) as f:
            content = f.read()
            if version_info.major == 2 and isinstance(content, unicode):
                content = content.decode()
        if version_info.major >= 3:
            content = bytes(content, 'utf-8')
        return content

    def run_cmd(self, cmd, input_text):
        print("Running:", ' '.join(cmd))
        process = Popen(self.cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate(input=input_text)
        return stdout, stderr

    def test(self):
        test_input = self.read_file(self.input_file)
        stdout, stderr = self.run_cmd(self.cmd, test_input)

        result = False

        if path.isfile(self.stdout_file):
            expected_stdout = self.read_file(self.stdout_file)
            if expected_stdout != stdout:
                print("Expected STDOUT:")
                print(expected_stdout)
                print("Received STDOUT:")
                print(stdout)
                if len(stderr):
                    print("Received STDERR:")
                    print(stderr)
            else:
                result = True

        if path.isfile(self.stderr_file):
            expected_stderr = self.read_file(self.stderr_file)
            if expected_stderr != stderr:
                result = False
                print("Expected STDERR:")
                print(expected_stderr)
                print("Received STDERR:")
                print(stderr)
            else:
                result = True

        return result


def _decode_list(data): # http://stackoverflow.com/a/6633651/908430
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv

def _decode_dict(data): # http://stackoverflow.com/a/6633651/908430
    rv = {}
    for key, value in data.items():
        if version_info.major == 2 and isinstance(key, unicode):
            key = key.encode('utf-8')
        if version_info.major == 2 and isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv

def is_input_file(name):
    name, first_ext = path.splitext(name)
    name, second_ext = path.splitext(name)

    if second_ext == '.in':
        return True
    return False

def parse_cmdline_args_json(cmdline_args_json):
    cmdline_args = list()

    for arg, val in cmdline_args_json.items():
        cmdline_args.append(arg)
        cmdline_args.append(dumps(val))

    return cmdline_args

def replace_at_sign_with_cmdline_args(case, cmdline_args):
    updated_cmd = list()
    for cmd_segment in case.cmd:
        if cmd_segment == '@':
            updated_cmd.extend(cmdline_args)
        else:
            updated_cmd.append(cmd_segment)
    case.cmd = updated_cmd

def set_cmdline_args_from_tests_json(tests_dir, test_cases):
    tests_json_file = path.join(tests_dir, "tests.json")
    with open(tests_json_file) as f:
        tests_json = loads(f.read(), object_hook=_decode_dict)

    for name, cmdline_args_json in tests_json.items():
        if name in test_cases.keys():
            case = test_cases[name]

            if isinstance(case, TestCase):
                cmdline_args = parse_cmdline_args_json(cmdline_args_json)
                replace_at_sign_with_cmdline_args(case, cmdline_args)

def clear_at_sign_from_cmd(test_cases):
    for case in test_cases.values():
        try:
            case.cmd.remove('@')
        except ValueError:
            pass

def get_test_cases(cmd, tests_dir):
    file_list = listdir(tests_dir)
    file_names = filter(lambda name: is_input_file(name), file_list)

    test_cases = OrderedDict()

    for file_name in file_names:
        out_file = path.join(tests_dir, TestCase.construct_stdout_file_name(file_name))
        err_file = path.join(tests_dir, TestCase.construct_stderr_file_name(file_name))

        if path.isfile(out_file) or path.isfile(err_file):
            test_case = TestCase(cmd, tests_dir, file_name)
            test_cases[test_case.name] = test_case
        else:
            name = TestCase.construct_test_name(file_name)
            test_cases[name] = None # missing stdout/stderr file

    set_cmdline_args_from_tests_json(tests_dir, test_cases)
    clear_at_sign_from_cmd(test_cases)

    return test_cases

class Color(object):
    # values from: https://github.com/ilovecode1/pyfancy/blob/master/pyfancy.py
    END = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    UNDERLINE = '\033[4m'

def color(text, color):
    return '%s%s%s' % (color, text, Color.END)

def test_cmd(cmd, tests_dir):
    test_cases = get_test_cases(cmd, tests_dir)

    print("Running %i tests...\n" % len(test_cases))

    total = len(test_cases)
    passed = 0
    missing_output_files = 0
    for name, case in test_cases.items():
        print(name + "...")

        result = None
        if case == None:
            print(color('No output file', Color.YELLOW))
            total -= 1
            missing_output_files += 1
        else:
            result = case.test()

        if result == True:
            print(color("Success", Color.GREEN))
        elif result == False:
            print(color("Failure", Color.RED))
        print()

        if result == True:
            passed += 1

    if passed == total:
        print("All tests passed.")
        if missing_output_files <= 0:
            return True
        else:
            print("%d tests are missing corresponding output files." % missing_output_files)
            return False
    else:
        print("%d tests passed, %d tests failed." % (passed, total - passed))
        return False

def validate_cmdline_args(args):
    if not path.isdir(args.tests_dir):
        print("The directory '%s' does not exist." % args.cmd)
        exit(1)

    if not path.isfile(args.cmd[0]):
        print("The command '%s' does not exist." % args.cmd)
        exit(1)

    at_sign_seen = False
    for cmd_segment in args.cmd:
        if cmd_segment == '@':
            if at_sign_seen:
                print("Only one '@' command-line args substituion marker allowed.")
                exit(1)
            at_sign_seen = True

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Light-weight Python templating engine.")
    parser.add_argument('tests_dir', type=str, help='The directory containing test cases')
    parser.add_argument('cmd', type=str, help='The command to test with any and all command-line\
arguments, and with an @ denoting where args from test.json should be injected', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    validate_cmdline_args(args)

    if test_cmd(args.cmd, args.tests_dir):
        exit(0)
    else:
        exit(1)

if __name__ == '__main__':
    main()
