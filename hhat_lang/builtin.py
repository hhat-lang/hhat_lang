"""Builtin functions"""


def builtin_print(memory, reference, indices=None, *values):
    if indices:
        print(memory[reference][indices])
    else:
        print(reference,
              ':\n',
              *[str(k) + ': ' + str(v) + '\n' for k, v in memory[reference].items()])


def builtin_add(*values):
    values_types = [type(k) for k in values]
    svt = set(values_types)
    if len(svt) == 1:
        if int in svt or float in svt:
            return sum(*values)
        if str in svt:
            return ''.join(values)
        raise TypeError("Wrong type for function.")
    else:
        return list(values)


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
