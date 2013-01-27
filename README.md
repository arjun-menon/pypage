Static Python Page Generator (pypage)
=====================================
**pypage** is a really simple static page generator for Python. Ever wanted to programmatically generate parts of your HTML page without resorting to server-side solutions? (perhaps you can only host static pages?) Well, that's where ***pyapge*** come in. It's a drop-dead simple solution for generating snippets or the whole of your static page using Python.

Tutorial
--------
Here's an example of what pypage does. For the following document:

```html
<html>
    <head>
        <title><py>write("Primary Colors")</py></title>
    </head>
    <body>
        List of primary colors:
        <ul>        
            <python>
            def li(item):
                return "<li>" + item + "</li>"

            def write_items(*items):
                write( "\n".join( li(item) for item in items ) )
            
            write_items('Red', 'Blue', 'Green')
            </python>
        </ul>
    </body>
</html>
```

Running `pypage`, turns it into:

```html
<html>
    <head>
        <title>Primary Colors</title>
    </head>
    <body>
        List of primary colors:
        <ul>        
            <li>Red</li>
            <li>Blue</li>
            <li>Green</li>
        </ul>
    </body>
</html>
```
**pypage** replaces the content enclosed by `<python>` and `<py>` in your static page, with the content (passed as strings) to the `write()` function within these enclosed code segments.

There are two types of Python code delimiters in *pypage*:

* Multi-line delimiters: The `<python>` tag is used when you have more than one line of Python code. If the opening `<python>` tag is indented by 8 spaces, *pypage* will remove the initial 8 characters from every line of code following the opening delimiter. A caveat of multi-line delimiters is that both the opening and closing tags have to be their own lines with no other tags/text/etc on those lines.

* In-line delimiters: The `<py>` tag is used for single lines of Python code. Both the opening and closing tags have to be on the same line.

Usage
-----
Passing the `-h` option to **pypage** will produce the following help message explaning how to use it:

    usage: pypage.py [-h] [-o OUTPUT_FILE] [-v] [-p] input_file

    Generates static HTML pages by executing the code within <python> and <py>
    tags, and replacing replacing them with the content passed to write() calls.

    positional arguments:
      input_file            HTML input file.

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT_FILE, --output_file OUTPUT_FILE
                            Write output to output_file. Default: stdout
      -v, --verbose         print a short message before preprocessing
      -p, --prettify        prettify the resulting HTML using BeautifulSoup --
                            requires BeautifulSoup4

Thanks
------
Thanks to [Anders Hammarquist](http://code.activestate.com/recipes/users/136364/) on ActiveState for writing the `importCode` [recipe](http://code.activestate.com/recipes/82234-importing-a-dynamically-generated-module/). (which I found via [StackOverflow](http://code.activestate.com/recipes/82234-importing-a-dynamically-generated-module/).)

License
-------
The [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0.html).
