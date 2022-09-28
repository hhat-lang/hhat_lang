"""Implement classical operators/functions"""

from .builtin import Operators

import pre_hhat.types as types


class Add(Operators):
    name = "ADD"

    def __call__(self, *args, **kwargs):
        if len(args) == 2:
            print(f"add (args + indices)? {args}")
            data_types = set(type(k) for k in args[0] + args[1])
            print(f"set data: {data_types} {types.is_circuit(data_types)}")
            if len(data_types) == 1:
                res = ()
                if len(args[0]) == len(args[1]):
                    for k, v in zip(*args):
                        res += ((k + v),)
                elif len(args[0]) == 1:
                    for k in args[1]:
                        res += ((args[0][0] + k),)
                elif len(args[1]) == 1:
                    for k in args[0]:
                        res += ((args[1][0] + k),)
            if types.is_circuit(data_types):
                print("sim?")
                res = kwargs["value_type"](kwargs["value_type"]().default[0])
                if len(args[0]) == len(args[1]):
                    for k, v in zip(*args):
                        if types.is_circuit(k) or types.is_circuit(v):
                            add = k + (v, kwargs["stack"])
                            print('AQUE')
                            res += add
                        else:
                            add = k + v
                            res += add
                elif len(args[0]) == 1:
                    for k in args[1]:
                        if types.is_circuit(k) or types.is_circuit(args[0][0]):
                            add = args[0][0] + (k, kwargs["stack"])
                            print('AQUIO')
                            res += add
                        else:
                            add = args[0][0] + k
                            res += add
                elif len(args[1]) == 1:
                    for k in args[0]:
                        if types.is_circuit(k) or types.is_circuit(args[1][0]):
                            print(f'seria aquia? {args[1][0]} {k}')
                            add = args[1][0] + (k, kwargs["stack"])
                            print(f'AQUIA {add} {res}')
                            res += add
                            print(f'aquia res {res}')
                        else:
                            print(f'seria aqui oto? {args[1][0]} {k}')
                            add = args[1][0] + k
                            print(f'AQUIA oto {add} {type(add)} {args[1][0]}')
                            res += add
                            print(f'AQUIA oto res {res} {type(res)}')
            return kwargs.get("value_type", args[0][0].__class__)(*res)
        else:
            if len(set(type(k) for k in args)) == 1:
                res = types.ArrayNull()
                for k in args:
                    res = res + k
                res = (res if isinstance(res, tuple) else res,)
                return kwargs.get("value_type", args[0].__class__)(*res)
        raise NotImplementedError(f"{self.__class__.__name__}: not implemented summing different data.")


class Print(Operators):
    name = "PRINT"

    def __call__(self, *args, **kwargs):
        if "value_type" in kwargs.keys():
            kwargs.pop("value_type")
        if "stack" in kwargs.keys():
            kwargs.pop("stack")

        if len(args) == 2:
            args = args[0] + args[1]
        new_args = [str(k).strip('"').strip("'") for k in args]
        print(*new_args, **kwargs)
        return types.ArrayNull()
