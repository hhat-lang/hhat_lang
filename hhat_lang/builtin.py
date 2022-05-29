"""Builtin functions"""
import networkx as nx


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


def btin_eq(*values, buffer=False):
    if len(values) > 1:
        res = values[0]
        for k0, k in enumerate(values):
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
    def get_type(value):
        if isinstance(value, str):
            if value.startswith('0b'):
                return 'bin'
        return type(value)

    type_list = set([get_type(v) for v in values])
    if len(type_list) == 1:
        if int in type_list or float in type_list:
            return sum(values)
        if str in type_list:
            return ''.join(values)
        return tuple(values)
    if len(type_list) == 2:
        if 'bin' in type_list:
            res = []
            for v in values:
                if isinstance(v, int):
                    res.append(v)
                elif isinstance(v, str):
                    if v.startswith('0b') and str in type_list:
                        res.append(chr(int(v, 2)))
                    elif v.startswith('0b') and int in type_list:
                        res.append(int(v, 2))
            return sum(res) if int in type_list else ''.join(res)
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


def btin_q_x(*values, buffer=False):
    # print(f'@X values={values}')
    g = nx.DiGraph()
    for k in values:
        g.add_node(k, data='X')
    # print('btin_q_x', g)
    return g


def btin_q_z():
    pass


def btin_q_y():
    pass


def btin_q_h(*values, buffer=False):
    # print(f'@H values={values}')
    g = nx.DiGraph()
    for k in values:
        g.add_node(k, data='H')
    # ('btin_q_h', g)
    return g


def btin_q_cnot(*values, buffer=False):
    # print(f'@CNOT values={values}')
    g = nx.DiGraph()
    for k in values:
        g.add_node(k)
    g.add_edge(values[0], values[1], data='CNOT')
    # print('btin_q_cnot', g)
    return g


def btin_q_swap():
    pass


def btin_q_toffoli():
    pass


def btin_q_ccz():
    pass


def btin_q_init(*values, buffer=False):
    pass


def btin_q_reset():
    pass


def btin_q_sync(*values, buffer=False):
    pass


def btin_q_and(*values, buffer=False):
    pass


def btin_q_or(*values, buffer=False):
    pass
