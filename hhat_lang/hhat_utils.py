from typing import Any


def get_types_set(*data: Any) -> set:
    types = set(k.type for k in data)
    types.discard("")
    return types
