Static Python Page Generator (pypage)
=====================================
**pypage** is a really simple static page generator for Python. Ever wanted to programmatically generate parts of your HTML page without resorting to server-side solutions? (perhaps you can only host static pages?) Well, that's where *pypage* comes in. It's a drop-dead simple solution for generating snippets or the whole of your static page using Python.

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

* Multi-line delimiters: The `<python>` tag is used when you have more than one line of Python code. If the opening `<python>` tag is indented by 8 spaces, *pypage* will remove the initial 8 characters from every line of code following the opening delimiter. _Note:_ A caveat of multi-line delimiters is that both the opening and closing tags have to be on their own lines with no other non-space characters on them.

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

### Using pypage as a library
**pypage** exports two functions that enable it to be used as a library. The functions are:
 * `pypage(input_file, verbose=False, prettify=False)` — this function takes as argument a string of the contents 
    of the input page and returns the resulting page (also as a string).
 * `pypage_multi(*files, prepend_path='' verbose=False, prettify=False)` — this functions takes as arguments the names of one 
    or more files to be processed. The keyword argument `prepend_path` will be prepended before each file's name along with a 
    trailing `\` character. `pypage_multi` returns a dictionary mapping the file names to strings representing their 
    corresponding generated output pages.

Installation
------------
There is no straightforward way of installing *pypage* at the moment.

On POSIX systems, an easy way to use *pypage* either as a library or as a command-line tool would be to symlink to `pypage.py` on 
the `/usr/bin` directory (for use as a command-line tool) or on the `/usr/lib/python3/dist-packages` directory (for use as a 
Python3 library).

*pypage* has only been tested with Python 3 and most probably will not work under Python 2.x. To get updates 
automatically, you could clone this git repo and setup a cron job to `git pull` every now and then.

License
-------
The [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0.html).
