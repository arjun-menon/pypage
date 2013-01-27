Static Python Page Generator (pypage)
=====================================
**pypage** is a really simple static page generator for Python. Ever wanted to programmatically generate parts of your HTML page without resorting to server-side solutions? (perhaps you can only host static pages?) Well, that's where **pyapge** come in. It's a drop-dead simple solution for generating snippets or the whole of you static page using Python.

Usage
-----
**pypage** replaces the content enclosed by `<python>` and `<py>` in your static page, with content (passed as strings) to the `write(str)` function within these code segments.

### Multi-line Delimiter
The `<python>` tag is used when you have more the one line of  Python code.

Here is an example of how it works:

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

            def write_list(*items):
                write( "\n".join( li(item) for item in items ) )
            
            write_list('Red', 'Blue', 'Green')
            </python>
        </ul>
    </body>
</html>
```

On running `pypage`, the above document gets turned into:

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

