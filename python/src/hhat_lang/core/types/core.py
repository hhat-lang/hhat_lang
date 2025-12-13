from __future__ import annotations

import sys
from typing import Any, Iterable

from hhat_lang.core.data.core import (
    CompositeSymbol,
    Literal,
    Symbol,
    SymbolObj,
)
from hhat_lang.core.data.utils import isquantum
from hhat_lang.core.error_handlers.errors import (
    ErrorHandler,
    TypeMemberAlreadyExistsError,
    TypeMemberOverflowError,
)
from hhat_lang.core.types.abstract_base import BaseTypeDataBin, BaseTypeDef, M
from hhat_lang.core.types.utils import BaseTypeEnum
from hhat_lang.core.utils import SymbolOrdered


def is_valid_member(datatype: BaseTypeDef, member: str | Symbol | CompositeSymbol) -> bool:
    """
    Check if a datatype member is valid for the given datatype, e.g. quantum
    datatype supports classical members, but a classical datatype cannot contain
    any quantum members.
    """

    if not datatype.is_quantum and isquantum(member):
        return False

    return True


##################
# SINGLE SECTION #
##################

# types annotation for SingleDataBin
SingleT = Symbol | CompositeSymbol
SingleC = tuple[Symbol | CompositeSymbol] | tuple
SingleM = None


class SingleDataBin(BaseTypeDataBin[SingleT, SingleC, SingleM]):
    _container: SingleC
    _locked: bool

    def __init__(self):
        self._container = ()
        self._lock = False

    def add_member(self, type_name: SingleT, **kwargs: Any) -> SingleDataBin | ErrorHandler:
        if not self._locked:
            self._container += (type_name,)
            self._locked = True
            return self

        return TypeMemberOverflowError()

    def __getitem__(self, item: Any) -> SingleT:
        return self._container[0]

    def __iter__(self) -> Iterable:
        return iter(self._container)


class SingleTypeDef(BaseTypeDef[SingleT, None]):
    _container: SingleDataBin
    _t_type = BaseTypeEnum.SINGLE

    def __init__(self, name: Symbol):
        self._name = name
        self._is_quantum = isquantum(name)
        self._container = SingleDataBin()

    def add_member(self, type_name: SingleT | None, **kwargs: Any) -> SingleTypeDef:
        match res := self._container.add_member(type_name=type_name):
            case TypeMemberOverflowError():
                sys.exit(res(self._name, self._t_type))

            case _:
                return self

    def __iter__(self) -> Iterable:
        return iter(self._container)

    def __repr__(self) -> str:
        return f"{self._name}<single>:{self._container[0]}"


##################
# STRUCT SECTION #
##################

StructT = SymbolObj
StructC = SymbolOrdered[Symbol, SymbolObj]
StructM = Symbol


class StructDataBin(BaseTypeDataBin[StructT, StructC, StructM]):
    _container: StructC
    _num_members: int

    def __init__(self):
        self._container = SymbolOrdered()
        self._num_members = 0

    def add_member(
        self, type_name: StructT, member_name: StructM, **kwargs: Any
    ) -> BaseTypeDataBin | ErrorHandler:
        if member_name not in self._container:
            self._container[member_name] = type_name
            self._num_members += 1
            return self

        return TypeMemberAlreadyExistsError()

    def __getitem__(self, item: Symbol) -> StructT:
        return self._container[item]

    def __iter__(self) -> Iterable:
        return iter(self._container.items())


class StructTypeDef(BaseTypeDef[StructT, StructM]):
    _num_members: int
    _container: StructDataBin
    _t_type = BaseTypeEnum.STRUCT

    def __init__(self, name: Symbol, num_members: int):
        self._name = name
        self._num_members = num_members
        self._is_quantum = isquantum(name)
        self._container = StructDataBin()

    def add_member(self, type_name: StructT, member_name: StructM, **kwargs: Any) -> StructTypeDef:
        if self._num_members > 0:

            match res := self._container.add_member(type_name=type_name, member_name=member_name):
                case TypeMemberAlreadyExistsError():
                    sys.exit(res(self._name, member_name))

                case _:
                    self._num_members -= 1
                    return self

        sys.exit(TypeMemberOverflowError()(self._name, self._t_type))

    def __iter__(self) -> Iterable:
        return iter(self._container)

    def __repr__(self) -> str:
        members = "{" + " ".join(f"{k}:{v}" for k, v in self) + "}"
        return f"{self._name}<struct>{members}"


################
# ENUM SECTION #
################

EnumT = Literal | StructDataBin
EnumC = SymbolOrdered[Symbol, Symbol | StructTypeDef]
EnumM = Symbol | StructDataBin


class EnumDataBin(BaseTypeDataBin[EnumT, EnumC, EnumM]):
    _container: EnumC
    _counter: int

    def __init__(self, num_members: int):
        self._data = SymbolOrdered()
        self._counter = 1 if num_members else 0

    def add_member(
        self, member_name: EnumM | None, **kwargs: Any
    ) -> BaseTypeDataBin | ErrorHandler:
        if member_name not in self._container:

            match member_name:
                case Symbol():
                    self._counter *= 2
                    self._container[member_name] = self._counter

                case StructTypeDef():
                    self._container[member_name.name] = member_name

            return self

        return TypeMemberAlreadyExistsError()

    def __getitem__(self, item: Symbol) -> EnumT:
        return self._container[item]

    def __iter__(self) -> Iterable:
        return iter(self._container.items())


class EnumTypeDef(BaseTypeDef[EnumT, StructM]):
    _num_members: int
    _container: EnumDataBin
    _t_type = BaseTypeEnum.ENUM

    def __init__(self, name: Symbol, num_members: int):
        self._name = name
        self._num_members = num_members
        self._is_quantum = isquantum(name)
        self._container = EnumDataBin(num_members)

    def add_member(self, member_name: M | None, **kwargs: Any) -> BaseTypeDef:
        if self._num_members > 0:

            match res := self._container.add_member(member_name):
                case TypeMemberAlreadyExistsError():
                    sys.exit(res(self._name, member_name))

                case _:
                    self._num_members -= 1
                    return self

        sys.exit(TypeMemberOverflowError()(self._name, self._t_type))

    def __iter__(self) -> Iterable:
        return iter(self._container)

    def __repr__(self) -> str:
        members = "{" + " ".join(f"{k}" if isinstance(v, int) else f"{v}" for k, v in self) + "}"
        return f"{self._name}<enum>{members}"
