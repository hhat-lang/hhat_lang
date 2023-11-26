from __future__ import annotations
from enum import Enum


class TypeToken(str, Enum):
    DEFAULT = "default-type"
    ATOMIC  = "atomic"

    BOOLEAN = "bool"
    INTEGER = "int"
    Q_ARRAY = "@array"
    HASHMAP = "hashmap"

    BOOLEAN_ARRAY = "bool-array"
    INTEGER_ARRAY = "int-array"
    ATOMIC_ARRAY  = "atomic-array"

    MULTI_ARRAY = "multi-array"
