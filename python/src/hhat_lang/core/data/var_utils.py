from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from typing import TypeVar, Any, Generic, Iterable

from hhat_lang.core.data.core import Symbol, CompositeSymbol
from hhat_lang.core.data.utils import DataKind, isquantum
from hhat_lang.core.error_handlers.errors import DataInitializationArgumentsError
from hhat_lang.core.memory.utils import ScopeValue
from hhat_lang.core.types.abstract_base import BaseTypeDef

T = TypeVar("T")


class DataHeader:
    """
    To hold relevant and unique information regarding a data container
    (variable, temporary data, etc.). Each data header must have a name,
    a type, a kind (mutable, appendable, etc.) and an uid value (scope value).
    """

    _name: Symbol | CompositeSymbol
    _type: BaseTypeDef
    _is_quantum: bool
    _kind: DataKind
    _uid: ScopeValue
    _hash_value: int
    __slots__ = ("_name", "_type", "_is_quantum", "_kind", "_uid", "_hash_value")

    def __init__(
        self, name: Symbol | CompositeSymbol, data_type: BaseTypeDef, kind: DataKind, counter: int
    ):
        if (
            isinstance(name, Symbol | CompositeSymbol)
            and isinstance(data_type, BaseTypeDef)
            and isinstance(kind, DataKind)
            and isinstance(counter, int)
        ):
            self._name = name
            self._type = data_type
            self._kind = kind
            self._is_quantum = isquantum(name)
            self._uid = ScopeValue((name, data_type, kind), counter=counter)
            self._hash_value = hash((name, data_type, self._uid))

        else:
            sys.exit(
                DataInitializationArgumentsError(name, data_type, kind=kind, counter=counter)()
            )

    @property
    def name(self) -> Symbol | CompositeSymbol:
        return self._name

    @property
    def type(self) -> BaseTypeDef:
        return self._type

    @property
    def is_quantum(self) -> bool:
        return self._is_quantum

    @property
    def kind(self) -> DataKind:
        return self._kind

    @property
    def uid(self) -> int:
        return self._uid.value

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)

        return False


class DataCollection(ABC, Generic[T]):
    _data: T

    @abstractmethod
    def insert(self, value: Any) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get(self, item: Any) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def __iter__(self) -> Iterable:
        raise NotImplementedError()

    def __getitem__(self, item: Any) -> Any:
        return self.get(item)
