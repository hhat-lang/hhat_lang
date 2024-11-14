"""
Useful properties to help building the IRs (CoreIR depends on them).
"""

from __future__ import annotations

from collections import OrderedDict
from enum import StrEnum
from typing import Any, Iterable

from hhat_lang.dialect_builder.ir.result_handler import Result, ResultType


class DataTypesEnum(StrEnum):
    ENUM = "enum"
    STRUCT = "struct"
    UNION = "union"
    MEMBER = "member"


class NameSpace:
    def __init__(self, *names: Any):
        self._names: tuple[str, ...] = names
        self._full_name: str = ".".join(name for name in self._names)

    def add(self, *sub_namespaces: str) -> NameSpace:
        return NameSpace((*self._names, *sub_namespaces))

    @property
    def full_name(self) -> str:
        return self._full_name

    def __call__(self, *sub_namespaces: str) -> NameSpace:
        return self.add(*sub_namespaces)

    def __hash__(self) -> int:
        return hash(self._names)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, NameSpace):
            return self._names == other._names
        raise NotImplementedError


class TypeName:
    def __init__(self, namespace: NameSpace, name: str):
        self._namespace = namespace
        self._name = name

    @property
    def namespace(self) -> NameSpace:
        return self._namespace

    @property
    def name(self) -> str:
        return self._name

    @property
    def full_name(self):
        return f"{self._namespace}.{self._name}"

    @property
    def full_name_tuple(self):
        return self._namespace, self._name


class TypeMember:
    def __init__(self, member_name: str, member_type: str):
        self._name = member_name
        self._type = member_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def full_name_tuple(self) -> tuple[str]:
        return (self._name,)

    @property
    def type(self) -> str:
        return self._type


# class TypeOld:
#     _namespace: str
#     _name: str
#     _datatype: DataTypesEnum
#     _body: dict[tuple[str, str], Type]
#
#     def __init__(
#         self, type_name: str, datatype: DataTypesEnum, namespace: str | None = None
#     ):
#         self._namespace = namespace or "main"
#         self._name = type_name
#         self._datatype = datatype
#         self._body = dict()
#         self._has_body: bool = False
#
#     @property
#     def namespace(self) -> str:
#         return self._namespace
#
#     @property
#     def name(self) -> str:
#         return self._name
#
#     @property
#     def full_name(self) -> str:
#         return f"{self._namespace}.{self._name}"
#
#     @property
#     def full_name_tuple(self) -> tuple[str, ...]:
#         return self.namespace, self.name
#
#     @property
#     def datatype(self) -> DataTypesEnum:
#         return self._datatype
#
#     @property
#     def body(self) -> Any:
#         return self._body
#
#     @property
#     def has_body(self) -> bool:
#         return self._has_body
#
#     def add_body(self, body: tuple[tuple[tuple[str, str], Type], ...]) -> Type:
#         if not self.has_body:
#             for name, value in body:
#                 if name not in self._body:
#                     if name == self.full_name_tuple:
#                         raise ValueError(
#                             f"types cannot be recursively defined; member name '{name}'"
#                             f" is the type name '{self.full_name_tuple}'."
#                         )
#
#                     if isinstance(value, Type):
#                         self._body[name] = value
#                     else:
#                         raise ValueError(
#                             f"type {self.full_name} ({self.datatype.value}) "
#                             f"has a member with invalid type '{value}'."
#                         )
#                 else:
#                     raise ValueError(
#                         f"type {self.full_name} ({self.datatype.value}) "
#                         f"has a duplicated member {name} defined."
#                     )
#         return self
#
#     def __hash__(self) -> int:
#         return hash((self._namespace, self._name, self._datatype))
#
#     def __eq__(self, other: Any) -> bool:
#         if isinstance(other, Type):
#             return hash(self) == hash(other) and hash(self.body) == hash(other.body)
#         return False
#
#     def __contains__(self, item: Any) -> bool:
#         return item in self._body


class Type:
    def __init__(self, datatype: DataTypesEnum, namespace: str, name: str):
        self.type: DataTypesEnum = datatype
        self._namespace: str = namespace
        self._name: str = name

    @property
    def namespace(self):
        return self._namespace

    @property
    def name(self):
        return self._name

    @property
    def full_name_tuple(self):
        return self.namespace, self.name


TypeBodyData = OrderedDict[tuple[str, ...], Type | TypeMember]


class TypeBody:

    def __init__(self):
        self._data: TypeBodyData = OrderedDict()

    def add(self, member: Type | TypeMember) -> Result:
        if member.full_name_tuple not in self._data:
            self._data[member.full_name_tuple] = member
            result = Result(ResultType.OK)
        else:
            result = Result(ResultType.ERROR)
        return result(member.full_name_tuple)

    @property
    def data(self) -> TypeBodyData:
        return self._data

    def __getitem__(self, item: tuple[str, ...]) -> Result:
        data = self._data.get(item, False)
        if data:
            return Result(ResultType.OK)(data)
        return Result(ResultType.ERROR)(item)

    def __iter__(self) -> Iterable:
        yield from self._data.values()
