"""Implement classical operators/functions"""

from .builtin import Operators

import pre_hhat.types as types


class Add(Operators):
    name = "ADD"

    def __call__(self, *args, **kwargs):
        if len(args) == 2:
            args1_types = set(type(p) for k in args[1] for p in k)
            args0_types = set(type(p) for k in args[0] for p in k)
            data_types = args1_types.union(args0_types)
            print(args, data_types)
            res = ()
            if len(data_types) == 1:
                if len(args[0]) == len(args[1]):
                    for k, v in zip(*args):
                        # res += (k + v),
                        res += kwargs["value_type"](k+v),
                elif len(args[0]) == 1:
                    for k in args[1]:
                        # res += (args[0][0] + k),
                        res += kwargs["value_type"](args[0][0] + k),
                elif len(args[1]) == 1:
                    for k in args[0]:
                        # res += (args[1][0] + k),
                        res += kwargs["value_type"](args[0][0] + k),
                return res
            elif types.is_circuit(data_types):
                default = kwargs['value_type']().default
                res = kwargs["value_type"](default[0] if default else default)
                if len(args[0]) == len(args[1]):
                    # print('ARGS:', args[0], args[1])
                    for k, v in zip(*args):
                        if types.is_circuit(k) or types.is_circuit(v):
                            # print(f"* arg0: {k}\narg1: {v}")
                            add = k + (v, kwargs["stack"])
                            # print(f"* res add = {add} {type(add)}")
                            # res += add
                        else:
                            add = k + v
                            # res += add
                        res += kwargs["value_type"](add)
                elif len(args[0]) == 1:
                    for k in args[1]:
                        if types.is_circuit(k) or types.is_circuit(args[0][0]):
                            add = args[0][0] + (k, kwargs["stack"])
                            # res += add
                        else:
                            add = args[0][0] + k
                            # res += add
                        res += kwargs["value_type"](add)
                elif len(args[1]) == 1:
                    for k in args[0]:
                        print('* add aqui de novo')
                        if types.is_circuit(k) or types.is_circuit(args[1][0]):
                            add = args[1][0] + (k, kwargs["stack"])
                            # res += add
                        else:
                            add = args[1][0] + k
                            # res += add
                        print(f'* add res={add} type={type(add)} vals={[type(p) for p in add]}')
                        print(f'* value type={kwargs["value_type"]} -> type add[0]={type(add[0])}')
                        val = kwargs["value_type"](add)
                        print(f'* oi {val} | type res={type(res)}')
                        res += val
                        print('hmm')
                return res,
            # return kwargs.get("value_type", args[0][0].__class__)(*res),
            print(f'* final: add res={res} type={type(res)} vals={[type(k) for k in res]}')
        else:
            if len(set(type(k) for k in args)) == 1:
                res = types.ArrayNull()
                for k in args:
                    res = res + k
                res = (res if isinstance(res, tuple) else res,)
                return kwargs.get("value_type", args[0].__class__)(*res),
        raise NotImplementedError(f"{self.__class__.__name__}: not implemented summing different data.")


class Print(Operators):
    name = "PRINT"

    def __call__(self, *args, **kwargs):
        if "value_type" in kwargs.keys():
            kwargs.pop("value_type")
        if "stack" in kwargs.keys():
            kwargs.pop("stack")

        if len(args) == 2:
            if isinstance(args[0], tuple) and isinstance(args[1], tuple):
                args = args[0] + args[1]
            elif isinstance(args[0], types.SingleNull):
                args = (args[1],)
        for n, k in enumerate(args):
            if not isinstance(k, types.SingleNull):
                k = str(k).strip('"').strip("'") if isinstance(k, types.SingleStr) else k
                if n < len(args) - 1:
                    print(k, end=" ")
                else:
                    print(k)
        return types.ArrayNull()
