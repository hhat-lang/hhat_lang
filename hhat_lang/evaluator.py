"""
Perform a pre-evaluation and evaluation on the parsed code
"""

try:
    from data_types import (NullType, BoolType, IntType,
                            RegisterType, FloatType, StrType,
                            CircuitType, ListType, HashmapType,
                            MeasurementType)
    import builtin as btin
    from memory import Memory
    import parse_keys as pk
    from tokens import tokens
except ImportError:
    from hhat_lang.data_types import (NullType, BoolType, IntType,
                                      RegisterType, FloatType, StrType,
                                      CircuitType, ListType, HashmapType,
                                      MeasurementType)
    import hhat_lang.builtin as btin
    from hhat_lang.memory import Memory
    import hhat_lang.parse_keys as pk
    from hhat_lang.tokens import tokens
import time
import ast
import pprint
from typing import Any, Union, Dict, Tuple, Optional
from rply.token import Token


# TOKEN_ENDSWITH = ['LITERAL', 'SYMBOL', 'GATE', 'SIGN', 'LOGOP', 'COND', 'TYPE', 'STAR']
#
#
# def join_token_group():
#     token_group = {k: () for k in TOKEN_ENDSWITH}
#     for key, value in tokens.items():
#         token_group[TOKEN_ENDSWITH if key.endswith(TOKEN_ENDSWITH) else None] += (value,)
#     return token_group
#
#
# token_map = join_token_group()


class PreEvaluator:
    def __init__(self, parsed_code: Tuple, debug: Optional[bool] = False):
        self.parsed_code = parsed_code
        self.debug = debug
        self.pre_eval_handlers = {dict: self.dict_handler,
                                  tuple: self.tuple_handler,
                                  Token: self.token_handler}
        self.pre_evaluated_code = ()
        self.code_str_max = 200
        self.code_str_last = int(self.code_str_max * 0.95) - 5

    def debug_print(self, *msg):
        if self.debug:
            print(*msg)

    def format_gate_type_str(self, value: str) -> str:
        return 'q_' + value[1:]

    def print_code_lim(self, code):
        code_str = str(code)
        if len(code_str) > self.code_str_max:
            return code_str[:self.code_str_last] + '[...]' + code_str[-5:]
        return code_str

    def dict_handler(self, code_slice: Dict) -> Tuple:
        tmp_parsed_code = ()
        for k in pk.PROGRAM_LIST_EXPRS:
            if not set(code_slice.keys()).symmetric_difference(set(k)):
                self.debug_print(f'**[dict] {k}')
                for v in k:
                    if v not in ['symbol', 'type']:
                        self.debug_print(f'code:{v} | value={code_slice[v]} ')
                        tmp_parsed_code += (f'code:{v}', self.pre_eval_run(code_slice[v]))
                    else:
                        tmp_parsed_code += (self.pre_eval_run(code_slice[v]),)
        self.debug_print(f'-[dict] parsed_code = {self.print_code_lim(tmp_parsed_code)}')
        return tmp_parsed_code

    def tuple_handler(self, code_slice: Optional[Tuple] = None) -> Tuple:
        tmp_parsed_code = ()
        for k in code_slice:
            res = self.pre_eval_run(k)
            tmp_parsed_code += (res,)
        self.debug_print(f'-[tuple] parsed_code = {self.print_code_lim(tmp_parsed_code)}')
        return tmp_parsed_code

    def token_handler(self, code_slice: Token) -> Union[Tuple, str, int, float]:
        token_type = code_slice.gettokentype()
        token_value = code_slice.value
        res = ''
        if token_type.endswith('LITERAL'):
            if token_type.startswith('STRING'):
                res = ast.literal_eval(f'"str:{token_value}"')
            else:
                res = ast.literal_eval(token_value)
        elif token_type.endswith('SYMBOL'):
            res = ast.literal_eval(f'"symbol:{token_value}"')
        elif token_type.endswith('TYPE'):
            res = ast.literal_eval(f'"type:{token_type}"')
        elif token_type.endswith('GATE') or token_type == 'MEASURE':
            res = ast.literal_eval(f'"type:{self.format_gate_type_str(token_value)}"')
        elif token_type.endswith('NULL'):
            res = ast.literal_eval(f'"indices:{token_value}"')
        else:
            if token_type in tokens.keys():
                res = ast.literal_eval(f'"builtin:{token_value}"')
            else:
                res = ast.literal_eval(f'"unknown:{token_value}"')
        self.debug_print(f'-[token] parsed_code = {self.print_code_lim(res)}')
        return res

    def pre_eval_run(self, parsed_code: Optional[Union[Tuple, Dict, Token]] = None) -> Tuple:
        if parsed_code is None:
            parsed_code = self.parsed_code
        if isinstance(parsed_code, Token):
            return self.token_handler(parsed_code)
        tmp_parsed_code = ()
        tmp_parsed_code += self.pre_eval_handlers[type(parsed_code)](parsed_code)
        self.debug_print(f'-[pre_eval] parsed_code = {self.print_code_lim(tmp_parsed_code)}')
        return tmp_parsed_code

    def pre_eval_exec(self):
        self.pre_evaluated_code = self.pre_eval_run()
        return self.pre_evaluated_code

    def print_pre_eval_exec(self, print_code: bool = True):
        self.debug_print('=' * 16)
        self.debug_print('= PreEvaluator =')
        self.debug_print('=' * 16)
        self.debug_print(f'* Running | -[DEBUG MODE] = {self.debug}\n')
        self.pre_eval_exec()
        self.debug_print('* Done.')
        self.debug_print('-' * 80)
        if print_code:
            self.debug_print(f'* Pre Eval Code | [PRINT CODE] = {print_code}')
            self.debug_print('', '=' * 7, '\n= START =\n', '=' * 7)
            pprint.pprint(self.pre_evaluated_code)
            self.debug_print('', '=' * 5, '\n= END =\n', '=' * 5)
            self.debug_print('-' * 80)
        self.debug_print()


