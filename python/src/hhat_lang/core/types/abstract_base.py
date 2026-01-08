from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Iterable, TypeVar

from hhat_lang.core.data.core import Symbol
from hhat_lang.core.types.utils import AbstractTypeDef, BaseTypeEnum


class Size:
    """Size in bits"""

    _size: int

    def __init__(self, size: int):
        self._size = size

    @property
    def size(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return f"Size({self.size})"


class QSize:
    """
    Quantum size in terms of indexes (qubit number). It may not include
    ancillas used by the lower-level languages.
    """

    _min: int
    _max: int | None

    def __init__(self, min_num: int, max_num: int | None = None):
        self._min = min_num
        self._max = max_num

    @property
    def min(self) -> int:
        return self._min

    @property
    def max(self) -> None | int:
        return self._max

    @property
    def size(self) -> tuple[int, int | None]:
        return self._min, self._max

    def add_max(self, max_num: int) -> None:
        if isinstance(max_num, int) and self._max is None:
            self._max = max_num

    def __repr__(self) -> str:
        return f"QSize(min={self.min}{f'|max={self.max}' if self.max else ''})"


#########################################
# TYPES MEMBERS AND CONTAINERS SECTIONS #
#########################################


# To facilitate type annotation checks, some generic type values are defined
T = TypeVar("T")  # type name
C = TypeVar("C")  # container type
M = TypeVar("M")  # member name


class BaseTypeDef(AbstractTypeDef, Generic[T, M]):
    """
    Base data type class to be used by single, struct, enum, etc. type definitions
    """

    _name: Symbol
    _type: BaseTypeEnum
    _container: BaseTypeDataBin
    _is_quantum: bool
    _is_builtin: bool
    _size: Size
    _qsize: QSize
    _is_array: bool
    _is_size_set: bool = False

    @property
    def name(self) -> Symbol:
        return self._name

    @property
    def type(self) -> BaseTypeEnum:
        return self._t_type

    @property
    def is_quantum(self) -> bool:
        return self._is_quantum

    @property
    def is_array(self) -> bool:
        return self._is_array

    @property
    def is_builtin(self) -> bool:
        return self._is_builtin

    @property
    def size(self) -> Size:
        return self._size

    @property
    def qsize(self) -> QSize:
        return self._qsize

    @abstractmethod
    def add_member(
        self, type_name: T | None, member_name: M | None, **kwargs: Any
    ) -> BaseTypeDef:
        raise NotImplementedError()

    def set_sizes(self, size: Size, qsize: QSize | None = None) -> BaseTypeDef:
        self._size = size
        self._qsize = qsize or QSize(0, 0)
        self._is_size_set = True
        return self

    def is_size_set(self) -> bool:
        return self._is_size_set

    def __contains__(self, item: Any) -> bool:
        return item in self._container

    @abstractmethod
    def __getitem__(self, item: int | Symbol) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def __iter__(self) -> Iterable:
        raise NotImplementedError()

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError()


class BaseTypeDataBin(ABC, Generic[T, C, M]):
    """
    Base type data bin class to be used by single, struct, enum, etc.
    member/type information storage.
    """

    _container: C

    @property
    def container(self) -> C:
        return self._container

    @abstractmethod
    def add_member(self, **kwargs: Any) -> BaseTypeDataBin:
        """
        Add a new member to the data bin. It can contain ``type_name`` (of type ``T``),
        ``member_name`` (of type ``M``), or only one of them.
        """
        raise NotImplementedError()

    @abstractmethod
    def __getitem__(self, item: Symbol | int) -> T:
        raise NotImplementedError()

    @abstractmethod
    def __iter__(self) -> Iterable:
        raise NotImplementedError()
