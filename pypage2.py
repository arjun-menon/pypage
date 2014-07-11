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

import string, sys, os

def indent(lines, level=1, spaces=4):
    return '\n'.join( ' '  * spaces * level + line for line in lines.splitlines())

def indent2(lines, level=1, spaces=4):
    return '\n'.join( ' '  * spaces * level + line for line in lines.split('\n'))

class RootNode(object):
    def __init__(self):
        self.children = list()
    def __repr__(self):
        return "Tree:\n" + indent('\n'.join(repr(child) for child in self.children))

class TextNode(object):
    """
    A leaf node containing text.
    """
    def __init__(self):
        self.src = str()
    def __repr__(self):
        return 'Text:\n' + indent(self.src) + '\n'

class DelimitedNode(object):
    """
    A type representing all delimited nodes.

    Derived classes must have:
        open_delim: string containig the opening delimiter
        close_delim: string containig the closing delimiter

        src: the body of the delimited tag
        loc: location (line & column numbers) of the 
             opening delimiter in the source
    """
    def __init__(self):
        pass

class CodeNode(DelimitedNode):
    """
    A leaf node containing Python code.
    """
    open_delim, close_delim = '{{', '}}'

    def __init__(self, loc):
        self.loc = loc
        self.src = str()
    def __repr__(self):
        return 'Code:\n' + indent(self.src) + '\n'

class TagNode(DelimitedNode):
    """
    A node containing special directives.
    """
    open_delim, close_delim = '{%', '%}'

    def __init__(self, loc):
        self.loc = loc
        self.src = str()
        self.children = list()
    def __repr__(self):
        return "{%% %s %%}:\n" % self.src + indent('\n'.join(repr(child) for child in self.children))

class CloseTagNode(object):
    """
    A TagNode with an empty body is replaced with this.
    """
    def __init__(self):
        self.src = None
    def __repr__(self):
        return 'CloseTagNode.\n'

delimitedNodeTypes = [CodeNode, TagNode]
open_delims = { t.open_delim : t for t in delimitedNodeTypes }

class PypageSyntaxError(Exception):
    def __init__(self):
        self.description = 'undefined'
    def __str__(self):
        return "Syntax Error: " + self.description

class NodeIncompleteDelimited(PypageSyntaxError):
    def __init__(self, node):
        self.node = node
        self.description = "Missing closing '%s' for opening '%s' at line %d, column %d." % ( 
            self.node.close_delim, self.node.open_delim, 
            self.node.loc[0], self.node.loc[1] )

class UnboundCloseTag(PypageSyntaxError):
    def __init__(self, node):
        self.node = node
        self.description = "UnboundCloseTag"

class UnclosedTag(PypageSyntaxError):
    def __init__(self, node):
        self.node = node
        self.description = "UnclosedTag"

def lex(src):
    tokens = list()

    node = None

    i = 0
    line, line_c = 1, 0
    while i < len(src) - 1:
        c  = src[i]
        c2 = src[i] + src[i+1]

        if c == '\n':
            line += 1
            line_c = 0
        else:
            line_c += 1

        # If we don't belong to any node, we need 
        # to find a node to belong to. We look for 
        # any valid opening delimiters, and if there 
        # are none, then we become a TextNode.
        if not node:
            if c2 in open_delims.keys():
                node = open_delims[c2]((line, line_c))
                i += 2
                continue
            else:
                node =  TextNode()

        # If we're in a TextNode currently, then we look 
        # for opening delimiters that'll end this TextNode.
        if isinstance(node, TextNode):
            if c2 in open_delims.keys():
                tokens.append(node)
                node = open_delims[c2]((line, line_c))
                i += 2
                continue

        # If we're in a DelimitedNode, then we look for 
        # closing delimiters that'll complete this node.
        if isinstance(node, DelimitedNode):
            if c2 == node.close_delim:
                # If we're in a TagNode, will strip node.src
                if isinstance(node, TagNode):
                    node.src = node.src.strip()

                    if not node.src:
                        node = CloseTagNode()

                tokens.append(node)
                node = None
                i += 2
                continue

        if i < len(src) - 2:
            node.src += c
            i += 1
        else:
            node.src += c2
            i += 2

    if node:
        if isinstance(node, TextNode):
            tokens.append(node)
            node = None
        else:
            raise NodeIncompleteDelimited(node)

    return tokens

def build_tree(node, toks):
    try:
        while True:
            tok = toks.next()

            if isinstance(tok, CloseTagNode):
                if isinstance(node, TagNode):
                    return
                else:
                    raise UnboundCloseTag(node)

            node.children.append(tok)

            if isinstance(tok, TagNode):
                build_tree(tok, toks)
    
    except StopIteration:
        if not isinstance(node, RootNode):
            raise UnclosedTag(node)

def execute(src):
    try:
        tokens = lex(src)
    
        tree = RootNode()

        tokens_iterator = iter(tokens)

        build_tree(tree, tokens_iterator)

    except PypageSyntaxError as e:
        print e
        return

    print tree

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

    execute(source)
