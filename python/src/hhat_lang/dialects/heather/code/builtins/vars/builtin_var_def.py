from __future__ import annotations

import sys
from typing import Any

from hhat_lang.core.code.ir_block import IRBlock, IRInstr
from hhat_lang.core.data.core import Literal, LiteralArray, Symbol
from hhat_lang.core.data.utils import DataKind
from hhat_lang.core.data.var_def import DataDef
from hhat_lang.core.data.var_utils import (
    DataHeader,
    get_data_type_collection,
)
from hhat_lang.core.error_handlers.errors import (
    ContainerVarError,
    ErrorHandler,
    ImmutableDataReassignmentError,
    InvalidContentDataError,
    LazySequenceConsumedError,
)
from hhat_lang.core.types.abstract_base import BaseTypeDef

AppendableDataTypes = IRBlock | IRInstr | Literal | LiteralArray


class Constant(DataDef):
    """
    Constant data container class. To be used on constant definition files.

    Constants are importable, global reaching pieces of immutable data.
    """

    def __init__(self, name: Symbol, data_type: BaseTypeDef, counter: int):
        self._header = DataHeader(
            name=name, data_type=data_type, kind=DataKind.CONSTANT, counter=counter
        )
        self._data_type = get_data_type_collection(self._header.type.type)(DataKind.CONSTANT)

    def assign(self, *args: Any, **kwargs: Any) -> DataDef:
        pass

    def get(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def borrow_to(self):
        pass

    def return_borrow(self):
        pass


class Immutable(DataDef):
    """Immutable data container class. To be used for immutable variables."""

    def assign(self, *args: Any, **kwargs: Any) -> DataDef:
        pass

    def get(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def borrow_to(self):
        pass

    def return_borrow(self):
        pass


class Mutable(DataDef):
    """
    Mutable data container class. To be used for mutable variables (that
    are not appendable; Check out ``Appendable`` data container for more
    information.)
    """

    def __init__(self, name: Symbol, data_type: BaseTypeDef, counter: int):
        self._header = DataHeader(
            name=name, data_type=data_type, kind=DataKind.MUTABLE, counter=counter
        )
        self._data_type = get_data_type_collection(self._header.type.type)(DataKind.MUTABLE)

    def assign(self, *args: Any, **kwargs: Any) -> DataDef:
        pass

    def get(self, *args: Any, **kwargs: Any) -> Any:
        pass

    def borrow_to(self):
        pass

    def return_borrow(self):
        pass


class Appendable(DataDef):
    """
    Appendable data container class. To be used for appendable variables, such as quantum data.
    It uses ``LazySequence`` class to store its content. Check that class out for more
    information about lazy sequence.
    """

    def __init__(self, name: Symbol, data_type: BaseTypeDef, counter: int):
        self._header = DataHeader(
            name=name, data_type=data_type, kind=DataKind.APPENDABLE, counter=counter
        )
        self._data_type = get_data_type_collection(self._header.type.type)(DataKind.APPENDABLE)

    def assign(self, *args: AppendableDataTypes, **_kwargs: Any) -> Appendable:
        for k in args:
            if isinstance(k, AppendableDataTypes):

                match res := self._data_type.insert(k):
                    case ImmutableDataReassignmentError():
                        sys.exit(res(self.name))

                    case InvalidContentDataError():
                        sys.exit(res(self.name, k))

                    case LazySequenceConsumedError():
                        sys.exit(res(self.name))

                    case ErrorHandler():
                        sys.exit(res())

                    case _:
                        continue

            else:
                sys.exit(ContainerVarError(self.name)())

        return self

    def get(self, member: Symbol | BaseTypeDef, **_kwargs: Any) -> AppendableDataTypes:
        return self._data_type.get(member)

    def borrow_to(self):
        pass

    def return_borrow(self):
        pass
