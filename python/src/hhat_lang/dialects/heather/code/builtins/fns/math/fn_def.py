from __future__ import annotations

import sys
from functools import reduce
from typing import Any

from hhat_lang.core.data.core import (
    CoreLiteral,
)
from hhat_lang.core.error_handlers.errors import FunctionExecutionError


####################
# ADDITION SECTION #
####################


def _add_res(*args: CoreLiteral) -> str:
    if len(args) >= 2:
        return str(
            reduce(lambda x, y: x + float(y.value), args[1:], float(args[0].value))
        )

    sys.exit(
        FunctionExecutionError(
            *args, fn_name="add", reason="operation needs more than 1 argument"
        )()
    )


def builtin_fn_int_add(*args: CoreLiteral, fn_path) -> CoreLiteral:
    return CoreLiteral(
        str(reduce(lambda x, y: x + int(y.value), args[1:], int(args[0].value))),
        lit_type="int",
    )


def builtin_fn_float_add(*args: CoreLiteral) -> CoreLiteral:
    return CoreLiteral(_add_res(*args), lit_type="float")


def builtin_fn_int_float_add(*args: CoreLiteral) -> CoreLiteral:
    return CoreLiteral(_add_res(*args), lit_type="float")


#######################
# SUBTRACTION SECTION #
#######################


def _sub_res(*args: CoreLiteral) -> str:
    if len(args) >= 2:
        return str(
            reduce(lambda x, y: x - float(y.value), args[1:], float(args[0].value))
        )

    sys.exit(
        FunctionExecutionError(
            *args, fn_name="sub", reason="operation needs more than 1 argument"
        )()
    )


def builtin_fn_int_sub(*args: CoreLiteral) -> CoreLiteral:
    return CoreLiteral(
        str(reduce(lambda x, y: x - int(y.value), args[1:], int(args[0].value))),
        lit_type="int",
    )


def builtin_fn_float_sub(*args: CoreLiteral) -> Any:
    return CoreLiteral(_sub_res(*args), lit_type="float")


def builtin_fn_int_float_sub(*args: CoreLiteral) -> Any:
    return CoreLiteral(_sub_res(*args), lit_type="float")


##########################
# MULTIPLICATION SECTION #
##########################


def _mul_res(*args: CoreLiteral) -> str:
    if len(args) >= 2:
        return str(
            reduce(lambda x, y: x * float(y.value), args[1:], float(args[0].value))
        )

    sys.exit(
        FunctionExecutionError(
            *args, fn_name="mul", reason="operation needs more than 1 argument"
        )()
    )


def builtin_fn_int_mul(*args: CoreLiteral) -> CoreLiteral:
    return CoreLiteral(
        str(reduce(lambda x, y: x * int(y.value), args[1:], int(args[0].value))),
        lit_type="int",
    )


def builtin_fn_float_mul(*args: Any) -> CoreLiteral:
    return CoreLiteral(_mul_res(*args), lit_type="float")


def builtin_fn_int_float_mul(*args: Any) -> CoreLiteral:
    return CoreLiteral(_mul_res(*args), lit_type="float")


####################
# DIVISION SECTION #
####################


def _div_res(*args: CoreLiteral) -> str:
    if len(args) >= 2:
        return str(
            reduce(lambda x, y: x / float(y.value), args[1:], float(args[0].value))
        )

    sys.exit(
        FunctionExecutionError(
            *args, fn_name="div", reason="operation needs more than 1 argument"
        )()
    )


def builtin_fn_int_div(*args: CoreLiteral) -> CoreLiteral:
    return CoreLiteral(
        str(reduce(lambda x, y: x // int(y.value), args[1:], int(args[0].value))),
        lit_type="int",
    )


def builtin_fn_float_div(*args: CoreLiteral) -> CoreLiteral:
    return CoreLiteral(_div_res(*args), lit_type="float")


def builtin_fn_int_float_div(*args: CoreLiteral) -> CoreLiteral:
    return CoreLiteral(_div_res(*args), lit_type="float")


def builtin_fn_float_int_div(*args: CoreLiteral) -> CoreLiteral:
    return CoreLiteral(_div_res(*args), lit_type="float")


#################
# POWER SECTION #
#################


def builtin_fn_int_pow(base: CoreLiteral, power: CoreLiteral) -> CoreLiteral:
    return CoreLiteral(str(int(base.value) ** int(power.value)), lit_type="int")


def builtin_fn_float_pow(base: CoreLiteral, power: CoreLiteral) -> CoreLiteral:
    return CoreLiteral(str(float(base.value) ** float(power.value)), lit_type="float")


def builtin_fn_int_float_pow(base: CoreLiteral, power: CoreLiteral) -> CoreLiteral:
    return CoreLiteral(str(int(base.value) ** float(power.value)), lit_type="float")


def builtin_fn_float_int_pow(base: CoreLiteral, power: CoreLiteral) -> CoreLiteral:
    return CoreLiteral(str(float(base.value) ** int(power.value)), lit_type="float")


########################
# CONSTRUCTORS SECTION #
########################

# TODO: create a class to work as the "math" module

