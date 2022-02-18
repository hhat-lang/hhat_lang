from hht_errorhandler import error_handler_wrapper as hht_error
from rply.token import BaseBox, Token
from hht_types import (DataType, RegisterDataType, )


class TypesExpr(BaseBox):
    def __init__(self, token_tuple):
        self.self_atype = self.__class__
        self.atype = token_tuple[0]
        self.symbol = token_tuple[1]
        self.value = token_tuple[2]
        self.size = 0

    def get_value(self):
        if isinstance(self.value, Token):
            return self.value.value
        elif isinstance(self.value, self.self_atype):
            return self.value.get_value()
        else:
            return ''


class NullExpr(TypesExpr):
    def __init__(self, token_tuple):
        super().__init__(token_tuple)


class IntExpr(TypesExpr):
    def __init__(self, token_tuple):
        super().__init__(token_tuple)


class RegisterExpr(TypesExpr):
    def __init__(self, token_tuple):
        super().__init__(token_tuple)
