from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable

from hhat_lang.core.data.core import CompositeSymbol, Symbol
from hhat_lang.core.data.utils import VariableKind, AbstractDataContainer
from hhat_lang.core.error_handlers.errors import ErrorHandler
from hhat_lang.core.types.utils import BaseTypeEnum, AbstractDataTypeStructure
from hhat_lang.core.utils import SymbolOrdered


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


class BaseTypeDataStructure(AbstractDataTypeStructure):
    """Base type class for data structures, such as single, struct, enum and union."""

    _name: Symbol | CompositeSymbol
    _ds_type: BaseTypeEnum
    _type_container: SymbolOrdered
    _tmp_container: tuple[Symbol | CompositeSymbol] | None
    """temporary container for yet-to-be-validated members"""

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
    def type(self) -> BaseTypeEnum:
        return self._ds_type

    @property
    def ds(self) -> SymbolOrdered:
        return self._type_container

    @property
    def is_quantum(self) -> bool:
        return self._is_quantum

    @property
    def is_builtin(self) -> bool:
        return self._is_builtin

    @property
    def size(self) -> Size | None:
        return self._size

    @size.setter
    def size(self, value: Size) -> None:
        if isinstance(value, Size):
            self._size = value

    @property
    def qsize(self) -> QSize | None:
        return self._qsize

    @qsize.setter
    def qsize(self, value: QSize) -> None:
        if isinstance(value, QSize):
            self._qsize = value

    @property
    def is_array(self) -> bool:
        return self._array_type

    @property
    def members(self) -> tuple:
        return tuple(k for k in self)

    @property
    def tmp_members(self) -> tuple[Symbol | CompositeSymbol] | None:
        """
        Temporary place to hold members that need validation, e.g. their types are
        not yet defined at symbol table's ``TypeTable`` or ref table's ``RefTypeTable``.
        """

        return self._tmp_container

    @abstractmethod
    def add_member(self, *args: Any, **kwargs: Any) -> Any | ErrorHandler:
        raise NotImplementedError()

    @abstractmethod
    def add_tmp_member(self, *args: Any, **kwargs: Any) -> Any:
        """
        Add temporary member. It is used when the member is not validated yet,
        for instance, when its type is in another file or ahead in the parsed
        code. It must be added as a member later on with ``add_member`` method.
        """

        raise NotImplementedError()

    @abstractmethod
    def __call__(
        self,
        *,
        var_name: Symbol,
        flag: VariableKind,
        **kwargs: Any,
    ) -> AbstractDataContainer | ErrorHandler:
        raise NotImplementedError()

    def __contains__(self, item: Any) -> bool:
        return item in self._type_container

    def __iter__(self) -> Iterable:
        return iter(self._type_container.items())
