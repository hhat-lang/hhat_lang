from __future__ import annotations

from numpy import sin, cos, tan, pi

import sys

from hhat_lang.core.code.base import FnHeaderDef
from hhat_lang.core.data.core import (
    Literal,
    Symbol,
)
from hhat_lang.core.error_handlers.errors import FunctionExecutionError
from hhat_lang.core.fns.core import include_builtin_fn
from hhat_lang.core.memory.core import MemoryManager

from hhat_lang.dialects.heather.code.builtins.fns.math.trigonometry import (
    TRIGONOMETRY_MODULE_PATH,
)

##################
# COSINE SECTION #
##################


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("cos"),
        fn_type=Symbol("int"),
        args_names=(Symbol("a")),
        args_types=(Symbol("float")),
    ),
    fn_path=TRIGONOMETRY_MODULE_PATH,
)
def builtin_fn_int_rad_cos(angle: Literal, mem: MemoryManager) -> Literal:
    return Literal(str(int(cos(angle))), lit_type=Symbol("int"))


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("cos"),
        fn_type=Symbol("float"),
        args_names=(Symbol("a")),
        args_types=(Symbol("float")),
    ),
    fn_path=TRIGONOMETRY_MODULE_PATH,
)
def builtin_fn_float_rad_cos(angle: Literal, mem:MemoryManager) -> Literal:
    return Literal(str(float(cos(angle))), lit_type=Symbol("float"))


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("cos"),
        fn_type=Symbol("int"),
        args_names=(Symbol("a")),
        args_types=(Symbol("float")),
    ),
    fn_path=TRIGONOMETRY_MODULE_PATH,
)
def builtin_fn_int_deg_cos(angle: Literal, mem:MemoryManager) -> Literal:
    return Literal(str(int(cos(angle) * 180/pi)), lit_type=Symbol("int"))


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("cos"),
        fn_type=Symbol("float"),
        args_names=(Symbol("a")),
        args_types=(Symbol("float")),
    ),
    fn_path=TRIGONOMETRY_MODULE_PATH,
)
def builtin_fn_int_deg_cos(angle: Literal, mem:MemoryManager) -> Literal:
    return Literal(str(float(cos(angle) * 180/pi)), lit_type=Symbol("float"))


################
# SINE SECTION #
################


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("sin"),
        fn_type=Symbol("int"),
        args_names=(Symbol("a")),
        args_types=(Symbol("float")),
    ),
    fn_path=TRIGONOMETRY_MODULE_PATH,
)
def builtin_fn_int_rad_sin(angle: Literal, mem: MemoryManager) -> Literal:
    return Literal(str(int(sin(angle))), lit_type=Symbol("int"))


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("sin"),
        fn_type=Symbol("float"),
        args_names=(Symbol("a")),
        args_types=(Symbol("float")),
    ),
    fn_path=TRIGONOMETRY_MODULE_PATH,
)
def builtin_fn_float_rad_sin(angle: Literal, mem:MemoryManager) -> Literal:
    return Literal(str(float(sin(angle))), lit_type=Symbol("float"))


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("sin"),
        fn_type=Symbol("int"),
        args_names=(Symbol("a")),
        args_types=(Symbol("float")),
    ),
    fn_path=TRIGONOMETRY_MODULE_PATH,
)
def builtin_fn_int_deg_sin(angle: Literal, mem:MemoryManager) -> Literal:
    return Literal(str(int(sin(angle) * 180/pi)), lit_type=Symbol("int"))


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("sin"),
        fn_type=Symbol("float"),
        args_names=(Symbol("a")),
        args_types=(Symbol("float")),
    ),
    fn_path=TRIGONOMETRY_MODULE_PATH,
)
def builtin_fn_int_deg_sin(angle: Literal, mem:MemoryManager) -> Literal:
    return Literal(str(float(sin(angle) * 180/pi)), lit_type=Symbol("float"))


###############
# TAN SECTION #
###############


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("tan"),
        fn_type=Symbol("int"),
        args_names=(Symbol("a")),
        args_types=(Symbol("float")),
    ),
    fn_path=TRIGONOMETRY_MODULE_PATH,
)
def builtin_fn_int_rad_tan(angle: Literal, mem: MemoryManager) -> Literal:
    if angle != pi/4:
        return Literal(str(int(tan(angle))), lit_type=Symbol("int"))
    
    sys.exit(
        FunctionExecutionError(
            angle, fn_name="tan", reason="invalid angle for tangent"
        )()
    )



@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("tan"),
        fn_type=Symbol("float"),
        args_names=(Symbol("a")),
        args_types=(Symbol("float")),
    ),
    fn_path=TRIGONOMETRY_MODULE_PATH,
)
def builtin_fn_float_rad_tan(angle: Literal, mem:MemoryManager) -> Literal:
    if angle != pi/4:
        return Literal(str(float(tan(angle))), lit_type=Symbol("float"))
    
    sys.exit(
        FunctionExecutionError(
            angle, fn_name="tan", reason="invalid angle for tangent"
        )()
    )


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("tan"),
        fn_type=Symbol("int"),
        args_names=(Symbol("a")),
        args_types=(Symbol("float")),
    ),
    fn_path=TRIGONOMETRY_MODULE_PATH,
)
def builtin_fn_int_deg_tan(angle: Literal, mem:MemoryManager) -> Literal:
    if angle != pi/4:
        return Literal(str(int(tan(angle) * 180/pi)), lit_type=Symbol("int"))
    
    sys.exit(
        FunctionExecutionError(
            angle, fn_name="tan", reason="invalid angle for tangent"
        )()
    )


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("tan"),
        fn_type=Symbol("float"),
        args_names=(Symbol("a")),
        args_types=(Symbol("float")),
    ),
    fn_path=TRIGONOMETRY_MODULE_PATH,
)
def builtin_fn_int_deg_tan(angle: Literal, mem:MemoryManager) -> Literal:
    if angle != pi/4:
        return Literal(str(float(tan(angle) * 180/pi)), lit_type=Symbol("float"))
    
    sys.exit(
        FunctionExecutionError(
            angle, fn_name="tan", reason="invalid angle for tangent"
        )()
    )