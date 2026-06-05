from __future__ import annotations

import importlib
import inspect
import pkgutil
from typing import Any

FN_RESOLVE_PATH = __name__
__all__ = []


def load_builtin_fns(package_name: Any | None = None) -> None:
    package_name = package_name if package_name else FN_RESOLVE_PATH
    package = importlib.import_module(package_name)

    for module_info in pkgutil.walk_packages(
        package.__path__,
        prefix=package.__name__ + ".",
    ):
        module = importlib.import_module(module_info.name)

        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if name.startswith("builtin"):
                globals()[name] = obj
                __all__.append(name)
