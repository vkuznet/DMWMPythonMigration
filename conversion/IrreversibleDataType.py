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
    echo = ["#echo"]
    importFrom=["#import, #from"]
    slurp=["#slurp"]
    block = ["#block"]

