======
pypage
======
pypage is a document templating engine for Python programmers with a short learning curve.

**Why use pypage?**

- Easy to pick up. Syntax similar to Python's.
- You need an eval-based templating engine.

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
In order to embed code in a document, you wrap Python code with ``{{`` and ``}}``. The ``{{ ... }}`` constructs are called **code tags**. There are two kinds of code tags: *inline* and *multiline*.

Inline Code Tags
++++++++++++++++
Inline code tags occur entirely on the same line, i.e. the closing ``}}`` appears on the same line as the opening ``{{``. Here is an example of an inline code tag::

    There are {{ 5 + 2 }} days in a week.

The above, when processed by pypage, yields::

    There are 7 days in a week.

The Python ``eval`` statement is used to execute the code between the delimiters. The result of the expression evaluation is converted into a string (with ``str``) and the code tag is replaced with it.

Multi-line Code Tags
++++++++++++++++++++
Multi-line code tags, as their name suggests, span multiple lines. The sole distinguishing characteristic between it and an inline code tag is the presence of one or more newline (``\n``) characters between the ``{{`` and ``}}``. 

Here's an example of a multi-line code tag:

.. code-block:: python

    {{
        x = 5
        y = 2

        write("There are", x + y, "days in a week.")
    }}

The Python ``exec`` function is used to execute this multi-line snippet of code. A ``write`` function, similar to the Python 3 ``print`` function, is used to inject text into document in place of the multi-line code tag.

Execution Environment
^^^^^^^^^^^^^^^^^^^^^
All code tags share a common environment for local and global environments. As such, a variable instantiated in a code tag at the beginning of the document, will be available to all other code tags in the document. When pypage is invoked as library, an initial seed environment consisting of a Python dictionary mapping variable names to values, can be provided.

The ``write`` function
^^^^^^^^^^^^^^^^^^^^^
``write`` is modeled after the Python 3 ``print`` function.

*Note:* If ``write`` is called from a single-line code tag, the information passed to ``write`` is written to the document, and the result of the expression evaluation (a ``None``) is discarded.

Automatic Indentation
^^^^^^^^^^^^^^^^^^^^^
The second line of code determines indentation. All lines of code after the second must match its indentation or be empty. The output is indented based on the second line's indentation.

Whitespace Removal
^^^^^^^^^^^^^^^^^^
If a block tag is on a line by itself, surrounded only by whitespace, then that whitespace is automatically excluded from the output. This allows you indent your block tags without worrying about any excess whitespace floating around.

Why have distinct inline code tags?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
It's easier to write ``{{x}}`` than to write ``{{ write(x) }}``. Many a time, all we need to do is inject the value of a 
variable at a specific location in the document. A simple ``{{ x }}`` is clean, and the standard with multiple other templating engines.

Block Tags
~~~~~~~~~~

Block tags look like this::

  {% for i in range(10) %}
      The square of {{i}} is {{i*i}}.
  {% %}

A block tag begins with ``{% tag_name ... %}`` and ends with ``{% %}``. Optionally, the end ``{% %}`` can be of the form ``{% endtag_name %}``, which in the above example would be ``{% endfor %}``).

The next sections will describe in detail the code tag, and each type of block tag.

Conditional Blocks (``if``, ``elif``, ``else``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For Loops
^^^^^^^^^
Unlike Python, Jekyll doesn't leak loop variables.

Loop variables effectively override variables with the same name(s) for the duration of the loop. pypage backs up identically-named variables, and from within the loop, only the loop variables are accessible.


While Loops
^^^^^^^^^^^
  - dofirst option
  - slow option


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

- Some other templating languages: Jinja, Liquid, Smarty, Django, Mustache, Handlebars, 

- investiage: MarkupSafe (Jinja dependency)

- colorful command-line output

.. _reStructuredText: http://docutils.sourceforge.net/docs/user/rst/quickref.html
.. _Jinja: http://jinja.pocoo.org/docs/
.. _Liquid: https://github.com/Shopify/liquid/wiki/Liquid-for-Designers
