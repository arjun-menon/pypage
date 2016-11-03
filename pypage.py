#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) Arjun G. Menon

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import string, sys, time, os, cgi, json

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
        num_of_lines = 1 + self.src.count('\n')
        if self.src.endswith('\n'):
            num_of_lines -= 1
        if self.src.startswith('\n'):
            num_of_lines -= 1

        if num_of_lines <= 1:
            return 'Text:\n' + indent( repr(self.src) )
        else:
            return 'Text-multiline:\n' + indent(self.src)

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
    escape_delims = {'\{':'{', '\}':'}'}

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
        return 'Code-%s:\n' % ('inline' if '\n' not in self.src else 'block') + indent(self.src)

class CommentTag(TagNode):
    """
    A leaf node containing ignored content.
    """
    open_delim, close_delim = '{#', '#}'

    def __init__(self, loc):
        super(CommentTag, self).__init__(loc)

    def __repr__(self):
        return 'Comment-raw:\n' + indent(self.src)

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
        return "%s %s %s:\n" % (self.open_delim, self.src, self.close_delim) + indent('\n'.join(repr(child) for child in self.children))

    def run(self, pe):
        raise Exception("BlockTag.run not implemented in %r" % type(self))

class ConditionalBlock(BlockTag):
    """
    Implements `if`, `elif` and `else` conditional block tags.
    """
    tag_if = 'if'
    tag_elif = 'elif'
    tag_else = 'else'
    tag_options = [tag_if, tag_elif, tag_else]
    tag_startswith = 'if' # for compatibility with EndBlockTag

    @staticmethod
    def identify(src):
        return bool(any(src.strip().startswith(sw) for sw in ConditionalBlock.tag_options))

    def __init__(self, node):
        super(ConditionalBlock, self).__init__(node.loc)
        self.src = node.src.strip()

        self.tag_type = first_true(lambda sw: self.src.startswith(sw), self.tag_options)
        self.expr = self.src[len(self.tag_type):].strip()

        if self.tag_type == self.tag_else:
            if self.expr:
                raise ExpressionProhibited(self)
            self.expr = 'True'

        if not self.expr:
            raise ExpressionMissing(self)

        self.continuation = None

    def __repr__(self):
        return "%s %s %s:\n" % (self.open_delim, self.src, self.close_delim) + indent(
            '\n'.join(repr(child) for child in self.children)) + (
            '\n' + indent(repr(self.continuation)) if self.continuation else '')

    def run(self, pe):
        output = str()

        if pe.raw_eval(self.expr):
            output = exec_tree(self, pe)
        elif self.continuation:
            output = self.continuation.run(pe)

        return output

class ForBlock(BlockTag):
    """
    The for loop tag. {% for ... in ... %}

    The `for` expression is evaluated in/as a generator expression.
    """
    tag_startswith = 'for '

    @staticmethod
    def identify(src):
        return src.strip().startswith(ForBlock.tag_startswith)

    def __init__(self, node):
        super(ForBlock, self).__init__(node.loc)
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
                return dict( zip( self.targets, result ) )

        while True:
            try:
                pe.env.update( get_for_targets() )

                output += exec_tree(self, pe)

            except StopIteration:
                break

        for target in self.targets:
            if target in pe.env:
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
            target_set = set( filter(lambda s: isidentifier(s), target_list) )
            targets |= target_set

        if not targets:
            raise IncorrectForTag

        return tuple(sorted(targets))

    def _construct_generator_expression(self):
        return "((%s) %s)" % (', '.join(self.targets), self.src)

class WhileBlock(BlockTag):
    """
    The while loop tag. {% while ... %}
    """
    tag_startswith = 'while '
    loop_time_limit = 2.0 # seconds

    dofirst_startswith = 'dofirst '
    slow_endswith = 'slow'

    @staticmethod
    def identify(src):
        return src.strip().startswith(WhileBlock.tag_startswith)

    def __init__(self, node):
        super(WhileBlock, self).__init__(node.loc)
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

            if not self.slow and time.time() - loop_start_time > WhileBlock.loop_time_limit:
                # TODO: more elegant handling
                print("Loop '%s' terminated." % self.expr, file=sys.stderr)
                break

        return output

