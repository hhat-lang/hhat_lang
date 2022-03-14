"""Data AST"""

try:
    from error_handler import error_handler_wrapper as hht_error
except ImportError:
    from hhat_lang.error_handler import error_handler_wrapper as hht_error
from typing import Any, Optional
from rply.token import BaseBox, Token


class Data(BaseBox):
    def __init__(self,
                 symbol: Token,
                 type_rkw: Optional[Token] = None,
                 size: Optional[Any] = None,
                 value: Optional[Any] = None,
                 prop: Optional[Any] = None):
        self.atype = type_rkw.value if type_rkw else type_rkw
        self.symbol = symbol.value
        self.size = size.value if size else size
        self.value_expr = value
        self.property = prop.value if prop else prop
        self.value = value.value if not isinstance(value, tuple) and value is not None else value

    def __repr__(self):
        class_name = f"{self.__class__.__name__}"
        data_info = f"""
        - atype={self.atype}
        - symbol={self.symbol}
        - size={self.size}
        - value={self.value_expr}
        """
        return f"{class_name}({data_info})"

    def get_symbol(self):
        return self.symbol

    def get_value(self):
        return self.value_expr

    def get_prop(self):
        return self.property

    def get_atype(self):
        return self.atype

    # def error_output_msg(self, msg, *args):
    #     return f"{msg} {' '.join(args)}(lineno={self.lineno}, colno={self.colno})"


class DataDeclaration(Data):
    def __init__(self,
                 type_rkw: Token,
                 symbol: Token,
                 size: Optional[Any] = None,
                 value_expr: Optional[Any] = None):
        super().__init__(type_rkw=type_rkw, symbol=symbol, size=size, value=value_expr)
        data_vals = {'type': self.atype, 'symbol': self.symbol}
        if size is not None:
            data_vals.update({'size_decl': size.value})
        if value_expr is not None:
            data_vals.update({'assign_expr': value_expr.value})
        self.value = {'attr_decl': data_vals}

    def store_mem(self):
        mem_ref = {'atype': self.atype}
        if self.value_expr:
            mem_ref.update({'data': self.value_expr})
        return mem_ref


class DataAssign(Data):
    def __init__(self, symbol: Token, value_expr: Any):
        super().__init__(symbol=symbol, value=value_expr)
        data_vals = {'symbol': self.symbol, 'assign_expr': value_expr.value}
        self.value = data_vals

    @staticmethod
    def check_valid_value(mem_data, data):
        if mem_data['atype'] == data.atype:
            return True
        return False

    @hht_error
    def write_mem(self, mem_data, data):
        if self.check_valid_value(mem_data, data):
            return {'data': data}
        raise TypeError("Wrong datatype.")


class DataCall(Data):
    def __init__(self, symbol: Token, value: Any):
        super().__init__(symbol=symbol, value=value.value)
        data_vals = {'caller': self.symbol, 'caller_args': self.value}
        self.value = data_vals

    def read_mem(self, mem_data):
        if self.property:
            return mem_data['data'][self.property]
        return mem_data['data']
