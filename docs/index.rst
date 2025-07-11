PyPage |pypi| |docs| |test|
===========================

PyPage is a document template engine for Python programmers with a
short learning curve.

**Why use PyPage?**

-  Easy to pick up. Syntax similar to Python's.
-  You need an eval-based template engine.

PyPage can be used in conjunction with the static site generator Alteza_ to build websites.

PyPage supports Python 3.x and 2.7, and has been tested
(using test_cmd_) on CPython and PyPy.

**What does it look like?**

.. code:: html

    Some fruits with the character `r` in their name:
    <ul>
      {% for fruit in ['Apple', 'Strawberry', 'Orange', 'Raspberry'] if 'r' in fruit %}
        <li>
          {{ fruit }}
        </li>
      {% endfor %}
    </ul>

**Installation**

You can `install <https://docs.python.org/3/installing/>`_ PyPage easily with `pip <https://pip.pypa.io/en/stable/>`_:

.. code::

    pip install pypage

Try running ``pypage -h`` to see the command-line options available.


**Why another templating language?**

PyPage is lets you embed Python code easily and flexibly in textual documents (such as Markdown_, HTML, reStructuredText_, plain text, etc). It lets you construct powerful  programmatically-generated documents by embedding Python code in an elegant and flexible manner. Its syntax is similar to and partially inspired by the templating languages Jinja_ and Liquid_.

While there are many templating engines out there, the primarily advantage of PyPage is the fact that its syntax is very close to Python's, and therefore the learning curve is very short for Python programmers.

Rather than create a new mini domain-specific language for constructs such as ``for`` and ``if``, PyPage does a teeny tiny bit of obvious string manipulation, and passes your logical directives unaltered to the Python interpreter. As such, PyPage inherits Python's syntax for the most part. For example, ``for`` loops in PyPage get converted into Python's generator expressions. The ``for`` loop in a Python generator expression (or list comprehension) is far more powerful than its regular ``for`` loop. This means that PyPage ``for`` loops are richer and more expressive than you'd otherwise expect, while the learning curve is nearly non-existent.

The primary disadvantage of using PyPage instead of a templating engine like Liquid is that PyPage does not operate on a restricted non-Turing-complete subset of programming languages, as Liquid for instance does. Liquid allows untrusted users to write and upload their own templates, because the expressiveness of Liquid is limited such that there is an implicit guarantee that the template will be processed in a reasonable (probably linear) amount of time using a reasonable amount of system resources. As such, Liquid's templating language is rather limited -- it offers a limited number of pre-defined functions/filters, and the overall flexibility of the language has been constrained in order to guarantee termination in a reasonable amount of time.

PyPage, on the other hand gives the template writer full unfettered access to the Python interpreter. As such, PyPage is meant only for use in trusted contexts (or containers), and in some ways it's similar to PHP in that a you're mixing a full-blown programming language (Python) and text that could be HTML.

This brings us to another topic: mixing code and UI. It is generally frowned upon to mix logic/code and the UI (or "view"). So it is good practise to not do any intelligent processing within your PyPage template. Instead, you can do it in a separate program, and pass an *environment* containing the results, to PyPage. An environment is a dictionary of variables that is passed to Python's ``exec``, and is therefore accessible from all of the code in the PyPage template. From within your template you can focus solely on how to transform these input variables into the HTML/rST/other page you're building.

A pleasant aspect of PyPage, in comparison to other templating languages is that you don't have to learn much new syntax. It's probably the easiest to learn and most *flexible* templating language out there. It is highly flexible because of the plethora of easy-to-use powerful constructs that PyPage offers.

.. _Markdown: https://en.wikipedia.org/wiki/Markdown
.. _reStructuredText: http://docutils.sourceforge.net/docs/user/rst/quickref.html
.. _Liquid: https://github.com/Shopify/liquid/wiki/Liquid-for-Designers
.. _Jinja: https://github.com/pallets/jinja


.. contents:: **Table of Contents**


Embedding Code
--------------

In order to embed code in a document, you wrap Python code with ``{{``
and ``}}``. The ``{{ ... }}`` constructs are called **code tags**. There
are two kinds of code tags: *inline* and *multiline*.

Inline Code Tags
^^^^^^^^^^^^^^^^

