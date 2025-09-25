from __future__ import annotations

from collections import OrderedDict
from typing import Any, Callable, Iterable

from hhat_lang.core.data.core import CoreLiteral, WorkingData, Symbol
from hhat_lang.core.data.variable import BaseDataContainer, VariableTemplate
from hhat_lang.core.error_handlers.errors import (
    ErrorHandler,
    TypeSingleError,
    CastNegToUnsignedError,
    CastIntOverflowError,
    CastError,
)
from hhat_lang.core.types import POINTER_SIZE
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure
from hhat_lang.core.types.abstract_base import Size, QSize

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
    def __init__(self, name: Symbol, bitsize: Size | None = None, qsize: QSize | None = None):
        super().__init__(name, is_builtin=True)
        self._type_container: list = [name]
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
                    type_ds=OrderedDict({x.type: self._type_container}),
                    is_mutable=True,
                )
                variable(*args)
                return variable

        return TypeSingleError(self._name)

    def __contains__(self, item: Any) -> bool:
        pass

    def __iter__(self) -> Iterable:
        pass


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
                return CoreLiteral(data.value, ds.name.value)

            return CastIntOverflowError(data, ds.name)

        if isinstance(data, BaseDataContainer):
            val = data.get()
            if data.type in int_types:

                if val < 0:
                    return CastNegToUnsignedError(val, ds.members[0][1])

                if val < max_value:
                    return CoreLiteral(val.name, ds.name.value)

                return CastIntOverflowError(val, ds.name)

            return CastError(ds.name, val)

    # something else?
    raise NotImplementedError()


#######################
# BUILT-IN DATA TYPES #
#######################

# classical
Int = BuiltinSingleDS(Symbol("int"))
Bool = BuiltinSingleDS(Symbol("bool"), Size(8))
U16 = BuiltinSingleDS(Symbol("u16"), Size(16))
U32 = BuiltinSingleDS(Symbol("u32"), Size(32))
U64 = BuiltinSingleDS(Symbol("u64"), Size(64))

# quantum
QBool = BuiltinSingleDS(Symbol("@bool"), Size(POINTER_SIZE), qsize=QSize(1))
QU2 = BuiltinSingleDS(Symbol("@u2"), Size(POINTER_SIZE), qsize=QSize(2))
QU3 = BuiltinSingleDS(Symbol("@u3"), Size(POINTER_SIZE), qsize=QSize(3))
QU4 = BuiltinSingleDS(Symbol("@u4"), Size(POINTER_SIZE), qsize=QSize(4))
