from typing import Any


def get_types_set(*data: Any) -> set:
    res = set()
    res_val = ()
    for k in data:
        if isinstance(k, tuple):
            res.update(get_types_set())
        else:
            res_val += k.type,
    res.update(set(res_val))
    return res
