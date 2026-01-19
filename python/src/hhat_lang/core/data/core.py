"""
Syntax examples made in this module are just for anecdotal purposes;
H-hat core's super-module does not have any syntax or grammar definitions.
"""

from __future__ import annotations

import struct
import sys
from enum import Enum, auto
from functools import reduce
from typing import Any, Iterable

from hhat_lang.core.data.utils import has_same_paradigm, isquantum
from hhat_lang.core.error_handlers.errors import (
    ArrayElemsNotSameError,
    ArrayQuantumClassicalMixedError,
    LiteralTypeMismatchError,
)


class AllNoneQuantum(Enum):
    """
    Class to be used when checking whether an array is either fully quantum or classical, or mixed.
    """

    AllQuantum = auto()
    NoneQuantum = auto()
    Mixed = auto()


ACCEPTABLE_TYPE_VALUES: dict = {
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
    """
    It just exists to be used as 'default' class check for the ``ACCEPTABLE_TYPE_VALUES`` dict.
    """

    pass


class CompositeGroup(Enum):
    SymbolAttrs = auto()
    LiteralArray = auto()


##################
# SYMBOL SECTION #
##################


class Symbol:
    """
    It can be a variable, a function, a type, an argument or a parameter name.
    """

    _value: str
    _is_quantum: bool
    _hash_value: int
    __slots__ = ("_value", "_is_quantum", "_hash_value")

    def __init__(self, value: str):
        self._value = value
        self._is_quantum = value.startswith("@")
        self._hash_value = hash(self._value)

    @property
    def value(self) -> str:
        return self._value

    @property
    def is_quantum(self) -> bool:
        return self._is_quantum

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        return hash(self) == hash(other)

    def __bool__(self) -> bool:
        """
        This method is for when using truthiness expressions, like::

            Symbol("a") or Symbol("b")  # returns `Symbol("a")`
            Symbol("null") or Symbol("x")  # returns `Symbol("b")`
            Symbol("null") or None  # returns `None`
        """

        return self._value != "null"

    def __repr__(self) -> str:
        return f"{self._value}"


class Tmp(Symbol):
    """
    To be used as a temporary symbol only. Especially useful when handling
    quantum functions results without assigning the result to a variable. For
    instance::

        @redim(@0)

    This should be defined as ``Tmp("@redim(@0)")`` symbol inside a data
    container.
    """

    def append_to_name(self, text: str) -> Tmp:
        self._value += f"({text})"
        return self


class Alias(Symbol):
    """
    Alias to a type or function name
    """

    def __init__(self, value: str):
        super().__init__(value)


class CompositeSymbol:
    """
    When a symbol has attributes, properties or methods. It can be an import::

        use(type:math.arithmetic.{add sub})

    it can be a type member::

        point.x
        sys-flag.ERROR
        @bell_t.@source
    """

    _value: tuple[Symbol, ...]
    _type: CompositeGroup
    _is_quantum: bool
    _hash_value: int
    __slots__ = ("_value", "_type", "_is_quantum", "_hash_value")

    def __init__(self, value: tuple[Symbol, ...]):
        self._value = value
        self._type = CompositeGroup.SymbolAttrs
        self._is_quantum = value[0].is_quantum
        self._hash_value = hash((hash(self._value), hash(self._type), hash(self._is_quantum)))

    @property
    def value(self) -> tuple[Symbol, ...]:
        return self._value

    @property
    def type(self) -> CompositeGroup:
        return self._type

    @property
    def is_quantum(self) -> bool:
        return self._is_quantum

    def __eq__(self, other: Any) -> bool:
        return hash(self) == hash(other)

    def __hash__(self) -> int:
        return self._hash_value

    def __iter__(self) -> Iterable:
        return iter(self._value)

    def __repr__(self) -> str:
        return ".".join(str(k) for k in self._value)


class AsArray:
    """
    A class to resolve the representation of array of symbols, as in ``[u32]``.
    Usually to be used for types definition.
    """

    _value: Symbol | CompositeSymbol
    _is_quantum: bool
    __slots__ = ("_value", "_is_quantum", "_hash_value")

    def __init__(self, value: Symbol | CompositeSymbol):
        self._value = value
        self._is_quantum = value.is_quantum
        self._hash_value = hash((self.__class__.__name__, self._value))

    @property
    def value(self) -> Symbol | CompositeSymbol:
        return self._value

    @property
    def is_quantum(self) -> bool:
        return self._is_quantum

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        return hash(self) == hash(other)

    def __repr__(self) -> str:
        return f"[{self._value}]"


class Atomic(Symbol):
    """
    An atomic data.
    """

    pass


class Pointer(Symbol):
    """A pointer representation."""

    pass


class Reference(Symbol):
    """A reference representation"""

    pass


###################
# LITERAL SECTION #
###################


class Literal:
    """
    Any defined literal by the dialect. Examples::

        1               // integer
        "hoi quantum!"  // string
        @4              // quantum unsigned integer
        19.0i           // imaginary

    ``Literal``'s ``value`` should be the literal's string and ``lit_type`` argument
    should be its type as a ``Symbol`` or ``CompositeSymbol`` instance::

        Literal("1", Symbol("int"))             // H-hat literal for integer 1
        Literal("hoi quantum!", Symbol("str"))  // H-hat literal for string
        Literal("@4", Symbol("@int"))           // H-hat literal for quantum unsigned integer
        Literal("19.0i", Symbol("imag"))        // H-hat literal for imaginary
    """

    _value: str
    _type: Symbol | CompositeSymbol
    _is_quantum: bool
    _hash_value: int
    _bin: str
    __slots__ = ("_value", "_type", "_is_quantum", "_hash_value", "_bin")

    def __init__(self, value: str, lit_type: Symbol | CompositeSymbol):
        if has_same_paradigm(value, lit_type):
            self._value = value
            self._type = lit_type
            self._is_quantum = isquantum(value)
            self._hash_value = hash((self.value, self.type))
            self._bin = self.transform_bin()

        else:
            sys.exit(LiteralTypeMismatchError(value, lit_type)())

    @property
    def value(self) -> str:
        return self._value

    @property
    def type(self) -> Symbol | CompositeSymbol:
        return self._type

    @property
    def is_quantum(self) -> bool:
        return self._is_quantum

    @property
    def bin(self) -> str:
        return self._bin

    def transform_bin(self) -> str:
        value: str

        try:
            # works if integer
            value = bin(int(self.value.strip("@")))[2:]

        except ValueError:
            try:
                # works if float
                value = "".join(f"{k:08b}" for k in struct.pack(">d", float(self.value.strip("@"))))

            except ValueError:
                # works if string
                value = "".join(f"{ord(s):08b}" for s in self.value)

        return value

    def _op_bitwise(self, op: str, other: Any) -> bool:
        # TODO: improve this function to account for custom checks, e.g. for quantum data

        if isinstance(other, self.__class__):
            return getattr(self.value, op)(other.value)

        if isinstance(other, ACCEPTABLE_TYPE_VALUES.get(self._type, InvalidType)):
            return getattr(self.value, op)(other)

        return False

    def __le__(self, other) -> bool:
        return self._op_bitwise("__le__", other)

    def __ge__(self, other) -> bool:
        return self._op_bitwise("__ge__", other)

    def __lt__(self, other) -> bool:
        return self._op_bitwise("__lt__", other)

    def __ne__(self, other) -> bool:
        return self._op_bitwise("__ne__", other)

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)

        return False

    def __repr__(self) -> str:
        return f"{self._value}<{self._type}>"


