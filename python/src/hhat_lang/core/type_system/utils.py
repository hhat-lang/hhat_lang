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
    SINGLE = "single"


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
        if isinstance(namespace, NameSpace) and isinstance(name, str):
            self._namespace: NameSpace = namespace
            self._name: str = name
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

    def __hash__(self) -> int:
        return hash(self.full_name)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FullName):
            return self._namespace == other._namespace and self._name == other._name
        raise NotImplementedError

    def __repr__(self) -> str:
        return ".".join((self.namespace.namespace_str, self.name))
