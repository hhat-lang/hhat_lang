from __future__ import annotations

import sys
import ctypes
from typing import Any, NoReturn, Callable

from hhat_lang.core.data.core import CoreLiteral
from hhat_lang.core.data.variable import BaseDataContainer
from hhat_lang.core.error_handlers.errors import (
    InvalidDataContainerCastError,
    EvaluatorCastWildcardBuiltinTypeError,
    EvaluatorCastDataError,
    DataOverflowError
)

# TODO: implement complex data conversion functions as well


###############
# DEFINITIONS #
###############

U32_MAX: int = 2 << 31
I32_MAX: int = (2 << 31) - 1
U64_MAX: int = 2 << 63
I64_MAX: int = (2 << 63) - 1
F32_MAX: float = (1 - 2**(-24)) * (2 << 127)
# (not representable in python) F64_MAX = (1 - 2**(-54)) * (2**1024)

U32_MIN: int = 0
I32_MIN: int = -(2 << 31)
U64_MIN: int = 0
I64_MIN: int = -(2 << 63)
F32_MIN: float = -F32_MAX
# (not representable in python) F64_MIN = -F64_MAX


########################
# CONVENIENT FUNCTIONS #
########################

def _invalid_case_cast(data: Any, f_type: str, t_type: str) -> NoReturn:
    sys.exit(
        InvalidDataContainerCastError(data, f_type, t_type)()
    )


def _cast_to(
    data: BaseDataContainer | CoreLiteral | Any,
    cast_fn: Callable,
    from_type: str,
    to_type: str
) -> CoreLiteral:
    """
    Simple casting function using a ``cast_fn`` function to convert ``data``
    from ``from_type`` to ``to_type``.
    """

    match data:
        case BaseDataContainer():
            literal: CoreLiteral = next(iter(data.data))
            return CoreLiteral(str(cast_fn(literal.value)), to_type)

        case CoreLiteral():
            return CoreLiteral(str(cast_fn(data.value)), to_type)

        case _:
            return _invalid_case_cast(data, from_type, to_type)


#####################
# BOOLEAN FUNCTIONS #
#####################

