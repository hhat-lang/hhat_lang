from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable

from hhat_lang.core.data.core import CompositeSymbol, Symbol, WorkingData
from hhat_lang.core.data.utils import VariableKind
from hhat_lang.core.data.variable import BaseDataContainer, VariableTemplate
from hhat_lang.core.error_handlers.errors import ErrorHandler
from hhat_lang.core.utils import SymbolOrdered


class Size:
    """Size in bits"""

    _size: int

    def __init__(self, size: int):
        self._size = size

    @property
    def size(self) -> int:
        return self._size


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


class BaseTypeDataStructure(ABC):
    """Base type class for data structures, such as single, struct, enum and union."""

    _name: Symbol | CompositeSymbol
    _type_container: SymbolOrdered
    _is_quantum: bool
    _is_builtin: bool
    _size: Size | None
    _qsize: QSize | None
    _array_type: bool

    def __init__(
        self,
        name: Symbol | CompositeSymbol,
        is_builtin: bool = False,
        array_type: bool = False,
    ):
        self._name = name
        self._is_quantum = name.is_quantum
        self._is_builtin = is_builtin
        self._array_type = array_type

    @property
    def name(self) -> Symbol | CompositeSymbol:
        return self._name

    @property
    def is_quantum(self) -> bool:
        return self._is_quantum

    @property
    def is_builtin(self) -> bool:
        return self._is_builtin

    @property
    def size(self) -> Size | None:
        return self._size

    @property
    def qsize(self) -> QSize | None:
        return self._qsize

    @property
    def is_array(self) -> bool:
        return self._array_type

    @property
    def members(self) -> tuple:
        return tuple(k for k in self)

    @abstractmethod
    def add_member(self, member_type: Any, member_name: Any) -> Any | ErrorHandler: ...

    @abstractmethod
    def __call__(
        self,
        *args: Any,
        var_name: str,
        flag: VariableKind,
        **kwargs: dict[WorkingData, WorkingData | VariableTemplate],
    ) -> BaseDataContainer | ErrorHandler: ...

    def __contains__(self, item: Any) -> bool:
        return item in self._type_container

    def __iter__(self) -> Iterable:
        yield from self._type_container.items()
