from __future__ import annotations

from typing import Any

from hhat_lang.core.data.core import WorkingData, CompositeWorkingData, Symbol


def builtin_fn__print(*args: WorkingData | CompositeWorkingData, **_: Any) -> Symbol:
    # transforming WorkingData/CompositeWorkingData into python objects
    for k in args:
        match k:
            case WorkingData():
                print(k.value, end="")

            case CompositeWorkingData():
                print(*k.value, end="")

            case _:
                raise NotImplementedError(f"print with {type(k)} not implemented")

    print()
    return Symbol("empty")
