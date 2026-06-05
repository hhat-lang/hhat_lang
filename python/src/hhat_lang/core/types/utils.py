from __future__ import annotations

from abc import ABC
from enum import Enum, auto


class BaseTypeEnum(Enum):
    """Enum data type structures for types definitions instances"""

    CORE = auto()
    """the core types, such as bool, integers and floats types, string"""

    SINGLE = auto()
    STRUCT = auto()
    ENUM = auto()

    REMOTE_UNION = auto()
    """
    ``REMOTE_UNION``: a new data structure to be used in the future to handle remote 
    quantum data; name yet to be settled
    """


class AbstractTypeDef(ABC):
    """Abstract data type structure. To avoid circular imports."""

    _type: BaseTypeEnum

    @property
    def type(self) -> BaseTypeEnum:
        return self._type