class CaptureBlock(BlockTag):
    """
    Capture all content within this tag, and bind it to a variable.
    """
    tag_startswith = 'capture '

    @staticmethod
    def identify(src):
        return src.strip().startswith(CaptureBlock.tag_startswith)

    def __init__(self, node):
        super(CaptureBlock, self).__init__(node.loc)
        self.src = node.src.strip()

        self.varname = self.src[len(self.tag_startswith):].strip()

        if not isidentifier(self.varname):
            raise InvalidCaptureBlockVariableName(self.varname)

    def run(self, pe):
        capture_output = exec_tree(self, pe)
        pe.env[self.varname] = capture_output
        return ""

class CommentBlock(BlockTag):
    """
    The comment tag. All content within this tag is ignored.
    """
    tag_startswith = 'comment'

    @staticmethod
    def identify(src):
        return src.strip().startswith(CommentBlock.tag_startswith)

    def __init__(self, node):
        super(CommentBlock, self).__init__(node.loc)
        self.src = node.src

    def __repr__(self):
        return "Comment:\n" + indent('\n'.join(repr(child) for child in self.children))

    def run(self, pe):
        return ""

class EndBlockTag(BlockTag):
    """
    Signifies a closing tag.

    An EndBlockTag that has a whitespace-only body (e.g. {%    %}) can
    close any kind of block. On the other hand, an EndBlockTag that
    specifies the name of a type of block, using the 'end'+block_type_name
    format (e.g. {% endif %}, {% endfor %}) can only close that kind of block.
    If the block type name does not match the block it is trying to close,
    a MismatchingEndBlockTag exception will be thrown.
    """
    @staticmethod
    def identify(src):
        "Return `True` if `src` denotes a closing tag."
        name = src.strip()
        if name == "":
            return True
        elif name.startswith('end'):
            return True

    def __init__(self, node):
        super(EndBlockTag, self).__init__(node.loc)
        self.src = node.src
        self.tag_to_end = self.src.strip()[3:]

    def does_end(self, node):
        if self.tag_to_end == "":
            return True
        elif self.tag_to_end == node.tag_startswith.strip():
            return True
        else:
            return False

    def __repr__(self):
        return 'EndBlockTag.\n'

class PypageSyntaxError(Exception):
    def __init__(self, description='undefined'):
        self.description = description
    def __str__(self):
        return "Syntax Error: " + self.description

class IncompleteTagNode(PypageSyntaxError):
    def __init__(self, node):
        self.description = "Missing closing '%s' for opening '%s' at line %d, column %d." % (
            node.close_delim, node.open_delim, node.loc[0], node.loc[1])

class MultiLineBlockTag(PypageSyntaxError):
    def __init__(self, node):
        self.description = "The tag starting at line %d, column %d, spans multiple lines. This is not permitted. \
Block tags ('%s ... %s') must be on one line." % (node.loc[0], node.loc[1], node.open_delim, node.close_delim)

class UnboundEndBlockTag(PypageSyntaxError):
    def __init__(self, node):
        self.description = "Unbound closing tag '%s%s%s' at line %d, column %d." % (
           node.open_delim, node.src, node.close_delim, node.loc[0], node.loc[1])

class MismatchingEndBlockTag(PypageSyntaxError):
    def __init__(self, end_tag, block_tag):
        self.description = "The end tag %s%s%s at line %d, column %d should be %s end%s %s, as it corresponds to the block tag %s %s %s at line %d, column %d." % (
            end_tag.open_delim, end_tag.src, end_tag.close_delim, end_tag.loc[0], end_tag.loc[1],
            end_tag.open_delim, block_tag.tag_startswith.strip(), end_tag.close_delim,
            block_tag.open_delim, block_tag.src, block_tag.close_delim, block_tag.loc[0], block_tag.loc[1])

