"""
The IR recognized by H-hat's core code.
"""

from __future__ import annotations

from typing import Any

from hhat_lang.dialect_builder.ir.constructors import DataTypesEnum, Type


class CoreIR:
    def __init__(self):
        self._functions: IRFunctions = IRFunctions()
        self._types: IRTypes = IRTypes()
        self._variables: IRVariables = IRVariables()
        self._main: IRMain = IRMain()

    @property
    def functions(self) -> IRFunctions:
        return self._functions

    @property
    def types(self) -> IRTypes:
        return self._types

    @property
    def variables(self) -> IRVariables:
        return self._variables

    @property
    def main(self) -> IRMain:
        return self._main


class IRFunctions:
    pass


class IRTypes:
    def __init__(self):
        self._data = dict()

    def add_type(self, name: tuple[str, ...], obj: Type) -> IRTypes:
        if name != obj.full_name_tuple:
            raise ValueError(
                f"type names do not match between name '{name}' and "
                f"obj '{obj.full_name_tuple}' to be added to the IR."
            )

        if name not in self._data:
            self._data[name] = obj
        return self

    def add_type_obj(self, obj: Type) -> IRTypes:
        self.add_type(obj.full_name_tuple, obj)
        return self

    def __getitem__(self, name: tuple[str, ...]) -> Type:
        return self._data[name]

    def __setitem__(self, name: tuple[str, ...], value: Type) -> None:
        self.add_type(name, value)


class TypeContent:
    pass


class IRVariables:
    pass


class IRMain:
    pass
