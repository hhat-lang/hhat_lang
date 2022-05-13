"""
Perform a pre-evaluation and evaluation on the parsed code
"""
import time

try:
    from parser import parser

    from builtin import btin_add, btin_print
    from lexer import lexer
except (ImportError, ModuleNotFoundError):
    from hhat_lang.lexer import lexer
    from hhat_lang.parser import parser
    from hhat_lang.builtin import (
        btin_add, btin_print, btin_and, btin_or, btin_not, btin_eq, btin_neq, btin_gt, btin_gte, btin_lt, btin_lte
        )

import ast
from copy import deepcopy


class Eval:
    def __init__(self, debug=False):
        self.debug = debug
        self.mem = {'cur': {}}
        self.k = self.start_kwargs()
        self.main_handlers = {tuple: self.tuple_handler, str: self.str_handler}
        self.block_prefix = {
            'scope': self.prefix_scope,
            'symbol': self.prefix_symbol,
            'qsymbol': self.prefix_qsymbol,
            'type': self.prefix_type,
            'int': self.prefix_int,
            'float': self.prefix_float,
            'str': self.prefix_str,
            'indices': self.prefix_indices,
            'builtin': self.prefix_builtin,
            'op': self.prefix_op,
            'loop': self.prefix_loop,
            'code': self.prefix_code,
            'end': self.prefix_end
            }
        self.default_len = {
            'int': 1, 
            'str': 1, 
            'float': 1, 
            'null': 0, 
            'circuit': 1, 
            'measurement': 1, 
            'hashmap': 1, 
            'bool': 1
            }
        self.default_val = {
            'int': 0,
            'str': '',
            'float': 0.0,
            'null': None,
            'circuit': None,
            'measurement': {},
            'hashmap': {},
            'bool': None
            }
        self.type2type = {int: 'int', str: 'str', float: 'float'}
        self.builtin_funcs = {'print': btin_print, 'add': btin_add}
        self.op_funcs = {
            'and': btin_and, 
            'or': btin_or, 
            'eq': btin_eq, 
            'neq': btin_neq, 
            'gt': btin_gt, 
            'gte': btin_gte, 
            'lt': btin_lt, 
            'lte': btin_lte
            }

    def dprint(self, origin, *msg, **msgs):
        if self.debug:
            print(f'* [debug:eval]: [{origin}]:')
            for k in msg:
                print(f'   ----> {k}', **msgs)
            if 'end' not in msgs.keys():
                print()

    @staticmethod
    def start_kwargs():
        return {
            'scope': None,
            'attr_name': None,
            'attr_type': None,
            'attr_size': None,
            'idx_or_val': None,
            'prev_cmd': None,
            'cur_cmd': None,
            'return_flag': False,
            'cond_test': None,
            'loop_flag': False,
            'loop_pos': None,
            'loop_range': (),
            'args': (),
            'attr_idx': (),
            'caller_idx': (),
            'from_attr': (),
            'to_target': ()
            }

    # MISC

    @staticmethod
    def split_str_code(code):
        _idx = code.index(':')
        return code[:_idx], code[_idx+1:]

    def check_type(self, data):
        _attr_type = self.k['attr_type']
        if not _attr_type:
            _attr_type = self.mem['cur'][self.k['scope']][self.k['attr_name']]['type']

        _data_type = self.type2type[type(data)]
        if _data_type == _attr_type:
            return data

        raise ValueError(f"Wrong type in attribute {self.k['scope']}.{self.k['attr_name']} .")

    # MEMORY FUNCS

    def store_data(self):
        self.dprint('[mem]', 'storing data')
        _cur = self.mem['cur']

        if self.k['scope'] not in _cur.keys():
            _cur[self.k['scope']] = {}

        _scope = _cur[self.k['scope']]
        if self.k['attr_name']:
            if not _scope.get(self.k['attr_name']):
                _scope[self.k['attr_name']] = {'data': {}}
                _attr_mem = _scope[self.k['attr_name']]
                _attr_mem['type'] = self.k['attr_type'] if self.k['attr_type'] else None
                _attr_mem['size'] = self.k['attr_size'] if self.k['attr_size'] else None

            if _scope[self.k['attr_name']]['size']:
                _attr_mem = _scope[self.k['attr_name']]

                if self.k['to_target'] and self.k['attr_idx']:
                    if len(self.k['to_target']) == len(self.k['attr_idx']):
                        _attr_mem['data'].update(
                            {key: self.check_type(value) for key, value in zip(
                                self.k['attr_idx'], 
                                self.k['to_target']
                                )})

                    elif len(self.k['to_target']) == 1:
                        _attr_mem['data'].update({key: self.check_type(self.k['to_target'][0]) for key in self.k['attr_idx']})

                    else:
                        raise ValueError(f"Cannot write data {self.k['to_target']} into {self.k['scope']}.{self.k['attr_name']}: too many args.")

                else:
                    _attr_mem['data'].update({p: self.default_val[_attr_mem['type']] for p in range(_attr_mem['size'])})

    def read_data(self, attr=None, data=None, cond=None):
        _res = ()
        self.dprint('[read_data]', f'data={data} cond={cond}')

        if attr is None:
            attr = self.k['attr_name']
        
        if data:
            for p in data:
                if isinstance(p, int):
                    if not cond:
                        _res += (self.mem['cur'][self.k['scope']][attr]['data'][p],)

                    else:
                        if p in cond:
                            _res += (self.mem['cur'][self.k['scope']][attr]['data'][p],)

                elif isinstance(p, str):
                    if not cond:
                        _res += (self.mem['cur'][self.k['scope']][attr][p],)

                    else:
                        if p in cond:
                            _res += (self.mem['cur'][self.k['scope']][attr][p],)

        else:
            if not isinstance(data, (int, float, str, tuple)):
                for key, value in self.mem['cur'][self.k['scope']][attr]['data'].items():
                    if not cond:
                        _res += (value,)

                    else:
                        if key in cond:
                            _res += (value,)
                            
        return _res

    def get_data(self, attr=None):
        if attr is None:
            attr = self.k['attr_name']
            
        return tuple(self.mem['cur'][self.k['scope']][attr]['data'].items())

    def get_data_values(self, attr=None):
        if attr is None:
            attr = self.k['attr_name']

        return tuple(self.mem['cur'][self.k['scope']][attr]['data'].values())

    def get_data_keys(self, attr=None):
        if attr is None:
            attr = self.k['attr_name']

        return tuple(self.mem['cur'][self.k['scope']][attr]['data'].keys())

    # PREFIX TYPES

    def prefix_int(self, code):
        lit_code = ast.literal_eval(code)
        self.dprint('[pfx--int]', code)

        if self.k['cur_cmd'] == 'call':
            if self.k['prev_cmd'] == 'opt_assign':
                self.k['attr_idx'] += (lit_code,)
                self.k['from_attr'] += self.read_data(data=(lit_code,))

            elif self.k['prev_cmd'] == 'caller_args':
                self.k['args'] += (lit_code,)

            elif self.k['prev_cmd'] == 'assign_value':
                self.k['to_target'] += (lit_code,)

        elif self.k['cur_cmd'] == 'size_decl':
            self.k['attr_size'] = lit_code

        elif self.k['cur_cmd'] == 'opt_assign':
            self.k['attr_idx'] += (lit_code,)
            self.k['from_attr'] += self.read_data(data=(lit_code,))

        elif self.k['cur_cmd'] == 'loop':
            self.k['loop_range'] += (lit_code,)

    def prefix_float(self, code):
        pass

    def prefix_str(self, code):
        lit_code = ast.literal_eval(code)
        self.dprint('[pfx--str]', code)

        if self.k['cur_cmd'] == 'call':
            if self.k['prev_cmd'] == 'caller_args':
                self.k['args'] += (lit_code,)

    # PREFIX FUNCS

    def prefix_scope(self, code):
        self.dprint('[pfx--scope]', code)
        self.k['scope'] = code

    def prefix_symbol(self, code):
        self.dprint('[pfx--sym]', code)

        if self.k['cur_cmd'] == None and self.k['attr_name'] == None:
            self.k['scope'] = code

        elif self.k['cur_cmd'] in ['attr_decl', 'attr_assign']:
            self.k['attr_name'] = code

        elif self.k['cur_cmd'] == 'call':
            if self.k['prev_cmd'] == 'assign_value':
                _caller_idx = self.k['args']
                _vals = self.read_data(attr=code, cond=_caller_idx)
                self.k['to_target'] += _vals

            elif self.k['prev_cmd'] == 'caller_args':
                _vals = self.read_data(attr=code)
                self.k['args'] += _vals

        elif self.k['cur_cmd'] == 'caller':
            self.k['to_target'] += self.read_data(attr=code, data=self.k['args'])

    def prefix_qsymbol(self, code):
        self.dprint('[pfx--qsym]', code)

    def prefix_type(self, code):
        self.dprint('[pfx--type]', code)
        if self.k['cur_cmd'] == 'attr_decl':
            self.k['attr_type'] = code

    def prefix_indices(self, code):
        self.dprint('[pfx--idx]', code)
        _res = ()

        if code == 'all':
            _res = self.get_data_keys()

        self.k['attr_idx'] += _res
        self.k['from_attr'] += self.read_data(data=_res)

    def prefix_builtin(self, code):
        self.dprint('[pfx--btin]', code)
        _args = (self.k['args'], self.k['from_attr'])
        self.dprint(f'[pfx--btin] [{code}]', f'args={_args}')
        _res = self.builtin_funcs[code](_args)

        if _res:
            if self.k['attr_name']:
                self.k['to_target'] = _res
                self.k['args'] = ()

            else:
                self.k['args'] = _res

    def prefix_op(self, code):
        self.dprint('[pfx--op]', code)
        _args = (self.k['args'], self.k['from_attr'])
        self.dprint(f'[pfx--op] [{code}]', f'args={_args}')
        _res = self.op_funcs[code](_args)

        if _res:
            if self.k['attr_name']:
                self.k['to_target'] = _res
                self.k['args'] = ()

            else:
                self.k['args'] = _res

    def prefix_loop(self, code):
        self.dprint('[pfx--loop]', code)
        self.k['loop_pos'] = (code,)
        self.k['loop_flag'] = True

    def prefix_if(self, code):
        if code == 'cond_test':
            self.k

        elif code == 'cond_body':
            pass

    def prefix_elif(self, code):
        pass

    def prefix_else(self, code):
        pass

    def prefix_code(self, code):
        self.dprint('[pfx--code]', code)
        self.k['prev_cmd'] = self.k['cur_cmd']
        self.k['cur_cmd'] = code

        if self.k['cur_cmd'] == 'body':
            self.store_data()

        elif self.k['cur_cmd'] == 'conditional':
            self.k['cond_test'] = None

    def prefix_end(self, code):
        self.dprint('[pfx--end]', code)
        
        if code == 'assign_value':
            if self.k['to_target']:
                self.store_data()

            self.k['args'] = ()
            self.k['attr_idx'] = ()
            self.k['to_target'] = ()
            self.k['from_attr'] = ()
            self.dprint(f'[pfx--end] [{code}]', f'mem: {self.mem}')

        elif code == 'opt_assign':
            self.k['to_target'] = ()

        elif code == 'call':
            if self.k['prev_cmd'] == 'caller_args':
                pass

            elif self.k['prev_cmd'] == 'caller':
                pass

        elif code == 'assign_expr':
            self.k['attr_name'] = None
            self.k['attr_type'] = None
            self.k['attr_size'] = None

        elif code == 'attr_decl':
            self.k['attr_size'] = self.k['attr_size'] if self.k['attr_size'] else self.default_len[self.k['attr_type']]
            self.store_data()
            self.dprint(f'[pfx--end] [{code}]', f'mem: {self.mem}')

        elif code == 'loop':
            _loop = self.k['loop_range']
            _loop_vals = tuple(range(_loop[0], _loop[1]))

            if self.k['prev_cmd'] == 'opt_assign':
                self.k['attr_idx'] += _loop_vals
                self.k['from_attr'] += self.read_data(data=_loop_vals)

            elif self.k['prev_cmd'] == 'assign_value':
                self.k['to_target'] += _loop_vals

            self.k['loop_range'] = ()
            self.k['loop_flag'] = False
            self.k['loop_pos'] = ()

        elif code == 'conditional':
            self.k['cond_test'] = None
            
        elif code == 'cond_test':
            if self.k['cond_test']:
                pass

            else:
                pass

        elif code == 'main':
            self.dprint('[pfx--end] [main]', f'mem={self.mem}')

        self.k['cur_cmd'] = self.k['prev_cmd']

    # MAIN HANDLERS

    def tuple_handler(self, code):
        for p in code:
            self.main_handlers[type(p)](p)

    def str_handler(self, code):
        self.dprint(f'[str]', f'code={code}', f'k={self.k}')
        prefix, suffix = self.split_str_code(code)
        self.block_prefix[prefix](suffix)

    def eval_exec(self, code):
        self.main_handlers[type(code)](code)

    def run(self, code):
        print('Running H-hat code:\n')
        t0 = time.process_time()
        self.eval_exec(code)
        tf = time.process_time()
        print(f'\nDone. Processed in {round(tf-t0,6)}s.')


