try:
    from error_handler import *  # error_handler_wrapper as hht_error
except ImportError:
    from hhat_lang.error_handler import *  # error_handler_wrapper as hht_error

import ast
from typing import Dict, List

from networkx import Graph
from rply.token import BaseBox


def measurement_type(data):
    return


def circuit_type(data):
    op = Graph()

    return


def literal_type(data):
    """" return literals for int/float/bool types"""
    return ast.literal_eval(data.value)


def int_type(data):
    return ast.literal_eval(data.value)


def str_type(data):
    return data.value


def bool_type(data):
    return ast.literal_eval(data.value)


def float_type(data):
    return ast.literal_eval(data.value)


class Types(BaseBox):
    def __init__(self, entity):
        self.value = entity.value_expr
        self.self_atype = Types
        self.atype = self.get_atype(entity.atype)

    def get_atype(self, value=None):
        if value:
            if isinstance(value, self.self_atype):
                return
            else:
                raise TypeExcpt()
        return 0


class NullType(Types):
    def __init__(self, entity):
        self.self_atype = None
        super().__init__(entity)


class BoolType(Types):
    def __init__(self, entity):
        self.self_atype = bool
        super().__init__(entity)


class RegisterType(Types):
    def __init__(self, entity):
        self.self_atype = Dict[str, int]
        super().__init__(entity)


class IntType(Types):
    def __init__(self, entity):
        self.self_atype = int
        super().__init__(entity)


class FloatType(Types):
    def __init__(self, entity):
        self.self_atype = float
        super().__init__(entity)


class StrType(Types):
    def __init__(self, entity):
        self.self_atype = str
        super().__init__(entity)


class ListType(Types):
    def __init__(self, entity):
        self.self_atype = list
        super().__init__(entity)


class CircuitType(Types):
    def __init__(self, entity):
        self.self_atype = list
        super().__init__(entity)


class HashmapType(Types):
    def __init__(self, entity):
        self.self_atype = dict
        super().__init__(entity)


class MeasurementType(Types):
    def __init__(self, entity):
        self.self_atype = dict
        super().__init__(entity)
