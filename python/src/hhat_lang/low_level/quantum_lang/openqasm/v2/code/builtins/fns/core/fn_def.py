from __future__ import annotations

import sys
from typing import Any

from hhat_lang.core.code.base import BaseFnKey
from hhat_lang.core.data.core import Symbol, Tmp, CoreLiteral, TypeSymbolSetter
from hhat_lang.core.data.variable import BaseDataContainer, VariableTemplate
from hhat_lang.core.error_handlers.errors import FnWrongDataError
from hhat_lang.core.fns.core import include_builtin_fn
from hhat_lang.core.memory.core import MemoryManager
from hhat_lang.low_level.quantum_lang.openqasm.v2.code.builtins.fns.core import (
    LLQ_MODULE_PATH,
)


@include_builtin_fn(
    fn_entry=BaseFnKey(
        fn_name=Tmp("@redim"),
        fn_type=Symbol("@bool"),
        args_names=(Symbol("@a"),),
        args_types=(Symbol("@bool"),),
    ),
    fn_path=LLQ_MODULE_PATH,
)
def builtin_fn_qbool_qredim(
    *args: CoreLiteral | BaseDataContainer, mem: MemoryManager
) -> BaseDataContainer:
    # can only accept one argument
    match arg := args[0]:
        case CoreLiteral():
            # VariableTemplate(var_name=Tmp("@redim").complement_name(arg.value),type_name=TypeSymbolSetter(arg.type),ds_data)
            pass

        case BaseDataContainer():
            pass

        case _:
            sys.exit(FnWrongDataError(type(args[0]))())


@include_builtin_fn(
    fn_entry=BaseFnKey(
        fn_name=Tmp("@redim"),
        fn_type=Symbol("@int"),
        args_names=(Symbol("@a"),),
        args_types=(Symbol("@int"),),
    ),
    fn_path=LLQ_MODULE_PATH,
)
def builtin_fn_qint_qredim(
    *args: CoreLiteral | BaseDataContainer, mem: MemoryManager
) -> BaseDataContainer:
    pass


@include_builtin_fn(
    fn_entry=BaseFnKey(
        fn_name=Tmp("@redim"),
        fn_type=Symbol("@u2"),
        args_names=(Symbol("@a"),),
        args_types=(Symbol("@u2"),),
    ),
    fn_path=LLQ_MODULE_PATH,
)
def builtin_fn_qu2_qredim(
    *args: CoreLiteral | BaseDataContainer, mem: MemoryManager
) -> BaseDataContainer:
    pass


@include_builtin_fn(
    fn_entry=BaseFnKey(
        fn_name=Tmp("@redim"),
        fn_type=Symbol("@u3"),
        args_names=(Symbol("@a"),),
        args_types=(Symbol("@u3"),),
    ),
    fn_path=LLQ_MODULE_PATH,
)
def builtin_fn_qu3_qredim(
    *args: CoreLiteral | BaseDataContainer, mem: MemoryManager
) -> BaseDataContainer:
    pass


@include_builtin_fn(
    fn_entry=BaseFnKey(
        fn_name=Tmp("@redim"),
        fn_type=Symbol("@u4"),
        args_names=(Symbol("@a"),),
        args_types=(Symbol("@u4"),),
    ),
    fn_path=LLQ_MODULE_PATH,
)
def builtin_fn_qu4_qredim(
    *args: CoreLiteral | BaseDataContainer, mem: MemoryManager
) -> BaseDataContainer:
    pass


@include_builtin_fn(
    fn_entry=BaseFnKey(
        fn_name=Tmp("@sync"),
        fn_type=Symbol("@bell_t"),
        args_names=(Symbol("@s"), Symbol("@t")),
        args_types=(Symbol("@bool"), Symbol("@bool")),
    ),
    fn_path=LLQ_MODULE_PATH,
)
def builtin_fn_qbool_qsync(
    *args: CoreLiteral | BaseDataContainer, mem: MemoryManager
) -> BaseDataContainer:
    pass


@include_builtin_fn(
    fn_entry=BaseFnKey(
        fn_name=Tmp("@sync"),
        fn_type=Symbol("@ghz2_t"),
        args_names=(Symbol("@s"), Symbol("@t")),
        args_types=(Symbol("@u2"), Symbol("@u2")),
    ),
    fn_path=LLQ_MODULE_PATH,
)
def builtin_fn_qu2_qsync(
    *args: CoreLiteral | BaseDataContainer, mem: MemoryManager
) -> BaseDataContainer:
    pass


@include_builtin_fn(
    fn_entry=BaseFnKey(
        fn_name=Tmp("@sync"),
        fn_type=Symbol("@ghz3_t"),
        args_names=(Symbol("@s"), Symbol("@t")),
        args_types=(Symbol("@u3"), Symbol("@u3")),
    ),
    fn_path=LLQ_MODULE_PATH,
)
def builtin_fn_qu3_qsync(
    *args: CoreLiteral | BaseDataContainer, mem: MemoryManager
) -> BaseDataContainer:
    pass


@include_builtin_fn(
    fn_entry=BaseFnKey(
        fn_name=Tmp("@sync"),
        fn_type=Symbol("@ghz4_t"),
        args_names=(Symbol("@s"), Symbol("@t")),
        args_types=(Symbol("@u4"), Symbol("@u4")),
    ),
    fn_path=LLQ_MODULE_PATH,
)
def builtin_fn_qu4_qsync(
    *args: CoreLiteral | BaseDataContainer, mem: MemoryManager
) -> BaseDataContainer:
    pass
