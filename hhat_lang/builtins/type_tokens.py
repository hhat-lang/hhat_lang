from __future__ import annotations
from enum import StrEnum


class TypeToken(StrEnum):
    DEFAULT = "default-type"

    BOOLEAN = "bool"
    INTEGER = "int"
    Q_ARRAY = "@array"

    BOOLEAN_ARRAY = "bool-array"
    INTEGER_ARRAY = "int-array"

    MULTI_ARRAY = "multi-array"
