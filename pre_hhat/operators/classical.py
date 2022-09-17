from .builtin import Operators

from pre_hhat.types.builtin import (SingleInt,
                                    SingleStr,
                                    SingleBool,
                                    SingleNull,
                                    ArrayNull,
                                    ArrayBool,
                                    ArrayInt,
                                    ArrayStr,
                                    ArrayCircuit)


class Add(Operators):
    name = 'ADD'

    def __call__(self, *args, **kwargs):
        if len(args) == 2:
            if len(set(type(k) for k in args[0]+args[1])) == 1:
                res = ()
                if len(args[0]) == len(args[1]):
                    for k, v in zip(*args):
                        res += (k + v),
                elif len(args[0]) == 1:
                    for k in args[1]:
                        res += (args[0][0] + k),
                return kwargs.get('value_type', args[0][0].__class__)(*res)
        else:
            if len(set(type(k) for k in args)) == 1:
                res = ArrayNull()
                for k in args:
                    res = res + k
                res = res if isinstance(res, tuple) else res,
                return args[0].__class__(*res)
        raise NotImplemented(f"{self.__class__.__name__}: not implemented summing different data.")


class Print(Operators):
    name = 'PRINT'

    def __call__(self, *args, **kwargs):
        if 'value_type' in kwargs.keys():
            kwargs.pop('value_type')
        if len(args) == 2:
            args = args[0] + args[1]
        new_args = [str(k).strip('"').strip("'") for k in args]
        print(*new_args, **kwargs)
        return ArrayNull()
