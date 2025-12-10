from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable

from hhat_lang.core.data.core import Symbol, CompositeSymbol
from hhat_lang.core.data.utils import isquantum
from hhat_lang.core.types.abstract_base import QSize, Size
from hhat_lang.core.types.utils import AbstractDataTypeStructure, BaseTypeEnum
from hhat_lang.core.utils import SymbolOrdered


##############################################
# DATA TYPES MEMBERS AND CONTAINERS SECTIONS #
##############################################

class TypeContainer(ABC):
    _data: Any
    _resolved: bool
    _locked: bool

    def is_resolved(self) -> bool:
        return self._resolved

    @abstractmethod
    def add_member(
        self,
        type_name: Symbol | CompositeSymbol | None,
        member_name: Symbol | CompositeSymbol | None,
        **kwargs: Any
    ) -> TypeContainer:
        raise NotImplementedError()


class SingleContainer(TypeContainer):
    _data: Symbol | CompositeSymbol | None

    def __init__(self):
        self._data = None

    def add_member(self, type_name: Symbol | CompositeSymbol, **kwargs: Any) -> SingleContainer:
        if not self._locked:
            self._tmp_data = type_name
            self._locked = True
            return self

        raise ValueError("trying to add more members to single data structure")


class StructContainer(TypeContainer):
    _data: SymbolOrdered[Symbol, Symbol | CompositeSymbol]
    _num_members: int

    def __init__(self, num_members: int):
        self._data = SymbolOrdered()
        self._num_members = num_members

    def add_member(
        self,
        type_name: Symbol | CompositeSymbol | None,
        member_name: Symbol | CompositeSymbol | None,
        **kwargs: Any
    ) -> TypeContainer:
        pass


class EnumContainer(TypeContainer):
    pass


##########################
# DATA STRUCTURE SECTION #
##########################

class BaseDataType(AbstractDataTypeStructure):
    _name: Symbol | CompositeSymbol
    _ds_type: BaseTypeEnum
    _container: TypeContainer
    _tmp_container: tuple
    _is_quantum: bool
    _is_builtin: bool
    _size: Size
    _qsize: QSize
    _array_type: bool

    @abstractmethod
    def __iter__(self) -> Iterable:
        raise NotImplementedError()

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError()


class SingleDataType(BaseDataType):
    _ds_type = BaseTypeEnum.SINGLE

    def __init__(self, name: Symbol, num_members: int):
        self._name = name
        self._is_quantum = isquantum(name)
        self._container = StructContainer(num_members)

    def __iter__(self) -> Iterable:
        return iter(self._container)

    def __repr__(self) -> str:
        pass
