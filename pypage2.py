#!/usr/bin/python

# Copyright (C) 2014 Arjun G. Menon

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import itertools, sys, time, os

class RootNode(object):
    """
    Root node of the abstract syntax tree.
    """
    def __init__(self):
        self.children = list()

    def __repr__(self):
        return "Root:\n" + indent('\n'.join(repr(child) for child in self.children))

class TextNode(object):
    """
    A leaf node containing text.
    """
    def __init__(self):
        self.src = str()

    def __repr__(self):
        return 'Text:\n' + indent_filtered(self.src)

class TagNode(object):
    """
    A tag node.

    Members:
        src: the body of the tag (content between delimiters)
        loc: location of the opening delimiter, in a tuple of 
             the form: (line_number, column_number)

    Subclasses must have:
        open_delim:  string containig the opening delimiter
        close_delim: string containig the closing delimiter
    """
    def __init__(self, loc):
        self.src = str()
        self.loc = loc

class CodeTag(TagNode):
    """
    A leaf node containing Python code.
    """
    open_delim, close_delim = '{{', '}}'

    def __init__(self, loc):
        super(CodeTag, self).__init__(loc)

    def __repr__(self):
        return 'Code:\n' + indent_filtered(self.src)

class BlockTag(TagNode):
    """
    A block tag contains sepcial directives and subsumes 
    a part of the document into `self.children`.

    Members:
        children: child nodes belonging to this node
    """
    open_delim, close_delim = '{%', '%}'

    def __init__(self, loc):
        super(BlockTag, self).__init__(loc)
        self.children = list()

    def __repr__(self):
        return "{%% %s %%}:\n" % self.src + indent('\n'.join(repr(child) for child in self.children))

    def run(self, pe):
        raise Exception("BlockTag.run not implemented in %r" % type(self))

class ForTag(BlockTag):
    """
    The for loop tag. {% for ... in ... %}

    The `for` expression is evaluated in/as a generator expression.
    """
    tag_startswith = 'for '

    @staticmethod
    def identify(src):
        return src.strip().startswith(ForTag.tag_startswith)

    def __init__(self, node):
        super(ForTag, self).__init__(node.loc)
        self.src = node.src.strip()

        self.targets = self._find_targets()
        self.genexpr = self._construct_generator_expression()

    def run(self, pe):
        output = str()

        conflicting = set(pe.env.keys()) & set(self.targets)
        backup = { x : pe.env[x] for x in conflicting }

        gen = pe.raw_eval(self.genexpr)

        def get_for_targets():
            result = next(gen)

            if len(self.targets) == 1:
                return { self.targets[0] : result }
            else:
                return { k : v for k, v in zip( self.targets, result ) }

        while True:
            try:
                pe.env.update( get_for_targets() )

                output += exec_tree(self, pe)

            except StopIteration:
                break

        for target in self.targets:
            del pe.env[target]

        pe.env.update(backup)

        return output

    def _find_targets(self):
        """
        Some of the Python grammar rules behind generator expressions are:

            generator_expression ::=  "(" expression comp_for ")"
            comprehension ::=  expression comp_for
            comp_for      ::=  "for" target_list "in" or_test [comp_iter]
            comp_iter     ::=  comp_for | comp_if
            comp_if       ::=  "if" expression_nocond [comp_iter]
            target_list   ::=  target ("," target)* [","]

        The grammar we are permitting here will be a subset of the full Python grammar. 
        We will expect a comma-separated list of identifiers between 'for' and 'in'.

        All target lists will be combined into the `targets` set, and returned.
        """

        targets = set()
        tokens = self.src.split()

        while tokens:
            try:
                for_index = tokens.index('for')
                in_index = tokens.index('in')
            except ValueError:
                break

            target_list_str = ''.join(tokens[for_index + 1 : in_index])
            tokens = tokens[in_index+1:]

            target_list = [''.join(c for c in s if c.isalnum() or c=='_') for s in target_list_str.split(',')]
            target_set = set( itertools.ifilter(lambda s: isidentifier(s), target_list) )
            targets |= target_set
        
        if not targets:
            raise IncorrectForTag

        return tuple(sorted(targets))

    def _construct_generator_expression(self):
        return "((%s) %s)" % (', '.join(self.targets), self.src)

