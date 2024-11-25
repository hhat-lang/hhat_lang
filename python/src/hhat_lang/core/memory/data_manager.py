from __future__ import annotations

from typing import Any, Iterator

from hhat_lang.core.memory.utils import Scope


class DataReference:
    _data: dict[Scope, Any] = dict()

    def add(self, scope: Scope, value: Any) -> None:
        if isinstance(scope, Scope):
            self._data[scope] = value
        else:
            raise ValueError("scope must be of Scope type on ReferenceData")

    def get(self, scope: Scope) -> Any:
        return self._data[scope]

    def free(self, scope: Scope) -> Any:
        return self._data.pop(scope)

    def __getitem__(self, scope: Scope) -> Any:
        return self.get(scope)

    def __setitem__(self, scope: Scope, value: Any) -> None:
        self.add(scope, value)

    def __iter__(self) -> Iterator:
        yield from self._data.items()

    def view(self) -> str:
        res = "#DataReference\n  "
        res += "\n  ".join(f"{k}:{v}" for k, v in self._data.items())
        res += "\n" + "-" * 40 + "\n#.\n"
        return res

    def __repr__(self) -> str:
        return "DataRef(" + " ".join(f"{k}:{v}" for k, v in self._data.items()) + ")"


class DynamicMemoryManager:
    """
    Manages all the dynamic memory in the program, storing the runtime variables,
    functions and main execution.
    """

    _main: DataReference
    _fn: DataReference
    _var: DataReference

    def __init__(self):
        self._main = DataReference()
        self._fn = DataReference()
        self._var = DataReference()

    def add_main(self, data: Any, scope: Scope | None = None) -> None:
        self._main.add(scope if scope is not None else Scope("main"), data)

    def get_main(self, scope: Scope | None = None) -> Any:
        return self._main[scope if scope is not None else Scope("main")]

    def free_main(self, scope: Scope | None = None) -> None:
        self._main.free(scope if scope is not None else Scope("main"))

    def add_fn(self, data: Any, scope: Scope) -> None:
        self._fn.add(scope, data)

    def get_fn(self, scope: Scope) -> Any:
        return self._fn[scope]

    def free_fn(self, scope: Scope) -> None:
        self._fn.free(scope)

    def add_var(self, data: Any, scope: Scope) -> None:
        self._var.add(scope, data)

    def get_var(self, scope: Scope) -> Any:
        return self._var[scope]

    def free_var(self, scope: Scope) -> None:
        self._var.free(scope)

    def view(self) -> str:
        res = "#DynamicMemoryManager"
        res += "\n  - Main\n"
        res += "\n    ".join(f"{k}:{v}" for k, v in self._main)
        res += "\n  - Functions\n"
        res += "\n    ".join(f"{k}:{v}" for k, v in self._fn)
        res += "\n  - Variables\n"
        res += "\n    ".join(f"{k}:{v}" for k, v in self._var)
        res += "\n#.\n"
        return res
