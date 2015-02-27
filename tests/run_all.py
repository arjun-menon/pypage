#!/usr/bin/python

from json import loads
from collections import OrderedDict
from subprocess import Popen, PIPE, STDOUT
from os import path

def test_input_output(input_text, output_text):
    process = Popen(["../pypage.py", "-"], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    process_output = process.communicate(input=input_text)[0]
    process.wait()
    return process_output == output_text

def get_output_file_name(input_file_name):
    input_file_root, file_ext = path.splitext(input_file_name)
    file_root, in_ext = path.splitext(input_file_root)

    assert in_ext == ".in"
    return file_root + ".out" + file_ext

def get_test_data(input_file_name):
    output_file_name = get_output_file_name(input_file_name)

    with open(input_file_name) as input_file:
        input_text = input_file.read().decode()

    with open(output_file_name) as output_file:
        output_text = output_file.read().decode()

    return input_text, output_text

def run_all():
    with open("tests.json") as tests_json:
        tests = loads(tests_json.read(), object_pairs_hook=OrderedDict)

    print "Running %i tests..." % len(tests)

    passed = 0
    for name, input_file_name in tests.items():
        print name + "...", 

        input_text, output_text  = get_test_data(input_file_name)
        success = test_input_output(input_text, output_text)

        print "Success" if success else "Failure"
        if success:
            passed += 1

    if passed == len(tests):
        print "All tests passed."
    else:
        print "%d tests passed, %d tests failed." % (passed, len(tests) - passed)

if __name__ == "__main__":
    run_all()
