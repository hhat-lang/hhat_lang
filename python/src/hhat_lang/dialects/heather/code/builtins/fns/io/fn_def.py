from __future__ import annotations

from typing import Any

from hhat_lang.core.code.base import FnHeaderDef
from hhat_lang.core.data.core import ObjArray, SimpleObj, Symbol
from hhat_lang.core.fns.core import include_builtin_fn
from hhat_lang.dialects.heather.code.builtins.fns.io import PRINT_PATH


@include_builtin_fn(
    fn_entry=FnHeaderDef(
        fn_name=Symbol("print"),
        fn_type=Symbol("null"),
        args_names=(Symbol(""),),
        args_types=(Symbol(""),),
    ),
    fn_path=PRINT_PATH,
)
def builtin_fn__print(*args: SimpleObj | ObjArray, **_: Any) -> Symbol:
    # transforming into python objects
    for k in args:
        match k:
            case SimpleObj():
                print(k.value, end="")

            case ObjArray():
                print(*k.value, end="")

            case _:
                raise NotImplementedError(f"print with {type(k)} not implemented")

    print()
    return Symbol("empty")