class Code:
    """
    Execution the code from text to evaluation/interpreting code
    """

    def __init__(self, code, debug=False):
        self.code = code
        self.debug = debug
        self.lex_code = None
        self.parse_code = None
        self.ir_code = None

    def lex(self):
        """
        Provides the tokens sequence for the given code.

        Returns
        -------
        iterable containing the tokens
        """
        self.lex_code = lexer.lex(self.code)

        return deepcopy(self.lex_code)

    def parse(self):
        """
        Parse the data, structuring the tokens into data.

        Returns
        -------
        tuple of dictionaries, tuples and tokens
        """
        lex_code = deepcopy(self.lex_code)
        parse_code = parser.parse(lex_code)
        self.parse_code = parse_code.value

        return self.parse_code

    def eval(self):
        """
        Evaluate the intermediate representation code
        and execute the code
        """
        ev = Eval(debug=self.debug)
        ev.run(self.parse_code)
        del ev.mem

    def run(self):
        """
        Bundle function to run all the previous functions
        """
        self.lex()
        self.parse()
        self.eval()


if __name__ == '__main__':
    c = "main null C: (int res: (:add(1 1), :print))"
    code_exec = Code(c)
    code_exec.run()
    c2 = """
        main null C: (
            int a = (:2, :add(1 4), :print) 
            int b(3) = (:a,
                        0:print, 
                        (0 1):add(-6),
                        (0 2):print('before='),
                        :print('final='))
            int c(5) = (0:b(1), 
                        :print('c with b(1)='), 
                        1..4:b(2), 
                        :print('c with b(2) in 1..4='),
                        (2 3):b(0 1),
                        :print('c with b(0 1) in (2 3)='),
                        0..3:12..15,
                        :print('c range 12..15 in 0..3='))
        )
    """
    code_exec2 = Code(c2)
    code_exec2.run()