class WhileTag(BlockTag):
    """
    The while loop tag. {% while ... %}
    """
    tag_startswith = 'while '
    loop_time_limit = 2.0 # seconds

    dofirst_startswith = 'dofirst '
    slow_endswith = 'slow'

    @staticmethod
    def identify(src):
        return src.strip().startswith(WhileTag.tag_startswith)

    def __init__(self, node):
        super(WhileTag, self).__init__(node.loc)
        self.src = node.src.strip()
        self.expr = self.src[len(self.tag_startswith):].strip()

        # Check if there's a dofirst:
        if self.expr.startswith(self.dofirst_startswith):
            self.expr = self.expr[len(self.dofirst_startswith) : ].strip()
            self.dofirst = True
        else:
            self.dofirst = False

        # Check if this loop is slow:
        if self.expr.endswith(self.slow_endswith):
            self.expr = self.expr[ : -len(self.slow_endswith)].strip()
            self.slow = True
        else:
            self.slow = False

    def run(self, pe):
        output = str()

        if self.dofirst:
            output += exec_tree(self, pe)

        loop_start_time = time.time()

        while pe.raw_eval(self.expr):
            output += exec_tree(self, pe)

            if not self.slow and time.time() - loop_start_time > 2.0:
                # TODO: more elegant handling
                print "Loop '%s' terminated." % self.expr
                break

        return output

class ConditionalTag(BlockTag):
    """
    Implements `if`, `elif` and `else` conditional block tags.
    """
    tag_if = 'if'
    tag_elif = 'elif'
    tag_else = 'else'
    tag_startswith_options = [tag_if, tag_elif, tag_else]

    @staticmethod
    def identify(src):
        return bool(any(src.strip().startswith(sw) for sw in ConditionalTag.tag_startswith_options))

    def __init__(self, node):
        super(ConditionalTag, self).__init__(node.loc)
        self.src = node.src.strip()

        self.tag_startswith = first_true(lambda sw: self.src.startswith(sw), self.tag_startswith_options)
        self.expr = self.src[len(self.tag_startswith):].strip()

        if self.tag_startswith == self.tag_else:
            if self.expr:
                raise PypageSyntaxError("An `else` tag cannot have an expression.")
            self.expr = 'True'

        if not self.expr:
            raise ExpressionMissing(self)

        self.continuation = None

    def __repr__(self):
        return "{%% %s %%}:\n" % (self.src) + indent(
            '\n'.join(repr(child) for child in self.children)) + (
            '\n' + indent(repr(self.continuation)) if self.continuation else '')

    def run(self, pe):
        if pe.raw_eval(self.expr):
            output = exec_tree(self, pe)
        else:
            output = self.continuation.run(pe)

        return output

class CaptureTag(BlockTag):
    """
    Capture all content within this tag, and bind it to a variable.
    """
    tag_startswith = 'capture '

    @staticmethod
    def identify(src):
        return src.strip().startswith(CaptureTag.tag_startswith)

    def __init__(self, node):
        super(CaptureTag, self).__init__(node.loc)
        self.src = node.src.strip()

        self.varname = self.src[len(self.tag_startswith):].strip()

        if not isidentifier(self.varname):
            raise PypageSyntaxError("Incorrect CommentTag: '%s' is not a valid Python identifier." % self.varname)

    def __repr__(self):
        return "{%% %s %%}:\n" % self.src + indent('\n'.join(repr(child) for child in self.children))

    def run(self, pe):
        capture_output = exec_tree(self, pe)
        pe.env[self.varname] = capture_output
        return ""

class CommentTag(BlockTag):
    """
    The comment tag. All content within this tag is ignored.
    """
    tag_startswith = 'comment'

    @staticmethod
    def identify(src):
        return src.strip().startswith(CommentTag.tag_startswith)

    def __init__(self, node):
        super(CommentTag, self).__init__(node.loc)
        self.src = node.src.strip()

    def __repr__(self):
        return "{%% %s %%}:\n" % self.src + indent('\n'.join(repr(child) for child in self.children))

    def run(self, pe):
        return ""

class CloseTag(BlockTag):
    """
    Signifies a closing tag. A CloseTag has a whitespace-only body, i.e.: {%    %}
    """
    @staticmethod
    def identify(src):
        "Return `True` if `src` denotes a closing tag."
        return not src.strip()

    def __init__(self, node):
        super(CloseTag, self).__init__(node.loc)

    def __repr__(self):
        return 'CloseTag.\n'

class PypageSyntaxError(Exception):
    def __init__(self, description='undefined'):
        self.description = description
    def __str__(self):
        return "Syntax Error: " + self.description

