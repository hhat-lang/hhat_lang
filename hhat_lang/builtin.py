"""Builtin functions"""


def btin_print(vals):
    args, attr = vals
    print(*args, *attr)

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


def btin_add(vals):
    args, attr = vals
    _num_types = set([type(k) for k in args])
    _total = ()

    if len(_num_types) == 1:
        if _num_types.issubset({int, float, str, tuple, list}):
            _res = 0 if _num_types.issubset({int, float}) else '' if _num_types.issubset({str}) else ()
                
            for k in args:
                _res += k

            if attr:
                for k in attr:
                    _total += (k + _res,)

            else:
                _total = (_res,)

        else:
            _total = None

    else:
        _res = ()
        for k in vals:
            _res += (k,)

        if attr:
            for k in attr:
                _total += (_res,)

        else:
            _total = (_res,)

    return _total


def builtin_mult(): pass


def builtin_div(): pass


def builtin_power(): pass


def builtin_sqrt(): pass


def builtin_int_sqrt(): pass


def builtin_len(): pass


def builtin_q_h(): pass


def builtin_q_x(): pass


def builtin_q_z(): pass


def builtin_q_y(): pass
