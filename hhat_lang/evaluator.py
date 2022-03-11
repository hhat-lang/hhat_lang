"""
Perform a pre-evaluation and evaluation on the parsed code
"""

try:
    # import builtin as btin
    from lexer import lexer
    from parser import parser
    from memory import Memory
    import parse_keys as pk
    from tokens import tokens
except ImportError:
    from hhat_lang.lexer import lexer
    from hhat_lang.parser import parser
    # import hhat_lang.builtin as btin
    from hhat_lang.memory import Memory
    import hhat_lang.parse_keys as pk
    from hhat_lang.tokens import tokens
import time
import ast
import pprint
from typing import Union, Dict, Tuple, Optional
from rply.token import Token


BUILTIN_FUNCS = ['ADD', 'PRINT']


class PreEval:
    def __init__(self, debug=True):
        self.mem = {'scope': {'main': None, 'function': {}}}
        self.debug = debug
        self.pe_handlers = {dict: self.dict_handler,
                            tuple: self.tuple_handler,
                            Token: self.token_handler}
        self.token_literal_handlers = {'INT_LITERAL': 'int',
                                       'STRING_LITERAL': 'str',
                                       'FLOAT_LITERAL': 'float',
                                       'SYMBOL': 'symbol',
                                       'Q_SYMBOL': 'qsymbol',
                                       'P_SYMBOL': 'psymbol',
                                       'D_SYMBOL': 'dsymbol',
                                       'MEASURE': self.format_qtype,
                                       'STAR': 'indices'}
        self.token_other_handlers = {'TYPE': 'type',
                                     'GATE': self.format_qtype,
                                     'NULL': 'indices'}

    def dprint(self, *msg, **msgs):
        if self.debug:
            print('* [pre_eval:debug]=', *msg, **msgs)

    @staticmethod
    def format_qtype(text):
        return 'type:q_' + text[1:]

    @staticmethod
    def format_start():
        return 'indices:self'

    def dict_handler(self, code, scope=None, scope_name=None):
        self.dprint(f'>> dict called')
        tmp_code = ()
        tmp_scope = scope
        tmp_name = scope_name
        for k in pk.PROGRAM_LIST_EXPRS:
            if not set(code.keys()).symmetric_difference(set(k)):
                for v0, v in enumerate(k):
                    self.dprint(f'[dict] code={v} | value={code[v]} | tmp_scope={tmp_scope}')
                    tmp_scope = v if v in ['main', 'function'] else tmp_scope
                    res, tmp_scope, tmp_name = self.pre_eval_exec(code[v], tmp_scope, tmp_name)
                    if v not in ['symbol', 'type', 'main', 'function']:
                        tmp_code += (f'code:{v}', res)
                    elif v in ['main', 'function']:
                        tmp_code += (f'scope:{v}', res)
                        scope = v
                    else:
                        tmp_code += (res,)
                    tmp_scope = None
                tmp_code += ('end:',)
                self.dprint(f'[dict] scope={scope} | tmp_scope={tmp_scope} | scope_name={scope_name} | tmp_name={tmp_name}')
                if scope and tmp_name:
                    self.dprint(f'[dict] got scope={scope} | tmp_name={tmp_name}')
                    if scope == 'main':
                        mem_save = self.mem['scope'][scope] = tmp_code[1]
                    elif scope == 'function':
                        mem_save = self.mem['scope'][scope][tmp_name] = tmp_code[1]
        return tmp_code, tmp_scope, tmp_name

    def tuple_handler(self, code, scope=None, scope_name=None):
        self.dprint(f'>> tuple called')
        tmp_code = ()
        tmp_scope = scope
        tmp_name = scope_name
        for k in code:
            self.dprint(f'[tuple] iter code={k}')
            res, tmp_scope, tmp_name = self.pre_eval_exec(k, scope, scope_name)
            tmp_code += (res,)
        return tmp_code, tmp_scope, tmp_name

    def token_handler(self, code, scope=None, scope_name=None):
        self.dprint(f'>> token called')
        tmp_scope = scope
        tmp_name = scope_name
        token_t = code.gettokentype()
        # TODO: will need to change this token_v
        # approach when including circuits and etc
        token_v = f'{code.value}'
        if token_t.endswith('SYMBOL') and tmp_scope in ['function', 'main']:
            self.dprint(f'[token](tmp_name) symbol={token_v}')
            tmp_name = token_v
        _token_res = self.token_literal_handlers.get(token_t, False)
        if not _token_res:
            for k in self.token_other_handlers.keys():
                if token_t.endswith(k):
                    _token_res = self.token_other_handlers[k]
                    if isinstance(_token_res, str):
                        return ':'.join([_token_res, token_v]), tmp_scope, tmp_name
                    else:
                        return _token_res(token_v), tmp_scope, tmp_name
        if token_t in BUILTIN_FUNCS:
            return ':'.join(['builtin', token_v]), tmp_scope, tmp_name
        if isinstance(_token_res, str):
            return ':'.join([_token_res, token_v]), tmp_scope, tmp_name
        return _token_res(token_v), tmp_scope, tmp_name

    def pre_eval_exec(self, code, scope=None, scope_name=None):
        self.dprint(f'>> eval called')
        _val = self.pe_handlers[type(code)]
        res, tmp_scope, tmp_name = _val(code, scope, scope_name)
        tmp_code = res
        return tmp_code, tmp_scope, tmp_name

    def run(self, code):
        res = self.pre_eval_exec(code)
        return self.mem, res[0]

    def print_run(self, code, show_mem=True, show_code=False):
        print()
        print(f'###########')
        print(f'# PreEval #')
        print(f'###########')
        print()
        print('- Running pre-evaluation on code...')
        t0 = time.process_time()
        res_mem, res_code = self.run(code)
        tf = time.process_time()
        print(f'- Done.')
        print(f'- Finished in {round(tf-t0,7)}s.')
        print()
        if show_mem:
            print(f'## Code Organization ##')
            print()
            pprint.pprint(res_mem)
            print('-'*80)
            print()
        if show_code:
            print(f'## Code Pre-Evaluated ##')
            print()
            pprint.pprint(res_code)
            print('-'*80)
            print()
        print('End.')
        print()
        return show_mem



