"""Builtin functions"""


def btin_print(vals):
    args, attr = vals
    print(*args, *attr)
    return None


def btin_add(vals):
    args, attr = vals
    _num_types = set([type(k) for k in args])
    _total = ()
    if len(_num_types) == 1:
        if _num_types.issubset({int, float, str, tuple, list}):
            _res = 0 if _num_types.issubset({int, float}) else '' if _num_types.issubset(
                {str}) else ()
            for k in args:
                _res += k
            for k in attr:
                _total += (k + _res,)
        else:
            _total = None
    else:
        _res = ()
        for k in vals:
            _res += (k,)
        for k in attr:
            _total += (_res,)
    return _total


def builtin_mult():
    pass


def builtin_div():
    pass


def builtin_power():
    pass


def builtin_sqrt():
    pass


def builtin_int_sqrt():
    pass


def builtin_len():
    pass


def builtin_q_h():
    pass


def builtin_q_x():
    pass


def builtin_q_z():
    pass


def builtin_q_y():
    pass
