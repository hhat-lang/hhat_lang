from hht_lang.hht_errorhandler import error_handler_wrapper as hht_error
from rply.token import BaseBox, Token


class Data(BaseBox):
    def __init__(self, symbol, type_rkw=None, size=None, value=None, prop=None):
        self.atype = type_rkw
        self.symbol = symbol
        self.size = size
        self.value = value
        self.property = prop

    def __repr__(self):
        return f"{self.__class__.__name__}(atype={self.atype} symbol={self.symbol} size={self.size} value={self.value})"

    def get_symbol(self):
        return self.symbol

    def get_value(self):
        return self.value

    def get_prop(self):
        return self.property

    def get_atype(self):
        return self.atype

    # def error_output_msg(self, msg, *args):
    #     return f"{msg} {' '.join(args)}(lineno={self.lineno}, colno={self.colno})"


class DataDeclaration(Data):
    def __init__(self, type_rkw, symbol, size=None, value_expr=None):
        print('datadec?')
        super().__init__(type_rkw=type_rkw, symbol=symbol, size=size,value=value_expr)

    def store_mem(self):
        mem_ref = {'atype': self.atype}
        if self.value:
            mem_ref.update({'data': self.value})
        return mem_ref


class DataAssignment(Data):
    def __init__(self, symbol, value_expr):
        super().__init__(symbol=symbol, value=value_expr)

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


class DataRetrieval(Data):
    def __init__(self, symbol, prop=None):
        super().__init__(symbol=symbol, prop=prop)

    def read_mem(self, mem_data):
        if self.property:
            return mem_data['data'][self.property]
        return mem_data['data']
