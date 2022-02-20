from hht_errorhandler import error_handler_wrapper as hht_error
from rply.token import BaseBox
from typing import List
from networkx import Graph


class TypesRKW(BaseBox):
    def __init__(self, entity):
        self.value = entity.value_expr
        self.self_atype = TypesRKW
        self.atype = self.get_atype(entity.atype)

    @hht_error
    def get_atype(self, value=None):
        if value:
            if isinstance(value, self.self_atype):
                return
            else:
                raise TypeError()
        return 0


class NullRKW(TypesRKW):
    def __init__(self, entity):
        self.self_atype = None
        super().__init__(entity)


class BoolRKW(TypesRKW):
    def __init__(self, entity):
        self.self_atype = bool
        super().__init__(entity)


class RegisterRKW(TypesRKW):
    def __init__(self, entity):
        self.self_atype = List[int]
        super().__init__(entity)


class IntRKW(TypesRKW):
    def __init__(self, entity):
        self.self_atype = int
        super().__init__(entity)


class FloatRKW(TypesRKW):
    def __init__(self, entity):
        self.self_atype = float
        super().__init__(entity)


class StrRKW(TypesRKW):
    def __init__(self, entity):
        self.self_atype = str
        super().__init__(entity)


class ListRKW(TypesRKW):
    def __init__(self, entity):
        self.self_atype = list
        super().__init__(entity)


class GatesRKW(TypesRKW):
    def __init__(self, entity):
        self.self_atype = list
        super().__init__(entity)


class HashmapRKW(TypesRKW):
    def __init__(self, entity):
        self.self_atype = dict
        super().__init__(entity)


class MeasurementRKW(TypesRKW):
    def __init__(self, entity):
        self.self_atype = dict
        super().__init__(entity)

