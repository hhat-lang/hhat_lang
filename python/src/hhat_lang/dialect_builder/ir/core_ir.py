"""
The IR recognized by H-hat's core code.
"""

from __future__ import annotations

from hhat_lang.core.type_system.base import BaseDataType


# TODO: make it child of `hhat_lang.core.ir.BaseIR`
class CoreIR:
    def __init__(self):
        self._functions: IRFns = IRFns()
        self._types: IRTypes = IRTypes()
        self._main: IRMain = IRMain()

    @property
    def functions(self) -> IRFns:
        return self._functions

    @property
    def types(self) -> IRTypes:
        return self._types

    @property
    def main(self) -> IRMain:
        return self._main


class IRFns:
    pass


class IRTypes:
    def __init__(self):
        self._data = dict()

    def add_type(self, obj: BaseDataType) -> IRTypes:
        if obj.name not in self._data:
            self._data[obj.name] = obj
        return self

    def add_type_obj(self, obj: BaseDataType) -> IRTypes:
        self.add_type(obj)
        return self

    def __getitem__(self, name: tuple[str, ...]) -> BaseDataType:
        return self._data[name]

    def __setitem__(self, value: BaseDataType) -> None:
        self.add_type(value)


class TypeBody:
    """
    Body of the type, e.g. type members (content)
    """

    pass


class IRMain:
    pass


class IRLiteral:
    pass


class IRId:
    pass


class IRExpr:
    pass


class IRDeclare:
    pass


class IRAssign:
    pass


class IRCall:
    pass


class IRClojureBody:
    """
    Body of the clojure, e.g. function, main, control flows
    """

    pass
