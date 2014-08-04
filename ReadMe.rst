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

Rather than create a new mini domain-specifc language for constructs such as ``for`` and ``if``, 
pypage does a teeny tiny bit of obvious string manipulation, and passes your logical directives 
unaltered to the Python interpreter. As such, pypage inherits Python's syntax for the most part. 
For example, ``for`` loops in ``pypage`` get converted into Pythons's generator expressions. The 
``for`` loop in a Python generator expression (or list comprehension) is far more powerful than 
its regular ``for`` loop. This means that pypage ``for`` loops are richer and more expressive 
than you'd otherwise expect, while the learning curve is nearly non-existent.

The primary disadvantage of using pypage instead of a templating engine like Liquid is that pypage 
does not operate on a restricted subset of programming languages, as Liquid for instance does. 
Liquid allows untrusted users to write and upload their own templates, because the expressives of 
Liquid is limited such that there is an implicit guarantee that the template will be processed in 
a reasonable (probably linear) amount of time using a reasonable amount of system resources. As 
such, Liquid's templting language is rather limited -- it offers a limited number of pre-defined 
functions/filters, and the overall flexibility of the language has been constrained in order to 
guarantee termination in a reasonable amount of time.

pypage, on the other hand gives the template writer full unfettered access to the Python 
interpreter. As such, pypage is meant only for internal use, and in some ways it's similar to 
PHP in that a you're mixing a full-blown programming language (Python) and text that could be HTML.

This brings us to another topic: mixing code and UI. It is generally frowned upon to mix logic/code 
and the UI (or "view"). So it is good practise to not do any intelligent processing within your 
pypage template. Instead, you can do it in a separate program, and pass an *environment* containing 
the results, to pypage. An environment is a dictionary of variables that is passed to Python's 
``exec``, and is theferoe accessible from all of the code in the pypage template. From within your 
template you can focus solely on how to transform these input variables into the HTML/rST/other 
page you're building.

A pleasant aspect of pypage, in comparison to other templating languages is that you don't have to 
learn much new syntax. It's probably the easiest tolearn and most *flexible* templating language 
out there. It is highly flexible because of the plethora of easy-to-use powerful constructs that 
pypage offers.

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
Loop variables are stored pesudo-*locally*.


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

- [nope] Raw tag

- Include tag

- Optional close tag in the form of "endtag"

- Loop controls (continue & break)

- Function tag

- Handle user code errors gracefully with an optional "embed_errors" option

- Raise an error for 2 sec+ while loops.

- Support '=' assignment in single-line code tags


- (Maybe) Provide Jinja2-like filter (|) by overloading the bitwise OR operator (if possible).

- it might be a good idea to port to python 3 for better unicode handling  (& upd. the shebang)
  see https://docs.python.org/dev/howto/unicode.html  & research how unicode works in py 2.x

- Do not allow (i.e. strip out) invalid chars in for tag target list

- Remove CommentBlock (maybe)

- Optionally import itertools

- investiage: MarkupSafe (Jinja dependency)

- Other templating languages: Jinja, Liquid, Smarty, Django, Mustache, Handlebars, 

- colorful command-line output


pypage-site

- Custom h1/h2/h3/etc level rST extension

- password protection (with nodejs & SJCL)

- Related Posts rST extension

wrong: escaping is off by default, because docutils or python-markdown will take care of it.
  so you might need to have escaping enabled by default...
    you're doing: txt -- (docutils.rST) --> html_body -- (pypage) --> html_page