class Evalu:
    def __init__(self, do_debug=True):
        self.mem = Memory(do_debug)
        self.do_debug = do_debug
        self.all_builtins = {'add': self.builtin_add, 'print': self.builtin_print}
        self.convert_type_str = {'NULL_TYPE': None, 'STRING_TYPE': str, 'INTEGER_TYPE': int, 'FLOAT_TYPE': float, 'LIST_TYPE': list}
        self.revert_type_str = {v:k for k, v in self.convert_type_str.items()}

    def dprint(self, *msg, **msgs):
        if self.do_debug:
            print('=[debug]=', *msg, **msgs)

    def eprint(self, *msg, **msgs):
        print(*msg, **msgs)

    def create_attr_mem(self, mem_ref, size=None):
        if not self.mem.get(mem_ref):
            self.dprint(f'[create_attr_mem] mem has {mem_ref}? no, {self.mem.get(mem_ref)}')
            # create an empty object to mark the attribute as existing in the memory
            self.mem[mem_ref] = True
            if mem_ref[-1] in [int, float, None]:
                # where to place the actual data
                self.mem[(mem_ref[0], mem_ref[1], 0, mem_ref[3])]
                # properties of the attribute below
                self.mem[(mem_ref[0], mem_ref[1], 'size', int)] = 1  # if mem_ref[3] in [int, float] else 0
                self.mem[(mem_ref[0], mem_ref[1], 'type', str)] = self.revert_type_str[mem_ref[3]]
            elif mem_ref[-1] in [str, list]:
                if size is not None:
                    if size > 0:
                        [self.mem[(mem_ref[0], mem_ref[1], k, mem_ref[3])] for k in range(size)]
                        self.mem[(mem_ref[0], mem_ref[1], 'size', int)] = size
                        self.mem[(mem_ref[0], mem_ref[1], 'type', str)] = self.revert_type_str[mem_ref[3]]
                    else:
                        raise ValueError(f"No negative size. Reference to attribute {mem_ref}.")
                else:
                    raise ValueError(f"No size declared for the attribute {mem_ref}.")

    def builtin_add(self, mem_ref, values, pos_elem=None):
        if pos_elem is None:
            pos_elem = (mem_ref[2],)
        new_mem_ref = iter((mem_ref[0], mem_ref[1], k, mem_ref[3]) for k in pos_elem)
        self.dprint(f'[add] -- mem_ref={mem_ref} | values={values} | pos_elem={pos_elem}')
        for k in new_mem_ref:
            self.dprint(f'[add] mem_ref={k} | mem value={self.mem[k]}')
            values_types = [type(k) for k in values]
            svt = set(values_types)
            if len(svt) == 1:
                if int in svt or float in svt:
                    _ref = self.mem[k]
                    if isinstance(_ref, list):
                        if _ref:
                            self.mem[k] = _ref + [sum(values)]
                        else:
                            self.mem[k] = sum(values)
                    else:
                        self.mem[k] = _ref + sum(values)
                elif str in svt:
                    self.mem[k] = str(_ref) + ''.join(values)
                else:
                    raise TypeError("Wrong type for function.")
            else:
                self.mem[k] = _ref + list(values)

    def builtin_print(self, mem_ref, args, pos_elem=None):
        self.dprint(f'[print] invoked | args={args} | pos_elem={pos_elem}')
        if mem_ref[3] == list:
            preffix = '('
            suffix = ')'
        elif mem_ref[3] in [int, float]:
            preffix = ''
            suffix = ''
        elif mem_ref[3] == str:
            preffix = '"'
            suffix = '"'
        else:
            preffix = ''
            suffix = ''

        if args:
            res = args
            self.dprint('{SYSTEM OUTPUT} PRINT: ', end='')
            print(*[ast.literal_eval(k) if isinstance(k, str) else k for k in res], end=' ')

        if pos_elem is not None:
            print(preffix, end='')
            for k in pos_elem:
                res = self.mem[(mem_ref[0], mem_ref[1], k, mem_ref[3])]
                self.dprint('SYSTEM OUTPUT PRINT: ', end='')
                print(f'{res} ', end='')
            print(f'\b{suffix}', end='')
        else:
            if mem_ref[-1]:
                res = self.mem[mem_ref]
                self.dprint('{SYSTEM OUTPUT} PRINT: ', end='')
                print(f'{preffix}', end='')
                print(res, end='')
                print(f'{suffix}', end='')
        print()


    def tuple_code(self, code, code_attr, mem_ref, args, pos_elem=None):
        old_args = ()
        new_pos_elem = ()
        old_code_attr = code_attr
        if code_attr in ['assign_expr']:
            if mem_ref[-1]:
                new_args = None if not args else args[0]
            self.create_attr_mem(mem_ref, new_args)
        for k in code:
            self.dprint(f'[tuple] current code={k} | old_code_attr={old_code_attr} | code_attr={code_attr}')
            code_attr, mem_ref, args, pos_elem = self.eval_run(k, code_attr, mem_ref, args, pos_elem)
            if old_code_attr == 'caller_args':
                old_args += args
            elif old_code_attr == 'size_decl':
                old_args = args
            elif old_code_attr == 'opt_assign':
                self.dprint(f'[tuple code](loop) opt_assign={pos_elem}, args={args}')
                new_pos_elem += pos_elem
        if old_code_attr in ['caller_args', 'size_decl']:
            args = old_args
            self.dprint(f'[tuple code] mem_ref={mem_ref} | args={args} | pos_elem={pos_elem}')
            # define memory here?
            if mem_ref[-1]:
                new_args = None if not args else args[0]
                self.create_attr_mem(mem_ref, new_args)
        elif old_code_attr in ['opt_assign']:
            self.dprint(f'[tuple code] opt_assign={new_pos_elem}')
            pos_elem = new_pos_elem
        elif old_code_attr in ['call']:
            self.dprint(f'[tuple](old_code_attr=call) args={args} [to be vanished]')
            args = ()
        self.dprint(f'[tuple](old_code_attr) {old_code_attr}={args} | pos_elem={pos_elem}')
        return code_attr, mem_ref, args, pos_elem

    def str_code(self, code, code_attr=None, mem_ref=None, args=None, pos_elem=None):
        self.dprint(f'[str] pre-data: code_attr={code_attr} | mem_ref={mem_ref} | args={args} | pos_elem={pos_elem}')
        if ':' in code:
            _res = code.index(':')
            _attr = code[:_res]
            _value = code[_res+1:]
            if _attr == 'code':
                code_attr = _value
                if _value in ['main', 'function']:
                    mem_ref = (None, None, None, None)
                    args = ()
            elif _attr == 'type':
                mem_ref = (mem_ref[0], mem_ref[1], None, self.convert_type_str[_value])
            elif _attr == 'symbol':
                if code_attr == 'main' or code_attr == 'function':
                    mem_ref = (_value, None, None, None)
                elif code_attr == 'attr_decl':
                    mem_ref = (mem_ref[0], _value, None, mem_ref[2])
            elif _attr == 'builtin':
                self.all_builtins[_value](mem_ref, args, pos_elem)
            elif _attr == 'indices':
                if _value == 'all':
                    self.dprint(f'[str] got all?')
                    if mem_ref[3] is not None:
                        pos_elem = tuple(k for k in range(self.mem[(mem_ref[0], mem_ref[1], 'size', int)]))
                        self.dprint(f'[str] pos_elem={pos_elem}')
                else:
                    pass
            elif _attr == 'end':
                code_attr = _attr
            elif _attr == 'str':
                args = (_value,)
        self.dprint(f'[str] current data: code={code} | attr={code_attr} | mem_ref={mem_ref} | args={args} | pos_elem={pos_elem}')
        return code_attr, mem_ref, args, pos_elem

    def other_code(self, code, code_attr, mem_ref, args, pos_elem=None):
        if isinstance(code, (int, float)):
            if code_attr == 'opt_assign':
                return code_attr, mem_ref, args, (code,)
            return code_attr, mem_ref, (code,), pos_elem
        else:
            raise NotImplementedError("other_code not implemented yet.")

    def eval_run(self, code, code_attr=None, mem_ref=None, args=None, pos_elem=None):
        if mem_ref is None:
            mem_ref = (None, None, None, None)
        if isinstance(code, tuple):
            self.dprint('[eval] type tuple')
            new_code_attr, new_mem_ref, new_args, new_pos_elem = self.tuple_code(code, code_attr, mem_ref, args, pos_elem)
        elif isinstance(code, str):
            self.dprint('[eval] type str')
            new_code_attr, new_mem_ref, new_args, new_pos_elem = self.str_code(code, code_attr, mem_ref, args, pos_elem)
        else:
            self.dprint(f'[eval] type {type(code)}')
            new_code_attr, new_mem_ref, new_args, new_pos_elem = self.other_code(code, code_attr, mem_ref, args, pos_elem)
        return new_code_attr, new_mem_ref, new_args, new_pos_elem


    def eval_exec(self, code, show_memory=True):
        print('Executing code:\n')
        t0 = time.process_time()
        self.eval_run(code)
        tf = time.process_time()
        print(f'\nDone.\nExecuted in {round(tf-t0,9)}s')
        print()
        if show_memory:
            pprint.pprint(self.mem)


if __name__ == '__main__':
    c = "main null C: (int res: (:add(1 1), :print))"
    lc = lexer.lex(c)
    pc = parser.parse(lc)
    pe = PreEval(False)
    pcode = pe.print_run(pc.value)
    # elu = Evalu(False)
    # elu.eval_exec(pcode)
    # print(f'- builtin = {[k for k in dir(btin) if "__" not in k and k.startswith("builtin")]}')
