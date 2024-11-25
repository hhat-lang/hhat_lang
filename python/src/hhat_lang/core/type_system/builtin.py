from __future__ import annotations

from hhat_lang.core.type_system import FullName, NameSpace
from hhat_lang.core.type_system.base import BaseDataType, SingleBaseMember


class BuiltinNamespace(NameSpace):
    _is_builtin = True
    _names = ()


class BuiltinType(BaseDataType[SingleBaseMember]):
    def __init__(self, name: str):
        super().__init__(FullName(BuiltinNamespace(name), name))
        self._is_builtin = True

    def add_member(self, new_member: SingleBaseMember) -> BuiltinType:
        self._data[self._name] = new_member
        return self
