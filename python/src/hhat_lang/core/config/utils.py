from __future__ import annotations

from functools import wraps
from pathlib import Path
from typing import Callable, Any

conversion_types: dict[str, Callable[[Path], dict | Any]] = dict()
"""
Dictionary to hold all the available conversion types used in H-hat configuration files.
The key is the name, e.g. "json", and the value is the function to execute the proper type 
conversion, e.g. ``read_json`` .
"""


def insert_reader(ext: str) -> Callable:
    def decorator(fn: Callable[[Path], dict | Any]) -> Callable:
        @wraps(fn)
        def wrapper(arg: Path) -> dict | Any:
            return fn(arg)

        conversion_types[ext] = wrapper
        return wrapper

    return decorator


@insert_reader("json")
def read_json(file: Path) -> dict:
    import json

    return json.load(open(file))


@insert_reader("toml")
def read_toml(file: Path) -> Any:
    raise NotImplementedError("reading TOML config files for H-hat not implemented yet.")


@insert_reader("yaml")
def read_yaml(file: Path) -> dict:
    raise NotImplementedError("reading YAML config files for H-hat not implemented yet.")


def read_file(file: Path) -> dict | Any:
    """
    Reads H-hat's project configuration file.
    """

    read_fn: Callable[[Path], dict | Any] = conversion_types.get(file.name.split(".")[-1])
    return read_fn(file)
