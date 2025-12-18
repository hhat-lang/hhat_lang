from __future__ import annotations

import sys
from abc import abstractmethod
from typing import Any, Generic, Iterable

from hhat_lang.core.data.core import CompositeSymbol, Symbol
from hhat_lang.core.data.utils import AbstractDataContainer
from hhat_lang.core.data.var_utils import DataCollection, DataHeader, T
from hhat_lang.core.error_handlers.errors import (
    VariableFreeingBorrowedError,
)
from hhat_lang.core.types.abstract_base import BaseTypeDef


class DataContainer(AbstractDataContainer, Generic[T]):
    """
    Data container for constant, variable and temporary data definitions.
    """

    _header: DataHeader
    _data: DataCollection[T]
    _borrowed: DataHeader | None

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
    def data(self) -> DataCollection[T]:
        return self._data

    @abstractmethod
    def assign(self, *args: Any, **kwargs: Any) -> DataContainer[T]:
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
        return iter(self._data)

    def free(self) -> None:
        if self._borrowed:
            sys.exit(VariableFreeingBorrowedError(self.name)())

        del self
        return None
