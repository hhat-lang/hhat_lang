from __future__ import annotations

from typing import Any


class WorkingData:
    """
    Defines everything that can work as a literal, a variable, a function
    or a type name.
    """

    _name: str
    _type: str

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._type

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, WorkingData):
            if self.name == other.name and self.type == other.type:
                return True
        return False

    def __hash__(self) -> int:
        return hash((self.name, self.type))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name} {self.type})"


class Symbol(WorkingData):
    """
    It can be a variable, a function, a type, an argument or a parameter name.
    """

    def __init__(self, name: str, symbol_type: str | None = None):
        self._name = name
        self._type = symbol_type

    def __repr__(self) -> str:
        type_txt = "" if self.type is None else f" {self.type}"
        return f"{self.__class__.__name__}({self.name}{type_txt})"


class Atomic(Symbol):
    """
    An atomic data.
    """

    pass


class Literal(WorkingData):
    """
    Any defined literal by the dialect.
    """

    def __init__(self, value: Any, lit_type: str):
        self._name = value
        self._type = lit_type
