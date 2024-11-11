"""
Useful properties to help building the IRs (CoreIR depends on them).
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Iterable


class DataTypesEnum(StrEnum):
    ENUM = "enum"
    STRUCT = "struct"
    UNION = "union"
    MEMBER = "member"


class Type:
    _namespace: str
    _name: str
    _datatype: DataTypesEnum
    _body: dict[tuple[str, str], Type]

    def __init__(
        self, type_name: str, datatype: DataTypesEnum, namespace: str | None = None
    ):
        self._namespace = namespace or "main"
        self._name = type_name
        self._datatype = datatype
        self._body = dict()
        self._has_body: bool = False

    @property
    def namespace(self) -> str:
        return self._namespace

    @property
    def name(self) -> str:
        return self._name

    @property
    def full_name(self) -> str:
        return f"{self._namespace}.{self._name}"

    @property
    def full_name_tuple(self) -> tuple[str, ...]:
        return self.namespace, self.name

    @property
    def datatype(self) -> DataTypesEnum:
        return self._datatype

    @property
    def body(self) -> Any:
        return self._body

    @property
    def has_body(self) -> bool:
        return self._has_body

    def add_body(self, body: tuple[tuple[tuple[str, str], Type], ...]) -> Type:
        if not self.has_body:
            for name, value in body:
                if name not in self._body:
                    if name == self.full_name_tuple:
                        raise ValueError(
                            f"types cannot be recursively defined; member name '{name}'"
                            f" is the type name '{self.full_name_tuple}'."
                        )

                    if isinstance(value, Type):
                        self._body[name] = value
                    else:
                        raise ValueError(
                            f"type {self.full_name} ({self.datatype.value}) "
                            f"has a member with invalid type '{value}'."
                        )
                else:
                    raise ValueError(
                        f"type {self.full_name} ({self.datatype.value}) "
                        f"has a duplicated member {name} defined."
                    )
        return self

    def __hash__(self) -> int:
        return hash((self._namespace, self._name, self._datatype))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Type):
            return hash(self) == hash(other) and hash(self.body) == hash(other.body)
        return False

    def __contains__(self, item: Any) -> bool:
        return item in self._body
