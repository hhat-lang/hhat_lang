"""Implement classical operators/functions"""

from .builtin import Operators

import pre_hhat.types as types


class Add(Operators):
    name = "ADD"

    def _get_data_types(self, data):
        val = set()
        if isinstance(data, types.SingleType):
            return {type(data)}

        for k in data:
            if isinstance(k, types.SingleType):
                val = val.union({type(k)})
            elif isinstance(k, types.ArrayType):
                if types.is_circuit(k):
                    val = val.union({type(k)})
                else:
                    val = val.union(self._get_data_types(k))
        return val

    def __call__(self, *args, **kwargs):
        if len(args) == 2 and isinstance(args[0], tuple):
            args0_types = self._get_data_types(args[0])
            args1_types = self._get_data_types(args[1])
            data_types = args1_types.union(args0_types)
            res = ()
            if len(data_types) == 1:
                if len(args[0]) == len(args[1]):
                    for k, v in zip(*args):
                        res += kwargs["value_type"](k+v),
                elif len(args[0]) == 1:
                    for k in args[1]:
                        res += kwargs["value_type"](args[0][0] + k),
                elif len(args[1]) == 1:
                    for k in args[0]:
                        res += kwargs["value_type"](args[0][0] + k),
                return res
            elif types.is_circuit(data_types):
                default = kwargs['value_type']().default
                res = kwargs["value_type"](default[0] if default else default)
                if len(args[0]) == len(args[1]):
                    for k, v in zip(*args):
                        if types.is_circuit(k) or types.is_circuit(v):
                            add = k + (v, kwargs["stack"])
                        else:
                            add = k + v
                        res += kwargs["value_type"](add)
                elif len(args[0]) == 1:
                    for k in args[1]:
                        if types.is_circuit(k) or types.is_circuit(args[0][0]):
                            add = args[0][0] + (k, kwargs["stack"])
                        else:
                            add = args[0][0] + k
                        res += kwargs["value_type"](add)
                elif len(args[1]) == 1:
                    for k in args[0]:
                        if types.is_circuit(k) or types.is_circuit(args[1][0]):
                            add = args[1][0] + (k, kwargs["stack"])
                        else:
                            add = args[1][0] + k
                        val = kwargs["value_type"](add)
                        res += val
                return res,
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
