from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from collections import OrderedDict
from collections.abc import Mapping
from typing import (
    Any,
    Generic,
    Hashable,
    Iterator,
    Protocol,
    TypeVar,
    runtime_checkable,
)
from uuid import NAMESPACE_OID

from hhat_lang.core.data.core import Symbol, CompositeSymbol
from hhat_lang.core.error_handlers.errors import ErrorHandler
from hhat_lang.core.types.utils import AbstractTypeDef


def gen_uuid(obj: Hashable) -> int:
    return int(uuid.uuid5(NAMESPACE_OID, f"{obj}").hex, 16)


@runtime_checkable
class KeyObj(Protocol):
    """A generic key object to bound as key to ``SymbolOrdered`` instance."""

    @property
    def value(self) -> Any:
        pass

    def __hash__(self) -> int:
        pass

    def __eq__(self, other: Any) -> bool:
        pass


@runtime_checkable
class KeyObjType(Protocol):
    @property
    def members(self) -> Any:
        pass


@runtime_checkable
class ValueObj(Protocol):
    """A generic value object to bound as value to ``SymbolOrdered`` instance."""

    @property
    def value(self) -> Any:
        pass


Key = TypeVar("Key", bound=KeyObj | KeyObjType)
Value = TypeVar("Value", bound=ValueObj | AbstractTypeDef)

Keys = KeyObj | KeyObjType


class HatOrderedDict(Mapping, Generic[Key, Value]):
    """
    A special OrderedDict that accepts Symbol as keys but transforms them
    as str to unpack the class. Useful for building data structures such
    as ``SingleTypeDef``, ``StructTypeDef``, etc.
    """

    _data: OrderedDict[Key, Value]

    def __init__(self, data: dict | OrderedDict | None = None):
        self._data = OrderedDict() if data is None else OrderedDict(data)

    def __setitem__(self, key: Key, value: Value) -> None:
        if isinstance(key, Keys):
            self._data[key] = value

        else:
            raise ValueError(
                f"{key} ({type(key)}) is not valid key for data collection."
            )

    def __getitem__(self, key: Key) -> Any:
        if isinstance(key, Keys):
            return self._data[key]

        raise KeyError(f"'{key}' is not found in data collection.")

    def __len__(self) -> int:
        return len(self._data)

    def items(self) -> Iterator:
        yield from self._data.items()

    def keys(self) -> Iterator:
        for k in self._data.keys():
            yield k.value if hasattr(k, "value") else k

    def values(self) -> Iterator:
        return iter(self._data.values())

    def __iter__(self) -> Iterator:
        return iter(self._data)

    def __repr__(self) -> str:
        return str(self._data)


class Result(ABC):
    """The `Result` class is meant to be used for instructions execution results"""

    def __init__(self, value: Any):
        self.value = value

    @abstractmethod
    def result(self) -> Any: ...


class Ok(Result):
    """Use `Ok` when an instruction result returns successfully."""

    def result(self) -> Any:
        return self.value


class Error(Result):
    """Use `Error` when an instruction result returns an error (`ErrorHandler`)."""

    def result(self) -> ErrorHandler:
        return self.value
