from __future__ import annotations

import sys
from functools import reduce
from typing import Any

from hhat_lang.core.code.base import FnHeaderDef
from hhat_lang.core.data.core import (
    Literal,
    Symbol,
)
from hhat_lang.core.error_handlers.errors import FunctionExecutionError
from hhat_lang.core.fns.core import include_builtin_fn
from hhat_lang.core.memory.core import MemoryManager
from hhat_lang.dialects.heather.code.builtins.fns.math.arithmetic import (
    ARITHMETIC_MODULE_PATH,
)

####################
# ADDITION SECTION #
####################


def _add_res(*args: Literal, mem: MemoryManager) -> str:
    if len(args) >= 2:
        return str(
            reduce(lambda x, y: x + float(y.value), args[1:], float(args[0].value))
        )

    sys.exit(
        FunctionExecutionError(
            *args, fn_name="add", reason="operation needs more than 1 argument"
        )()
    )


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("add"),
        fn_type=Symbol("int"),
        args_names=(Symbol("a"), Symbol("b")),
        args_types=(Symbol("int"), Symbol("int")),
    ),
    fn_path=ARITHMETIC_MODULE_PATH,
)
def builtin_fn_int_add(*args: Literal, mem: MemoryManager) -> Literal:
    """Add two integer numbers `a+b` and return an integer `c`."""
    return Literal(
        str(reduce(lambda x, y: x + int(y.value), args[1:], int(args[0].value))),
        lit_type=Symbol("int"),
    )


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("add"),
        fn_type=Symbol("float"),
        args_names=(Symbol("a"), Symbol("b")),
        args_types=(Symbol("float"), Symbol("float")),
    ),
    fn_path=ARITHMETIC_MODULE_PATH,
)
def builtin_fn_float_add(*args: Literal, mem: MemoryManager) -> Literal:
    return Literal(_add_res(*args, mem=mem), lit_type=Symbol("float"))


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("add"),
        fn_type=Symbol("float"),
        args_names=(Symbol("a"), Symbol("b")),
        args_types=(Symbol("int"), Symbol("float")),
    ),
    fn_path=ARITHMETIC_MODULE_PATH,
)
def builtin_fn_int_float_add(*args: Literal, mem: MemoryManager) -> Literal:
    return Literal(_add_res(*args, mem=mem), lit_type=Symbol("float"))


#######################
# SUBTRACTION SECTION #
#######################


def _sub_res(*args: Literal, mem: MemoryManager) -> str:
    if len(args) >= 2:
        return str(
            reduce(lambda x, y: x - float(y.value), args[1:], float(args[0].value))
        )

    sys.exit(
        FunctionExecutionError(
            *args, fn_name="sub", reason="operation needs more than 1 argument"
        )()
    )


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("sub"),
        fn_type=Symbol("int"),
        args_names=(Symbol("a"), Symbol("b")),
        args_types=(Symbol("int"), Symbol("int")),
    ),
    fn_path=ARITHMETIC_MODULE_PATH,
)
def builtin_fn_int_sub(*args: Literal, mem: MemoryManager) -> Literal:
    return Literal(
        str(reduce(lambda x, y: x - int(y.value), args[1:], int(args[0].value))),
        lit_type=Symbol("int"),
    )


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("sub"),
        fn_type=Symbol("float"),
        args_names=(Symbol("a"), Symbol("b")),
        args_types=(Symbol("float"), Symbol("float")),
    ),
    fn_path=ARITHMETIC_MODULE_PATH,
)
def builtin_fn_float_sub(*args: Literal, mem: MemoryManager) -> Any:
    return Literal(_sub_res(*args, mem=mem), lit_type=Symbol("float"))


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("sub"),
        fn_type=Symbol("float"),
        args_names=(Symbol("a"), Symbol("b")),
        args_types=(Symbol("int"), Symbol("float")),
    ),
    fn_path=ARITHMETIC_MODULE_PATH,
)
def builtin_fn_int_float_sub(*args: Literal, mem: MemoryManager) -> Any:
    return Literal(_sub_res(*args, mem=mem), lit_type=Symbol("float"))


##########################
# MULTIPLICATION SECTION #
##########################


