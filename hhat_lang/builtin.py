"""Builtin functions"""


def btin_print(*values, buffer=False):
    if buffer:
        print(*values, end=' ')
    else:
        print(*values)
    return None


def btin_and(vals):
    if len(vals) > 1:
        res = vals[0]
        for k0, k in enumerate(vals):
            if k0 != 0:
                res = res and k
        return res
    raise ValueError(f'"and" operator must have at least 2 values to operate.')


def btin_or(vals):
    if len(vals) > 1:
        res = vals[0]
        for k0, k in enumerate(vals):
            if k0 != 0:
                res = res or k
        return res
    raise ValueError(f'"or" operator must have at least 2 values to operate.')


def btin_not(vals):
    return tuple(not k for k in vals)


def btin_eq(vals):
    if len(vals) > 1:
        res = vals[0]
        for k0, k in enumerate(vals):
            if k0 != 0:
                res = res == k
        return res
    raise ValueError(f'"eq" operator must have at least 2 values to operate.')


def btin_neq(vals):
    if len(vals) > 1:
        res = vals[0]
        for k0, k in enumerate(vals):
            if k0 != 0:
                res = res != k
        return res
    raise ValueError(f'"neq" operator must have at least 2 values to operate.')


def btin_gt(vals):
    if len(vals) > 1:
        res = vals[0]
        for k0, k in enumerate(vals):
            if k0 != 0:
                res = res > k
        return res
    raise ValueError(f'"gt" operator must have at least 2 values to operate.')


def btin_gte(vals):
    if len(vals) > 1:
        res = vals[0]
        for k0, k in enumerate(vals):
            if k0 != 0:
                res = res >= k
        return res
    raise ValueError(f'"gte" operator must have at least 2 values to operate.')


def btin_lt(vals):
    if len(vals) > 1:
        res = vals[0]
        for k0, k in enumerate(vals):
            if k0 != 0:
                res = res < k
        return res
    raise ValueError(f'"lt" operator must have at least 2 values to operate.')


def btin_lte(vals):
    if len(vals) > 1:
        res = vals[0]
        for k0, k in enumerate(vals):
            if k0 != 0:
                res = res <= k
        return res
    raise ValueError(f'"lte" operator must have at least 2 values to operate.')


def btin_add(*values, buffer=False):
    type_list = set([type(v) for v in values])
    if len(type_list) == 1:
        if int in type_list or float in type_list:
            return sum(values)
        if str in type_list:
            return ''.join(values)
        return tuple(values)
    else:
        return tuple(values)


def btin_mult():
    pass


def btin_div():
    pass


def btin_pow():
    pass


def btin_sqrt():
    pass


def btin_int_sqrt():
    pass


def btin_len():
    pass


def btin_q_h():
    pass


def btin_q_x():
    pass


def btin_q_z():
    pass


def btin_q_y():
    pass
