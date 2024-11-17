"""
Useful properties to help building the IRs (CoreIR depends on them).
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any


class DataTypesEnum(StrEnum):
    ENUM = "enum"
    STRUCT = "struct"
    UNION = "union"
    MEMBER = "member"


class QSize:
    def __init__(self):
        self._min: int = 0
        self._max: int | None = None

    @property
    def min(self) -> int:
        return self._min

    @property
    def max(self) -> int | None:
        return self._max

    def add_min(self, value: int) -> QSize:
        self._min = value if isinstance(value, int) else 0
        return self

    def add_max(self, value: int) -> QSize:
        self._max = value if isinstance(value, int) else None
        return self


class NameSpace:
    def __init__(self, *names: Any):
        self._names: tuple[str, ...] = names
        self._full_name: str = ".".join(name for name in self._names)

    def add(self, *sub_namespaces: str) -> NameSpace:
        return NameSpace((*self._names, *sub_namespaces))

    @property
    def namespace_str(self) -> str:
        return self._full_name

    def __call__(self, *sub_namespaces: str) -> NameSpace:
        return self.add(*sub_namespaces)

    def __hash__(self) -> int:
        return hash(self._names)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, NameSpace):
            return self._names == other._names
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.namespace_str


class FullName:
    def __init__(self, namespace: NameSpace, name: str):
        self._namespace: NameSpace = namespace
        self._name: str = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def namespace(self) -> NameSpace:
        return self._namespace

    @property
    def full_name(self) -> str:
        return self._namespace.namespace_str + self._name

    def __hash__(self) -> int:
        return hash(self.full_name)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FullName):
            return self._namespace == other._namespace and self._name == other._name
        raise NotImplementedError

    def __repr__(self) -> str:
        return ".".join((self.namespace.namespace_str, self.name))


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

