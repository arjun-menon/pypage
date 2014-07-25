======
pypage
======
pypage is a Python-based document templating engie, that lets you construct powerful  
programmatically-generated documents by embedding Python code in an elegant and flexible manner. 
Its syntax is similar to and partially inspired by other templating languages Jinja_ and Liquid_.

pypage is a text-based templating engine, that lets you embed Python code easily and 
flexibly in textual documents (such as HTML, reStructuredText_, plain text, etc). Its syntax 
is similar to and partially inspired by the templating languages Jinja_ and Liquid_.

Why another templating language?
--------------------------------
While there are many templating engines out there, the primarily advantage of pypage is the fact 
that its syntax is very close to Python's, and therefore the learning curve is very short for 
Python programmers.

Rather than create a new sub-language and syntax for constructs such as ``for`` and ``while`` loops, 
pypage directly evaluates a lot of the code you write directly in the Python interpreter. As such, 
pypage effectively inherits Python's syntax in a lot of its constructs. This means richer and 
more expressive constructs (see pypage's `for loop`_), and a shorter learning curve.

The primary disadvantage of using pypage versus a templating engine such as Liquid_ is that pypage 
gives the template writer full unfettered access to the Python interpreter. As such the template 
is effectively no longer *secure*, and there is no time bound on the template's processing 
time. This means that pypage is really only meant for internal use, and you can't allow external 
users to write templates, etc.

It is also worth noting that the practice of mixing code and UI (or "view") is generally 
deeply frowned upon. The entire reason behind the existence of the plethora of templating 
languages we have today is to *separate logic and UI*. However, what I've noticed is that 
secure templating languages ultimately end up being sub-Turing-complete programming languages with 
an implicit time complexity bound (i.e. guaranteed termination in a reasonable amount of time). 
The effect of this is that template authors end up having to learn a whole new language altogether. 

My personal opinion is that security and implicit complexity bounds are closely related topics that 
deserve *very close attention*.


also: Smarty, Django, Mustache, Handlebars, 

investiage: MarkupSafe (Jinja dependency), 

.. _reStructuredText: http://docutils.sourceforge.net/docs/user/rst/quickref.html
.. _Jinja: http://jinja.pocoo.org/docs/
.. _Liquid: https://github.com/Shopify/liquid/wiki/Liquid-for-Designers


User Manual
-----------
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

Whitespace and Newline Reduction
################################


If a block tag is on a line by itself, surrounded only by whitespace, then that whitespace is 
automatically excluded from the output. This allows you indent your block tags without 
worrying about any excess whitespace floating around.


The write(...) function
#######################

...

*Note:* If ``write`` is called from a single-line code tag, the information passed to ``write`` is 
written to the document, and the result of the expression evaluation (a ``None``) is discarded.

For Loops
~~~~~~~~~


Unlike Python, Jekyll doesn't leak loop variables.


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




Todos
-----

- Include tag

- Optional close tag in the form of "endtag"

- Loop controls (continue & break)

- Disallow ';' in single-line code tags -- for consistency, and to avoid quoted semicolon problems.
- support '=' single equals in {{ ... }} single line

- (Maybe) Provide Jinja2-like filter (|) by overloading the bitwise OR operator (if possible).

- it might be a good idea to port to python 3 for better unicode handling  (& upd. the shebang)
  see https://docs.python.org/dev/howto/unicode.html  & research how unicode works in py 2.x

- Do not allow (i.e. strip out) invalid chars in for tag target list

- Handle user code errors gracefully with an optional "embed_errors" option

- Raise an error for 2 sec+ while loops.

- Remove the CommentBlockTag (maybe)

- Raw tag

- Centralize strings such as '{{', ('\{' : '{'), '{%', etc

- Function tag

- Store for loop variables *locally*.

- Optionally import itertools

pypage-site (maybe?)

- Custom h1/h2/h3/etc level rST extension

- Related Posts rST extension

wrong: escaping is off by default, because docutils or python-markdown will take care of it.
  so you might need to have escaping enabled by default...
    you're doing: txt -- (docutils.rST) --> html_body -- (pypage) --> html_page

