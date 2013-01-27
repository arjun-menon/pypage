#!/usr/bin/python3

import sys, re

class PythonCode(object):
    """ A light-weight wrapper around `string` to detect the difference 
        between a plain old string and a string containing Python code. """

    def __init__(self, code, id_level):
        assert( type(code) == str )
        self.code, self.id_level = code, id_level

    def __repr__(self):
        return "PythonCode:\n%s" % self.code

class execPythonCode(object):
    @staticmethod
    def importCode(code,name,add_to_sys_modules=0):
        # Found this at: http://code.activestate.com/recipes/82234-importing-a-dynamically-generated-module/
        #           via: http://stackoverflow.com/questions/3614537/python-import-string-of-python-code-as-module
        """
        Import dynamically generated code as a module. code is the
        object containing the code (a string, a file handle or an
        actual compiled code object, same types as accepted by an
        exec statement). The name is the name to give to the module,
        and the final argument says wheter to add it to sys.modules
        or not. If it is added, @staticmethoda subsequent import statement using
        name will return this module. If it is not added to sys.modules
        import will try to load it in the normal fashion.

        import foo

        is equivalent to

        foofile = open("/path/to/foo.py")
        foo = importCode(foofile,"foo",1)

        Returns a newly generated module.
        """
        import sys,imp

        module = imp.new_module(name)

        exec(code, module.__dict__)
        if add_to_sys_modules:
            sys.modules[name] = module

        return module

    def __init__(self, code_objects):
        self.count = len(code_objects)

        code = """
__output__ = [""]*{count}

def write(s):
    __output__[__section__] += str(s)

{code}""".format(
        count = self.count,
        code = '\n'.join(
        "__section__ = %d\n" % i + "".join(str(c) for c in co.code) 
                for i, co in enumerate(code_objects) ) )

        self.m = self.importCode(code, "preprocessor_module")

        # apply indentation to output
        id_levels = list(map(lambda o: o.id_level, code_objects))
        for i, o in enumerate(self.m.__output__):
            self.m.__output__[i] = '\n'.join( ' ' * id_levels[i] + s for s in o.split('\n') )

    def __len__(self):
        return self.count

    class execPythonCodeOutputIterator(object):
        def __init__(self, output, length):
            self.output, self.length = output, length
            self.i = 0
        def __iter__(self):
            return self
        def __next__(self):
            if self.i < self.length:
                output_i = self.output[self.i]
                self.i += 1
                return output_i
            else:
                raise StopIteration()

    def __iter__(self):
        return self.execPythonCodeOutputIterator(self.m.__output__, self.count)


def process_python_tags(lines):
    """ Proces <python> ... </python> tags

        These tags are used when you want indentation in your Python code to 
        keep it consistent with indentation of the surrounding HTML. This 
        function removes the indentation from your code based on the amount of 
        whitespace preceding the opening <python> tag.

        Argument: list of strings representing each line of an unprocessed HTML file

        Returns: a list containing either `string` or `PythonCode` objects, where 
        plain string lines have been concatenated and PythonCode strings have been 
        adjusted for indentation and concatenated.
    """
    long_delimiter_open  =  '<python>'
    long_delimiter_close = '</python>'

    short_delimiter_open  =  '<py>'
    short_delimiter_close = '</py>'

    re_delimiter_open  = re.compile(r"\s*%s\s*\n" % long_delimiter_open)
    re_delimiter_open_tag_only = re.compile(r"%s" % long_delimiter_open)
    re_delimiter_close = re.compile(r"\s*%s\s*\n" % long_delimiter_close)

    re_short_open  =  re.compile(short_delimiter_open)
    re_short_close =  re.compile(short_delimiter_close)

    def find_indentation_level(opening_line):
        m = re_delimiter_open_tag_only.search(opening_line)
        assert(m != None)

        return m.start()

    result = list()

    mode_plain, mode_code = 'plain', 'code' # the 2 possible collect modes

    collect = ""
    id_level = 0
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

def preprocess(input_file):
    with open(input_file) as f:
        lines = f.readlines()

    result = process_python_tags(lines)

    output = execPythonCode( list(filter(lambda x: type(x) == PythonCode, result)) )
    outputIter = iter(output)

    for ri in range( len(result) ):
        if type(result[ri]) == PythonCode:
            result[ri] = next(outputIter)

    return ''.join(result)

def main(input_file, verbose=False, prettify=False):
    if verbose:
        print("Preprocessing file %s" % input_file)

    result = preprocess(input_file)

    if prettify:
        from bs4 import BeautifulSoup
        result = BeautifulSoup(result).prettify()

    return result

def preprocess_multiple_files(path, *files, verbose=False, prettify=False):
    return { filename : main(path+'/'+filename, verbose, prettify) for filename in files }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="""
Generates static HTML pages by executing the code within <python> and <py> tags, and replacing replacing them with the content passed to write() calls.""")
    parser.add_argument('input_file', type=str, help="HTML input file.")
    parser.add_argument('-v', '--verbose', action='store_true', help='print a short message before preprocessing')
    parser.add_argument('-p', '--prettify', action='store_true', help='prettify the resulting HTML using BeautifulSoup -- requires BeautifulSoup4')
    args = parser.parse_args()

    print( main(args.input_file, args.verbose, args.prettify) , end='' )
