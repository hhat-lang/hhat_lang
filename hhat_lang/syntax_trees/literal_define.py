import re


def literal_bool_define(value: str) -> bool:
    bool_vals = dict(T=True, F=False)
    if res := bool_vals.get(value, False):
        return res
    raise ValueError(f"wrong value for boolean ({value}).")


def literal_int_define(value: str) -> int:
    if res := re.match(r"^(0|-?[1-9][0-9]*)$", value):
        return int(res.group())
    raise ValueError(f"wrong value for integer ({value}).")
