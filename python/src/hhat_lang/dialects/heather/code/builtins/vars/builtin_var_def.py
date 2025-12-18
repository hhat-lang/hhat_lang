from __future__ import annotations

import sys
from typing import Any, Iterable

from hhat_lang.core.code.ir_block import AppendableData, IRBlock, IRInstr
from hhat_lang.core.data.core import Literal, LiteralArray, Symbol
from hhat_lang.core.data.utils import DataKind
from hhat_lang.core.data.var_def import DataContainer
from hhat_lang.core.data.var_utils import DataCollection, DataHeader, T
from hhat_lang.core.error_handlers.errors import ContainerVarError
from hhat_lang.core.types.abstract_base import BaseTypeDef


class Constant(DataContainer[tuple]):
    """
    Constant data container class. To be used on constant definition files.

    Constants are importable, global reaching pieces of immutable data.
    """

    def __init__(self, name: Symbol, data_type: BaseTypeDef, counter: int):
        self._header = DataHeader(
            name=name, data_type=data_type, kind=DataKind.CONSTANT, counter=counter
        )

    def assign(self, *args: Any, **kwargs: Any) -> DataContainer[tuple]:
        pass

    def get(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def borrow_to(self):
        pass

    def return_borrow(self):
        pass


class Immutable(DataContainer[Any]):
    """Immutable data container class. To be used for immutable variables."""

    def assign(self, *args: Any, **kwargs: Any) -> DataContainer[T]:
        pass

    def get(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def borrow_to(self):
        pass

    def return_borrow(self):
        pass


class Mutable(DataContainer[Any]):
    """
    Mutable data container class. To be used for mutable variables (that
    are not appendable; Check out ``Appendable`` data container for more
    information.)
    """

    def __init__(self, name: Symbol, data_type: BaseTypeDef, counter: int):
        self._header = DataHeader(
            name=name, data_type=data_type, kind=DataKind.MUTABLE, counter=counter
        )

    def assign(self, *args: Any, **kwargs: Any) -> DataContainer[T]:
        pass

    def get(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def borrow_to(self):
        pass

    def return_borrow(self):
        pass


class AppendableCollection(DataCollection[AppendableData]):
    _data: AppendableData

    def __init__(self):
        self._data = AppendableData()

    def insert(self, value: Any) -> None:
        self._data.insert(value)

    def get(self, item: Any) -> Any:
        return self._data.get(item)

    def __iter__(self) -> Iterable:
        return iter(self._data)


class Appendable(DataContainer[AppendableData]):
    """
    Appendable data container class. To be used for appendable variables, such as quantum data.
    It uses ``AppendableObj`` class to store its content. Check that out for more information
    about appendable data.
    """

    def __init__(self, name: Symbol, data_type: BaseTypeDef, counter: int):
        self._header = DataHeader(
            name=name, data_type=data_type, kind=DataKind.APPENDABLE, counter=counter
        )
        self._data = AppendableCollection()

    def assign(
        self, *args: IRBlock | IRInstr | Literal | LiteralArray, **_kwargs: Any
    ) -> Appendable:
        for k in args:
            if isinstance(k, IRBlock | IRInstr | Literal | LiteralArray):
                self._data.insert(k)

            else:
                sys.exit(ContainerVarError(self.name)())

        return self

    def get(self, member: Symbol | BaseTypeDef, **_kwargs: Any) -> Any:
        pass

    def borrow_to(self):
        pass

    def return_borrow(self):
        pass
