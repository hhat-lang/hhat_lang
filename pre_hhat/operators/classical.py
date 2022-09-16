from .builtin import Operators

from pre_hhat.types.builtin import (ArrayNull, ArrayBool, ArrayInt, ArrayStr, ArrayCircuit)


class Add(Operators):
    name = 'ADD'

    def __call__(self, *args, **kwargs):
        if len(args) == 2:
            if len(set(type(k) for k in args[0]+args[1])) == 1:
                res = ()
                for k, v in zip(*args):
                    res += (k + v),
                return args[0][0].__class__(*res)
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
        if len(args) == 2:
            args = args[0] + args[1]
        new_args = [str(k).strip('"').strip("'") for k in args]
        print(*new_args, **kwargs)
        return ArrayNull()