def _mul_res(*args: Literal, mem: MemoryManager) -> str:
    if len(args) >= 2:
        return str(
            reduce(lambda x, y: x * float(y.value), args[1:], float(args[0].value))
        )

    sys.exit(
        FunctionExecutionError(
            *args, fn_name="mul", reason="operation needs more than 1 argument"
        )()
    )


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("mul"),
        fn_type=Symbol("int"),
        args_names=(Symbol("a"), Symbol("b")),
        args_types=(Symbol("int"), Symbol("int")),
    ),
    fn_path=ARITHMETIC_MODULE_PATH,
)
def builtin_fn_int_mul(*args: Literal, mem: MemoryManager) -> Literal:
    return Literal(
        str(reduce(lambda x, y: x * int(y.value), args[1:], int(args[0].value))),
        lit_type=Symbol("int"),
    )


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("mul"),
        fn_type=Symbol("float"),
        args_names=(Symbol("a"), Symbol("b")),
        args_types=(Symbol("float"), Symbol("float")),
    ),
    fn_path=ARITHMETIC_MODULE_PATH,
)
def builtin_fn_float_mul(*args: Any, mem: MemoryManager) -> Literal:
    return Literal(_mul_res(*args, mem=mem), lit_type=Symbol("float"))


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("mul"),
        fn_type=Symbol("float"),
        args_names=(Symbol("a"), Symbol("b")),
        args_types=(Symbol("int"), Symbol("float")),
    ),
    fn_path=ARITHMETIC_MODULE_PATH,
)
def builtin_fn_int_float_mul(*args: Any, mem: MemoryManager) -> Literal:
    return Literal(_mul_res(*args, mem=mem), lit_type=Symbol("float"))


####################
# DIVISION SECTION #
####################


def _div_res(*args: Literal, mem: MemoryManager) -> str:
    if len(args) >= 2:
        return str(
            reduce(lambda x, y: x / float(y.value), args[1:], float(args[0].value))
        )

    sys.exit(
        FunctionExecutionError(
            *args, fn_name="div", reason="operation needs more than 1 argument"
        )()
    )


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("div"),
        fn_type=Symbol("int"),
        args_names=(Symbol("a"), Symbol("b")),
        args_types=(Symbol("int"), Symbol("int")),
    ),
    fn_path=ARITHMETIC_MODULE_PATH,
)
def builtin_fn_int_div(*args: Literal, mem: MemoryManager) -> Literal:
    return Literal(
        str(reduce(lambda x, y: x // int(y.value), args[1:], int(args[0].value))),
        lit_type=Symbol("int"),
    )


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("div"),
        fn_type=Symbol("float"),
        args_names=(Symbol("a"), Symbol("b")),
        args_types=(Symbol("float"), Symbol("float")),
    ),
    fn_path=ARITHMETIC_MODULE_PATH,
)
def builtin_fn_float_div(*args: Literal, mem: MemoryManager) -> Literal:
    return Literal(_div_res(*args, mem=mem), lit_type=Symbol("float"))


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("div"),
        fn_type=Symbol("float"),
        args_names=(Symbol("a"), Symbol("b")),
        args_types=(Symbol("int"), Symbol("float")),
    ),
    fn_path=ARITHMETIC_MODULE_PATH,
)
def builtin_fn_int_float_div(*args: Literal, mem: MemoryManager) -> Literal:
    return Literal(_div_res(*args, mem=mem), lit_type=Symbol("float"))


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("div"),
        fn_type=Symbol("float"),
        args_names=(Symbol("a"), Symbol("b")),
        args_types=(Symbol("float"), Symbol("int")),
    ),
    fn_path=ARITHMETIC_MODULE_PATH,
)
def builtin_fn_float_int_div(*args: Literal, mem: MemoryManager) -> Literal:
    return Literal(_div_res(*args, mem=mem), lit_type=Symbol("float"))


#################
# POWER SECTION #
#################


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("pow"),
        fn_type=Symbol("int"),
        args_names=(Symbol("a"), Symbol("b")),
        args_types=(Symbol("int"), Symbol("int")),
    ),
    fn_path=ARITHMETIC_MODULE_PATH,
)
def builtin_fn_int_pow(base: Literal, power: Literal, mem: MemoryManager) -> Literal:
    return Literal(str(int(base.value) ** int(power.value)), lit_type=Symbol("int"))


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("pow"),
        fn_type=Symbol("float"),
        args_names=(Symbol("a"), Symbol("b")),
        args_types=(Symbol("float"), Symbol("float")),
    ),
    fn_path=ARITHMETIC_MODULE_PATH,
)
def builtin_fn_float_pow(base: Literal, power: Literal, mem: MemoryManager) -> Literal:
    return Literal(
        str(float(base.value) ** float(power.value)), lit_type=Symbol("float")
    )


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("pow"),
        fn_type=Symbol("float"),
        args_names=(Symbol("a"), Symbol("b")),
        args_types=(Symbol("int"), Symbol("float")),
    ),
    fn_path=ARITHMETIC_MODULE_PATH,
)
def builtin_fn_int_float_pow(
    base: Literal, power: Literal, mem: MemoryManager
) -> Literal:
    return Literal(str(int(base.value) ** float(power.value)), lit_type=Symbol("float"))


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("pow"),
        fn_type=Symbol("float"),
        args_names=(Symbol("a"), Symbol("b")),
        args_types=(Symbol("float"), Symbol("int")),
    ),
    fn_path=ARITHMETIC_MODULE_PATH,
)
def builtin_fn_float_int_pow(
    base: Literal, power: Literal, mem: MemoryManager
) -> Literal:
    return Literal(str(float(base.value) ** int(power.value)), lit_type=Symbol("float"))
