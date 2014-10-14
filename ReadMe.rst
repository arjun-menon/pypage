======
pypage
======
pypage is a document templating engine for Python programmers with a short learning curve.

**Why use pypage?**

- Easy to pick up. Syntax similar to Python's.
- You need an eval-based temaplting engine.

**What does it look like?**

.. code-block:: html

    <ul id="users">
      {% for user in users %}
        <li>
          <a href="mailto: {{ html_ascii( user.email ) }}">{{ user.name }}</a>
        </li>
      {% endfor %}
    </ul>

User Guide
----------

Embedding Code
~~~~~~~~~~~~~~
In order to embed codein a document, you wrap Python code with ``{{`` and ``}}``. The ``{{ ... }}`` constructs are called **code tags**. There are two kinds of code tags: *inline* and *multiline*.

Inline Code Tags
++++++++++++++++
Inline code tags occur entirely on the same line, i.e. the closing ``}}`` appears on the same line as the opening ``{{``. Here is an example of an inline code tag::

    There are {{ 5 + 2 }} days in a week.

The above, when processed by pypage, yields::

    There are 7 days in a week.

pypage evaluates the code inside the delimiters using the Python ``eval`` statement. As ``eval`` expects an *expression*, the code inside the inline code tag must be an expression. The result of the evaluation of this expression is stringified (with ``str``) and substituted in place of the inline code tag.

Multi-line Code Tags
++++++++++++++++++++
A multi-line code tag is a code tag that spans multiple lines. The sole distinguishing characteristic is the presence of a newline character in the code. Here's an example:

.. code-block:: python

    {{
        x = 5
        y = 2

        write("There are", x + y, "days in a week.")
    }}

The code above is executed using the Python ``exec`` function. Python's ``exec`` is similar to ``eval`` except in that it is not restricted to exressions, and allows you to execute arbitary pieces of Python code.

The ``write`` function seen above is a special function provided by pypage that can be used to inject output into the document in place of the code tag. This ``write`` function is modeled after the Python 3.x ``print`` function. More on it later.

Why is there a separate inline tag?
```````````````````````````````````
It is easier to write ``{{x}}`` than to write ``{{ write(x) }}``, and in many cases we need to is inject the contents of a variable into various parts of textual document. The separate treatment of inline code tags makes a pypage template look cleaner. In addition, other templating engines use very similar or exactly the same syntax.

The ``write`` function
++++++++++++++++++++++

The ``write`` function is modeled after Python 3's ``print`` function.


*Note:* If ``write`` is called from a single-line code tag, the information passed to ``write`` is written to the document, and the result of the expression evaluation (a ``None``) is discarded.


Automatic Indentation
+++++++++++++++++++++


The second line of code determines indentation.All lines of code after the second must match its indentation or be empty. The output is indented based on the second line's indentation.


Whitespace Removal
++++++++++++++++++


If a block tag is on a line by itself, surrounded only by whitespace, then that whitespace is automatically excluded from the output. This allows you indent your block tags without worrying about any excess whitespace floating around.


The Execution Environment
+++++++++++++++++++++++++

The environment (global & local variables) is persisted throughout the document, both while invoking ``exec`` and ``eval``.

injections by ``for``


Block Tags
~~~~~~~~~~

Block tags look like this::

  {% for i in range(10) %}
      The square of {{i}} is {{i*i}}.
  {% %}

A block tag begins with ``{% tag_name ... %}`` and ends with ``{% %}``. Optionally, the end ``{% %}`` can be of the form ``{% endtag_name %}``, which in the above example would be ``{% endfor %}``).

The next sections will describe in detail the code tag, and each type of block tag.


Conditional Blocks (``if``, ``elif``, ``else``)
+++++++++++++++++++++++++++++++++++++++++++++++


For Loops
+++++++++


Unlike Python, Jekyll doesn't leak loop variables.
Loop variables are stored pesudo-*locally*.





While Loops
+++++++++++


  - dofirst option
  - slow option



Comments
~~~~~~~~
two ways
{# #} (Jinja)
{% comment %} {% %} (Liquid)



Todos
-----

- Include tag

- fix whitespace reduction bug (see if-2.txt)

- Raw tag (similar to the {# ... #} comment tags)

- an option within the embedded code to suppress/override (or select) automatic indentation

- Loop controls (continue & break)

- Function tag

- Handle user code errors gracefully with an optional "embed_errors" option

- Raise an error for 2 sec+ while loops.

- Support '=' assignment in single-line code tags

- while loops: 2 sec+ loops should just issue a warning

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

- you're doing: txt -- (docutils.rST) --> html_body -- (pypage) --> html_page

- Custom h1/h2/h3/etc level rST extension

- password protection (with nodejs & SJCL)

- Related Posts rST extension

- you don't need escape write(...) calls because docutils or python-markdown will take care of it. (?)


.. _reStructuredText: http://docutils.sourceforge.net/docs/user/rst/quickref.html
.. _Jinja: http://jinja.pocoo.org/docs/
.. _Liquid: https://github.com/Shopify/liquid/wiki/Liquid-for-Designers