class MismatchingIndentation(PypageSyntaxError):
    def __init__(self, mismatching_line_num, mismatching_line_code, second_line_num, indentation_chars):
        self.description = "Mismtaching indentation in line %d: %r. \
Indentation must match the second line of code in the tag (i.e. line %d). \
The expected minimum indentation is: %r (%d characters)." % (
    mismatching_line_num, mismatching_line_code, second_line_num, indentation_chars, len(indentation_chars))

class UnclosedTag(PypageSyntaxError):
    def __init__(self, node):
        self.description = "Missing closing '%s %s' tag for opening '%s%s%s' at line %d, column %d." % (
            node.open_delim, node.close_delim, node.open_delim, node.src, node.close_delim, node.loc[0], node.loc[1])

class ExpressionMissing(PypageSyntaxError):
    def __init__(self, node):
        self.description = "Expression missing in `%s` tag at line %d, column %d." % (node.tag_startswith, node.loc[0], node.loc[1])

class ExpressionProhibited(PypageSyntaxError):
    def __init__(self, node):
        self.description = "The `%s` tag at line %d, column %d, must appear by itself without any text next to it." % (node.tag_startswith, node.loc[0], node.loc[1])

class ElifOrElseWithoutIf(PypageSyntaxError):
    def __init__(self, node):
        self.description = "Missing initial `if` tag for conditional `%s` tag at line %d, column %d." % (node.tag_startswith, node.loc[0], node.loc[1])

class IncorrectForTag(PypageSyntaxError):
    def __init__(self, node):
        self.description = "Incorrect `for` tag syntax: '%s'" % node.src

class InvalidCaptureBlockVariableName(PypageSyntaxError):
    def __init__(self, varname):
        self.description = "Incorrect CaptureBlock: '%s' is not a valid Python variable name." % varname

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
    return all( [bool(s) and (s[0].isalpha() or s[0]=='_')] +
        list(map(lambda c: c.isalnum() or c=='_', s)) )

def first_occurrence(text, c):
    "Position of the first occurence of character ``c`` in ``text``."
    for i in range(len(text)):
        if text[i] == c:
            return i

def last_occurrence(text, c):
    "Position of the last occurence of character ``c`` in ``text``."
    for i in range(len(text)-1, -1, -1):
        if text[i] == c:
            return i

def lex(src):
    assert isinstance(src, str)

    tagNodeTypes = TagNode.__subclasses__()
    open_delims = { t.open_delim : t for t in tagNodeTypes }
    comment_tag_depth = 0

    blockTagTypes = BlockTag.__subclasses__()

    tokens = list()
    node = None

    i = 0
    line_number, newline_position = 1, 0
    while i < len(src) - 1:
        c  = src[i]
        c2 = src[i] + src[i+1]

        if c == '\n':
            line_number += 1
            newline_position = i
        column_number = i - newline_position

        # We don't belong to any node, so:
        #   - Look for any TagNode open_delims
        #   - If there aren't any, create a TextNode
        if not node:
            if c2 in open_delims.keys():
                node = open_delims[c2]((line_number, column_number))
                i += 2
                continue
            else:
                node =  TextNode()

        # If in TextNode, look for open_delims
        if isinstance(node, TextNode) and c2 in open_delims.keys():
            tokens.append(node)
            node = open_delims[c2]( (line_number, column_number) )
            if isinstance(node, CommentTag):
                comment_tag_depth += 1

            i += 2
            continue

        # Handle nested comment tags (e.g. {# ... {# ... #} ... #})
        if isinstance(node, CommentTag) and c2 == CommentTag.open_delim:
            comment_tag_depth += 1
            node.src += c2

            i += 2
            continue

        # If in TagNode, look for close_delim
        if isinstance(node, TagNode) and c2 == node.close_delim:
            if isinstance(node, BlockTag):
                if '\n' in node.src:
                    # a BlockTag must be on a single line
                    raise MultiLineBlockTag(node)

                nodeType = first_true(lambda t: t.identify(node.src), blockTagTypes)
                if nodeType == None:
                    raise UnknownTag(node)
                else:
                    node = nodeType(node)

            if isinstance(node, CommentTag):
                comment_tag_depth -= 1

                if comment_tag_depth != 0:
                    # skip this comment close tag
                    node.src += c2

                    i += 2
                    continue

            tokens.append(node)
            node = None

            i += 2
            continue

        # Skip escaped characters
        if c2 in TagNode.escape_delims:
            node.src += TagNode.escape_delims[c2]

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

