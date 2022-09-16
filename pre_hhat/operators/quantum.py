from .builtin import Operators


class X(Operators):
    name = '@X'

    def __call__(self, *args, **kwargs):
        return 0


class H(Operators):
    name = '@H'

    def __call__(self, *args, **kwargs):
        return 0
