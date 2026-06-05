from __future__ import annotations

import ctypes
import sys
from functools import wraps
from typing import Any, Callable, NoReturn

from hhat_lang.core.cast.base import CastFnType
from hhat_lang.core.data.core import Literal
from hhat_lang.core.data.var_def import DataDef
from hhat_lang.core.error_handlers.errors import (
    DataOverflowError,
    EvaluatorCastDataError,
    EvaluatorCastWildcardBuiltinTypeError,
    InterpreterEvaluationError,
    InvalidDataContainerCastError,
)

# TODO: implement complex data conversion functions as well


###############
# DEFINITIONS #
###############

U32_MAX: int = 2 << 31
I32_MAX: int = (2 << 31) - 1
U64_MAX: int = 2 << 63
I64_MAX: int = (2 << 63) - 1
F32_MAX: float = (1 - 2 ** (-24)) * (2 << 127)
# (not representable in python) F64_MAX = (1 - 2**(-54)) * (2**1024)

U32_MIN: int = 0
I32_MIN: int = -(2 << 31)
U64_MIN: int = 0
I64_MIN: int = -(2 << 63)
F32_MIN: float = -F32_MAX
# (not representable in python) F64_MIN = -F64_MAX


########################
# FUNCTIONS DICTIONARY #
########################


cast_fns_dict: dict[tuple[str, str], CastFnType] = dict()
"""
Dictionary to hold all the available cast functions. 
The key is a pair tuple with 'from_type' and 'to_type', and
the value is the function to perform the casting operation.
"""


def insert_cast_fns(entry_types: tuple[str, str]) -> Callable:
    """
    Decorator function to store entry_types (tuple) as key and the function
    as value in the ``cast_fns_dict`` dictionary.
    """

    # check whether entry data has the correct type and shape
    if not (isinstance(entry_types, tuple) and len(entry_types) == 2):
        raise InterpreterEvaluationError(
            error_where="appending cast functions",
            msg=(
                f"a cast function must provide a tuple with 'from_type' and "
                f"'to_type' types names, but got {entry_types} ({type(entry_types)})."
            ),
        )

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(data: DataDef | Literal | Any) -> Literal:
            return fn(data)

        cast_fns_dict[entry_types] = wrapper
        return wrapper

    return decorator


########################
# CONVENIENT FUNCTIONS #
########################


def _invalid_case_cast(data: Any, f_type: str, t_type: str) -> NoReturn:
    sys.exit(InvalidDataContainerCastError(data, f_type, t_type)())


def _cast_to(
    data: DataDef | Literal | Any,
    cast_fn: Callable,
    from_type: str,
    to_type: str,
) -> Literal:
    """
    Simple casting function using a ``cast_fn`` function to convert ``data``
    from ``from_type`` to ``to_type``.
    """

    match data:
        case DataDef():
            literal: Literal = next(iter(data.data))
            return Literal(str(cast_fn(literal.value)), to_type)

        case Literal():
            return Literal(str(cast_fn(data.value)), to_type)

        case _:
            return _invalid_case_cast(data, from_type, to_type)


#####################
# BOOLEAN FUNCTIONS #
#####################


