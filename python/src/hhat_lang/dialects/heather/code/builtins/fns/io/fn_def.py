from __future__ import annotations

from typing import Any

from hhat_lang.core.data.core import WorkingObj, CompositeWorkingObj, Symbol


def builtin_fn__print(*args: WorkingObj | CompositeWorkingObj, **_: Any) -> Symbol:
    # transforming WorkingData/CompositeWorkingData into python objects
    for k in args:
        match k:
            case WorkingObj():
                print(k.value, end="")

            case CompositeWorkingObj():
                print(*k.value, end="")

            case _:
                raise NotImplementedError(f"print with {type(k)} not implemented")

    print()
    return Symbol("empty")
