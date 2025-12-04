from __future__ import annotations

from typing import Any, Callable
from functools import wraps
from pathlib import Path

from hhat_lang.core.code.abstract import RefTable
from hhat_lang.core.code.base import BaseFnCheck


def include_builtin_fn(fn_entry: BaseFnCheck) -> Callable:
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, fn_path: Path, ref_table: RefTable) -> Any:
            ref_table.fns.add_ref(fn_entry, fn_path)
            return fn(*args, fn_path=fn_path, ref_table=ref_table)

        # TODO: finish implementing it
