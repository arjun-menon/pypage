#!/usr/bin/python3

# Copyright 2013 Arjun G. Menon

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__all__ = ['pypage', 'pypage_multi']

import sys, imp, re

def importCode(code,name):
    # Based on http://code.activestate.com/recipes/82234-importing-a-dynamically-generated-module/
    module = imp.new_module(name)
    exec(code, module.__dict__)
    return module

class PythonCode(object):
    """ A light-weight wrapper around `string` to detect the difference 
        between a plain old string and a string containing Python code. """

    def __init__(self, code, id_level, index):
        assert( type(code) == str )
        self.code, self.id_level, self.index = code, id_level, index

    def __repr__(self):
        return "PythonCode:\n%s" % self.code

class execPythonCode(object):
    def __init__(self, code_objects):
        code = """
__output__ = [""]*{count}

def write(s):
    __output__[__section__] += str(s)

{code}""".format(
        count = len(code_objects),
        code = '\n'.join(
        "__section__ = %d\n" % i + "".join(str(c) for c in co.code) 
                for i, co in enumerate(code_objects) ) )

        self.m = importCode(code, 'pypage_transient')

        # apply indentation to output:
        id_levels = list(map(lambda o: o.id_level, code_objects))
        for i, o in enumerate(self.m.__output__):
            self.m.__output__[i] = '\n'.join( ' ' * id_levels[i] + s for s in o.split('\n') )

    def __iter__(self):
        def output_iterator():
            for o in self.m.__output__:
                yield o
        return output_iterator()

def process_python_tags(lines,
        multiline_delimiter_open  =  '<python>',
        multiline_delimiter_close = '</python>',
        inline_delimiter_open  =  '<py>',
        inline_delimiter_close = '</py>'):
    """ Proces <python>...</python> and <py>...</py> tags

        Args:
            lines: list of strings representing each line of an unprocessed HTML file
            keywords args: their names explain what they are for

        Returns:
            A list containing either `string` or `PythonCode` objects, where 
            plain string lines have been concatenated and PythonCode strings have been 
            adjusted for indentation and concatenated.

        Notes:
            These tags are used when you want indentation in your Python code to 
            keep it consistent with indentation of the surrounding HTML. This 
            function removes the indentation from your code based on the amount of 
            whitespace preceding the opening <python> tag.
    """

    re_delimiter_open  = re.compile(r"\s*%s\s*\n" % multiline_delimiter_open)
    re_delimiter_open_tag_only = re.compile(r"%s" % multiline_delimiter_open)
    re_delimiter_close = re.compile(r"\s*%s\s*\n" % multiline_delimiter_close)

    re_short_open  =  re.compile(inline_delimiter_open)
    re_short_close =  re.compile(inline_delimiter_close)

    def find_indentation_level(opening_line):
        m = re_delimiter_open_tag_only.search(opening_line)
        assert(m != None)

        return m.start()

    result = list()

    mode_plain, mode_code = 'plain', 'code' # the 2 possible collect modes

    collect = ""
    id_level = 0
    pc_index = 0
    mode = mode_plain

    for n, line in enumerate(lines):
        op = re_delimiter_open.match(line)
        cl = re_delimiter_close.match(line)
        ops = re_short_open.search(line)
        cls = re_short_close.search(line)

        if op:
            result.append(collect)

            collect = ""
            id_level = find_indentation_level(line)
            mode = mode_code

        elif cl:
            result.append( PythonCode(collect, id_level, pc_index) )
            pc_index += 1

            collect = '\n'
            id_level = 0
            mode = mode_plain

        elif ops and cls:
            # captured in the following manner:
            # ...pre_py...<py>...in_py...</py>...post_py...
            pre_py = line[:ops.start()]
            in_py = line[ops.end() : cls.start()]
            post_py = line[cls.end():]
            
            collect += pre_py
            result.append(collect)

            collect = in_py
            result.append( PythonCode(collect, 0, pc_index) )
            pc_index += 1

            collect = post_py

        elif mode == mode_plain:
            collect += line

        elif mode == mode_code:
            collect += line[id_level:] if len(line) > id_level else "\n"

    result.append(collect)

    return result

def process_file(input_text):
    chunks = process_python_tags(input_text)
    output_iter = iter( execPythonCode([ c for c in chunks if type(c) == PythonCode ]) )
    return ''.join( next(output_iter) if type(c) == PythonCode else c for c in chunks )

def pypage(input_text, verbose=False, prettify=False):
    if verbose:
        print("Preprocessing file %s" % input_file)

    result = process_file(input_text)

    if prettify:
        from bs4 import BeautifulSoup
        result = BeautifulSoup(result).prettify()

    return result

def pypage_multi(*files, prepend_path='', verbose=False, prettify=False):
    return { filename : pypage( open( prepend_path + '/' + filename ).readlines() , verbose, prettify ) for filename in files }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generates static HTML pages by executing the code within <python> and <py> tags, and replacing replacing them with the content passed to write() calls.")
    parser.add_argument('input_file', type=str, help="HTML input file.")
    parser.add_argument('-o', '--output_file', nargs=1, type=str, default=None, help='Write output to output_file. Default: stdout')
    parser.add_argument('-v', '--verbose', action='store_true', help='print a short message before preprocessing')
    parser.add_argument('-p', '--prettify', action='store_true', help='prettify the resulting HTML using BeautifulSoup -- requires BeautifulSoup4')
    args = parser.parse_args()

    result = pypage( open(args.input_file).readlines(), args.verbose, args.prettify )

    if args.output_file:
        with open(args.output_file[0], 'w') as f:
            f.write(result)
    else:
        print(result, end="")
