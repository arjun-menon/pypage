======
pypage
======
pypage is a Python-based templating engine, that lets embed logic and Python code easily and 
flexibly in textual documents (such as HTML, reStructuredText_, plain text, etc). Its syntax 
is similar to, and partially inspired by the templating languages Jinja_ and Liquid_.

.. _reStructuredText: http://docutils.sourceforge.net/docs/user/rst/quickref.html
.. _Jinja: http://jinja.pocoo.org/docs/
.. _Liquid: https://github.com/Shopify/liquid/wiki/Liquid-for-Designers

Features
--------

- Code tag

  - Intelligent Indentation Handling

    The second line of code determines indentation.
    All lines of code after the second must match its indentation or be empty.
    The output is indented based on the second line's indentation.

- Block tag

If a block tag is on a line by itself, surrounded only by whitespace, then that whitespace is 
automatically excluded from the output. This allows you indent your block tags without 
worrying about any excess whitespace floating around.

- Conditional (if, elif, else) tag


- For loop tag


- While tag

  - dofirst option
  - slow option


- Capture tag


- Comment tag


Todos
~~~~~

- Include tag

- Optional close tag in the form of "endtag"

- Do not allow (i.e. strip out) invalid chars in for tag target list

- Handle user code errors gracefully with an optional "embed_errors" option

- Raise an error for 2 sec+ while loops.

- Remove the CommentBlockTag (maybe)

- Raw tag

