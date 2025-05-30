"""To handle the `imports` part, for both types and functions"""

from __future__ import annotations

import os
from functools import reduce
from operator import iconcat
from pathlib import Path
from typing import Any

from hhat_lang.core.code.ast import AST
from hhat_lang.dialects.heather.code.ast import (
    CompositeId,
    CompositeIdWithClosure,
    Imports,
)


def parse_types(code: Any) -> Any:
    pass


def parse_types_compositeid(code: CompositeId) -> Any:
    # get the type path from the code
    type_path = Path(*reduce(iconcat, code.value, ()))
    # join the type path with its full path from the project path
    type_path = Path(".").resolve() / "hhat_types" / type_path
    # add .hat for the type file name (which should be the last item in the tuple)
    file_name = type_path.name + ".hat"
    full_path = type_path.parent / file_name

    if full_path.exists():
        data = open(full_path, "r").read()


def parse_types_compositeidwithclosure(code: CompositeIdWithClosure) -> Any:
    pass


def parse_fns(code: Any) -> Any:
    pass


def parse_imports(code: Imports) -> Any:
    pass