Inline code tags occur entirely on the same line, i.e. the closing
``}}`` appears on the same line as the opening ``{{``. Here is an
example of an inline code tag:

.. code:: python

    There are {{ 5 + 2 }} days in a week.

The above, when processed by PyPage, yields:

::

    There are 7 days in a week.

The Python ``eval`` statement is used to execute the code in an inline
code tag. The result of the expression evaluation is converted into a
string (with ``str``) and the code tag is replaced with it.

Multiline Code Tags
^^^^^^^^^^^^^^^^^^^

Multiline code tags span multiple lines. The presence of one or more
newline (``\n``) characters between the ``{{`` and ``}}`` distinguishes
it from an inline code tag. Here's an example:

.. code:: python

    {{
        x = 5
        y = 2

        write("There are", x + y, "days in a week.")
    }}

The Python ``exec`` function is used to execute the code in a multiline
code tag.

Why have distinct inline code tags? It's easier to write ``{{x}}`` than
to write ``{{ write(x) }}``. Many a time, all we need to do is inject
the value of a variable at a specific location in the document.

Execution Environment
^^^^^^^^^^^^^^^^^^^^^

All code is executed in a shared common environment. I.e., the ``locals`` and
``globals`` passed into ``eval`` and ``exec`` is a single shared dictionary,
for all code tags in the same file.

As such, a variable instantiated in a code tag at the
beginning of the document, will be available to all other code tags in
the document. When PyPage is invoked as library, an initial seed
environment consisting of a Python dictionary mapping variable names to
values, can be provided.

The write function
''''''''''''''''''

A ``write`` function similar to the Python 3's ``print`` function
is accessible from both kinds of code tags. It writes text into
the document that substitutes/replaces the code tag it's used in.

.. code:: python

    write(*object, sep=' ', end='\n')

Objects passed to it are stringified with ``str``, concatenated together
with ``sep``, and terminated with ``end``. The outputs of multiple calls
to ``write`` in a code tag are concatenated together, and the resulting
final output is injected in place of the code tag.

If ``write`` is called from an inline code tag, the result of evaluating
the expression (a ``None``, since ``write`` will return a ``None``) is
ignored, and the output of the ``write`` call is used instead.

Block Tags
----------

Block tags simplify certain tasks that would otherwise be cumbersome and
ugly if done exclusively with code tags. One of the things it lets you
do is wrap part of your page in an `if/else
conditional <http://en.wikipedia.org/wiki/Conditional_(computer_programming)>`__,
or a `for/while
loop <http://en.wikipedia.org/wiki/Control_flow#Loops>`__.

Here's an example of the ``for`` block tag:

.. code:: python

    {% for i in range(10) %}
        The square of {{i}} is {{i*i}}.
    {% %}

A block tag begins with ``{% tag_name ... %}`` and ends with ``{% %}``.
Optionally, the end ``{% %}`` can be of the form ``{% endtag_name %}``
(i.e. prepend the ``tag_name`` with ``end``), which in the above example
would be ``{% endfor %}``).

Conditional Blocks
^^^^^^^^^^^^^^^^^^

It's best to explain this with an example:

.. code:: python

    Hey,
    {{
      import random
      # Randomly pick a greeting
      greeting = random.randint(1,4)
    }}
    {% if greeting == 1 %}
      Hello
    {% elif greeting == 2 %}
      Bonjour
    {% elif greeting == 3 %}
      Hey
    {% else %}
      Hi
    {% %}

When the above template is run, the resulting page will contain a
randomly chosen greeting. As is evident, PyPage syntax for if/elif/else
conditions closely mirrors Python's. The terminal ``{% %}`` can be
replaced with an ``{% endif %}`` with no change in meaning (as with any
block tag).

For Loops
^^^^^^^^^

Let's start with a simple example:

.. code:: python

    {% for vowel in ['a', 'e', 'i', 'o', 'u'] %}{{vowel}} {% %}

This will print out the vowels with a space after every character.

Now that's an ordinary for loop. PyPage permits for loops that are more
expressive than traditional Python for loops, by leveraging Python's
*generator expressions*.

Here's an example of something that would be impossible to do in Python
(with a regular for loop):

.. code:: python

    {% for x in [1,2,3] for y in ['a','b','c'] %}
        {{x}} ~ {{y}}
    {%%}

The above loop would result in:

::

    1 ~ a
    1 ~ b
    1 ~ c
    2 ~ a
    2 ~ b
    2 ~ c
    3 ~ a
    3 ~ b
    3 ~ c

*Internally*, PyPage morphs the expression
``for x in [1,2,3] for y in ['a','b','c']`` into the generator
expression ``(x, y) for x in [1,2,3] for y in ['a','b','c']``. It
exposes the the loop variables ``x`` and ``y`` by injecting them into
your namespace.

*Note:* Injected loop variables replace variables with the same name for
the duration of the loop. After the loop, the old variables with the
identical names are restored (PyPage backs them up).

While Loops
^^^^^^^^^^^

A while loops looks like ``{{% while condition %}} ... {{% %}``, where
``condition`` can be any Python expression. Here's an example:

.. code:: python

    {{
        i = 10
        j = 20
    }}
    Numbers from {{i}} to {{j}}:
    {% while i <= j %}
    {{
        write(str(i))
        i += 1
    }}
    {% %}

This would simply list the numbers from 10 to 20.

dofirst Loops
'''''''''''''

.. code:: python

    {% while dofirst False %}
    That's all, folks!
    {%%}

Adding a ``dofirst`` right after the ``while`` and before the expression
ensures that the loop is run *at least once*, before the condition is
evaluated.

Long Loops
''''''''''

If a loop runs *for more than 2 seconds*, PyPage stops executing it, and
writes an error message to ``stdout`` saying that the loop had been
terminated. As PyPage is mostly intended to be used as a templating
language, loops generally shouldn't be running for longer than two
seconds, and this timeout was added to make it easier to catch accidental
infinite loops. If you actually need a loop to run for longer than 2
seconds, you can add the keyword ``slow`` right after the condition expression
(``{{% while condition slow %}}``), and that would suppress this 2-second timeout.

Capture Blocks
^^^^^^^^^^^^^^

You can capture the output of part of your page using the ``capture``
tag:

.. code:: python

    {% capture x %}
      hello {{"bob"}}
    {% %}

The tag above will not yield any output, but rather a new variable ``x``
will be created that captures the output of everything enclosed by it
(which in this case is ``"hello bob"``).

Function Blocks
^^^^^^^^^^^^^^^

You can define functions using the ``def`` tag:

.. code:: python

    {% def anchor name href %}
      <a href="{{href}}">{{name}}</a>
    {% %}

The tag above will not yield any output, but rather create a new function ``anchor`` that behaves like a function, and returns the output of everything enclosed by it, with the named positional arguments injected (in an effective stacked local scope) as expected. In this example, we can invoke it with ``{{ anchor('Wikipedia', 'https://en.wikipedia.org') }}``.

Finer Details
-------------

Inheritance (with inject and exists)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The approach taken by PyPage toward template inheritance is quite distinct from that of other
templating engines (`like Jinja's <http://jinja.pocoo.org/docs/2.10/templates/#template-inheritance>`_).
It's a lot simpler. You call a PyPage-provided function ``inject`` with the path of a *PyPage template* you want
to inject (i.e. "*extend*" in Jinja parlance), and PyPage will process that template under the current scope (with all
previously defined variables being available to the injected template), and the ``inject`` function will return its output.

A base template could look like this:

.. code:: html

    <html>
    <head>
        <title>
            {% if exists('title') %}
            {{ title }}
            {% else %}
            No title
            {% %}
        </title>
    </head>
    <body>
    {{ body }}
    </body>
    </html>

A derived templates only needs to define ``body`` and optionally ``title``, to "extend" the template above.

.. code::

    {% capture body %}
    The HTML body content would go in here.
    {% %}
    {{ inject('...path to the base template...') }}

We didn't specify a ``title`` above, but if we wanted to, we'd just need to make sure it was defined before ``inject``
was called. The base template checks whether a ``title`` variable exists by calling the function ``exists``. As is obvious,
the ``exists`` function simply takes a variable name as a string, and returns a boolean indicating whether the variable
exists in the scope.

This approach to inheritance is explicit and easy-to-grasp. Rather than have complex inheritance rules, with a default
block definition that is optionally overridden by a derived template, we make things more explicit by using conditionals
for cases where we want to provide a default/fallback definition. We error out if a definition is expected to be provided,
and is not present. The output of the "dervied" template is clear and obvious, with this approach.

The include function
''''''''''''''''''''

If you want to include (as in, substitute) a file directly without processing it with PyPage, you can use the
``include`` function. It functions like the ``inject`` function, taking the path to a file as argument, and
returning the contents of the file unprocessed.

Comments
^^^^^^^^

Comment Tags
''''''''''''

Anything bounded by ``{#`` and ``#}`` will be omitted from the output.
For example:

.. code:: html

    <p>
      Lorem ipsum dolor sit amet
      {#
        <ul>
            Non sequitur
        </ul>
      #}
      consectetur adipisicing elit
    </p>

Comment Blocks
''''''''''''''

You can also easily comment an existing block, by simply placing the word ``comment`` in front of it:

.. code:: html

    <p>
      Lorem ipsum dolor sit amet
        {% comment for i in range(10) %}
            N = {{i}}
        {% %}
      consectetur adipisicing elit
    </p>

The ``comment`` keyword before the ``for`` above results in the entire block
being commented out and omitted from the output.

Whitespace & Indentation
^^^^^^^^^^^^^^^^^^^^^^^^

Whitespace Removal
''''''''''''''''''

If a block tag is on a line by itself, surrounded only by whitespace,
then that whitespace is automatically excluded from the output. This
allows you indent your block tags without worrying about excess
whitespace in the generated document.

Automatic Indentation
'''''''''''''''''''''

PyPage smartly handles indentation for you. In a multi-line code tag, if
you consistently indent your Python code with a specific amount of
whitespace, that indentation will be stripped off before executing the
code block (as Python is indentation-sensitive), and the resulting
output of that code block will be re-indented with same whitespace that
the initial code block was.

The whitespace preceding the second line of code determines the
peripheral indentation for the entiee block. All subsequent lines (after
second) must begin with exact same whitespace that preceded the second
line, or be an empty line.

For example:

.. code:: html

    <p>
      Lorem ipsum dolor sit amet
        <ul>
          {{
            def foo():
              write("Hello!")
            foo()
          }}
        </ul>
      consectetur adipisicing elit
    </p>

would produce the following output:

.. code:: html

    <p>
      Lorem ipsum dolor sit amet
        <ul>
            Hello!
        </ul>
      consectetur adipisicing elit
    </p>

Note that the ``Hello!`` was indented with same whitespace that the code
in the code block was.

PyPage automatically intends the output of a multi-line tag to match the
indentation level of the code tag. The number of whitespace characters
at the beginning of the second line of the code block determines the
indentation level for the whole block. All lines of code following the
second line must at least have the same level of indentation as the
second line (or else, a PypageSyntaxError exception will be thrown).

Development
^^^^^^^^^^^
PyPage has no dependencies, and the entire code is in a single file, ``pypage.py``.

It is also written in Python compatible with both Python 2.7 and Python 3.x.

To run the tests, first install `test_cmd`_:

.. _test_cmd: https://github.com/arjun-menon/test_cmd

.. code::

    pip install test_cmd

Then run the following command at the root of this repository:

.. code::

    test_cmd tests env/bin/python pypage.py @ -

A bit of history
''''''''''''''''
PyPage was started on January 25, 2013 (`an early commit <https://github.com/arjun-menon/pypage/commit/de81a71220d483cd57c8bd82c4445ee3467d1a2f>`_). But it went underwent a pretty heavy rewrite from scratch in the summer of 2014 (`an early commit from July 11, 2014 <https://github.com/arjun-menon/pypage/commit/1d2f6fe0ec41fcdabf1da1d1928c3711a5c3722d>`_ from during that rewrite, and `other commits from around then <https://github.com/arjun-menon/pypage/commits/master/?after=105d5b3ff523d7a4e1c092200c4299546246c586+209>`_) which gave it the form it has today.

Later in 2015, tests were added (`e.g. some commits <https://github.com/arjun-menon/pypage/commits/master/?before=105d5b3ff523d7a4e1c092200c4299546246c586+140>`_) with a dedicated testing tool, test_cmd_, which was actually created speficially for PyPage. This in-depth documentation came around in late 2016 (`some of those commits <https://github.com/arjun-menon/pypage/commits/master/?before=105d5b3ff523d7a4e1c092200c4299546246c586+105>`_).

Many small improvements and enhancements have been made to PyPage since then. And PyPage now serves as the template engine of the Alteza_ static site generator (which was originally called ``pypage-site``).

Ideas for the future: a Rust rewrite, perhaps?
''''''''''''''''''''''''''''''''''''''''''''''
I'm thinking that the core logic in this could be rewritten in Rust, using the `PyO3 <https://github.com/PyO3/pyo3>`_ library, which allows calling into Python easily.
Further, I could add `pulldown-cmark <https://crates.io/crates/pulldown-cmark>`_ as a dependency, to bundle Markdown processing into `pypapge`.
`Some of the logic <https://github.com/arjun-menon/alteza/blob/092122a9177d8d68c5cadd700ed8f46b0f5ff2be/alteza/content.py#L112-L142>`_ in Alteza_ could then be moved here.
Doing it in Rust would likely be a lot faster, and speed up Alteza_'s processing time quite substantially.

.. _Alteza: https://github.com/arjun-menon/alteza

License
^^^^^^^

`Apache License Version
2.0 <https://www.apache.org/licenses/LICENSE-2.0>`__

.. |pypi| image:: https://badge.fury.io/py/pypage.svg
   :target: https://pypi.python.org/pypi/pypage
.. |docs| image:: https://readthedocs.org/projects/pypage/badge/?version=latest&style=flat
   :target: https://pypage.readthedocs.io/en/latest/
.. |test| image:: https://github.com/arjun-menon/pypage/actions/workflows/test.yml/badge.svg
   :target: https://github.com/arjun-menon/pypage/actions/workflows/test.yml/
