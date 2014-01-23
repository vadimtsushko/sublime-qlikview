QlikView Tools for Sublime Text 2 (v0.1.11-dev)
================

##Sublime Text 2 language plugin for QlikView scripts


####Some features:


* Highlighting for strings, numbers, comments, variables, keywords, built-in functions e.t.c    
* Comment / uncomment code block with CTRL-/ key combination
* Ability to run load script from within Sublime Text 2

####Highlighting

* Both block comments (/\* \*/) and line comments (//) are supported.
* Variables, built-in functions and so on are trying properly show their boundaries by by coloring corresponding braces.
* Nesting supported for all constructs - variable as parameter of function, function within function, function within variable and so on
* Conflicts between some build-in functions and keywords (IF, LEFT, RIGHT, REPLACE) are resolving by context

![Sublime Text 2 QLikView plugin](http://monosnap.com/image/pf3hQRknTGUamkLpQjWtdx5fRLYLI6.png)

####Build System

Build system allow to `batch reload` of `qvw` file from within of corresponding `qvs` script file opened in Sublime Text. 
To run `batch reload` Sublime Text should be able to find corresponding `qvw` file. By default it will look up `qvw` file with same name as `qvs` script in same directory. For example. 



[Last changes](CHANGELOG.md) 