class LiteralArray:
    """
    Represent an array of literals of the same type::

        [1 2 3]
        [0.2 2.0 200.2 2020.2]
        ["h" "o" "i"]
    """

    _value: tuple[Literal, ...]
    _type: Symbol | CompositeSymbol
    _is_quantum: bool
    _hash_value: int
    __slots__ = ("_value", "_type", "_is_quantum", "_hash_value")

    def __init__(self, value: tuple[Literal, ...]):
        if has_same_type(*value):
            match all_or_none_quantum(value):
                case AllNoneQuantum.AllQuantum:
                    self._is_quantum = True

                case AllNoneQuantum.NoneQuantum:
                    self._is_quantum = False

                case AllNoneQuantum.Mixed:
                    sys.exit(ArrayQuantumClassicalMixedError(value)())

            self._value = value
            self._type = value[0].type
            self._hash_value = hash(value)

        else:
            sys.exit(ArrayElemsNotSameError(value)())

    @property
    def value(self) -> tuple[Literal, ...]:
        return self._value

    @property
    def type(self) -> Symbol | CompositeSymbol:
        return self._type

    @property
    def is_quantum(self) -> bool:
        return self._is_quantum

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)

        return False

    def __iadd__(self, other: Any) -> LiteralArray:
        if isinstance(other, LiteralArray) and hasattr(other, "value"):
            return LiteralArray(self._value + other.value)

        raise ValueError()

    def __add__(self, other: Any) -> LiteralArray:
        if isinstance(other, LiteralArray):
            return LiteralArray(self._value + other.value)

        if hasattr(other, "value"):
            return LiteralArray(self._value + (other.value,))

        raise ValueError()

    def __radd__(self, other: Any) -> LiteralArray:
        if isinstance(other, LiteralArray):
            return LiteralArray(other.value + self._value)

        if hasattr(other, "value"):
            return LiteralArray((other.value,) + self._value)

        raise ValueError()

    def __getitem__(self, item: int | Any) -> Literal:
        if isinstance(item, int):
            return self._value[item]
        raise ValueError()

    def __iter__(self) -> Iterable:
        return iter(self._value)

    def __repr__(self) -> str:
        return f"[{' '.join(str(k) for k in self._value)}]<{self._type}>"


