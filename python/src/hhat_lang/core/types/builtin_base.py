from __future__ import annotations

from typing import Any, Callable, Iterable, cast

from hhat_lang.core.data.core import CoreLiteral, Symbol, WorkingData
from hhat_lang.core.data.utils import VariableKind
from hhat_lang.core.data.variable import BaseDataContainer, VariableTemplate
from hhat_lang.core.error_handlers.errors import (
    CastError,
    CastIntOverflowError,
    CastNegToUnsignedError,
    ErrorHandler,
    TypeSingleError,
)
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure, QSize, Size
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
        self._bitsize = bitsize
        self._qsize = qsize if qsize is not None else QSize(0, 0)

    @property
    def bitsize(self) -> Size | None:
        return self._bitsize

    def cast_from(
        self, data: WorkingData, cast_fn: Callable
    ) -> CoreLiteral | BaseDataContainer:
        """Cast data to this type."""

        return cast_fn(self, data)

    def add_member(self, *args: Any) -> BuiltinSingleDS | ErrorHandler:
        return self

    def __call__(
        self,
        *args: Any,
        var_name: Symbol,
        **kwargs: dict[WorkingData, WorkingData | VariableTemplate],
    ) -> BaseDataContainer | ErrorHandler:
        if len(args) == 1:
            x = args[0]

            if x.type == self._type_container[0]:
                variable = VariableTemplate(
                    var_name=var_name,
                    type_name=self.name,
                    type_ds=SymbolOrdered({x.type: self._type_container}),
                    flag=VariableKind.MUTABLE,
                )

                if isinstance(variable, BaseDataContainer):
                    variable(*args)
                    return variable

                return variable  # type: ignore [return-value]

        return TypeSingleError(self._name)

    def __contains__(self, item: Any) -> bool:
        raise NotImplementedError()

    def __iter__(self) -> Iterable:
        raise NotImplementedError()


##################
# CAST FUNCTIONS #
##################


def int_to_uN(
    ds: BuiltinSingleDS, data: CoreLiteral | BaseDataContainer
) -> CoreLiteral | BaseDataContainer | ErrorHandler:

    if ds.bitsize is not None:
        max_value = 1 << ds.bitsize.size

        if isinstance(data, CoreLiteral):

            if data < 0:
                return CastNegToUnsignedError(data, ds.members[0][1])

            if data < max_value:
                lit_type = cast(str, ds.name.value)
                return CoreLiteral(data.value, lit_type)

            return CastIntOverflowError(data, ds.name)

        if isinstance(data, BaseDataContainer):
            val = data.get()
            if data.type in int_types:

                match val:
                    case ErrorHandler():
                        return val

                    case WorkingData():
                        if val < 0:
                            return CastNegToUnsignedError(val, ds.members[0][1])

                        if val < max_value:
                            lit_type = cast(str, ds.name.value)
                            return CoreLiteral(val.value, lit_type)

                        return CastIntOverflowError(val, ds.name)

            return CastError(ds.name, val)

    # something else?
    raise NotImplementedError()


# classical

# quantum
