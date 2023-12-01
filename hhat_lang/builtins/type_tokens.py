from __future__ import annotations
from enum import Enum


class TypeToken(str, Enum):
    DEFAULT = "default-type"
    NULL    = "null"
    ATOMIC  = "atomic"

    BOOLEAN = "bool"
    INTEGER = "int"
    Q_ARRAY = "@array"
    HASHMAP = "hashmap"

    BOOLEAN_ARRAY = "bool-array"
    INTEGER_ARRAY = "int-array"
    ATOMIC_ARRAY  = "atomic-array"

    MULTI_ARRAY   = "multi-array"

    @classmethod
    def has(cls, item: str) -> bool:
        return item in cls.__dict__.values()

    @classmethod
    def get_member(cls, item: str) -> TypeToken | None:
        for k, v in cls.__dict__.items():
            if item == v:
                return getattr(cls, k)
        return None
