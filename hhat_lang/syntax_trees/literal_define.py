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


def literal_str_define(value: str) -> str:
    if res := re.match(r"\"[.\s\w]*\"", value):
        return res.group()
    raise ValueError(f"wrong value for string ({value}).")


def literal_bin_define(value: str) -> str:
    if res := re.match(r"0[bB][0-1]+", value):
        return res.group()
    raise ValueError(f"wrong value for bin ({value}).")


def literal_hex_define(value: str) -> str:
    if res := re.match(r"0[xX][0-9a-fA-F]+", value):
        return res.group()
    raise ValueError(f"wrong value for hex ({value}).")


def literal_atomic_define(value: str) -> str:
    if res := re.match(r"\'[a-zA-Z][a-zA-Z\-_0-9]*", value):
        return res.group()
    raise ValueError(f"wrong value for atomic ({value}).")
