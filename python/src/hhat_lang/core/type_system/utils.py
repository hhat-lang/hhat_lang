"""
Useful properties to help building the IRs (CoreIR depends on them).
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from hhat_lang.core.utils.result_handler import Result, ResultType


class DataTypesEnum(StrEnum):
    ENUM = "enum"
    STRUCT = "struct"
    UNION = "union"
    TYPED_MEMBER = "typed_member"
    SINGLE = "single"
    MEMBER = "member"


class Size:
    def __init__(self):
        self._size: int | None = None

    @property
    def size(self) -> int | None:
        return self._size

    def add_size(self, size: int) -> Result:
        if self._size is None and isinstance(size, int):
            self._size = size
            res = Result(ResultType.OK)
        else:
            res = Result(ResultType.ERROR)
        return res(self._size)


class QSize:
    def __init__(self):
        self._min: int = 0
        self._max: int | None = None
        self._defined: bool = False

    @property
    def min(self) -> int:
        return self._min

    @property
    def max(self) -> int | None:
        return self._max

    @property
    def defined(self) -> bool:
        return self._defined

    def inc_min(self, value: int) -> QSize:
        if isinstance(value, int):
            self._min += value
        return self

    def inc_max(self, value: int | None) -> QSize:

        if self._max is None:

            if isinstance(value, int):
                self._max = value
                return self

            if value is None:
                return self

            raise ValueError("max value for QSize must be integer (or None)")

        if isinstance(value, int):
            self._max += value

        return self

    def add_sizes(self, min_value: int, max_value: int) -> QSize:

        if not self._defined:

            if isinstance(min_value, int) and isinstance(max_value, int):
                self._min = min_value
                self._max = max_value
                self._defined = True
                return self

            raise ValueError(f"min {min_value} and max {max_value} must be integers")
        raise ValueError("Qsizes already defined")


class NameSpace:
    _is_primitive: bool

    def __init__(self, *names: Any):
        self._names: tuple[str, ...] = names
        self._full_name: str = ".".join(name for name in self._names)
        self._is_primitive = False

    def add(self, *sub_namespaces: str) -> NameSpace:
        return NameSpace((*self._names, *sub_namespaces))

    @property
    def namespace_str(self) -> str:
        return self._full_name

    @property
    def is_primitive(self) -> bool:
        return self._is_primitive

    def __call__(self, *sub_namespaces: str) -> NameSpace:
        return self.add(*sub_namespaces)

    def __hash__(self) -> int:
        return hash(self._names)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, NameSpace):
            return self._names == other._names
        return False

    def __repr__(self) -> str:
        return self.namespace_str


class FullName:
    _namespace: NameSpace
    _name: str
    _is_quantum: bool

    def __init__(self, namespace: NameSpace, name: str):
        if isinstance(namespace, NameSpace) and isinstance(name, str):
            self._namespace = namespace
            self._name = name
            self._is_quantum = True if name.startswith("@") else False
        else:
            raise ValueError(
                f"invalid namespace {namespace} ({type(namespace)}) and name {name} ({type(name)})"
            )

    @property
    def name(self) -> str:
        return self._name

    @property
    def namespace(self) -> NameSpace:
        return self._namespace

    @property
    def full_name(self) -> str:
        return self._namespace.namespace_str + self._name

    @property
    def is_quantum(self) -> bool:
        return self._is_quantum

    def __hash__(self) -> int:
        return hash(self.full_name)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FullName):
            return self._namespace == other._namespace and self._name == other._name
        return False

    def __repr__(self) -> str:
        return (
            ".".join((self.namespace.namespace_str, self.name))
            if self.namespace.namespace_str
            else self.name
        )


class BuiltinNamespace(NameSpace):
    _is_primitive = True
    _names = ()
