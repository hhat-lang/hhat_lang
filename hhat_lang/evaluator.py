"""
Perform a pre-evaluation and evaluation on the parsed code
"""

try:
    from lexer import lexer
    from parser import parser
    from tokens import tokens
except ImportError:
    from hhat_lang.lexer import lexer
    from hhat_lang.parser import parser
    from hhat_lang.tokens import tokens
import ast
from copy import deepcopy


def btin_print(vals):
    args, attr = vals
    print(*args, *attr)
    return None

def btin_add(vals):
    args, attr = vals
    _num_types = set([type(k) for k in args])
    _total = ()
    if len(_num_types) == 1:
        if _num_types.issubset({int, float, str, tuple, list}):
            _res = 0 if _num_types.issubset({int, float}) else '' if _num_types.issubset({str}) else ()
            for k in args:
                _res += k
            for k in attr:
                _total += (k + _res,)
        else:
            _total = None
    else:
        _res = ()
        for k in vals:
            _res += (k,)
        for k in attr:
            _total += (_res,)
    return _total


class Eval:
    def __init__(self, debug=False):
        self.debug = debug
        self.mem = {'cur': {}}
        self.kws = self.start_kwargs()
        self.main_handlers = {tuple: self.tuple_handler, str: self.str_handler}
        self.block_prefix = {'scope': self.prefix_scope,
                             'symbol': self.prefix_symbol,
                             'qsymbol': self.prefix_qsymbol,
                             'type': self.prefix_type,
                             'int': self.prefix_int,
                             'float': self.prefix_float,
                             'str': self.prefix_str,
                             'indices': self.prefix_indices,
                             'builtin': self.prefix_builtin,
                             'loop': self.prefix_loop,
                             'code': self.prefix_code,
                             'end': self.prefix_end}
        self.default_len = {'int': 1, 'str': 1, 'float': 1, 'null': 0, 'circuit': 1, 'measurement': 1, 'hashmap': 1, 'bool': 1}
        self.default_val = {'int': 0,
                            'str': '',
                            'float': 0.0,
                            'null': None,
                            'circuit': None,
                            'measurement': {},
                            'hashmap': {},
                            'bool': None}
        self.builtin_funcs = {'print': btin_print, 'add': btin_add}

    def dprint(self, origin, *msg, **msgs):
        if self.debug:
            print(f'* [debug:eval]: [{origin}]:')
            for k in msg:
                print(f'   ----> {k}', **msgs)
            if 'end' not in msgs.keys():
                print()

    @staticmethod
    def start_kwargs():
        return {'scope': None,
                'attr_name': None,
                'attr_type': None,
                'attr_size': None,
                'idx_or_val': None,
                'prev_cmd': None,
                'cur_cmd': None,
                'return_flag': False,
                'loop_pos': None,
                'loop_range': (),
                'args': (),
                'tmp_args': (),
                'attr_idx': (),
                'from_attr': (),
                'to_attr': (),
                'attr_data': ()}

    def scope_handler(self, old_kws):
        # print(f'scope={old_kws["cur_cmd"]}')
        if old_kws['cur_cmd'] in ['caller_args', 'assign_value', 'caller', 'call', 'opt_assign', 'loop', 'assign_expr']:
            old_kws['to_attr'] = self.kws['to_attr']
            old_kws['from_attr'] = self.kws['from_attr']
            old_kws['args'] = self.kws['args']
            old_kws['attr_idx'] = self.kws['attr_idx']
            old_kws['loop_range'] = self.kws['loop_range']
            old_kws['loop_pos'] = self.kws['loop_pos']
            # old_kws['prev_cmd'] = self.kws['prev_cmd']
            # old_kws['cur_cmd'] = self.kws['cur_cmd']
        return old_kws

    @staticmethod
    def split_str_code(code):
        _idx = code.index(':')
        return code[:_idx], code[_idx+1:]

    # MEMORY FUNCS

    def store_data(self):
        if self.kws['attr_name']:
            _mem_data = self.mem['cur'][self.kws['scope']][self.kws['attr_name']]['data']
            _attr_indx = self.kws['attr_idx']
            data = self.kws['to_attr']
            # print(f'* * [store data] data={data} | attr idx={_attr_indx}')
            #if self.kws['idx_or_val'] == 'val':
            if len(data) == len(_attr_indx):
                # print('store okay!')
                for k, d in zip(_attr_indx, data):
                    _mem_data[k] = d
            else:
                if len(data) == 1:
                    # print('one to many')
                    for p in data:
                        for k in _attr_indx:
                            _mem_data[k] = p
            if self.kws['idx_or_val'] == 'idx':
                raise NotImplemented("Idx for Store Data not implemented yet.")


    # PREFIX TYPES

    def prefix_int(self, code):
        literal_code = ast.literal_eval(code)
        if self.kws['cur_cmd'] == 'size_decl':
            self.kws['attr_size'] = literal_code
        elif self.kws['cur_cmd'] == 'call':
            if self.kws['prev_cmd'] == 'opt_assign':
                # self.kws['to_attr'] += (literal_code,)
                self.kws['attr_idx'] += (literal_code,)
            elif self.kws['prev_cmd'] == 'caller_args':
                self.kws['args'] += (literal_code,)
            elif self.kws['prev_cmd'] == 'assign_value':
                self.kws['to_attr'] += (literal_code,)
        elif self.kws['cur_cmd'] == 'loop':
            # print('int loop?')
            if self.kws['prev_cmd'] in ['opt_assign', 'assign_value', 'assign_expr']:
                if self.kws['loop_pos'] == 'loop_start':
                    self.kws['loop_range'] += (literal_code,)
                elif self.kws['loop_pos'] == 'loop_end':
                    self.kws['loop_range'] += (literal_code,)
                else:
                    raise NotImplemented("Other loop option not implemented yet.")
        elif self.kws['cur_cmd'] == 'opt_assign':
            # print('here', literal_code)
            # print('int opt')
            self.kws['attr_idx'] += (literal_code,)
        elif self.kws['cur_cmd'] == 'assign_value':
            # print('int assign val')
            self.kws['to_attr'] += (literal_code,)
        # print(f'prev_cmd={self.kws["prev_cmd"]} | cur_cmd={self.kws["cur_cmd"]}')
        # print(self.kws)


    def prefix_float(self, code):
        pass

    def prefix_str(self, code):
        literal_code = ast.literal_eval(code)
        if self.kws['cur_cmd'] == 'call':
            if self.kws['prev_cmd'] == 'caller_args':
                self.kws['args'] += (literal_code,)

    # PREFIX FUNCS

    def prefix_scope(self, code):
        self.kws['cur_cmd'] = code

    def prefix_symbol(self, code):
        # print(f'got symbol? {code}')
        if self.kws['cur_cmd'] == 'main':
            self.kws['scope'] = code
        elif self.kws['cur_cmd'] == 'attr_decl':
            self.kws['attr_name'] = code
        elif self.kws['cur_cmd'] == 'call':
            if self.kws['prev_cmd'] == 'assign_value':
                self.kws['to_attr'] += tuple(k for k in self.mem['cur'][self.kws['scope']][code]['data'].values())
            else:
                self.kws['args'] += tuple(k for k in self.mem['cur'][self.kws['scope']][code]['data'].values())
        elif self.kws['cur_cmd'] == 'caller':
            # print(f'symb caller: {code} | prev={self.kws["prev_cmd"]}')
            if self.kws['prev_cmd'] == 'call':
                # print(f'sym caller {code} + (caller_args)? args={self.kws["args"]}')
                self.kws['to_attr'] += tuple(v for k, v in self.mem['cur'][self.kws['scope']][code]['data'].items() if k in self.kws['args'])
                # print(self.kws['to_attr'])
            elif self.kws['prev_cmd'] == 'caller_args':
                # print('sym caller + caller_args')
                self.kws['to_attr'] += tuple(v for k, v in self.mem['cur'][self.kws['scope']][code]['data'].items() if k in self.kws['args'])

    def prefix_qsymbol(self, code):
        self.prefix_symbol(code)

    def prefix_type(self, code):
        if self.kws['cur_cmd'] != 'main':
            self.kws['attr_type'] = code

    def prefix_indices(self, code):
        _data = self.mem['cur'][self.kws['scope']][self.kws['attr_name']]['data']
        if code == 'all':
            self.dprint(f'[pfx-idx]', f'code={code}', f'data={_data}')
            self.kws['attr_idx'] = tuple(_data.keys())
        elif code == 'self':
            self.kws['attr_idx'] = tuple(_data.keys())
            self.kws['idx_or_val'] = 'idx'

    def prefix_builtin(self, code):
        _data = self.mem['cur'][self.kws['scope']][self.kws['attr_name']]['data']
        _attr_idx = tuple(v for k, v in _data.items() if k in self.kws['attr_idx'])
        _vals = (self.kws['args'] + self.kws['from_attr'], _attr_idx)
        # print(f'builtin vals! ={_vals}')
        _res = self.builtin_funcs[code](_vals)
        if self.kws['idx_or_val'] == 'idx':
            raise NotImplemented("Builtin result in Index not implemented yet.")
        #elif self.kws['idx_or_val'] == 'val':
        else:
            # print(f'builtin? {code} | res={_res}')
            if _res:
                self.kws['to_attr'] = _res

    def prefix_loop(self, code):
        # print(f'loop {code}')
        self.kws['loop_pos'] = code

    def prefix_code(self, code):
        # print(f'current codes: prev={self.kws["prev_cmd"]} | cur={self.kws["cur_cmd"]}')
        if code == 'loop':
            # print('is loop?')
            if self.kws['prev_cmd'] in ['opt_assign', 'assign_value']:
                # print('prev opt or assign val')
                self.kws['cur_cmd'] = code
            elif self.kws['cur_cmd'] in ['opt_assign', 'assign_value']:
                # print('cur opt or assign val')
                self.kws['cur_cmd'] = code
        else:
            self.kws['prev_cmd'] = self.kws['cur_cmd']
            self.kws['cur_cmd'] = code
        # print(f'changed codes: prev={self.kws["prev_cmd"]} | cur={self.kws["cur_cmd"]}')
        if self.kws['prev_cmd'] == 'opt_assign':
            if self.kws['cur_cmd'] == 'call':
                self.kws['idx_or_val'] = 'val'
        if self.kws['cur_cmd'] == 'body':
            self.mem['cur'].update({self.kws['scope']: {}})

    def prefix_end(self, code):
        # print(f'=> code={code} | kws={self.kws}')
        # print(f'* * [mem]={self.mem["cur"]}')
        if self.kws['cur_cmd'] == 'attr_decl':
            _len = self.kws['attr_size'] if self.kws['attr_size'] else self.default_len[self.kws['attr_type']]
            self.mem['cur'][self.kws['scope']].update(
                {self.kws['attr_name']:
                     {'data': {k: self.default_val[self.kws['attr_type']] for k in range(_len)},
                      'type': self.kws['attr_type'],
                      'len': _len}})
        elif self.kws['cur_cmd'] == 'assign_value':
            self.store_data()
            self.kws['args'] = ()
            self.kws['tmp_args'] = ()
            self.kws['attr_data'] = ()
            self.kws['from_attr'] = ()
            self.kws['to_attr'] = ()
            self.kws['attr_idx'] = ()
            self.kws['loop_range'] = ()
        elif self.kws['cur_cmd'] == 'assign_expr':
            self.kws['attr_name'] = None
            self.kws['attr_type'] = None
            self.kws['attr_size'] = None
            self.kws['idx_or_val'] = None
            self.kws['loop_pos'] = None
            self.kws['args'] = ()
            self.kws['tmp_args'] = ()
            self.kws['attr_data'] = ()
            self.kws['from_attr'] = ()
            self.kws['to_attr'] = ()
            self.kws['attr_idx'] = ()
            self.kws['loop_range'] = ()
        elif self.kws['cur_cmd'] == 'loop':
            _start, _end = self.kws['loop_range']
            # print('loop?')
            if self.kws['prev_cmd'] == 'opt_assign':
                # print(f'loop + opt={_start, _end}')
                self.kws['attr_idx'] += tuple(k for k in range(_start, _end))
            elif self.kws['prev_cmd'] == 'assign_value':
                # print(f'loop + assign val={_start, _end}')
                self.kws['to_attr'] += tuple(k for k in range(_start, _end))
            elif self.kws['prev_cmd'] == 'assign_expr':
                # print(f'loop + assign expr={_start, _end}')
                self.kws['to_attr'] += tuple(k for k in range(_start, _end))
                # print(self.kws['to_attr'])
            self.kws['loop_pos'] = None
            self.kws['loop_range'] = ()
        elif self.kws['cur_cmd'] == 'main':
            self.kws = self.start_kwargs()
        # ... continue conditional execution above until the very end.
        # these last lines below must be the last ones.
        if self.kws['cur_cmd'] == 'call' and self.kws['prev_cmd'] == 'caller_args':
            self.kws['cur_cmd'] = 'caller_args'
        # if code == 'assign_expr':
        #     self.kws['cur_cmd'] = self.kws['prev_cmd']
        #     self.kws['prev_cmd'] = None
        else:
            self.kws['cur_cmd'] = self.kws['prev_cmd']
            self.kws['prev_cmd'] = None


    # MAIN HANDLERS

    def tuple_handler(self, code):
        self.dprint('[tuple]', f'kws={self.kws}')
        old_kws = deepcopy(self.kws)
        for k in code:
            self.dprint(f'[tuple] [iter]', f'kws={self.kws}', f'code={k}')
            self.main_handlers[type(k)](k)
        self.kws = deepcopy(self.scope_handler(old_kws))
        # print(f'-> kws={self.kws}')

    def str_handler(self, code):
        self.dprint(f'[str]', f'kws={self.kws}')
        prefix, suffix = self.split_str_code(code)
        # print(f'prev={self.kws["prev_cmd"]} | cur={self.kws["cur_cmd"]}')
        self.block_prefix[prefix](suffix)

    def eval_exec(self, code):
        self.main_handlers[type(code)](code)


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

    def pre_eval(self):
        """
        Pre-evaluate the parsed code.

        Returns
        -------
        tuples of strings
        """
        pre_code = PreEval(debug=self.debug)
        ir = pre_code.run(self.parse_code)
        self.ir_code = ir[0]
        return ir[1]

    def eval(self):
        """
        Evaluate the intermediate representation code
        and execute the code
        """
        ev = Eval(self.ir_code, debug=self.debug)
        ev.eval_run(self.ir_code)
        del ev.mem

    def run(self):
        """
        Bundle function to run all the previous functions
        """
        self.lex()
        self.parse()
        self.pre_eval()
        self.eval()


if __name__ == '__main__':
    c = "main null C: (int res: (:add(1 1), :print))"
    code_exec = Code(c)
    code_exec.run()
