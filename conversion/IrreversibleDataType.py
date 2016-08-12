from enum import Enum


class IrreversibleType(Enum):
    """
    Enumerator for cheetah expresion types that are rarely used or can't be converted
    """
    assertion = ["#assert"]
    includes = ["#include"]
    cachePlaceholder = ["$*"]
    filters = ["#filter"]
    extends = ["#extends"]
    implements = ["#implements"]
    attr = ["#attr"]
    deletion = ["#del"]
    raiseException = ["#raise"]
    errorCatcher = ["#errorCatcher"]
    breakpoint = ["#breakpoint"]
    encoding = ["#encoding"]
    shBang = ["#shBang"]

    tryCatch = ["#try", "#end try"]
    raw = ["#raw", "#end raw"]
    define = ["#def", "#end def"]
    repeat = ["#repeat", "#end repeat"]
    executePython = ["<%=", " %>"]
    executePythonNoOutput = ["<%", " %>"]
    compilerSettings = ["#compiler-settings", "#end #compiler-settings"]
    whileLoop = ["#while", "#end while"]
    unless = ["#unless", "#end unless"]
    cache = ["#cache", "#end cache"]


class DataTypes(Enum):
    """
     Enumerator for cheetah expresion types that might be problematic
     """
    echo = ["#echo"]
    importFrom = ["#import, #from"]
    slurp = ["#slurp"]
    block = ["#block"]
    ifBlock = ["#if"]
    stop = ["#stop"]
    forLoop = ["#for"]


explanations = {
    IrreversibleType.tryCatch: "Need to remove try catch statements\n",
    IrreversibleType.includes: "Jinja2 can't include python code. Templates have to be imported differently.\n"
                               "Need to remove includes from code\n",
    IrreversibleType.assertion: "Need to remove assertion\n",
    DataTypes.echo: "#Echo was replaced with: echo{number}"
                           " Need to add echo object to environment\n"
                           "Example: #echo 1+2; > {{echo1}} > def echo1(): return 1+2\n",
    IrreversibleType.compilerSettings: "Jinja2 doesn't have compiler settings. It should be removed\n",
    IrreversibleType.unless: "Jinja2 doesn't support unless. It should be removed\n",
    IrreversibleType.filters: "Jinja2 implements filter differently."
                              " Look up documentation and change code accordingly\n",
    IrreversibleType.executePython: "Python can't be executable in Jinja2. Code should be removed\n",
    IrreversibleType.executePythonNoOutput: "Python can't be executable in Jinja2. Code should be removed\n",
    DataTypes.importFrom: "Import was removed\n"
                          "Need to add imported object to environment to use as normal placeholder\n",
    DataTypes.forLoop: "Could not find end of the loop\n",
    DataTypes.ifBlock: "Could not find end of if statement\n",
    IrreversibleType.whileLoop: "Could not find end of the loop\n",
    IrreversibleType.raiseException: "Remove/replace exception raiser\n",

}
