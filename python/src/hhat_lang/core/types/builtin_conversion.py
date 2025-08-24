from __future__ import annotations

from typing import cast

from hhat_lang.core.data.core import CoreLiteral, Symbol, WorkingData
from hhat_lang.core.data.variable import BaseDataContainer
from hhat_lang.core.error_handlers.errors import (
    CastError,
    CastIntOverflowError,
    CastNegToUnsignedError,
    ErrorHandler,
)
from hhat_lang.core.types.builtin_base import BuiltinSingleDS, int_types

###################################
# COMPATIBLE CONVERTABLE TYPES #
###################################

compatible_types = {
    Symbol("int"): (
        Symbol("u16"),
        Symbol("u32"),
        Symbol("u64"),
        Symbol("i16"),
        Symbol("i32"),
        Symbol("i64"),
    ),
    Symbol("float"): (Symbol("f32"), Symbol("f64")),
    Symbol("@int"): (Symbol("@u2"), Symbol("@u3"), Symbol("@u4")),
}
"""dictionary to establish the relation between generic types (``int``, ``float``, ``@int``)
as their possible convertible types"""


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

                    case CoreLiteral():
                        if val < 0:
                            return CastNegToUnsignedError(val, ds.members[0][1])

                        if val < max_value:
                            lit_type = cast(str, ds.name.value)
                            return CoreLiteral(val.value, lit_type)

                        return CastIntOverflowError(val, ds.name)

            return CastError(ds.name, val)

    # something else?
    raise NotImplementedError()