def remove_whitespace_from_tokens(tokens):
    """
    Strip away the leading and trailing whitespace surrounding a tag.
    """
    stripped_prev = False
    for i in range(len(tokens)):
        if isinstance(tokens[i], TagNode):

            # Check if the previous token is a TextNode:
            leading_text, prev_nl_pos = [], None
            if i > 0 and isinstance(tokens[i-1], TextNode):
                prev_nl_pos = last_occurrence(tokens[i-1].src, '\n')
                if prev_nl_pos != None:
                    leading_text = tokens[i-1].src[prev_nl_pos+1:]
                else:
                    leading_text = tokens[i-1].src

            # Check if the next token is a TextNode:
            trailing_text, next_nl_pos = [], None
            if i < (len(tokens) - 1) and isinstance(tokens[i+1], TextNode):
                next_nl_pos = first_occurrence(tokens[i+1].src, '\n')
                if next_nl_pos != None:
                    trailing_text = tokens[i+1].src[:next_nl_pos+1]
                else:
                    trailing_text = tokens[i+1].src

            should_strip = all(c in string.whitespace for c in leading_text) and all(
                               c in string.whitespace for c in trailing_text) and not (
                               isinstance(tokens[i], CodeTag) and '\n' not in tokens[i].src )

            if should_strip:
                if prev_nl_pos != None:
                    tokens[i-1].src = tokens[i-1].src[:prev_nl_pos+1]

                if next_nl_pos != None:
                    tokens[i+1].src = tokens[i+1].src[next_nl_pos+1:]

                if stripped_prev and i-2 >= 0:
                    if isinstance(tokens[i-1], TextNode) and isinstance(tokens[i-2], TagNode):
                        if '\n' not in tokens[i-1].src and all(c in string.whitespace for c in tokens[i-1].src):
                            tokens[i-1].src = ''

            stripped_prev = should_strip

def prune_tokens(tokens):
    remove_whitespace_from_tokens(tokens)

    # Discard empty TextNode nodes
    new_tokens = list()
    for token in tokens:
        if not( isinstance(token, TextNode) and not token.src ):
            new_tokens.append(token)

    return new_tokens

