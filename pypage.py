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

class PythonCode(object):
    """ Store Python code.
            code: string containing the Python code.
            id_level: its former indentation level. """

    def __init__(self, code, id_level):
        assert( isinstance(code, str) )
        self.code, self.id_level = code, id_level

    def __repr__(self):
        return "PythonCode:\n%s" % self.code

def exec_python_code(code_objects):
    code = """
__output__ = [""]*{count}

def write(s):
    __output__[__section__] += str(s)

{code}""".format(
    count = len(code_objects),
    code = '\n'.join(
    "__section__ = %d\n" % i + "".join(str(c) for c in co.code) 
            for i, co in enumerate(code_objects) ) )
    
    transient_module = imp.new_module('pypage_transient')
    exec(code, transient_module.__dict__)

    # apply indentation to output:
    for i, output in enumerate(transient_module.__output__):
        transient_module.__output__[i] = '\n'.join(' ' * code_objects[i].id_level + s for s in output.split('\n'))

    # yield the output for each chunk:
    for output in transient_module.__output__:
        yield output

def split_text(lines, multiline_delimiter_open, multiline_delimiter_close,
                         inline_delimiter_open, inline_delimiter_close):
    """ Split the text (fed in as lines) into plan-text string and PythonCode objects.
        Python code is extractacted from from multi-line delimited (e.g. <python> ... </python>) 
        and in-line delimited (<py> ... </py>) code segments and stored in PythonCode.code along 
        with indentation for multi-line delimited code segments.

        Args:
            lines: list of strings representing each line of an unprocessed HTML file
            keywords args: the delimiters

        Returns:
            A list containing either `string` or `PythonCode` objects, where 
            plain string lines have been concatenated and PythonCode.code strings 
            have been adjusted for indentation and concatenated.
    """

    re_delimiter_open  = re.compile(r"\s*%s\s*\n" % multiline_delimiter_open)
    re_delimiter_open_tag_only = re.compile(r"%s" % multiline_delimiter_open)
    re_delimiter_close = re.compile(r"\s*%s\s*\n" % multiline_delimiter_close)

    re_short_open  =  re.compile(inline_delimiter_open)
    re_short_close =  re.compile(inline_delimiter_close)

    mode_plain, mode_code = 'plain', 'code' # the 2 possible collect modes
    mode = mode_plain
    id_level = 0
    collect = ""

    result = list()
    for n, line in enumerate(lines):
        op = re_delimiter_open.match(line)
        cl = re_delimiter_close.match(line)
        ops = re_short_open.search(line)
        cls = re_short_close.search(line)

        if op:
            result.append(collect)

            collect = ""
            id_level = re_delimiter_open_tag_only.search(line).start()
            mode = mode_code

        elif cl:
            result.append( PythonCode(collect, id_level) )

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
            result.append( PythonCode(collect, 0) )

            collect = post_py

        elif mode == mode_plain:
            collect += line

        elif mode == mode_code:
            collect += line[id_level:] if len(line) > id_level else "\n"

    result.append(collect)

    return result

def pypage(input_text, verbose=False, prettify=False,
            multiline_delimiter_open  =  '<python>',
            multiline_delimiter_close = '</python>',
            inline_delimiter_open  =  '<py>',
            inline_delimiter_close = '</py>'):
    if verbose:
        print("pypage: processing %s" % input_file)

    # split the text into plain text & PythonCode chunks:
    chunks = split_text(input_text, multiline_delimiter_open, multiline_delimiter_close, inline_delimiter_open, inline_delimiter_close)

    # execute code and collect output:
    output_iter = exec_python_code( [ c for c in chunks if isinstance(c, PythonCode) ] )

    # merge the outputs and form the resulting string
    result = ''.join( next(output_iter) if isinstance(c, PythonCode) else c for c in chunks )

    if prettify:
        from bs4 import BeautifulSoup
        result = BeautifulSoup(result).prettify()

    return result

def pypage_files(*files, prepend_path='', verbose=False, prettify=False, **delimiter_override):
    return { filename : pypage( open( prepend_path + '/' + filename ).readlines() , verbose, prettify, **delimiter_override ) for filename in files }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generates static HTML pages by executing the code within <python> and <py> tags, and replacing replacing them with the content passed to write() calls.")
    parser.add_argument('input_file', type=str, help="HTML input file.")
    parser.add_argument('-o', '--output_file', nargs=1, type=str, default=None, help='Write output to output_file. Default: stdout')
    parser.add_argument('-v', '--verbose', action='store_true', help='print a short message before preprocessing')
    parser.add_argument('-p', '--prettify', action='store_true', help='prettify the resulting HTML using BeautifulSoup -- requires BeautifulSoup4')
    parser.add_argument('-y', '--multiline_delim', nargs=2, type=str, default=["<python>", "</python>"], 
        help='override the default multi-line delimiters (<python> and </python>). Specify the opening and closing long delimiters, in sequence.')
    parser.add_argument('-z' '--inline_delim', nargs=2, type=str, default=["<py>", "</py>"], 
        help='override the default in-line delimiters (<py> and </py>). Specify the opening and closing short delimiters, in sequence.')
    args = parser.parse_args()

    result = pypage( open(args.input_file).readlines(), args.verbose, args.prettify, 
        args.multiline_delim[0], args.multiline_delim[1], args.inline_delim[0], args.inline_delim[1] )

    if args.output_file:
        with open(args.output_file[0], 'w') as f:
            f.write(result)
    else:
        print(result, end="")
