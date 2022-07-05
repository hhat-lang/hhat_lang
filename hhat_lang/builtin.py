"""Builtin functions"""
import networkx as nx


def unique_values(values):
    if len(set(values)) == len(values):
        return True
    return False


def btin_print(*values, buffer=False):
    if values:
        if buffer:
            print(*values, end=' ')
        else:
            print(*values)
    return None


def btin_and(*values, buffer=False):
    if len(values) > 1:
        res = values[0]
        for k0, k in enumerate(values):
            if k0 != 0:
                res = res and k
        return res
    raise ValueError(f'"and" operator must have at least 2 values to operate.')


def btin_or(*values, buffer=False):
    if len(values) > 1:
        res = values[0]
        for k0, k in enumerate(values):
            if k0 != 0:
                res = res or k
        return res
    raise ValueError(f'"or" operator must have at least 2 values to operate.')


def btin_not(*values, buffer=False):
    return tuple(not k for k in values)


def btin_eq(*values, buffer=False):
    if len(values) > 1:
        res = values[0]
        for k0, k in enumerate(values):
            if k0 != 0:
                res = res == k
        return res
    raise ValueError(f'"eq" operator must have at least 2 values to operate.')


def btin_neq(*values, buffer=False):
    if len(values) > 1:
        res = values[0]
        for k0, k in enumerate(values):
            if k0 != 0:
                res = res != k
        return res
    raise ValueError(f'"neq" operator must have at least 2 values to operate.')


def btin_gt(*values, buffer=False):
    if len(values) > 1:
        res = values[0]
        for k0, k in enumerate(values):
            if k0 != 0:
                res = res > k
        return res
    raise ValueError(f'"gt" operator must have at least 2 values to operate.')


def btin_gte(*values, buffer=False):
    if len(values) > 1:
        res = values[0]
        for k0, k in enumerate(values):
            if k0 != 0:
                res = res >= k
        return res
    raise ValueError(f'"gte" operator must have at least 2 values to operate.')


def btin_lt(*values, buffer=False):
    if len(values) > 1:
        res = values[0]
        for k0, k in enumerate(values):
            if k0 != 0:
                res = res < k
        return res
    raise ValueError(f'"lt" operator must have at least 2 values to operate.')


def btin_lte(*values, buffer=False):
    if len(values) > 1:
        res = values[0]
        for k0, k in enumerate(values):
            if k0 != 0:
                res = res <= k
        return res
    raise ValueError(f'"lte" operator must have at least 2 values to operate.')


def btin_abs(*values, buffer=False):
    return tuple(abs(k) for k in values)


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
    g = nx.Graph()
    for k in values:
        g.add_node(k, data='@x')
    return g


def btin_q_z(*values, buffer=False):
    g = nx.Graph()
    for k in values:
        g.add_node(k, data='@z')
    return g


def btin_q_y(*values, buffer=False):
    g = nx.Graph()
    for k in values:
        g.add_node(k, data='@y')
    return g


def btin_q_h(*values, buffer=False):
    g = nx.Graph()
    for k in values:
        g.add_node(k, data='@h')
    return g


def btin_q_cnot(*values, buffer=False):
    if unique_values(values):
        g = nx.Graph()
        for k0, k in enumerate(values):
            _data = 'control' if k == 0 else 'target'
            g.add_node(k, data=_data)
        g.add_edge(values[0], values[1], data='@cnot')
        return g
    raise ValueError(
        "control functions does not operates in the same indices as control and target.")


def btin_q_swap(*values, buffer=False):
    if unique_values(values):
        g = nx.Graph()
        for k in values:
            g.add_node(k)
        g.add_edge(values[0], values[1], data='@swap')
        return g
    raise ValueError(
        "control functions does not operates in the same indices as control and target.")


def btin_q_toffoli(*values, buffer=False):
    if unique_values(values):
        g = nx.Graph()
        for k0, k in enumerate(values):
            g.add_node(k, data='control' if k0 < 2 else 'target')
        for k in range(len(values) - 1):
            g.add_edge(values[k], values[k + 1], data='@toffoli')
        return g
    raise ValueError(
        "control functions does not operates in the same indices as control and target.")


def btin_q_ccz(*values, buffer=False):
    g = nx.Graph()

    return g


def btin_q_init(*values, buffer=False):
    g = nx.Graph()

    return g


def btin_q_reset(*values, buffer=False):
    g = nx.Graph()

    return g


def btin_q_sync(*values, buffer=False):
    g = nx.Graph()

    return g


def btin_q_and(*values, buffer=False):
    return btin_q_toffoli(*values, buffer)


def btin_q_or(*values, buffer=False):
    if unique_values(values):
        g_list = []
        for p in range(3):
            if p % 2 == 0:
                g = nx.Graph()
                for k0, k in enumerate(values):
                    if p != 2 and k0 < (len(values) - 1):
                        g.add_node(k, data='@x')
            else:
                g = nx.Graph()
                for k0, k in enumerate(values):
                    g.add_node(k, data='control' if k0 < 2 else 'target')
                for k in range(len(values) - 1):
                    g.add_edge(values[k], values[k + 1], data='@toffoli')
            g_list.append(g)
        return g_list
    raise ValueError(
        "control functions does not operates in the same indices as control and target.")