def bool_to_int(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from bool to int.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal data as int
    """

    return _cast_to(data, int, "bool", "int")


def bool_to_float(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from bool to float.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal data as float
    """

    return _cast_to(data, float, "bool", "float")


def bool_to_u32(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from bool to u32.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal data as u32
    """

    return _cast_to(data, int, "bool", "u32")


def bool_to_i32(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from bool to i32.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal data as i32
    """

    return _cast_to(data, int, "bool", "i32")


def bool_to_f32(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from bool to f32.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal data as f32
    """

    return _cast_to(data, float, "bool", "f32")


def bool_to_f64(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from bool to f64.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal data as f64
    """

    return _cast_to(data, float, "bool", "f64")


def int_to_bool(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from any int to bool.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal data as bool
    """

    from_type: str
    match data:
        case BaseDataContainer():
            literal: CoreLiteral = next(iter(data.data))
            from_type = literal.type

        case CoreLiteral():
            from_type = data.type

        case _:
            sys.exit(
                EvaluatorCastDataError(data)()
            )

    return _cast_to(data, int, from_type, "bool")


def float_to_bool(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from any float to bool.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal data as bool
    """

    from_type: str
    match data:
        case BaseDataContainer():
            literal: CoreLiteral = next(iter(data.data))
            from_type = literal.type

        case CoreLiteral():
            from_type = data.type

        case _:
            sys.exit(EvaluatorCastDataError(data)())

    return _cast_to(data, float, from_type, "bool")


#####################
# INTEGER FUNCTIONS #
#####################

def int_to_float(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from int to float. Data is expected to be
    a literal of type int (it must be checked by this function caller.)

    Args:
        data: CoreLiteral

    Returns:
        Literal data as a float
    """

    match data:
        case BaseDataContainer():
            # Probably itś not base data container, because the integer type should
            # be known already (u32, i32, u64, i64, ...) instead of generic int
            sys.exit(
                EvaluatorCastWildcardBuiltinTypeError("int")()
            )

        case CoreLiteral():
            return CoreLiteral(str(int(data.value)), "float")

        case _:
            _invalid_case_cast(data, "int", "float")


def _cast_to_smaller_bitsize(
    data: BaseDataContainer | CoreLiteral | Any,
    type_fn: Callable,
    cast_fn: Callable,
    min_value: Any,
    max_value: Any,
    data_type: str,
    to_type: str,
) -> CoreLiteral:
    """
    Cast wildcard type data given function its type (``type_fn``),
    a ``cast_fn`` (ctypes function) and number of bits (32, 64) to
    a specific type.
    """

    value: Any
    match data:
        case BaseDataContainer():
            value = type_fn(next(iter(data.data)))

        case CoreLiteral():
            value = type_fn(data.value)

        case _:
            sys.exit(EvaluatorCastDataError(data)())

    if value > max_value or value < min_value:
        sys.exit(DataOverflowError(data, data_type, to_type)())

    return CoreLiteral(str(cast_fn(value).value), to_type)


def int_to_u32(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from int to u32.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal as u32
    """

    return _cast_to_smaller_bitsize(
        data,
        int,
        ctypes.c_uint32,
        U32_MIN,
        U32_MAX,
        "int",
        "u32"
    )


def int_to_i32(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from int to i32.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal as i32
    """

    return _cast_to_smaller_bitsize(
        data,
        int,
        ctypes.c_int32,
        I32_MIN,
        I32_MAX,
        "int",
        "i32"
    )


def int_to_u64(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from int to u64.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal as u64
    """

    return _cast_to_smaller_bitsize(
        data,
        int,
        ctypes.c_uint64,
        U64_MIN,
        U64_MAX,
        "int",
        "u64"
    )


def int_to_i64(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from int to i64.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal as i64
    """

    return _cast_to_smaller_bitsize(
        data,
        int,
        ctypes.c_int64,
        I64_MIN,
        I64_MAX,
        "int",
        "i64"
    )


def u32_to_float(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from u32 to float.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal as float
    """

    return _cast_to(data, float, "u32", "float")


def u32_to_f32(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from u32 to f32.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal as f32
    """

    return _cast_to(data, float, "u32", "f32")


def u32_to_f64(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from u32 to f64.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal as f64
    """

    return _cast_to(data, float, "u32", "f64")


def u64_to_f32(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from u64 to f32.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal as f32
    """

    return _cast_to_smaller_bitsize(
        data,
        float,
        ctypes.c_float,
        F32_MIN,
        F32_MAX,
        "u64",
        "f32"
    )


def u64_to_f64(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from u64 to f64.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal as f64
    """

    return _cast_to(data, float, "u64", "f64")


def i32_to_f32(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from i32 to f32.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal as f32
    """

    return _cast_to(data, float, "i32", "f32")


def i32_to_f64(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from i32 to f64.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal as f64
    """

    return _cast_to(data, float, "i32", "f64")


def i64_to_f32(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from i64 to f32.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal as f32
    """

    return _cast_to_smaller_bitsize(
        data,
        float,
        ctypes.c_float,
        F32_MIN,
        F32_MAX,
        "i64",
        "f32"
    )


def i64_to_f64(data: BaseDataContainer | CoreLiteral | Any) -> CoreLiteral:
    """
    Cast conversion function from i64 to f64.

    Args:
        data: BaseDataContainer or CoreLiteral

    Returns:
        Literal as f64
    """

    return _cast_to(data, float, "i64", "f64")


###################
# FLOAT FUNCTIONS #
###################

def float_to_int(data: BaseDataContainer | CoreLiteral | Any) -> float:
    """
    Cast conversion function to convert float to int
    Args:
        data:

    Returns:

    """