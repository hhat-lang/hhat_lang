from __future__ import annotations

from functools import wraps
from pathlib import Path
from typing import Any, Callable

from hhat_lang.core.code.base import FnHeader, FnHeaderDef
from hhat_lang.core.code.ir_custom import ArgsValuesBlock
from hhat_lang.core.data.core import Literal
from hhat_lang.core.data.fn_def import BuiltinFnDef
from hhat_lang.core.data.var_def import DataDef
from hhat_lang.core.memory.core import MemoryManager

builtin_fns_path: dict[
    Path,
    dict[FnHeader, BuiltinFnDef],
] = dict()
"""
Built-in functions path dictionary. Contains all the built-in functions as 
value for a given path as key.
"""


def include_builtin_fn(fn_entry: FnHeaderDef, fn_path: Path) -> Callable:
    def decorator(fn: Callable) -> Callable:
        """
        fn argument is the actual built-in function implementation, for instance::

            builtin_fn_int_add(
                CoreLiteral(1, lit_type="int"),
                CoreLiteral(1, lit_type="int"),
                mem=mem
            )
            # outputs '2:int' (e.g. CoreLiteral(2, lit_type="int"))
        """

        @wraps(include_builtin_fn)
        def wrapper(*args: Any, mem: MemoryManager) -> Literal | DataDef:
            """
            Built-in function signature implementation. Returns the function call result.
            """

            return _builtin_fn_def(*args, mem=mem)

        args_values = ArgsValuesBlock(
            *tuple((a, b) for a, b in zip(fn_entry.args_names, fn_entry.args_types))
        )
        _builtin_fn_def = BuiltinFnDef(
            fn_name=fn_entry.name,
            fn_args=args_values,
            fn_type=fn_entry.type,
            fn_body=fn,
        )

        if fn_path in builtin_fns_path:
            builtin_fns_path[fn_path][_builtin_fn_def.fn_header] = _builtin_fn_def

        else:
            builtin_fns_path[fn_path] = {_builtin_fn_def.fn_header: _builtin_fn_def}

        return wrapper

    return decorator
