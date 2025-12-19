from __future__ import annotations

from abc import ABC
from enum import Enum, auto
from typing import Any


class DataKind(Enum):
    CONSTANT = auto()
    IMMUTABLE = auto()
    MUTABLE = auto()
    APPENDABLE = auto()


def isquantum(data: Any) -> bool:
    """Check if a given object is quantum"""

    if isinstance(data, str):
        return data.startswith("@")

    if hasattr(data, "is_quantum"):
        return data.is_quantum

    return False


def has_same_paradigm(data1: Any, data2: Any) -> bool:
    if isquantum(data1) and isquantum(data2):
        return True

    if not isquantum(data1) and not isquantum(data2):
        return True

    return False


class AbstractDataDef(ABC):
    """Abstract data container. To prevent circular imports"""
