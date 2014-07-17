======
pypage
======
pypage is a Python-based templating engine, that lets you embed Python code easily and 
flexibly in textual documents (such as HTML, reStructuredText_, plain text, etc). Its syntax 
is similar to and partially inspired by the templating languages Jinja_ and Liquid_.

.. _reStructuredText: http://docutils.sourceforge.net/docs/user/rst/quickref.html
.. _Jinja: http://jinja.pocoo.org/docs/
.. _Liquid: https://github.com/Shopify/liquid/wiki/Liquid-for-Designers

Manual
------
All of the magic in pypage happens via directives specified in tags. 
There are two kinds of tags in pypage: the code tag and the block tag. 

Here is an example of a code tag::

  {{ 1 + 2 }}

Code tags are delimited by ``{{`` and ``}}``. Everything in between is Python code. 
Code tags are discussed in detail in the `Embedding Python code`_ section.

Block tags look like this::

  {% for i in range(10) %}
      The square of {{i}} is {{i*i}}.
  {% %}

A block tag begins with ``{% tag_name ... %}`` and ends with ``{% %}``. Optionally, the end 
``{% %}`` can be of the form ``{% endtag_name %}``, which in the above example would be ``{% endfor %}``).

The next sections will describe in detail the code tag, and each type of block tag.

.. _`Embedding Python code`:

Embedding Python Code Using The {{ ... }} Code Tag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Code tags are used to embed Python code.
Code tags are treated differently based on whether they span one or multiple lines.

Single-line Code Tags
#####################

::
  {{ 1 + 2 }}

A single line code tag is usually treated as an *expression*, and the value resulting from its 
evaluation is passed to ``str()`` and written without alteration to the document.

Mutli-line Code Tags
####################

::
  {{
    for i in range(10):
        write('The square of', i, 'is', i*i, '.')
  }}

When the code tag spans multiple lines, it is no longer treated as a expression. 
Output is written by calls to the ``write`` function. The ``write`` functions behaves
very similarly to Python 3.x's ``print`` function. (More on it later.)

Multi-code tags are executed using Python's ``exec``. The environment (global & local variables) 
is always persisted throughout the document, both while invoking ``exec`` and ``eval``.

Indentation Handling
####################

The second line of code determines indentation.
All lines of code after the second must match its indentation or be empty.
The output is indented based on the second line's indentation.

The write(...) function
#######################

...

*Note:* If ``write`` is called from a single-line code tag, the information passed to ``write`` is 
written to the document, and the result of the expression evaluation (a ``None``) is discarded.

For Loops
~~~~~~~~~



Conditional if/elif/else Blocks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


While Loops
~~~~~~~~~~~


  - dofirst option
  - slow option



Capture Tag
~~~~~~~~~~~


Include Tag
~~~~~~~~~~~~


Comments
~~~~~~~~
two ways
{# #} (Jinja)
{% comment %} {% %} (Liquid)


Notes
~~~~~



If a block tag is on a line by itself, surrounded only by whitespace, then that whitespace is 
automatically excluded from the output. This allows you indent your block tags without 
worrying about any excess whitespace floating around.



Todos
-----

- Include tag

- Optional close tag in the form of "endtag"

- Disallow ';' in single-line code tags -- for consistency, and to avoid quoted semicolon problems.

- Do not allow (i.e. strip out) invalid chars in for tag target list

- Handle user code errors gracefully with an optional "embed_errors" option

- Raise an error for 2 sec+ while loops.

- Remove the CommentBlockTag (maybe)

- Raw tag

- Function tag

- Store for loop variables *locally*.

