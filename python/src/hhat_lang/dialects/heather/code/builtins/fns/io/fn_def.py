from __future__ import annotations

from typing import Any

from hhat_lang.core.data.core import SimpleObj, ObjArray, Symbol


def builtin_fn__print(*args: SimpleObj | ObjArray, **_: Any) -> Symbol:
    # transforming WorkingData/CompositeWorkingData into python objects
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
