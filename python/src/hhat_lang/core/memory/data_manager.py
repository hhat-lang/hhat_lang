from __future__ import annotations

from typing import Any, Iterator

from hhat_lang.core.memory.utils import Scope

from hhat_lang.dialects.heather.syntax.base import (
    BaseVariableContainer,
    Immutable,
    Replaceable,
    Appendable,
)


class DataReference:
    # TODO: reimplement it
    #  - needs to use `BaseVariableContainer` class as values
    _data: dict[Scope, dict[str, Any]]

    def __init__(self):
        self._data = dict()

    def add(self, scope: Scope, name: str, value: Any) -> None:
        if isinstance(scope, Scope):
            if scope in self._data:
                self._data[scope][name] = value
            else:
                self._data[scope] = {name: value}
        else:
            raise ValueError("scope must be of Scope type on ReferenceData")

    def add_scope(self, scope: Scope) -> None:
        if scope not in self._data:
            self._data[scope] = dict()

    def get(self, scope: Scope, name: str) -> Any:
        return self._data[scope][name]

    def get_scope(self, scope: Scope) -> dict[str, Any]:
        return self._data[scope]

    def free(self, scope: Scope, name: str) -> Any:
        return self._data[scope].pop(name)

    def free_scope(self, scope: Scope) -> dict[str, Any]:
        return self._data.pop(scope)

    def __getitem__(self, scope: Scope) -> Any:
        return self.get_scope(scope)

    def __setitem__(self, scope: Scope, value: Any) -> None:
        self.add(scope, value[0], value[1])

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
    # _var: DataReference

    def __init__(self):
        self._main = DataReference()
        self._fn = DataReference()
        # self._var = DataReference()

    def add_main_scope(self, scope: Scope) -> None:
        self._main.add_scope(scope)

    def add_main_data(self, name: str, data: Any) -> None:
        self._main.add(Scope("main"), name, data)

    def get_main_scope(self, scope: Scope) -> dict[str, Any]:
        return self._main.get_scope(scope)

    def get_main_data(self, name: str) -> Any:
        return self._main.get(Scope("main"), name)

    def free_main_scope(self) -> None:
        self._main.free_scope(Scope("main"))

    def free_main_data(self, name: str) -> None:
        self._main.free(Scope("main"), name)

    def add_fn_data(self, name: str, data: Any, scope: Scope) -> None:
        self._fn.add(scope, name, data)

    def get_fn_data(self, name: str, scope: Scope) -> Any:
        return self._fn.get(scope, name)

    def free_fn_data(self, name: str, scope: Scope) -> None:
        self._fn.free(scope, name)

    def free_fn_scope(self, scope: Scope) -> None:
        self._fn.free_scope(scope)

    # def add_var(self, data: Any, scope: Scope) -> None:
    #     self._var.add(scope, data)
    #
    # def get_var(self, scope: Scope) -> Any:
    #     return self._var[scope]
    #
    # def free_var(self, scope: Scope) -> None:
    #     self._var.free(scope)

    def view(self) -> str:
        res = "#DynamicMemoryManager"
        res += "\n  - Main\n"
        res += "\n    ".join(f"{k}:{v}" for k, v in self._main)
        res += "\n  - Functions\n"
        res += "\n    ".join(f"{k}:{v}" for k, v in self._fn)
        # res += "\n  - Variables\n"
        # res += "\n    ".join(f"{k}:{v}" for k, v in self._var)
        res += "\n#.\n"
        return res