class IncompleteTagNode(PypageSyntaxError):
    def __init__(self, node):
        self.description = "Missing closing '%s' for opening '%s' at line %d, column %d." % ( 
            node.close_delim, node.open_delim, node.loc[0], node.loc[1])

class MultiLineTag(PypageSyntaxError):
    def __init__(self, node):
        self.description = "The tag starting at line %d, column %d spans multiple lines. This is not permitted. \
All tags ('%s ... %s') must be on one line." % (node.loc[0], node.loc[1], node.open_delim, node.close_delim)

class UnboundCloseTag(PypageSyntaxError):
    def __init__(self, node):
        self.description = "Unbound closing tag '%s%s%s' at line %d, column %d." % (
           node.open_delim, node.src, node.close_delim, node.loc[0], node.loc[1])

class UnclosedTag(PypageSyntaxError):
    def __init__(self, node):
        self.description = "Missing closing '%s %s' tag for opening '%s%s%s' at line %d, column %d." % (
            node.open_delim, node.close_delim, node.open_delim, node.src, node.close_delim, node.loc[0], node.loc[1])

class ExpressionMissing(PypageSyntaxError):
    def __init__(self, node):
        self.description = "Expression missing in `%s` tag at line %d, column %d." % (node.tag_startswith, node.loc[0], node.loc[1])

class ElifOrElseWithoutIf(PypageSyntaxError):
    def __init__(self, node):
        self.description = "Missing initial `if` tag for conditional `%s` tag at line %d, column %d." % (node.tag_startswith, node.loc[0], node.loc[1])

class IncorrectForTag(PypageSyntaxError):
    def __init__(self, node):
        self.description = "Incorrect `for` tag syntax: '%s'" % node.src

class UnknownTag(PypageSyntaxError):
    def __init__(self, node):
        self.description = "Unknown tag '%s%s%s' at line %d, column %d." % (
            node.open_delim, node.src, node.close_delim, node.loc[0], node.loc[1])

def filterlines(text):
    return '\n'.join( filter(lambda line: line.strip(), text.splitlines()) )

def prepend(text, prefix):
    return '\n'.join( prefix + line for line in text.splitlines() )

def indent(text, level=1, width=4):
    return prepend(text, ' '  * width * level)

def indent_filtered(text, level=1, width=4):
    return prepend(filterlines(text), ' '  * width * level)

def first_true(function, sequence):
    """
    Return the first element of sequence for which 
    the result of applying function is True.
    Returns None if no element returns True.
    """
    for item in sequence:
        if function(item):
            return item

def isidentifier(s):
    # As per: https://docs.python.org/2/reference/lexical_analysis.html#identifiers
    return all( [bool(s) and (s[0].isalpha() or s[0]=='_')] + map(lambda c: c.isalnum() or c=='_', s) )

def lex(src):
    tagNodeTypes = [CodeTag, BlockTag]
    open_delims = { t.open_delim : t for t in tagNodeTypes }
    blockTagTypes = [ForTag, WhileTag, ConditionalTag, CaptureTag, CommentTag, CloseTag]

    tokens = list()
    node = None

    i = 0
    line, line_i = 1, 0
    while i < len(src) - 1:
        c  = src[i]
        c2 = src[i] + src[i+1]

        if c == '\n':
            line += 1
            line_i = i
        c_pos_in_line = i - line_i

        # We don't belong to any node, so:
        #   - Look for any TagNode open_delims
        #   - If there aren't any, create a TextNode
        if not node:
            if c2 in open_delims.keys():
                node = open_delims[c2]((line, c_pos_in_line))
                i += 2
                continue
            else:
                node =  TextNode()

        # If in TextNode, look for open_delims
        if isinstance(node, TextNode) and c2 in open_delims.keys():
            tokens.append(node)
            node = open_delims[c2]( (line, c_pos_in_line) )
            i += 2
            continue

        # If in TagNode, look for close_delim
        if isinstance(node, TagNode) and c2 == node.close_delim:
            if isinstance(node, BlockTag):
                if '\n' in node.src:
                    # a BlockTag must be on a single line
                    raise MultiLineTag(node)

                # Identify the block tag type, and convert it
                nodeType = first_true(lambda t: t.identify(node.src), blockTagTypes)
                if nodeType == None:
                    raise UnknownTag(node)
                else:
                    node = nodeType(node)

            tokens.append(node)
            node = None
            i += 2
            continue

        # Skipe escaped braces
        if c2 == '\{' or c2 == '\}':
            node.src += c2[1]
            i += 2
            continue

        if i < len(src) - 2:
            # Consume a character of source
            node.src += c
            i += 1
        else:
            # If we're at the second-to-last character, consume two
            node.src += c2
            i += 2

    if node:
        if isinstance(node, TextNode):
            tokens.append(node)
            node = None
        else:
            raise IncompleteTagNode(node)

    return tokens

