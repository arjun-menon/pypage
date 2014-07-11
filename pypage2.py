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

class TextNode(object):
    def __init__(self):
        self.src = ""

class DelimitedNode(object):
    def __init__(self):
        pass

class CodeNode(DelimitedNode):
    open_delim, close_delim = '{{', '}}'
    def __init__(self, loc):
        self.loc = loc
        self.src = ""

class TagNode(DelimitedNode):
    open_delim, close_delim = '{%', '%}'
    def __init__(self, loc):
        self.loc = loc
        self.src = ""

delimitedNodeTypes = [CodeNode, TagNode]
open_delims = { t.open_delim : t for t in delimitedNodeTypes }

class IncompleteDelimitedNode(Exception):
    def __init__(self, node):
        self.node = node
    def __str__(self):
        return "Syntax Error: Missing closing '%s' for opening '%s' at line %d, column %d." % ( 
            self.node.close_delim, self.node.open_delim, 
            self.node.loc[0], self.node.loc[1] )

def lex(src):
    tokens = list()

    current_node = None

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
        if not current_node:
            if c2 in open_delims.keys():
                current_node = open_delims[c2]((line, line_c))
                current_node.src += c2
                i += 2
                continue
            else:
                current_node =  TextNode()

        # If we're in a TextNode currently, then we look 
        # for opening delimiters that'll end this TextNode.
        if isinstance(current_node, TextNode):
            if c2 in open_delims.keys():
                tokens.append(current_node)
                current_node = open_delims[c2]((line, line_c))
                current_node.src += c2
                i += 2
                continue

        # If we're in a DelimitedNode, then we look for 
        # closing delimiters that'll complete this node.
        if isinstance(current_node, DelimitedNode):
            if c2 == current_node.close_delim:
                current_node.src += c2
                tokens.append(current_node)
                current_node = None
                i += 2
                continue

        current_node.src += c
        i += 1

    if current_node:
        if isinstance(current_node, TextNode):
            tokens.append(current_node)
            current_node = None
        else:
            raise IncompleteDelimitedNode(current_node)

    print '\n'.join( repr(node) + ": " + repr(node.src) for node in tokens)


def execute(src):
    try:
        lex(src)
    except IncompleteDelimitedNode as e:
        print e
        return

    return None

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
