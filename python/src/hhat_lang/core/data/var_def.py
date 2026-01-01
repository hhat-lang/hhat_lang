from __future__ import annotations

import sys
from abc import abstractmethod
from typing import Any, Iterable

from hhat_lang.core.data.core import CompositeSymbol, Symbol
from hhat_lang.core.data.utils import AbstractDataDef, DataKind, has_same_paradigm
from hhat_lang.core.data.var_utils import BaseCollection, DataHeader
from hhat_lang.core.error_handlers.errors import (
    VariableFreeingBorrowedError,
    QuantumDataNotAppendableError,
    sys_exit,
)
from hhat_lang.core.types.abstract_base import BaseTypeDef


class DataDef(AbstractDataDef):
    """
    Data container for constant, variable and temporary data definitions.
    """

    _header: DataHeader
    _data_type: BaseCollection
    _borrowed: DataHeader | None

    def __init__(self, *_args: Any, **kwargs: Any):
        self.check_type()

    @property
    def name(self) -> Symbol | CompositeSymbol:
        return self._header.name

    @property
    def type(self) -> BaseTypeDef:
        return self._header.type

    @property
    def is_quantum(self) -> bool:
        return self._header.is_quantum

    @property
    def kind(self):
        return self._header.kind

    @property
    def borrowed(self):
        return self._borrowed

    @property
    def data(self) -> BaseCollection:
        return self._data_type

    def check_type(self) -> None:
        if has_same_paradigm(self._header.name, self._header.type.name):
            if self.is_quantum and self._header.kind is DataKind.APPENDABLE:
                return None

            if not self.is_quantum:
                return None

        sys_exit(
            error_fn=QuantumDataNotAppendableError(self._header.name, self._header.kind)
        )

    def get_type_member(self, index: int) -> Symbol:
        return self.type[index][0]

    @abstractmethod
    def assign(self, *args: Any, **kwargs: Any) -> DataDef:
        """
        Assign some data to this data container. Should return itself.
        """

        raise NotImplementedError()

    @abstractmethod
    def get(self, *args: Any, **kwargs: Any) -> Any:
        """
        Retrieve data container content based on the given member, for instance.
        """

        raise NotImplementedError()

    @abstractmethod
    def borrow_to(self):
        """
        This data container method will take its own data and will borrow to the other data.
        """

        raise NotImplementedError()

    @abstractmethod
    def return_borrow(self):
        """
        This data container method will take its own data (which was borrowed) and give it back.
        """

        raise NotImplementedError()

    def __call__(self, *args, **kwargs):
        """
        Calling data container instance is the equivalent of using its `assign` method.
        """

        return self.assign(*args, **kwargs)

    def __iter__(self) -> Iterable:
        return iter(self._data_type)

    def free(self) -> None:
        if self._borrowed:
            sys.exit(VariableFreeingBorrowedError(self.name)())

        del self
        return None
