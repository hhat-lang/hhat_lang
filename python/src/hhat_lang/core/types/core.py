from __future__ import annotations

from collections import OrderedDict
from typing import Any

from hhat_lang.core.data.core import CompositeSymbol, Symbol, WorkingData
from hhat_lang.core.data.utils import VariableKind, has_same_paradigm, isquantum
from hhat_lang.core.data.variable import BaseDataContainer, VariableTemplate
from hhat_lang.core.error_handlers.errors import (
    ErrorHandler,
    TypeAndMemberNoMatchError,
    TypeQuantumOnClassicalError,
    TypeSingleError,
    TypeStructError,
)
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure, QSize, Size
from hhat_lang.core.utils import SymbolOrdered


def is_valid_member(
    datatype: BaseTypeDataStructure, member: str | Symbol | CompositeSymbol
) -> bool:
    """
    Check if a datatype member is valid for the given datatype, e.g. quantum
    datatype supports classical members, but a classical datatype cannot contain
    any quantum members.
    """

    if not datatype.is_quantum and isquantum(member):
        return False

    return True


class SingleDS(BaseTypeDataStructure):
    def __init__(
        self,
        name: Symbol | CompositeSymbol,
        size: Size | None = None,
        qsize: QSize | None = None,
    ):
        super().__init__(name)
        self._size = size
        self._qsize = qsize
        self._type_container: SymbolOrdered = SymbolOrdered()

    def add_member(
        self, member_type: BaseTypeDataStructure, _member_name: None = None
    ) -> SingleDS | ErrorHandler:

        if not is_valid_member(self, member_type.name):
            return TypeQuantumOnClassicalError(member_type.name, self.name)

        self._type_container[self.name] = member_type.name
        return self

    def __call__(
        self,
        *args: Any,
        var_name: Symbol,
        flag: VariableKind = VariableKind.IMMUTABLE,
        **kwargs: dict[WorkingData, WorkingData | BaseDataContainer],
    ) -> BaseDataContainer | ErrorHandler:
        if len(args) == 1:
            x = args[0]

            if x.type == self._type_container[self.name]:
                variable = VariableTemplate(
                    var_name=var_name,
                    type_name=self.name,
                    type_ds=SymbolOrdered({Symbol(x.type): self._type_container}),
                    flag=flag,
                )

                if isinstance(variable, BaseDataContainer):
                    variable(*args)
                    return variable

                return variable  # type: ignore [return-value]

        return TypeSingleError(self._name)


class ArrayDS(BaseTypeDataStructure):
    """This is an array data structure, to be thought as [u64] to represent an array of u64."""

    def __init__(
        self,
        name: Symbol | CompositeSymbol,
        size: Size | None = None,
        qsize: QSize | None = None,
    ):
        super().__init__(name, array_type=True)
        self._size = size
        self._qsize = qsize
        self._type_container: SymbolOrdered = SymbolOrdered()

    def add_member(self, member_type: Any, member_name: Any) -> Any | ErrorHandler:
        raise NotImplementedError()

    def __call__(
        self,
        *args: Any,
        var_name: str,
        flag: VariableKind = VariableKind.IMMUTABLE,
        **kwargs: dict[WorkingData, WorkingData | VariableTemplate],
    ) -> BaseDataContainer | ErrorHandler:
        raise NotImplementedError()


class StructDS(BaseTypeDataStructure):
    def __init__(
        self,
        name: Symbol | CompositeSymbol,
        size: Size | None = None,
        qsize: QSize | None = None,
    ):
        super().__init__(name)
        self._size = size
        self._qsize = qsize
        self._type_container: SymbolOrdered = SymbolOrdered()

    def add_member(
        self, member_type: BaseTypeDataStructure, member_name: Symbol | CompositeSymbol
    ) -> StructDS | ErrorHandler:

        # check if type and name are consistent, i.e. both quantum or classical
        if has_same_paradigm(member_type, member_name):

            if is_valid_member(self, member_type.name):
                self._type_container[member_name] = member_type.name
                return self

            return TypeQuantumOnClassicalError(member_type.name, self.name)

        return TypeAndMemberNoMatchError(member_type.name, self.name)

    def __call__(
        self,
        *args: Any,
        var_name: Symbol,
        flag: VariableKind = VariableKind.IMMUTABLE,
        **kwargs: dict[WorkingData, WorkingData | BaseDataContainer],
    ) -> BaseDataContainer | ErrorHandler:
        container: SymbolOrdered = SymbolOrdered()

        if len(args) == len(self._type_container):
            for k, (g, c) in zip(args, self._type_container.items()):

                if k.type == c:
                    container[g] = k

                else:
                    return TypeStructError(self._name)

        if len(kwargs) == len(self._type_container):
            for n, (k, v) in enumerate(kwargs.items()):

                if k in self._type_container:
                    container[k] = v

                else:
                    return TypeStructError(self._name)

        variable = VariableTemplate(
            var_name=var_name,
            type_name=self._name,
            type_ds=self._type_container,
            flag=flag,
        )

        if isinstance(variable, BaseDataContainer):
            variable(**container)
            return variable

        return variable  # type: ignore [return-value]


class UnionDS(BaseTypeDataStructure):
    def __init__(
        self,
        name: Symbol | CompositeSymbol,
        size: Size | None = None,
        qsize: QSize | None = None,
    ):
        super().__init__(name)
        self._size = size
        self._qsize = qsize
        self._type_container = SymbolOrdered()

    def add_member(self, member_type: str, member_name: str) -> UnionDS:
        raise NotImplementedError()

    def __call__(
        self,
        *args: Any,
        var_name: str,
        flag: VariableKind = VariableKind.IMMUTABLE,
        **kwargs: dict[WorkingData, WorkingData | BaseDataContainer],
    ) -> BaseDataContainer | ErrorHandler:
        raise NotImplementedError()


class EnumDS(BaseTypeDataStructure):
    def __init__(
        self,
        name: Symbol | CompositeSymbol,
        size: Size | None = None,
        qsize: QSize | None = None,
    ):
        super().__init__(name)
        self._size = size
        self._qsize = qsize
        self._type_container = SymbolOrdered()

    def add_member(self, member_type: str, member_name: str) -> EnumDS:
        raise NotImplementedError()

    def __call__(
        self,
        *args: Any,
        var_name: str,
        flag: VariableKind = VariableKind.IMMUTABLE,
        **kwargs: dict[WorkingData, WorkingData | BaseDataContainer],
    ) -> BaseDataContainer | ErrorHandler:
        raise NotImplementedError()
