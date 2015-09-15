pypage
======

[![Travis CI Build Status (Functional Tests)](https://travis-ci.org/arjungmenon/pypage.svg?branch=master)](https://travis-ci.org/arjungmenon/pypage)

pypage is a document templating engine for Python programmers with a short learning curve.

**Why use pypage?**

-   Easy to pick up. Syntax similar to Python's.
-   You need an eval-based templating engine.

**What does it look like?**

```html
<ul id="users">
  {% for user in users %}
    <li>
      <a href="mailto: {{ html_ascii( user.email ) }}">{{ user.name }}</a>
    </li>
  {% endfor %}
</ul>
```

User Guide
----------

### Embedding Code

In order to embed code in a document, you wrap Python code with `{{` and `}}`. The `{{ ... }}` constructs are called **code tags**. There are two kinds of code tags: *inline* and *multiline*.

#### Inline Code Tags

Inline code tags occur entirely on the same line, i.e. the closing `}}` appears on the same line as the opening `{{`. Here is an example of an inline code tag:

```python
There are {{ 5 + 2 }} days in a week.
```

The above, when processed by pypage, yields:

    There are 7 days in a week.

The Python `eval` statement is used to execute the code in an inline code tag. The result of the expression evaluation is converted into a string (with `str`) and the code tag is replaced with it.

#### Multiline Code Tags

Multiline code tags span multiple lines. The presence of one or more newline (`\n`) characters between the `{{` and `}}` distinguishes it from an inline code tag. Here's an example:

```python
{{
    x = 5
    y = 2

    write("There are", x + y, "days in a week.")
}}
```

Python's `exec` function is used to execute the code in a multiline code tag.

Why have distinct inline code tags? It's easier to write `{{x}}` than to write `{{ write(x) }}`. Many a time, all we need to do is inject the value of a variable at a specific location in the document.

##### The write function

The `write` function used above is similar to the Python 3's `print` function, and is accessible from both kinds of code tags. It injects text into the document in place of the code tag it's used in.

```python
write([object, ...], *, sep=' ', end='\n')
```

Objects passed to it are stringified with `str`, concatenated together with `sep`, and terminated with `end`. The outputs of multiple calls to `write` in a code tag are concatenated together, and the resulting final output is injected in place of the code tag.

If `write` is called from an inline code tag, the result of evaluating the expression (a `None`, since `write` will return a `None`) is ignored, and the output of the `write` call is used instead.

##### Execution Environment

All code tags share a common environment for local and global environments. As such, a variable instantiated in a code tag at the beginning of the document, will be available to all other code tags in the document. When pypage is invoked as library, an initial seed environment consisting of a Python dictionary mapping variable names to values, can be provided.

### Block Tags

Block tags simplify certain tasks that would otherwise be cumbersome and ugly if done exclusively with code tags. One of the things it lets you do is wrap part of your page in an [if/else conditional](http://en.wikipedia.org/wiki/Conditional_(computer_programming)), or a [for/while loop](http://en.wikipedia.org/wiki/Control_flow#Loops).

Here's an example of the `for` block tag:

```python
{% for i in range(10) %}
    The square of {{i}} is {{i*i}}.
{% %}
```

A block tag begins with `{% tag_name ... %}` and ends with `{% %}`. Optionally, the end `{% %}` can be of the form `{% endtag_name %}` (i.e. prepend the `tag_name` with `end`), which in the above example would be `{% endfor %}`).

#### Conditional Blocks

It's best to explain this with an example:

```python
Hey,
{{
  import random
  # Randomly pick a greeting
  greeting = random.randint(1,4)
}}
{% if greeting == 1 %}
  Howdy?
{% elif greeting == 2 %}
  How are you?
{% elif greeting == 3 %}
  Any news?
{% else %}
  What's up?
{% %}
```

When the above template is run, the resulting page will contain a randomly chosen greeting. As is evident, pypage syntax for if/elif/else conditions closely mirrors Python's. The terminal `{% %}` can be replaced with an `{% endif %}` with no change in meaning (as with any block tag).

#### For Loops

Let's start with a simple example:

```python
{% for vowel in ['a', 'e', 'i', 'o', 'u'] %}{{vowel}} {% %}
```

This will print out the vowels with a space after every character.

Now that's an ordinary for loop. pypage permits for loops that are more expressive than traditional Python for loops, by leveraging Python's *generator expressions*.

Here's an example of something that would be impossible to do in Python (with a regular for loop):

```python
{% for x in [1,2,3] for y in ['a','b','c'] %}
    {{x}} -> {{y}}
{%%}
```

The above loop would result in:

    1 -> a
    1 -> b
    1 -> c
    2 -> a
    2 -> b
    2 -> c
    3 -> a
    3 -> b
    3 -> c

*Internally*, pypage morphs the expression `for x in [1,2,3] for y in ['a','b','c']` into the generator expression `(x, y) for x in [1,2,3] for y in ['a','b','c']`. It exposes the the loop variables `x` and `y` by injecting them into your namespace.

*Note:* Injected loop variables replace variables with the same name for the duration of the loop. After the loop, the old variables with the identical names are restored (pypage backs them up).

#### While Loops
A while loops looks like ``{{% while condition %}} ... {{% %}``, where ``condition`` can be any Python expression. 
Here's an example:

```python
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
{%%}
```
This would simply list the numbers from 10 to 20.

##### While 'dofirst' Loops

```python
{% while dofirst False %}
That's all, folks!
{%%}
```

Adding a ``dofirst`` right after the ``while`` and before the expression ensures that the loop is 
run *at least once*, before the condition is evaluated.

##### Long Running While Loops
If a loop runs for more than 2 seconds, pypage stops executing it, and writes an error message to 
``stdout`` saying that the loop had been terminated. As pypage is mostly intended to be used as a 
templatig language, it is unlikely for loops to be running for more than 2 seconds, and this was 
added in to make it easier to catch accidental infinite loops. If you do wish for the loop to run 
for longer than 2 seoncds, you can add ``slow`` right after the expressions (``{{% while condition slow %%}}``), 
and that would suppress this 2-second timeout.

#### Capture Tag

You can capture the output of part of your page using the `capture` tag:

```python
{% capture x %}
  hello {{"bob"}}
{% %}
```

The above tag will not yield any output, but rather a new variable `x` will be created that captures the output of everything enclosed by it (which in this case is `"hello bob"`).

### Finer Details

#### Indentation & Whitespace

##### Automatic Indentation

pypage smartly handles indentation for you. In a multi-line code tag, if you consistently indent your Python code with a specific amount of whitespace, that indentation will be stripped off before executing the code block (as Python is indentation-sensitive), and the resulting output of that code block will be re-indented with same whitespace that the initial code block was.

The whitespace preceding the second line of code determines the peripheral indentation for the entiee block. All subsequent lines (after second) must begin with exact same whitespace that preceded the second line, or be an empty line.

For example:

```html
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
```

would produce the following output:

```html
<p>
  Lorem ipsum dolor sit amet
    <ul>
        Hello!
    </ul>
  consectetur adipisicing elit
</p>
```

Note that the `Hello!` was indented with same whitespace that the code in the code block was.

pypage automatically intends the output of a multi-line tag to match the indentation level of the code tag. The number of whitespace characters at the beginning of the second line of the code block determines the indentation level for the whole block. All lines of code following the second line must at least have the same level of indentation as the second line (or else, a PypageSyntaxError exception will be thrown).

##### Whitespace Removal

If a block tag is on a line by itself, surrounded only by whitespace, then that whitespace is automatically excluded from the output. This allows you indent your block tags without worrying about excess whitespace in the generated document.

### Commenting

#### The Comment Tag

Anything bounded by `{#` and `#}` will be omitted from the output. For example:

```html
<p>
  Lorem ipsum dolor sit amet
  {#
    <ul>
        Non sequitur
    </ul>
  #}
  consectetur adipisicing elit
</p>
```

#### Commenting a Block

You can comment an existing block easily, be placing the word

```html
<p>
  Lorem ipsum dolor sit amet
    {% comment for i in range(10) %}
        N = {{i}}
    {% %}
  consectetur adipisicing elit
</p>
```

The `comment` keyword before the `for` results in the entire block being commented out and omitted from the output.

License
-------

[Apache License Version 2.0](https://www.apache.org/licenses/LICENSE-2.0)
