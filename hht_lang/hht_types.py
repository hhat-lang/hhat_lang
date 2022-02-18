from hht_errorhandler import error_handler_wrapper as hht_error
from rply.token import BaseBox, Token
import re

"""
# memory:
# mem_ref = mem[(hash_ref, func_scope, symbol)]   # = {"datatype": type, "data": data}

# hash_ref formula:
onetime_hash = str(time.time_ns()) + program_name.extension)  # once per program/process
hash_ref = hashlib.sha256(onetime_hash.encode()).hexdigest()

# func_scope formula:
program_name + func

# symbol: variable's symbol
  
"""


class DataType(BaseBox):
    def __init__(self, value):
        self.value_expr = value
        self.lineno = self.value_expr.source_pos.lineno
        self.colno = self.value_expr.source_pos.colno
        self.datatype = self.__class__.__name__
        self.data_container = r""

    def error_output_msg(self, msg, *args):
        return f"{msg} {' '.join(args)}(lineno={self.lineno}, colno={self.colno})"

    def match_type(self, datatype):
        return datatype == self.datatype

    def check_data_input(self, data):
        res = re.findall(self.data_container, data)
        return True if res else False

    @staticmethod
    def reserve_mem(datatype):
        return {'datatype': datatype}

    @hht_error
    def store(self, mem_ref, data):
        if self.match_type(mem_ref["datatype"]) and self.check_data_input(data):
            return {'data': data}
        else:
            raise TypeError(self.error_output_msg("Invalid datatype."))

    @staticmethod
    def get(mem_ref):
        return mem_ref['data']

    def define_data_structure(self):
        pass

    def write(self, mem_ref, data):
        if data in self.data_container:
            return self.store(mem_ref, data)
        else:
            raise ValueError(self.error_output_msg("Invalid value for datatype."))

    def append(self):
        pass

    def read(self):
        pass


class RegisterDataType(DataType):
    def __init__(self, value):
        super().__init__(value)
        self.data_container = r"[0-1]"





