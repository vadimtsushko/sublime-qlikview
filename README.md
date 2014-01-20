QlikView Tools for Sublime Text 2 (v0.1.10)
================

Sublime Text 2 language plugin for QlikView scripts


####Some features:


* Highlighting for strings, numbers, comments, variables, keywords, built-in functions e.t.c    
* Comment/uncomment code block with CTRL-/ key combination
* Ability to run load script from within Sublime Text 2

####Highlighting

* Both block comments (/\* \*/) and line comments (//) are supported.
* Variables, built-in functions and so on are trying properly show their boundaries by by coloring corresponding braces.
* Nesting supported for all constucts - variable as parameter of function, function within function, function within variable and so on
* Conflicts between some build-in functions and keywords (IF, LEFT, RIGHT, REPLACE) are resolving by context
