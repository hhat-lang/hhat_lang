from __future__ import annotations

from typing import Any


def builtin_fn__print(*args: Any, **kwargs: Any) -> None:
    print(*args, **kwargs)


def builtin_fn_int_add(*args: Any) -> Any:
    pass


def builtin_fn_float_add(*args: Any) -> Any:
    pass


def builtin_fn_int_float_add(*args: Any) -> Any:
    pass


def builtin_fn_int_sub(*args: Any) -> Any:
    pass


