from __future__ import annotations

from typing import Any, Callable, Iterable

from hhat_lang.core.data.core import CoreLiteral, Symbol, WorkingData
from hhat_lang.core.data.utils import VariableKind
from hhat_lang.core.data.variable import BaseDataContainer, VariableTemplate
from hhat_lang.core.error_handlers.errors import (
    ErrorHandler,
)
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure, QSize, Size
from hhat_lang.core.types.utils import BaseTypeEnum
from hhat_lang.core.utils import SymbolOrdered

###############
# DEFINITIONS #
###############

# classical symbol
S_INT = Symbol("int")
S_BOOL = Symbol("bool")
S_U16 = Symbol("u16")
S_U32 = Symbol("u32")
S_U64 = Symbol("u64")

# quantum symbol
S_QINT = Symbol("@int")
S_QBOOL = Symbol("@bool")
S_QU2 = Symbol("@u2")
S_QU3 = Symbol("@u3")
S_QU4 = Symbol("@u4")

# sets
int_types: set = {S_INT, S_U16, S_U32, S_U64}
qint_types: set = {S_QINT, S_QU2, S_QU3, S_QU4}


######################################
# BUILT-IN DATA STRUCTURE STRUCTURES #
######################################


class BuiltinSingleDS(BaseTypeDataStructure):
    def __init__(
        self, name: Symbol, bitsize: Size | None = None, qsize: QSize | None = None
    ):
        super().__init__(name, is_builtin=True)
        self._type_container: SymbolOrdered = SymbolOrdered({0: name})
        self._size = bitsize
        self._qsize = qsize if qsize is not None else QSize(0, 0)
        self._ds_type = BaseTypeEnum.SINGLE

    @property
    def bitsize(self) -> Size | None:
        return self._size

    def cast_from(
        self, data: WorkingData, cast_fn: Callable
    ) -> CoreLiteral | BaseDataContainer:
        """Cast data to this type."""

        return cast_fn(self, data)

    def add_member(self, *args: Any) -> BuiltinSingleDS | ErrorHandler:
        return self

    def add_tmp_member(self, *args: Any, **kwargs: Any) -> Any:
        raise ValueError("built-in type cannot have unknown type at during IR-parsing time")

    def __call__(
        self,
        *,
        var_name: Symbol,
        flag: VariableKind = VariableKind.MUTABLE,
        **_: Any
    ) -> BaseDataContainer | ErrorHandler:
        return VariableTemplate(
            var_name=var_name,
            type_name=self.name,
            ds_data=SymbolOrdered({
                next(iter(self._type_container.values())): self._type_container
            }),
            ds_type=self._ds_type,
            flag=flag,
        )

    def __contains__(self, item: Any) -> bool:
        raise NotImplementedError()

    def __iter__(self) -> Iterable:
        raise NotImplementedError()