def prune_tokens(tokens):
    """
    Strip away newlines before or after a tag if there is nothing 
    but whitespace between the newline and the delimiter.
    """
    new_tokens = list()

    # TODO

    return tokens

def build_tree(node, tokens_iterator):
    try:
        while True:
            tok = next(tokens_iterator)

            if isinstance(tok, ConditionalTag):
                if tok.tag_startswith == ConditionalTag.tag_elif or tok.tag_startswith == ConditionalTag.tag_else:
                    if node.tag_startswith == ConditionalTag.tag_if or node.tag_startswith == ConditionalTag.tag_elif:
                        node.continuation = tok
                        build_tree(tok, tokens_iterator)
                        return
                    else:
                        raise ElifOrElseWithoutIf(tok)

                elif tok.tag_startswith == ConditionalTag.tag_else:
                    return

            if isinstance(tok, CloseTag):
                if isinstance(node, BlockTag):
                    return
                else:
                    raise UnboundCloseTag(tok)

            node.children.append(tok)

            if isinstance(tok, BlockTag):
                build_tree(tok, tokens_iterator)
    
    except StopIteration:
        if not isinstance(node, RootNode):
            raise UnclosedTag(node)

def parse(src):
    tokens = lex(src)
    tokens = prune_tokens(tokens)

    tree = RootNode()
    build_tree( tree, iter(tokens) )

    return tree

class PypageExec(object):
    """
    Execute or evaluate code, while persisting the environment.
    """
    def __init__(self, env=dict(), name='pypage_transient'):
        import __builtin__
        self.env = env
        self.env['__builtins__'] = __builtin__
        self.env['__package__'] = None
        self.env['__name__'] = name
        self.env['__doc__'] = None

        self.env['write'] = self.write

    def write(self, text):
        self.output += str(text)

    def run(self, code, loc):
        code_lines = code.split('\n')
        self.output = str()

        if len(code_lines) > 1:
            # Determine indentation level
            indentation_len = len(code_lines[1]) - len(code_lines[1].strip())
            indentation_chars = code_lines[1][:indentation_len]

            for i in range(1, len(code_lines)):
                # Ensure all code lines have the same base indendation:
                if code_lines[i][:indentation_len] != indentation_chars and code_lines[i].strip():
                    raise PypageSyntaxError("Mismtaching indentation in line %d: %r. \
Indentation must match the second line of code in the tag (i.e. line %d). \
The expected minimum indentation is: %r (%d characters)." % 
(loc[0] + i, code_lines[i], loc[0] +1, indentation_chars, len(indentation_chars)))

                # Strip away the base indentation:
                code_lines[i] = code_lines[i][indentation_len:]

            code = '\n'.join(code_lines)
            exec code in self.env

            # Add the base indentation to the output
            self.output = '\n'.join(
                indentation_chars + output_line if output_line.strip() else output_line 
                    for output_line in self.output.split('\n'))

            return self.output
        else:
            if ';' in code:
                exec code in self.env
                return self.output
            else:
                return str( eval(code, self.env) )

    def raw_eval(self, code):
        "Evaluate an expression, and return the result raw (without stringifying it)."
        return eval(code, self.env)

def exec_tree(parent_node, pe):
    output = str()

    for node in parent_node.children:

        if isinstance(node, TextNode):
            output += node.src

        elif isinstance(node, CodeTag):
            output += pe.run(node.src, node.loc)

        elif isinstance(node, BlockTag):
            output += node.run(pe)

    return output

def execute(src):
    tree = parse(src)
    #print tree
    pe = PypageExec()
    output = exec_tree(tree, pe)
    print output

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Light-weight Python templating engine.")
    parser.add_argument('source_file', type=str, help="Source file name")
    parser.add_argument('-t', '--target_file', nargs=1, type=str, default=None, help='Target file name; default: stdout')
    args = parser.parse_args()

    if not os.path.exists(args.source_file):
        print >> sys.stderr, "File %s does not exist." % repr(args.source_file)
        sys.exit(1)

    with open(args.source_file, 'r') as source_file:
        source = source_file.read()

    try:
        execute(source)
    except PypageSyntaxError as error:
        print error