######################################
# TUPLE OF COMPOSITE OBJECTS SECTION #
######################################


class ObjTuple:
    """
    Aggregate multiple data into a tuple. Data can be ``Symbol``, ``Literal``,
    ``CompositeSymbol`` and ``CompositeLiteral``. Example::

        [a b 1.0]
        [3 5.0 -12]
        [7i "hoi"]

    A composite tuple may not have a proper type definition; it should be thought
    as an aggregate of heterogeneous objects.
    """

    # TODO: implement it


##############
# UTIL TOOLS #
##############

SymbolObj = Symbol | CompositeSymbol | AsArray
LiteralObj = Literal | LiteralArray
SimpleObj = Symbol | Literal
ObjArray = LiteralArray | AsArray
HasQuantumT = SymbolObj | LiteralObj


def has_correct_paradigm_ordering(*obj_list: SimpleObj | ObjArray) -> bool:
    """
    Checks whether a tuple of ``Symbol`` or ``Literal`` has the correct paradigm ordering,
    that is: quantum can contain classical but classical cannot contain quantum. Examples::

        @some.@thing        // correct
        @other.thing        // correct
        some.thing          // correct
        @some.@long.thing   // correct
        @other.long.thing   // correct

        other.@thing        // incorrect
        @other.long.@thing  // incorrect
    """

    _is_quantum = obj_list[0].is_quantum

    for n, obj in enumerate(obj_list[1:]):
        if obj.is_quantum and not _is_quantum:
            return False

        _is_quantum = obj.is_quantum and _is_quantum

    return True


def all_or_none_quantum(value: tuple[Symbol | Literal, ...]) -> AllNoneQuantum:
    """
    Check whether all elements are quantum (``AllNoneQuantum.AllQuantum``),
    none are quantum (``AllNoneQuantum.NoneQuantum``), or mixed (``AllNoneQuantum.Mixed``).
    """

    if all(k.is_quantum for k in value):
        return AllNoneQuantum.AllQuantum

    if any(k.is_quantum for k in value):
        return AllNoneQuantum.Mixed

    return AllNoneQuantum.NoneQuantum


def has_same_type(*value: Literal) -> bool:
    """Check elements have the same type inside a literal tuple."""

    def _check_type(_new: Literal | bool, _acc: Literal | bool) -> bool:
        if isinstance(_new, Literal) and isinstance(_acc, Literal):
            return _acc if _new.type == _acc.type else False

        return False

    return reduce(_check_type, value)
