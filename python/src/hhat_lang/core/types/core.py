from __future__ import annotations

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
from hhat_lang.core.types.utils import BaseTypeEnum
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
    """Class to define data structure for single types."""

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
        self._ds_type = BaseTypeEnum.SINGLE

    def add_member(self, member_type: BaseTypeDataStructure) -> SingleDS | ErrorHandler:
        if not is_valid_member(self, member_type.name):
            return TypeQuantumOnClassicalError(member_type.name, self.name)

        if member_type.type != self.type:
            return TypeAndMemberNoMatchError(member_type, self.name)

        self._type_container[self.name] = member_type.name
        return self

    def add_tmp_member(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    def __call__(
        self,
        *,
        var_name: Symbol,
        flag: VariableKind = VariableKind.IMMUTABLE,
        **_: Any,
    ) -> BaseDataContainer | ErrorHandler:
        return VariableTemplate(
            var_name=var_name,
            type_name=self.name,
            ds_data=SymbolOrdered(
                {next(iter(self._type_container.values())): self._type_container}
            ),
            ds_type=self._ds_type,
            flag=flag,
        )

    def __repr__(self) -> str:
        member = "".join(str(k) for k in self._type_container.values())
        return f"{self.name}<single>:{member}"


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

    def add_tmp_member(self, *args: Any, **kwargs: Any) -> Any:
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
    """Class to define data structure for struct types."""

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
        self._ds_type = BaseTypeEnum.STRUCT

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

    def add_tmp_member(
        self,
        member_type: Symbol | CompositeSymbol,
        member_name: Symbol | CompositeSymbol,
    ) -> StructDS:
        self._tmp_container += ((member_type, member_name),)
        return self

    def __call__(
        self, *, var_name: Symbol, flag: VariableKind = VariableKind.IMMUTABLE, **_: Any
    ) -> BaseDataContainer | ErrorHandler:
        return VariableTemplate(
            var_name=var_name,
            type_name=self._name,
            ds_data=self._type_container,
            ds_type=self._ds_type,
            flag=flag,
        )

    def __repr__(self) -> str:
        members = (
            "{" + " ".join(f"{k}:{v}" for k, v in self._type_container.items()) + "}"
        )
        return f"{self.name}<struct>{members}"


class EnumDS(BaseTypeDataStructure):
    """Class to define data structure for enum types."""

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
        self._ds_type = BaseTypeEnum.ENUM

    def _get_member_name(self, member: BaseTypeDataStructure | Symbol) -> Symbol:
        match member:
            case Symbol():
                return member

            case BaseTypeDataStructure():
                return member.name

            case _:
                raise NotImplementedError()

    def add_member(
        self, member: BaseTypeDataStructure | Symbol
    ) -> EnumDS | ErrorHandler:
        member_name = self._get_member_name(member)

        if is_valid_member(self, member_name):
            self._type_container[member_name] = member
            return self

        return TypeQuantumOnClassicalError(member_name, self.name)

    def add_tmp_member(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    def __call__(
        self, *, var_name: Symbol, flag: VariableKind = VariableKind.IMMUTABLE, **_: Any
    ) -> BaseDataContainer | ErrorHandler:
        return VariableTemplate(
            var_name=var_name,
            type_name=self._name,
            ds_data=self._type_container,
            ds_type=self._ds_type,
            flag=flag,
        )


class RemoteUnionDS(BaseTypeDataStructure):
    """Class to define data structure for remote union types"""

    def add_member(self, *args: Any, **kwargs: Any) -> Any | ErrorHandler:
        raise NotImplementedError()

    def add_tmp_member(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    def __call__(
        self, *, var_name: Symbol, flag: VariableKind, **kwargs: Any
    ) -> BaseDataContainer | ErrorHandler:
        raise NotImplementedError()


class UnionDS(BaseTypeDataStructure):
    """Class to define data structure for union types."""

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
        self._ds_type = BaseTypeEnum.UNION

    def add_member(self, member_type: str, member_name: str) -> UnionDS:
        raise NotImplementedError()

    def add_tmp_member(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    def __call__(
        self, *, var_name: Symbol, flag: VariableKind = VariableKind.IMMUTABLE, **_: Any
    ) -> BaseDataContainer | ErrorHandler:
        return VariableTemplate(
            var_name=var_name,
            type_name=self._name,
            ds_data=self._type_container,
            ds_type=self._ds_type,
            flag=flag,
        )
