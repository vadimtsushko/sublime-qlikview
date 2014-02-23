QlikView Tools for Sublime Text
=============================

##Language plugin for QlikView load scripts


###Syntax Highlighting

* Both block comments (/\* \*/) and line comments (//) are supported. CTRL-/ key combination comment/uncomment code block with line comments (//)
* Variables, built-in functions and so on are trying properly show their boundaries by by coloring corresponding braces.
* Nesting supported for all constructs - variable as parameter of function, function within function, function within variable and so on
* Conflicts between some build-in functions and keywords (IF, LEFT, RIGHT, REPLACE) are resolving by context

![Sublime Text QLikView plugin](https://monosnap.com/image/R3lNiNrl9dKs143WVCh16vh9SIWd6F.png)

####Symbols

In qvs files subroutine names, variables in variable assignment commands and table identifiers marked as symbols. So `Goto Definition`, `Goto Symbol` and `Goto Symbol in Project` commands work.


####Build System

Build system allow to `batch reload` of qvw file from within of corresponding qvs script file opened in Sublime Text. 
To run `batch reload` Sublime Text should be able to find corresponding qvw file.
By default it will look up qvw file with same name as qvs script in same directory. For example: We are editing file `c:\QvProjects\Project1\Apps\LoadData.qvs` in Sublime Text. By invoking build system (keyboard shortcuts for this command are `F7` or `Ctrl-B`) we effectively run shell command 

    c:\Program Files\QlikView\qv.exe /R /NoData c:\QvProjects\Project1\Apps\LoadData.qvw

Hopefully script in your LoadData.qvw file contains line `$(must_include=LoadData.qvs)`  

If qvw file stays in another directory it may be indicated explicitly in first line of qvs script file by shebang-like comment string. For example, if your script file is `c:\QvProjects\Project1\Scripts\LoadData.qvs` corresponding qvd-generator `c:\QvProjects\Project1\Apps\LoadData.qvw` would be found if qvs script has first line

    //#!c:\QvProjects\Project1\Apps\LoadData.qvw

You may also use relative path syntax and skip file part of path string if base names of qvs and qvw file are identical. So in our last example we with same effect may put in first line of qvs script  

    //#!..\Apps

Ctrl-Shift-B key combination opens corresponding qlikview application instead of reloading it

####QVD Viewer

Clicking on QVD file in project panel instantly open view with information available in qvd header and LOAD statement for that QVD

![QVD Viewer](http://monosnap.com/image/3AcB6j9A7ktIx1FPyzgkflmWi63gh6.png)


##Expression Editor: Language plugin for editing QlikView expressions and variables

Expression editor used to write and store QlikView variables in convenient form.
Expression editor use YAML like format.

####Syntax highlighting

Expression editor highlight both syntax for it format and syntax of QlikView expressions edited.

![Expression editor](http://monosnap.com/image/iM1bfwD7PVuDp3eSjnKFmPjiVzI7ab.png)

On every save plugin autogenerate csv variable file in format used by QlikView Deployment Framework (by `LoadVariableCSV` subroutine)

Mandatory tags:

- LET or SET: precede name of expression. Corresponds to `Variable` field of standard QDF variable csv file 
- Definition: Corresponds to `VariableValue` field.

Optional tags:

- Tag (exported as `Priority` field of csv variable file)
- Description (exported as `Comments` field of csv variable file) 

Optional tags exported as additional variables (additional rows in csv variable file)

- Label
- Comment
- BackgroundColor
- FontColor
- TextFormat
- EnableCondition
- ShowCondition
- SortBy
- VisualCueUpper
- VisualCueLower
- Symbol
- ThousandSymbol
- MillionSymbol
- BillionSymbol

Usual minimal expression definition looks like

```
---
SET: SalesSum
Definition: Sum({<OperationType={Sale}>} Amount)
Label: Sales
Comment: Sales amount
```
And corresponding auto-generated csv file would be

```
VariableName,VariableValue,Comments,Priority
SET SalesSum,Sum({<OperationType={2}>} Amount),,
SET SalesSum.Comment,Sales amount,,
SET SalesSum.Label,Sales,,
```

####Symbols

In qlikview-vars files expression names (name after `LET` or `SET` tag) marked as symbols. So `Goto Definition`, `Goto Symbol` and `Goto Symbol in Project` commands work for expressions.

####Syntax checks

Minimal syntax checks provided: Checks for mandatory tags, checks for uniqueness of expression names  


## Installation :

### Using [Package Control][1] (*Recommended*)

For all Sublime Text 2/3 users we recommend install via [Package Control][1].

1. [Install][2] Package Control if you haven't yet.
2. Use `Ctrl+Shift+P` then `Package Control: Install Package`
3. Look for `QlikView Tools` and install it.

### Manual Install

1. Click the `Preferences > Browse Packages…` menu
2. Browse up a folder and then into the `Installed Packages/` folder
3. Download [zip package][3] rename it to `QlikView Tools.sublime-package` and copy it into the `Installed Packages/` directory
4. Restart Sublime Text

[Last changes](CHANGELOG.md)

### Compatibility

I've switched to ST3, further development will be focused on that platform.
Basic functionality (syntax highlighting for qvs files and expression files) should work on ST2.
Specifically QVD viewer does not for in ST2 and disabled explicitly in it.



 [home]: https://github.com/vadimtsusko/sublime-qlikview
 [1]: https://sublime.wbond.net/
 [2]: https://sublime.wbond.net/installation
 [3]: https://github.com/vadimtsusko/sublime-qlikview/archive/master.zip
