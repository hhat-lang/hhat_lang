from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Iterable, TypeVar

from hhat_lang.core.data.core import Symbol
from hhat_lang.core.error_handlers.errors import (
    ErrorHandler,
    TypeMemberAlreadyExistsError,
)
from hhat_lang.core.types.utils import AbstractTypeDef, BaseTypeEnum

K = TypeVar("K")
V = TypeVar("V")


class Size:
    def __init__(self, value, /):
        self.value = value

    def __add__(self, other: Any) -> Size:
        if isinstance(other, Size):
            return Size(self.value + other.value)

        raise ValueError(f"cannot add Size with {type(other)}")

    def __repr__(self) -> str:
        return f"Size({self.value})"


class QSize:
    def __init__(self, min_value, max_value, /):
        self.min = min_value
        self.max = max_value

    def __add__(self, other: Any) -> QSize:
        if isinstance(other, QSize):
            return QSize(self.min + other.min, self.max + other.max)

        raise ValueError(f"cannot add QSize with {type(other)}")

    def __repr__(self) -> str:
        return f"@Size({self.min if self.min else 0} {self.max if self.max else ''})"


class TypeDef(AbstractTypeDef, ABC, Generic[K, V]):
    _name: Symbol
    _type: BaseTypeEnum
    _members: TypeMembers
    _is_quantum: bool
    _size: Size
    _qsize: QSize
    _hash_value: int
    _is_core: bool = False
    """whether type is core, e.g. bool, integer, float, string"""

    def __init__(self, name: Symbol):
        self._name = name

    @property
    def name(self) -> Symbol:
        return self._name

    @property
    def is_quantum(self) -> bool:
        return self._is_quantum

    @property
    def size(self) -> Size:
        return self._size

    @property
    def qsize(self) -> QSize:
        return self._qsize

    @property
    def members(self) -> TypeMembers:
        return self._members

    @property
    def is_core(self) -> bool:
        return self._is_core

    @abstractmethod
    def add_member(self, *args: Any, **kwargs: Any) -> TypeDef:
        pass

    @abstractmethod
    def get_member(self, member: K) -> V:
        raise NotImplementedError()

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError()

    def set_sizes(self, size: Size, qsize: QSize | None = None) -> TypeDef[K, V]:
        self._size = size
        self._qsize = qsize if qsize is not None else QSize(0, 0)
        return self

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)

        return False

    def __len__(self) -> int:
        return len(self._members)

    def __iter__(self) -> Iterable:
        return iter(self._members)


class TypeMembers(ABC, Generic[K, V]):
    _is_leaf: bool
    _content: Any
    _hash_value: int | None

    @property
    def is_leaf(self) -> bool:
        return self._is_leaf

    @abstractmethod
    def __iadd__(self, other: Any) -> TypeMembers[K, V]:
        raise NotImplementedError()

    @abstractmethod
    def __getitem__(self, item: K) -> V:
        raise NotImplementedError()

    @abstractmethod
    def __iter__(self) -> Iterable:
        raise NotImplementedError()

    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def set_hash(self) -> None:
        raise NotImplementedError()

    def set_as_leaf(self) -> None:
        self._is_leaf = True

    def unset_as_leaf(self) -> None:
        self._is_leaf = False

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        return hash(self) == hash(other)
