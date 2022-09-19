import string

valid_hex = set(string.hexdigits)
valid_bin = {"0", "1"}


def is_hex(value):
    return True if set(value.strip("0x")).issubset(valid_hex) else False


def is_bin(value):
    return True if set(value.strip("0b")).issubset(valid_bin) else False


def hex2int(value):
    if is_hex(value):
        return int(value, 16)
    raise ValueError(f"{value} is not hex.")


def bin2int(value):
    if is_bin(value):
        return int(value, 2)
    raise ValueError(f"{value} is not bin.")
