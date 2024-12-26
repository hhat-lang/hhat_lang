"""
The IR that a dialects BaseAST will be converted to.

This is a dialects-specific IR, but H-hat provides it as a way
to have common structure for easy of conversion during the
CoreIR pass. It also should be used to do some import checking
for types and functions.
"""

from __future__ import annotations

from abc import ABC


class ASTtoIR(ABC):
    def __init__(self):
        self._header: IRHeader = IRHeader()
        self._body_not_main: IRBodyNotMain = IRBodyNotMain()
        self._main: IRMain = IRMain()

    @property
    def header(self) -> IRHeader:
        return self._header

    @property
    def main(self) -> IRMain:
        return self._main


class IRHeader:
    _imports: IRImports

    def __init__(self):
        self._imports = IRImports()


class IRImports:
    """
    Place all the imports references that are used throughout the code.
    The actual code for them should be at the `IRBodyNotMain` instance.
    """

    pass


class IRFns:
    pass


class IRTypes:
    pass


class IRMacros:
    pass


class IRBodyNotMain:
    """
    Should contain all the types and functions defined in the program.
    """

    def __init__(self):
        self._types: IRTypes = IRTypes()
        self._fns: IRFns = IRFns()


class IRMain:
    def __init__(self):
        self._main: tuple
