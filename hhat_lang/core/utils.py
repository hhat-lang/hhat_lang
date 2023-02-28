import hhat_lang.types as types
import string

valid_hex = set(string.hexdigits)
valid_bin = {"0", "1"}


def is_hex(value):
    if isinstance(value, str):
        return True if set(value.strip("0x")).issubset(valid_hex) else False
    return isinstance(value, types.SingleHex)


def is_bin(value):
    if isinstance(value, str):
        return True if set(value.strip("0b")).issubset(valid_bin) else False
    return isinstance(value, types.SingleBin)


def hex2int(value):
    if is_hex(value):
        return int(value, 16)
    raise ValueError(f"{value} is not hex.")


def bin2int(value):
    if is_bin(value):
        return int(value, 2)
    raise ValueError(f"{value} is not bin.")


def get_hex(value):
    if is_hex(value):
        return value.lower()
    if isinstance(value, int):
        return hex(value)
    if is_bin(value):
        return hex(int(value, 2))


def get_bin(value):
    if is_bin(value):
        return value
    if isinstance(value, int):
        return bin(value)
    if is_hex(value):
        return bin(int(value, 16))
