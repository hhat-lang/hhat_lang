from __future__ import annotations

from typing import Any, Callable
from functools import wraps
from pathlib import Path

from hhat_lang.core.code.base import BaseFnKey
from hhat_lang.core.code.ir_custom import ArgsValuesBlock
from hhat_lang.core.data.core import Literal, Tmp
from hhat_lang.core.data.fn_def import BuiltinFnDef
from hhat_lang.core.data.var_def import DataDef
from hhat_lang.core.memory.core import MemoryManager


builtin_fns_path: dict[Path, tuple[BuiltinFnDef, ...]] = dict()


def include_builtin_fn(fn_entry: BaseFnKey, fn_path: Path) -> Callable:
    def decorator(fn: Callable) -> BuiltinFnDef:
        """
        fn argument is the actual built-in function implementation, for instance::

            builtin_fn_int_add(
                CoreLiteral(1, lit_type="int"),
                CoreLiteral(1, lit_type="int"),
                mem=mem
            )
            # outputs '2:int' (e.g. CoreLiteral(2, lit_type="int"))
        """

        @wraps(fn)
        def wrapper(*args: Any, mem: MemoryManager) -> Literal | DataDef:
            """
            Built-in function signature implementation. Returns the function call result.
            """

            if isinstance(fn_entry.name, Tmp):
                fn_entry.complement_name(" ".join(str(k) for k in args))

            return _builtin_fn_def(*args, mem=mem)

        args_values = ArgsValuesBlock(
            *tuple((a, b) for a, b in zip(fn_entry.args_names, fn_entry.args_types))
        )
        _builtin_fn_def = BuiltinFnDef(
            fn_name=fn_entry.name,
            fn_args=args_values,
            fn_type=fn_entry.type,
            fn_body=wrapper,
        )

        if fn_path in builtin_fns_path:
            builtin_fns_path[fn_path] += (_builtin_fn_def,)

        else:
            builtin_fns_path[fn_path] = (_builtin_fn_def,)

        return _builtin_fn_def

    return decorator
