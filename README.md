QlikView Tools for Sublime Text 2/3 (v0.1.12)
================

##Sublime Text 2/3 language plugin for QlikView scripts


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

Build system allow to `batch reload` of qvw file from within of corresponding qvs script file opened in Sublime Text. 
To run `batch reload` Sublime Text should be able to find corresponding qvw file. By default it will look up qvw file with same name as qvs script in same directory. For example: We are editing file `c:\QvProjects\Project1\Apps\LoadData.qvs` in Sublime Text. By invoking build system (keyboard shortcuts for this command are `F7` or `Ctrl-B`) we effectively run shell command 

    c:\Program Files\QlikView\qv.exe /R /NoData c:\QvProjects\Project1\Apps\LoadData.qvw

Hopefully script in your LoadData.qvw file contains line `$(must_include=LoadData.qvs)`  

If qvw file stays in another directory it may be indicated explicitly in first line of qvs script file by shebang-like comment string. For example, if your script file is `c:\QvProjects\Project1\Scripts\LoadData.qvs` corresponding qvd-generator `c:\QvProjects\Project1\Apps\LoadData.qvw` would be found if qvs script has first line

    //#!c:\QvProjects\Project1\Scripts\LoadData.qvs

You may also use relative path syntax and skip file part of path string if base names of qvs and qvw file are identical. So in our last example we with same effect may put in first line of qvs script  

    //#!..\Scripts

## Installation :

### Using [Package Control][1] (*Recommended*)

For all Sublime Text 2/3 users we recommend install via [Package Control][1].

1. [Install][2] Package Control if you haven't yet.
2. Use `cmd+shift+P` then `Package Control: Install Package`
3. Look for `QlikView Tools` and install it.

### Manual Install

1. Click the `Preferences > Browse Packages…` menu
2. Browse up a folder and then into the `Installed Packages/` folder
3. Download [zip package][3] rename it to `QlikView Tools.sublime-package` and copy it into the `Installed Packages/` directory
4. Restart Sublime Text

[Last changes](CHANGELOG.md)

 [home]: https://github.com/vadimtsusko/sublime-qlikview
 [1]: https://sublime.wbond.net/
 [2]: https://sublime.wbond.net/installation
 [3]: https://github.com/vadimtsusko/sublime-qlikview/archive/master.zip
