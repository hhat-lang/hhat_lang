"""
The IR recognized by H-hat's core code.
"""

from __future__ import annotations

from typing import Protocol


class T(Protocol):
    @property
    def name(self) -> str: ...


class CoreIR:
    def __init__(self):
        self._functions: IRFunctions = IRFunctions()
        self._types: IRTypes = IRTypes()
        self._main: IRMain = IRMain()

    @property
    def functions(self) -> IRFunctions:
        return self._functions

    @property
    def types(self) -> IRTypes:
        return self._types

    @property
    def main(self) -> IRMain:
        return self._main


class IRFunctions:
    pass


class IRTypes:
    def __init__(self):
        self._data = dict()

    def add_type(self, obj: T) -> IRTypes:
        if obj.name not in self._data:
            self._data[obj.name] = obj
        return self

    def add_type_obj(self, obj: T) -> IRTypes:
        self.add_type(obj)
        return self

    def __getitem__(self, name: tuple[str, ...]) -> T:
        return self._data[name]

    def __setitem__(self, value: T) -> None:
        self.add_type(value)


class TypeContent:
    pass


class IRMain:
    pass