def build_tree(node, tokens_iterator):
    try:
        while True:
            tok = next(tokens_iterator)

            if isinstance(tok, ConditionalBlock):
                if tok.tag_type == ConditionalBlock.tag_elif or tok.tag_type == ConditionalBlock.tag_else:
                    if node.tag_type == ConditionalBlock.tag_if or node.tag_type == ConditionalBlock.tag_elif:
                        node.continuation = tok
                        build_tree(tok, tokens_iterator)
                        return
                    else:
                        raise ElifOrElseWithoutIf(tok)

                elif tok.tag_type == ConditionalBlock.tag_else:
                    return

            if isinstance(tok, EndBlockTag):
                if isinstance(node, BlockTag):
                    if tok.does_end(node):
                        return
                    else:
                        raise MismatchingEndBlockTag(tok, node)
                else:
                    raise UnboundEndBlockTag(tok)

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
    def __init__(self, seed_env):
        self.env = dict()
        self.env['__package__'] = None
        self.env['__name__'] = 'pypage_code'
        self.env['__doc__'] = None

        self.env.update(seed_env)

        self.env['write'] = self.write
        self.env['escape'] = cgi.escape

    def write(self, *args, **kwargs):
        """Writes *args to output.

        Optional keyword arguments: end = '\n', sep = ' ', escape = False

        Before writing each element of *args to output, end is appended to
        it, and all the elemented are joined using sep. If escape is True,
        then cgi.escape is applied on each element of *args.
        """

        def kwarg(name):
            if name in kwargs:
                return kwargs[name]

        def get_kwarg(name, default):
            return kwargs[name] if name in kwargs else default

        sep = str( get_kwarg('sep',  ' ') )
        end = str( get_kwarg('end', '\n') )
        escape = get_kwarg('escape', False)

        self.output += sep.join(cgi.escape(arg) if escape else str(arg) + end for arg in args)

    def run(self, code, loc):
        code_lines = code.split('\n')
        self.output = str()

        if len(code_lines) > 1:
            # Determine indentation level
            indentation_len = len(code_lines[1]) - len(code_lines[1].strip())
            indentation_chars = code_lines[1][:indentation_len]

            for i in range(1, len(code_lines)):
                # Ensure all code lines have the same base indentation:
                if code_lines[i][:indentation_len] != indentation_chars and code_lines[i].strip():
                    raise MismatchingIndentation(loc[0] + i, code_lines[i], loc[0] +1, indentation_chars)

                # Strip away the base indentation:
                code_lines[i] = code_lines[i][indentation_len:]

            code = '\n'.join(code_lines)
            self._exec(code)

            # Add the base indentation to the output
            self.output = '\n'.join(
                indentation_chars + output_line if output_line.strip() else output_line
                    for output_line in self.output.split('\n'))

            return self.output
        else:
            result = eval(code, self.env)

            if result:
                return str(result)
            else:
                # self.output will most likely be an empty string,
                # unless, write(...) was invoked within the {{...}}
                return self.output

    def _exec(self, code):
        # Workaround for a bug in early versions of Python 2.7 and PyPy2.7
        # that causes a syntax error: https://bugs.python.org/issue21591
        exec(code, self.env)

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

def pypage(source, seed_env=dict()):
    """pypage(source) -> output

    Takes source, transforms it and returns it.
    """
    tree = parse(source)
    pe = PypageExec(seed_env)
    return exec_tree(tree, pe)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Light-weight Python templating engine.")
    parser.add_argument('source_file', type=str, help="Source file name. Use - to read from stdin.")
    parser.add_argument('-o', '--output_file', nargs=1, type=str, default=None, help='output file name; default: stdout')
    parser.add_argument('-d', '--data', nargs=1, type=str, default=None, help='additional data to pass to the environment')
    parser.add_argument('--tree', action='store_true', help='print the abstract syntax tree and exit')
    args = parser.parse_args()

    if args.source_file == '-':
        source = sys.stdin.read()
    else:
        if os.path.exists(args.source_file):
            with open(args.source_file, 'r') as source_file:
                source = source_file.read()
        else:
            print("File %s does not exist." % repr(args.source_file), file=sys.stderr)
            sys.exit(1)

    try:
        tree = parse(source)

        if args.tree:
            print(tree)
            sys.exit(0)

        data = dict()
        if args.data:
            data = json.loads(args.data[0])
        pe = PypageExec(data)

        output = exec_tree(tree, pe)

    except PypageSyntaxError as error:
        print(error, file=sys.stderr)
        sys.exit(1)

    output_file = args.output_file[0] if args.output_file else None

    if not output_file:
        output_file = sys.stdout
    else:
        output_file = open(output_file, 'w')

    with output_file:
        output_file.write(output)

if __name__ == "__main__":
    main()
