from __future__ import annotations

import struct
from enum import Enum, auto
from functools import lru_cache
from typing import Any, Iterable

ACCEPTABLE_VALUES: dict = {
    "int": (int,),
    "u16": (int,),
    "u32": (int,),
    "u64": (int,),
    "float": (
        int,
        float,
    ),
    "char": (str,),
    "str": (str,),
}


class InvalidType:
    """It just exists to be used as 'default' instance for the ``ACCEPTABLE_VALUES`` above."""

    pass


class CompositeGroup(Enum):
    SymbolAttrs = auto()
    Array = auto()


class WorkingData:
    """
    Defines everything that can work as a literal, a variable, a function
    or a type name.
    """

    _value: str
    _type: str | tuple[str, ...]
    _is_quantum: bool
    _suppress_type: bool
    _hash_value: int
    __slots__ = ("_value", "_type", "_is_quantum", "_suppress_type", "_hash_value")

    def __init__(self):
        self._hash_value = hash((self.value, self.type))

    @property
    def value(self) -> str:
        return self._value

    @property
    def type(self) -> str | tuple[str, ...]:
        return self._type

    @property
    def is_quantum(self) -> bool:
        return self._is_quantum

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value and self.type == other.type

        return False

    def __repr__(self) -> str:
        type_txt = "" if self.type is None or self._suppress_type else f":{self.type}"
        return f"{self.value}{type_txt}"


class CompositeWorkingData:
    """
    Defines everything that can have multiple data grouped together, such as an array
    of data, or a variable with attribute/method, or a type or function with their
    namespace
    """

    _group: tuple[str, ...]
    _type: str
    _group_type: CompositeGroup
    _is_quantum: bool
    _suppress_type: bool
    _hash_value: int
    __slots__ = (
        "_group",
        "_type",
        "_group_type",
        "_is_quantum",
        "_suppress_type",
        "_hash_value",
    )

    def __init__(self):
        self._hash_value = hash(
            (
                hash(self._group),
                hash(self._type),
                hash(self._group_type),
                hash(self._is_quantum),
            )
        )

    @property
    def value(self) -> tuple[str, ...]:
        return self._group

    @property
    def type(self) -> str:
        return self._type

    @property
    def group_type(self) -> CompositeGroup:
        return self._group_type

    @property
    def is_quantum(self) -> bool:
        return self._is_quantum

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return (
                self._group == other._group
                and self._type == other._type
                and self._group_type == other._group_type
                and self._is_quantum == other._is_quantum
            )
        return False

    def __hash__(self) -> int:
        return self._hash_value

    def __iter__(self) -> Iterable:
        return iter(self._group)

    def __repr__(self) -> str:
        txt = "" if self.type is None or self._suppress_type else f":{self.type}"
        return ".".join(str(k) for k in self._group) + f"{txt}"


class Symbol(WorkingData):
    """
    It can be a variable, a function, a type, an argument or a parameter name.
    """

    def __init__(self, value: str, symbol_type: str | None = None):
        self._value = value
        self._type = symbol_type or "`symbol"
        self._is_quantum = value.startswith("@")
        self._suppress_type = True
        super().__init__()


class CompositeSymbol(CompositeWorkingData):
    """
    When a symbol has attributes, properties or methods.
    """

    def __init__(self, value: tuple[str, ...]):
        self._group = value
        self._type = "str"
        self._group_type = CompositeGroup.SymbolAttrs
        self._is_quantum = value[-1].startswith("@")
        self._suppress_type = True
        super().__init__()


class Atomic(Symbol):
    """
    An atomic data.
    """

    pass


class CoreLiteral(WorkingData):
    """
    Any defined literal by the dialect.
    """

    def __init__(self, value: str, lit_type: str | tuple[str, ...]):
        match lit_type:
            case str():
                if (value.startswith("@") and not lit_type.startswith("@")) or (
                    not value.startswith("@") and lit_type.startswith("@")
                ):
                    raise ValueError(
                        f"Literal got incompatible {value} value and type {lit_type}."
                    )
                self._is_quantum = lit_type.startswith("@")

            case tuple():
                if (value.startswith("@") and not lit_type[-1].startswith("@")) or (
                    not value.startswith("@") and lit_type[-1].startswith("@")
                ):
                    raise ValueError(
                        f"Literal got incompatible {value} value and type {lit_type}."
                    )
                self._is_quantum = lit_type[-1].startswith("@")

        self._value = value
        self._type = lit_type
        self._suppress_type = False
        super().__init__()

    @lru_cache
    def transform_bin(self) -> str:
        value: str

        try:
            # works if integer
            value = bin(int(self.value.strip("@")))[2:]

        except ValueError:
            try:
                # works if float
                value = "".join(
                    f"{k:08b}" for k in struct.pack(">d", float(self.value.strip("@")))
                )

            except ValueError:
                # works if string
                value = "".join(f"{ord(s):08b}" for s in self.value)

        return value

    def _op_bitwise(self, op: str, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return getattr(self.value, op)(other.value)

        if isinstance(other, ACCEPTABLE_VALUES.get(self._type, InvalidType)):
            return getattr(self.value, op)(other)

        return False

    # def __eq__(self, other: Any) -> bool:
    #     return self._op_bitwise("__eq__", other)

    def __le__(self, other) -> bool:
        return self._op_bitwise("__le__", other)

    def __ge__(self, other) -> bool:
        return self._op_bitwise("__ge__", other)

    def __lt__(self, other) -> bool:
        return self._op_bitwise("__lt__", other)

    def __ne__(self, other) -> bool:
        return self._op_bitwise("__ne__", other)

    @property
    def bin(self) -> str:
        return self.transform_bin()


class CompositeLiteral(CompositeWorkingData):
    """
    Mostly to represent array of literals.
    """

    pass


class CompositeMixData(CompositeWorkingData):
    """
    Account for all sorts of data in an array or symbol a composition.
    It can be an array with literals and variables, a symbol with
    multiple attributes or methods (wonder if it's useful to have anyway).
    """

    pass
