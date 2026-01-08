from __future__ import annotations

from typing import Any, Iterable

from hhat_lang.core.data.core import Symbol
from hhat_lang.core.data.utils import isquantum
from hhat_lang.core.types.abstract_base import BaseTypeDef, QSize, Size, T, M
from hhat_lang.core.types.core import (
    SingleDataBin,
    SingleT,
    StructDataBin,
    StructM,
    StructT,
    EnumT,
    EnumM,
)
from hhat_lang.core.types.utils import BaseTypeEnum

# DEFINITIONS #
###############

# classical symbol
S_INT = Symbol("int")
S_BOOL = Symbol("bool")
S_U16 = Symbol("u16")
S_U32 = Symbol("u32")
S_U64 = Symbol("u64")
S_I16 = Symbol("i16")
S_I32 = Symbol("i32")
S_I64 = Symbol("i64")
S_F32 = Symbol("f32")
S_F64 = Symbol("f64")

# quantum symbol
S_QINT = Symbol("@int")
S_QBOOL = Symbol("@bool")
S_QU2 = Symbol("@u2")
S_QU3 = Symbol("@u3")
S_QU4 = Symbol("@u4")

# sets
int_types: set = {S_INT, S_U16, S_U32, S_U64, S_I16, S_I32, S_I64}
float_types: set = {S_F32, S_F64}
qint_types: set = {S_QINT, S_QU2, S_QU3, S_QU4}


######################################
# BUILT-IN DATA STRUCTURE STRUCTURES #
######################################


class BuiltinSingleTypeDef(BaseTypeDef[SingleT, None]):
    _container: SingleDataBin
    _type = BaseTypeEnum.SINGLE
    _is_builtin = True

    def __init__(self, name: Symbol, size: Size, qsize: QSize | None = None):
        self._name = name
        self._is_quantum = isquantum(name)
        self._container = SingleDataBin()
        # built-in single is a member of itself
        self._container.add_member(name)
        self.set_sizes(size, qsize)

    def add_member(self, **kwargs: Any) -> BaseTypeDef:
        return self

    def __getitem__(self, item: int | Symbol) -> Any:
        return self._container[item]

    def __iter__(self) -> Iterable:
        return iter(self._container)

    def __repr__(self) -> str:
        return f"{self._name}<single>:{self._container[0]}"


class BuiltinStructTypeDef(BaseTypeDef[StructT, StructM]):
    _container: StructDataBin
    _type = BaseTypeEnum.STRUCT
    _is_builtin = True

    def __init__(self, name: Symbol, size: Size, qsize: QSize | None = None):
        self._name = name
        self._is_quantum = isquantum(name)
        self._container = StructDataBin()
        self.set_sizes(size, qsize)

    def add_member(
        self, type_name: StructT, member_name: StructM, **kwargs: Any
    ) -> BaseTypeDef:
        self._container.add_member(type_name=type_name, member_name=member_name)
        return self

    def __getitem__(self, item: int | Symbol) -> Any:
        return self._container[item]

    def __iter__(self) -> Iterable:
        return iter(self._container)

    def __repr__(self) -> str:
        members = "{" + " ".join(f"{k}:{v}" for k, v in self) + "}"
        return f"{self._name}<struct>{members}"


class BuiltinEnumTypeDef(BaseTypeDef[EnumT, EnumM]):
    def add_member(
        self, type_name: T | None, member_name: M | None, **kwargs: Any
    ) -> BaseTypeDef:
        pass

    def __getitem__(self, item: int | Symbol) -> Any:
        return self._container[item]

    def __iter__(self) -> Iterable:
        pass

    def __repr__(self) -> str:
        pass
