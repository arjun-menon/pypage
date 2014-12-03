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
**write**(``[object, ...], *, sep=' ', end='\n'``)

The ``write`` function works similarly to the Python 3 ``print`` function. The objects passed to it are stringified with ``str``, concatenated together with ``sep``, and appended with ``end``.

If there are multiple calls to ``write`` in a code tag, their outputs are concatenated together. The resulting final output is substituted in place of the code block in the generated document.

If ``write`` is called from an inline code tag, the information passed to ``write`` is used, and the result of the expression (``None``) is discarded.

Automatic Indentation
^^^^^^^^^^^^^^^^^^^^^
pypage automatically intends the output of a multi-line tag to match the indentation level of the code tag. The number of whitespace characters at the beginning of the second line of the code block determines the indentation level for the whole block. All lines of code following the second line must at least have the same level of indentation as the second line (or else, a PypageSyntaxError exception will be thrown).

Whitespace Removal
^^^^^^^^^^^^^^^^^^
If a block tag is on a line by itself, surrounded only by whitespace, then that whitespace is automatically excluded from the output. This allows you indent your block tags without worrying about excess whitespace in the generated document.

Why have distinct inline code tags?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
It's easier to write ``{{x}}`` than to write ``{{ write(x) }}``. Many a time, all we need to do is inject the value of a 
variable at a specific location in the document.

Block Tags
~~~~~~~~~~

Block tags look like this::

  {% for i in range(10) %}
      The square of {{i}} is {{i*i}}.
  {% %}

A block tag begins with ``{% tag_name ... %}`` and ends with ``{% %}``. Optionally, the end ``{% %}`` can be of the form ``{% endtag_name %}``, which in the above example would be ``{% endfor %}``).

The next sections will describe in detail the code tag, and each type of block tag.

For Loops
++++++++++
Loop variables effectively override variables with the same name(s) for the duration of the loop. pypage backs up identically-named variables, and from within the loop, only the loop variables are accessible.


Conditional Blocks
++++++++++++++++++


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