class FinalEvaluator:
    def __init__(self, parsed_code: Tuple,
                 program_name: str = None,
                 debug: Optional[bool] = True,
                 do_stats: Optional[bool] = False):
        self.program_name = program_name if program_name else hex(time.time_ns())
        self.parsed_code = parsed_code
        self.debug = debug
        self.eval_handlers = {str: self.str_eval_handler,
                              tuple: self.tuple_eval_handler,
                              'literal': self.literal_eval_handler}

        self.code_properties = {'type': self.type_handler,
                                'symbol': self.symbol_handler,
                                'builtin': self.builtin_handler,
                                'indices': self.indices_handler,
                                'str': self.literal_str_handler,
                                'code': self.code_handler}
        self.mem = Memory(program_name=self.program_name, do_stats=do_stats)

    def debug_print(self, *msg):
        if self.debug:
            print(*msg)

    def code_handler(self, value: str, current_code: Optional[Any] = None):
        code_attr = value.split(':')[1]
        return code_attr

    def symbol_handler(self, value: str, current_code: Optional[Any] = None):
        tmp_eval = ()
        return tmp_eval

    def type_handler(self, value: str, current_code: Optional[Any] = None):
        tmp_eval = ()
        return tmp_eval

    def builtin_handler(self, value: str, current_code: Optional[Any] = None):
        tmp_eval = ()
        return tmp_eval

    def indices_handler(self, value: str, current_code: Optional[Any] = None):
        tmp_eval = ()
        return tmp_eval

    def literal_str_handler(self, value: str, current_code: Optional[Any] = None):
        tmp_eval = ()
        return tmp_eval

    def str_eval_handler(self,
                         value: str,
                         code_attr: str = None,
                         code_slice: Optional[Any] = None):
        tmp_eval = ()
        value_prop, value_attr = value.split(':')
        if code_attr is None:
            self.debug_print(f'=[str_eval_handler] code_attr={code_attr}')
            tmp_eval = self.code_properties[value_prop](value_attr, code_slice)
        else:
            self.debug_print('Str Eval handler not none!')
            exit()
        return tmp_eval

    def tuple_eval_handler(self,
                           code_attr: str = None,
                           mem_ref_name: Tuple = None,
                           current_code: Tuple = None) -> Tuple:
        tmp_eval = ()
        for k in current_code:
            tmp_eval += self.eval_run(code_attr, mem_ref_name, k)
        return tmp_eval

    def literal_eval_handler(self, current_code: Tuple) -> Tuple:
        tmp_eval = ()
        return tmp_eval

    def enforce_type(self, current_code: Tuple, type_check: str):
        tmp_eval = ()
        return tmp_eval

    def eval_run(self,
                 code_attr: Optional[str] = None,
                 mem_ref_name: Optional[tuple] = None,
                 current_code: Optional[Union[Tuple, Dict, Token]] = None,
                 args: Optional[Any] = None):
        pc_type = type(current_code)
        self.debug_print(f'=[eval_run] pc_type={pc_type} | code_attr={code_attr}')
        tmp_eval = ()
        tmp_eval += self.eval_handlers.get(pc_type,
                                           self.literal_eval_handler)(code_attr,
                                                                      mem_ref_name,
                                                                      current_code, args)
        return tmp_eval


example = ({'main': {'type': Token('NULL_TYPE', 'null'),
                     'symbol': Token('SYMBOL', 'C'),
                     'body': ({'attr_decl': {'type': Token('INTEGER_TYPE', 'int'),
                                             'symbol': Token('SYMBOL', 'res'),
                                             'assign_expr': (
                                                 {'call': {'caller': Token('ADD', 'add'),
                                                           'caller_args': (Token('INT_LITERAL', '1'),
                                                                    Token('INT_LITERAL', '1'))},
                                                  'opt_assign': Token('ASSIGN_NULL', 'all')},
                                                 {'call': Token('PRINT', 'print'),
                                                  'opt_assign': Token('ASSIGN_NULL',
                                                                      'all')})}},)}},)

if __name__ == '__main__':
    pe = PreEvaluator(example, True)
    pe.print_pre_eval_exec()
    print(f'- builtin = {[k for k in dir(btin) if "__" not in k and k.startswith("builtin")]}')
