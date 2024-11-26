"""
The IR that a dialect AST will be converted to.

This is a dialect-specific IR, but H-hat provides it as a way
to have common structure for easy of conversion during the
CoreIR pass.
"""

from __future__ import annotations

from abc import ABC


class FirstIR(ABC):
    def __init__(self):
        self._header: FirstIRHeader = FirstIRHeader()
        self._main: FirstIRMain = FirstIRMain()

    @property
    def header(self) -> FirstIRHeader:
        return self._header

    @property
    def main(self) -> FirstIRMain:
        return self._main


class FirstIRHeader:
    _imports: FirstIRImports

    def __init__(self):
        self._imports = FirstIRImports()


class FirstIRImports:
    pass


class FirstIRFunctions:
    pass


class FirstIRTypes:
    pass


class FirstIRMacros:
    pass


class FirstIRMain:
    pass
