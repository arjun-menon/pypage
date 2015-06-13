Todo
----

  - Include tag
  - Fix trailing whitespace bug
  - Fix whitespace reduction bug (see if-2.txt)
  - Raw tag (similar to the {# ... #} comment tags)
  - an option within the embedded code to suppress/override (or select) automatic indentation
  - Loop controls (continue & break)
  - Function tag
  - Handle user code errors gracefully with an optional "embed_errors" option
  - Raise an exception for 2 sec+ while loops, or make the time limit optional
  - Support '=' assignment in single-line code tags (probably not)
  - (Maybe) Provide Jinja2-like filter (|) by overloading the bitwise OR operator (if possible).
  - get it work seamlessly in both py3 and py2
  - do not allow (i.e. strip out) invalid chars in for tag target list
  - investiage: MarkupSafe (Jinja dependency)
  - colorful command-line output
  - Investigate other templating languages: Jinja, Liquid, Smarty, Django, Mustache, Handlebars, etc.