@insert_cast_fns(("bool", "int"))
def bool_to_int(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from bool to int.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal data as int
    """

    return _cast_to(data, int, "bool", "int")


@insert_cast_fns(("bool", "float"))
def bool_to_float(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from bool to float.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal data as float
    """

    return _cast_to(data, float, "bool", "float")


@insert_cast_fns(("bool", "u32"))
def bool_to_u32(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from bool to u32.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal data as u32
    """

    return _cast_to(data, int, "bool", "u32")


@insert_cast_fns(("bool", "i32"))
def bool_to_i32(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from bool to i32.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal data as i32
    """

    return _cast_to(data, int, "bool", "i32")


@insert_cast_fns(("bool", "f32"))
def bool_to_f32(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from bool to f32.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal data as f32
    """

    return _cast_to(data, float, "bool", "f32")


@insert_cast_fns(("bool", "f64"))
def bool_to_f64(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from bool to f64.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal data as f64
    """

    return _cast_to(data, float, "bool", "f64")


@insert_cast_fns(("int", "bool"))
def int_to_bool(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from any int to bool.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal data as bool
    """

    from_type: str
    match data:
        case DataDef():
            literal: Literal = next(iter(data.data))
            from_type = literal.type

        case Literal():
            from_type = data.type

        case _:
            sys.exit(EvaluatorCastDataError(data)())

    return _cast_to(data, int, from_type, "bool")


@insert_cast_fns(("float", "bool"))
def float_to_bool(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from any float to bool.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal data as bool
    """

    from_type: str
    match data:
        case DataDef():
            literal: Literal = next(iter(data.data))
            from_type = literal.type

        case Literal():
            from_type = data.type

        case _:
            sys.exit(EvaluatorCastDataError(data)())

    return _cast_to(data, float, from_type, "bool")


#####################
# INTEGER FUNCTIONS #
#####################


@insert_cast_fns(("int", "float"))
def int_to_float(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from int to float. Data is expected to be
    a literal of type int (it must be checked by this function caller.)

    Args:
        data: CoreLiteral

    Returns:
        Literal data as a float
    """

    match data:
        case DataDef():
            # Probably itś not base data container, because the integer type should
            # be known already (u32, i32, u64, i64, ...) instead of generic int
            sys.exit(EvaluatorCastWildcardBuiltinTypeError("int")())

        case Literal():
            return Literal(str(int(data.value)), "float")

        case _:
            _invalid_case_cast(data, "int", "float")


def _cast_to_smaller_bitsize(
    data: DataDef | Literal | Any,
    type_fn: Callable,
    cast_fn: Callable,
    min_value: Any,
    max_value: Any,
    data_type: str,
    to_type: str,
) -> Literal:
    """
    Cast wildcard type data given function its type (``type_fn``),
    a ``cast_fn`` (ctypes function) and number of bits (32, 64) to
    a specific type.
    """

    value: Any
    match data:
        case DataDef():
            value = type_fn(next(iter(data.data)))

        case Literal():
            value = type_fn(data.value)

        case _:
            sys.exit(EvaluatorCastDataError(data)())

    if value > max_value or value < min_value:
        sys.exit(DataOverflowError(data, data_type, to_type)())

    return Literal(str(cast_fn(value).value), to_type)


@insert_cast_fns(("int", "u32"))
def int_to_u32(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from int to u32.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal as u32
    """

    return _cast_to_smaller_bitsize(data, int, ctypes.c_uint32, U32_MIN, U32_MAX, "int", "u32")


@insert_cast_fns(("int", "i32"))
def int_to_i32(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from int to i32.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal as i32
    """

    return _cast_to_smaller_bitsize(data, int, ctypes.c_int32, I32_MIN, I32_MAX, "int", "i32")


@insert_cast_fns(("int", "u64"))
def int_to_u64(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from int to u64.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal as u64
    """

    return _cast_to_smaller_bitsize(data, int, ctypes.c_uint64, U64_MIN, U64_MAX, "int", "u64")


@insert_cast_fns(("int", "i64"))
def int_to_i64(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from int to i64.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal as i64
    """

    return _cast_to_smaller_bitsize(data, int, ctypes.c_int64, I64_MIN, I64_MAX, "int", "i64")


@insert_cast_fns(("u32", "float"))
def u32_to_float(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from u32 to float.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal as float
    """

    return _cast_to(data, float, "u32", "float")


@insert_cast_fns(("u32", "f32"))
def u32_to_f32(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from u32 to f32.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal as f32
    """

    return _cast_to(data, float, "u32", "f32")


@insert_cast_fns(("u32", "f64"))
def u32_to_f64(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from u32 to f64.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal as f64
    """

    return _cast_to(data, float, "u32", "f64")


@insert_cast_fns(("u64", "f32"))
def u64_to_f32(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from u64 to f32.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal as f32
    """

    return _cast_to_smaller_bitsize(data, float, ctypes.c_float, F32_MIN, F32_MAX, "u64", "f32")


@insert_cast_fns(("u64", "f64"))
def u64_to_f64(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from u64 to f64.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal as f64
    """

    return _cast_to(data, float, "u64", "f64")


@insert_cast_fns(("i32", "f32"))
def i32_to_f32(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from i32 to f32.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal as f32
    """

    return _cast_to(data, float, "i32", "f32")


@insert_cast_fns(("i32", "f64"))
def i32_to_f64(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from i32 to f64.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal as f64
    """

    return _cast_to(data, float, "i32", "f64")


@insert_cast_fns(("i64", "f32"))
def i64_to_f32(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from i64 to f32.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal as f32
    """

    return _cast_to_smaller_bitsize(data, float, ctypes.c_float, F32_MIN, F32_MAX, "i64", "f32")


@insert_cast_fns(("i64", "f64"))
def i64_to_f64(data: DataDef | Literal | Any) -> Literal:
    """
    Cast conversion function from i64 to f64.

    Args:
        data: DataDef or CoreLiteral

    Returns:
        Literal as f64
    """

    return _cast_to(data, float, "i64", "f64")


###################
# FLOAT FUNCTIONS #
###################


@insert_cast_fns(("float", "int"))
def float_to_int(data: DataDef | Literal | Any) -> float:
    """
    Cast conversion function to convert float to int
    Args:
        data:

    Returns:

    """


#####################
# HASHMAP FUNCTIONS #
#####################


@insert_cast_fns(("hashmap", "int"))
def hashmap_to_int(data: DataDef | Any) -> Literal:
    """

    Args:
        data:

    Returns:

    """

    raise NotImplementedError()


@insert_cast_fns(("hashmap", "float"))
def hashmap_to_float(data: DataDef | Any) -> Literal:
    """

    Args:
        data:

    Returns:

    """

    raise NotImplementedError()


####################
# SAMPLE FUNCTIONS #
####################


@insert_cast_fns(("sample", "int"))
def sample_to_int(data: DataDef | Any) -> Literal:
    """

    Args:
        data:

    Returns:

    """

    raise NotImplementedError()


@insert_cast_fns(("sample", "float"))
def sample_to_float(data: DataDef | Any) -> Literal:
    """

    Args:
        data:

    Returns:

    """

    raise NotImplementedError()
