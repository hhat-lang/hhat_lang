from __future__ import annotations
from enum import Enum


# all the built-in types names should be defined in this list below:
types_list = [
    "default-type",
    "null",
    "atomic",
    "bool",
    "int",
    "float",
    "str",
    "bin",
    "hex",
    "@array",
    "hashmap",
]


class IterTypes:
    types = iter(types_list)

    @classmethod
    def __next__(cls):
        return next(cls.types)


class TypeToken(str, Enum):
    # DEFAULT = "default-type"
    # NULL    = "null"
    # ATOMIC  = "atomic"
    #
    # BOOLEAN = "bool"
    # INTEGER = "int"
    # FLOAT   = "float"
    # STRING  = "str"
    # BINARY  = "bin"
    # HEXADEC = "hex"
    # Q_ARRAY = "@array"
    # HASHMAP = "hashmap"
    #
    # BOOLEAN_ARRAY = "bool-array"
    # INTEGER_ARRAY = "int-array"
    # ATOMIC_ARRAY  = "atomic-array"
    #
    # MULTI_ARRAY   = "multi-array"

    DEFAULT = next(IterTypes())
    NULL    = next(IterTypes())
    ATOMIC  = next(IterTypes())
    BOOLEAN = next(IterTypes())
    INTEGER = next(IterTypes())
    FLOAT   = next(IterTypes())
    STRING  = next(IterTypes())
    BINARY  = next(IterTypes())
    HEXADEC = next(IterTypes())
    Q_ARRAY = next(IterTypes())
    HASHMAP = next(IterTypes())

    @classmethod
    def has(cls, item: str) -> bool:
        return item in cls.__dict__.values()

    @classmethod
    def get_member(cls, item: str) -> TypeToken | None:
        for k, v in cls.__dict__.items():
            if item == v:
                return getattr(cls, k)
        return None
