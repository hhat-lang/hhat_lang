from rply.token import BaseBox, Token
from hht_lang.hht_datadec import (Data, DataDeclaration, DataAssign, DataRetrieval)


class SuperBox(BaseBox):
    def __init__(self):
        self.value = ()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"


class TypeRKW(SuperBox):
    def __init__(self, value):
        super().__init__()
        self.value = value


class Test(SuperBox):
    def __init__(self, *args):
        super().__init__()
        for k in args:
            self.value += (k,)


class Program(SuperBox):
    def __init__(self, value1=None, value2=None):
        super().__init__()
        print(f'program?')
        if value1 is not None:
            self.value += (value1,)
        if value2 is not None:
            self.value += (value2,)

    def eval(self):
        pass


class GenExpr(SuperBox):
    def __init__(self, value=None):
        # if isinstance(value, DataDeclaration):
        #     pass
        # elif isinstance(value, DataAssignment):
        #     pass
        # elif isinstance(value, DataRetrieval):
        #     pass
        # else:
        #     pass
        super().__init__()
        if value is not None:
            self.value = value


class SizeDeclaration(SuperBox):
    def __init__(self, value=None):
        print('sizedec?')
        super().__init__()
        if value is not None:
            self.value = (value,)


class ValueExpr(SuperBox):
    def __init__(self, value=None):
        print('valuexpr?')
        super().__init__()
        if value is not None:
            self.value = value


class Value(SuperBox):
    def __init__(self, value):
        print('value?')
        super().__init__()
        self.value += (value,)


class ValueAssign(SuperBox):
    def __init__(self, value, opt=None, value2=None):
        print('valueassign?')
        super().__init__()
        self.value += (value,)
        if value2 is not None:
            if isinstance(value2, tuple):
                self.value += value2
            else:
                self.value += (value2,)


class ValueRetrieval(SuperBox):
    def __init__(self, value):
        print('valueret?')
        super().__init__()
        self.value = value


class ExprAssign(SuperBox):
    def __init__(self, value, optional=None, extra=None):
        print('exprassign?')
        super().__init__()
        self.value += (value,)
        if extra is not None:
            self.value += (extra,)


class InnerAssign(SuperBox):
    def __init__(self, value=None, optional=None):
        super().__init__()
        print('innerassign?')
        val = {}
        if value is not None:
            val.update({'value': value})
        if optional is not None:
            val.update({'opt': value})
        self.value += (val,)


class OptionalAssign(SuperBox):
    def __init__(self, value=None):
        print('opt?')
        super().__init__()
        if value is not None:
            self.value += (value,)
