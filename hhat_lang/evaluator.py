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
from copy import deepcopy
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
                                       #'MEASURE': '@return',  # self.format_qtype,
                                       'STAR': 'indices'}
        self.token_other_handlers = {'TYPE': 'type',
                                     'GATE': self.format_qtype,
                                     'NULL': 'indices'}

    def dprint(self, *msg, **msgs):
        if self.debug:
            print('* [pre_eval:debug]=', *msg, **msgs)

    @staticmethod
    def format_qtype(text):
        return 'builtin:q_' + text[1:]

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
                start_scope = ''
                for v0, v in enumerate(k):
                    if v0 == 0:
                        start_scope = v
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
                tmp_code += (f'end:{start_scope}',)
                self.dprint(
                    f'[dict] scope={scope} | tmp_scope={tmp_scope} | scope_name={scope_name} | tmp_name={tmp_name}')
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
        # TODO: will need to change this token_v approach when including circuits and etc
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
        print(f'- Finished in {round(tf - t0, 7)}s.')
        print()
        if show_mem:
            print(f'## Code Organization ##')
            print()
            pprint.pprint(res_mem)
            print('-' * 80)
            print()
        if show_code:
            print(f'## Code Pre-Evaluated ##')
            print()
            pprint.pprint(res_code)
            print('-' * 80)
            print()
        print('End.')
        print()


def builtin_add(vals):
    _types = [type(k) for k in vals]
    if set(_types).issubset({int, float}):
        return sum(vals),
    elif set(_types).issubset({str}):
        return ''.join(vals),
    else:
        return vals,


def builtin_print(vals):
    print(*vals)
    return ()


class Eval:
    # TODO: improve code clarity and readability
    def __init__(self, code, debug=False):
        self.debug = debug
        self.print_debug_flag = False
        self.code = code
        self.mem = {'main': {}, 'function': code['scope']['function'], 'current': {}}
        self.eval_handlers = {dict: self.dict_handler,
                              tuple: self.tuple_handler,
                              str: self.str_handler}
        self.preffix_handlers = {'code': self.preffix_code,
                                 'symbol': self.preffix_symbol,
                                 'type': self.preffix_type,
                                 'indices': self.preffix_indices,
                                 'builtin': self.preffix_builtin,
                                 'end': self.preffix_end}
        self.preffix_types = {'int': self.type_int,
                              'str': self.type_str,
                              'float': self.type_float}
        self.suffix_types = {'int': (int, 1, 0),
                             'str': (str, 1, ''),
                             'float': (float, 1, 0.0),
                             'null': (None, 0, None),
                             'list': (list, None, None)}
        self.builtin_handlers = {'add': builtin_add,
                                 'print': builtin_print}
        self.suffix_handlers = {'params': self.suffix_params,
                                'body': self.suffix_body,
                                'attr_decl': self.suffix_attr_decl,
                                'assign_expr': self.suffix_assign_expr,
                                'opt_assign': self.suffix_opt_assign,
                                'call': self.suffix_call,
                                'size_decl': self.suffix_size_decl,
                                'caller_args': self.suffix_caller_args,
                                'caller': self.suffix_caller,
                                'return': self.suffix_return}

    def dprint(self, *msg, **msgs):
        if self.debug:
            if self.print_debug_flag:
                print(*msg, **msgs)
            else:
                print('* [eval:debug]', *msg, **msgs)
            if 'end' in msgs.keys():
                self.print_debug_flag = True
            else:
                self.print_debug_flag = False

    @staticmethod
    def str_vals(attr):
        _idx = attr.index(':')
        return attr[:_idx], attr[_idx + 1:]

    @staticmethod
    def check_value_type(values):
        res = [type(k) for k in values]
        if len(res) > 1:
            return list
        return tuple(set(res))[0] if res else None

    def create_mem_slot(self, kwargs):
        self.dprint(f'[create mem slot] kwargs={kwargs}')
        _mem = self.mem['current'].get(kwargs['scope'], False)
        if _mem:
            _mem1 = _mem.get(kwargs['attr_name'], False)
            if not _mem1:
                self.mem['current'][kwargs['scope']][
                    kwargs['attr_name']] = {'data': {}, 'type': None, 'size': 0}
        else:
            self.mem['current'] = {kwargs['scope']:
                                       {kwargs['attr_name']:
                                            {'data': {}, 'type': None, 'size': 0}}}
        self.dprint(
            f'[create mem slot](mem check) attr={kwargs["attr_name"]} | data={self.mem["current"][kwargs["scope"]][kwargs["attr_name"]]}')

    def type_int(self, code, kwargs):
        res = ast.literal_eval(code)
        self.dprint(f'[type int](start) code={code} | kwargs={kwargs}')
        if kwargs['cur_attr'] == 'call':
            if kwargs['prev_attr'] == 'size_decl':
                self.mem['current'][kwargs['scope']][kwargs['attr_name']]['size'] = res
            elif kwargs['prev_attr'] == 'opt_assign':
                if self.mem['current'][kwargs['scope']][kwargs['attr_name']]['type'] in [int, list]:
                    if kwargs['attr_pos']:
                        for k in kwargs['attr_pos']:
                            self.mem['current'][kwargs['scope']][kwargs['attr_name']]['data'][
                                k] = res
                    else:
                        self.mem['current'][kwargs['scope']][kwargs['attr_name']]['data'][0] = res
                else:
                    raise ValueError("Attribute not of type 'int'.")
            else:
                if self.mem['current'][kwargs['scope']][kwargs['attr_name']]['type'] in [int, list]:
                    if kwargs['attr_pos']:
                        _vals = self.mem['current'][kwargs['scope']][kwargs['attr_name']][
                            'data'].keys()
                        for k1, k2 in zip(_vals, kwargs['attr_pos']):
                            self.mem['current'][kwargs['scope']][kwargs['attr_name']]['data'][
                                k1] = k2
                    else:
                        self.mem['current'][kwargs['scope']][kwargs['attr_name']]['data'][0] = res
                else:
                    raise ValueError("Attribute not of type 'int'.")
        elif kwargs['cur_attr'] in ['caller', 'caller_args']:
            kwargs['indices'] += (res,)
        elif kwargs['cur_attr'] == 'opt_assign':
            kwargs['attr_pos'] += (res,)
        self.dprint(f'[type int](end) code={code} | kwargs={kwargs}')
        return kwargs

    def type_float(self, code, kwargs):
        res = ast.literal_eval(code)
        if kwargs['cur_attr'] == 'call':
            if self.mem['current'][kwargs['scope']][kwargs['attr_name']]['type'] in [float, list]:
                self.mem['current'][kwargs['scope']][kwargs['attr_name']]['data'][0] = res
            else:
                raise ValueError("Attribute not of type 'float'.")
        elif kwargs['cur_attr'] == 'caller_args':
            kwargs['indices'] += (res,)
        return kwargs

    def type_str(self, code, kwargs):
        res = ast.literal_eval(code)
        if kwargs['cur_attr'] == 'call':
            if self.mem['current'][kwargs['scope']][kwargs['attr_name']]['type'] in [str, list]:
                self.mem['current'][kwargs['scope']][kwargs['attr_name']]['data'][0] += res
            else:
                raise ValueError("Attribute not of type 'str'.")
        elif kwargs['cur_attr'] in ['caller', 'caller_args']:
            kwargs['indices'] += (res,)
        return kwargs

    def suffix_params(self, code, kwargs):
        return kwargs

    def suffix_body(self, code, kwargs):
        kwargs['cur_attr'] = code
        type_val, type_size, _ = self.suffix_types[kwargs['attr_type']]
        self.mem['current'][kwargs['scope']] = {'data': {},
                                                'type': type_val,
                                                'size': type_size}
        kwargs['attr_type'] = None
        kwargs['attr_name'] = None
        return kwargs

    def suffix_attr_decl(self, code, kwargs):
        kwargs['prev_attr'] = kwargs['cur_attr']
        kwargs['cur_attr'] = code
        return kwargs

    def suffix_assign_expr(self, code, kwargs):
        size = self.mem['current'][kwargs['scope']][kwargs['attr_name']]['size']
        default_value = self.suffix_types[kwargs['attr_type']][2]
        self.mem['current'][kwargs['scope']][kwargs['attr_name']]['data'] = {k: default_value for k
                                                                             in range(size)}
        kwargs['prev_attr'] = kwargs['cur_attr']
        kwargs['cur_attr'] = code
        return kwargs

    def suffix_opt_assign(self, code, kwargs):
        kwargs['prev_attr'] = kwargs['cur_attr']
        kwargs['cur_attr'] = code
        return kwargs

    def suffix_call(self, code, kwargs):
        kwargs['prev_attr'] = kwargs['cur_attr']
        kwargs['cur_attr'] = code
        return kwargs

    def suffix_size_decl(self, code, kwargs):
        kwargs['prev_attr'] = kwargs['cur_attr']
        kwargs['cur_attr'] = code
        return kwargs

    def suffix_caller_args(self, code, kwargs):
        kwargs['prev_attr'] = kwargs['cur_attr']
        kwargs['cur_attr'] = code
        if kwargs['prev_attr'] == kwargs['cur_attr']:
            kwargs['assign_flag'] = True
            kwargs['tmp_indices'] = kwargs['indices']
            kwargs['indices'] = ()
        else:
            kwargs['assign_flag'] = False
            kwargs['tmp_indices'] = ()
        return kwargs

    def suffix_caller(self, code, kwargs):
        kwargs['prev_attr'] = kwargs['cur_attr']
        kwargs['cur_attr'] = code
        return kwargs

    def suffix_return(self, code, kwargs):
        kwargs['return_flag'] = True
        return kwargs

    def preffix_code(self, code, kwargs):
        _vals = self.suffix_handlers[code]
        return _vals(code, kwargs)

    def preffix_symbol(self, code, kwargs):
        self.dprint(f'[pffx sym](start) code={code} | kwargs={kwargs}')
        if kwargs['scope'] is None:
            kwargs['scope'] = code
        if kwargs['cur_attr'] == 'attr_decl':
            kwargs['attr_name'] = code
            self.create_mem_slot(kwargs)
        elif kwargs['cur_attr'] == 'call':
            if kwargs['prev_attr'] == 'size_decl':
                if self.mem['current'][kwargs['scope']][code]['type'] == int:
                    self.mem['current'][kwargs['scope']][kwargs['attr_name']]['size'] = \
                        self.mem['current'][kwargs['scope']][code]['data'][0]
            try:
                res = self.mem['current'][kwargs['scope']][code]['data']
                for k, v in res.items():
                    kwargs['indices'] += (v,)
            except Exception:
                # TODO: implement function control flow
                try:
                    res = self.mem['function'][code]['data']
                except Exception:
                    raise AttributeError(f"Attribute '{code}' not found.")
        elif kwargs['cur_attr'] == 'opt_assign':
            try:
                res = self.mem['current'][kwargs['scope']][code]['data']
                for k, v in res.items():
                    kwargs['attr_pos'] += (v,)
            except Exception:
                # TODO: implement function control flow
                raise AttributeError(f"Attribute '{code}' not found.")
        elif kwargs['cur_attr'] == 'caller':
            raise NotImplemented("Caller for symbol not implemented yet.")
        elif kwargs['cur_attr'] == 'caller_args':
            has_scope = self.mem['current'].get(kwargs['scope'], False)
            if has_scope:
                has_attr_mem = self.mem['current'][kwargs['scope']].get(code, False)
                if has_attr_mem:
                    for k, v in self.mem['current'][kwargs['scope']][code]['data'].items():
                        kwargs['indices'] += (v,)
        self.dprint(f'[pffx sym](end) kwargs={kwargs}')
        return kwargs

    def preffix_type(self, code, kwargs):
        kwargs['attr_type'] = code
        if kwargs['cur_attr'] == 'attr_decl':
            # kwargs['attr_type'] = code
            self.create_mem_slot(kwargs)
            val_type, type_size, default_value = self.suffix_types[code]
            self.mem['current'][kwargs['scope']][kwargs['attr_name']]['type'] = val_type
            if type_size is not None:
                self.mem['current'][kwargs['scope']][kwargs['attr_name']]['size'] = type_size
        return kwargs

    def preffix_indices(self, code, kwargs):
        self.dprint(f'[pffx indices] >> called | code={code}', end=' ')
        if code in ['all', 'self']:
            _vals = self.mem['current'][kwargs['scope']][kwargs['attr_name']]['data']
            self.dprint(f'| got vals={_vals}')
            for k, v in _vals.items():
                kwargs['attr_pos'] += (k,)
        return kwargs

    def preffix_builtin(self, code, kwargs):
        self.dprint(f'[{code.upper()}] = ', end='')
        btn_hdlr = self.builtin_handlers.get(code, False)
        if btn_hdlr:
            if kwargs['cur_attr'] in ['call', 'caller']:
                if kwargs['prev_attr'] == 'caller_args' and not kwargs['assign_flag']:
                    self.dprint(f'[pffx btn](caller_args) tmp_indices={kwargs["tmp_indices"]}')
                    kwargs['indices'] = kwargs['tmp_indices'] + kwargs['indices']
                    kwargs['tmp_indices'] = ()
                    kwargs['assign_flag'] = False
                params = kwargs['indices']
                if kwargs['attr_name']:
                    _vals = self.mem['current'][kwargs['scope']][kwargs['attr_name']]['data']
                    for k, v in _vals.items():
                        if k in kwargs['attr_pos']:
                            params += (v,)
                self.dprint(f'[pffx btn]({code}) PARAMS={params}')
                res = btn_hdlr(params)
                self.dprint(f'[pffx btn]({code}) res={res}')
                if res:
                    if kwargs['attr_name']:
                        for k1, k2 in zip(res, kwargs['attr_pos']):
                            self.mem['current'][kwargs['scope']][kwargs['attr_name']]['data'][
                                k2] = k1
                    else:
                        kwargs['indices'] = res
                else:
                    kwargs['indices'] = res
        return kwargs

    def preffix_end(self, code, kwargs):
        self.dprint('[pffx end]', end=' ')
        if not kwargs['return_flag']:
            if code == 'opt_assign':
                kwargs['attr_pos'] = ()
                kwargs['indices'] = ()
            elif code == 'attr_decl':
                kwargs['attr_name'] = None
                kwargs['attr_type'] = None
                kwargs['attr_pos'] = ()
                kwargs['tmp_indices'] += kwargs['indices']
                kwargs['indices'] = ()
            elif code == 'caller_args':
                kwargs['assign_flag'] = False
                kwargs['indices'] = kwargs['tmp_indices'] + kwargs['indices']
                kwargs['tmp_indices'] = ()
            kwargs['cur_attr'] = code
        else:
            if code == 'symbol':
                type_scope = self.mem['current'][kwargs['scope']]['type']
                type_value = self.check_value_type(kwargs['indices'])
                if type_scope == type_value:
                    for k0, k in enumerate(kwargs['indices']):
                        self.mem['current'][kwargs['scope']]['data'][k0] = k
                    # self.mem['current'][kwargs['scope']]['data'] = kwargs['indices']
                    self.mem['current'][kwargs['scope']]['size'] = len(kwargs['indices'])
                else:
                    raise ValueError(
                        f"Value(s) {kwargs['indices']} with type '{type_value}' different from scope's '{type_scope}'.")
        self.dprint('>> called')
        return kwargs

    def dict_handler(self, code, kwargs):
        res = code.get('scope', False)
        if res:
            res = res.get('main', False)
            if res:
                return self.eval_exec(res, kwargs)
        return {}

    def tuple_handler(self, code, kwargs):
        self.dprint(f'[tuple hndlr](start) kwargs={kwargs}')
        old_kwargs = kwargs
        for k in code:
            kwargs = self.eval_exec(k, kwargs)
            self.dprint(f'[tuple iter]({k}) kwargs={kwargs}')
        self.dprint(f'[tuple hndlr](end) kwargs={old_kwargs}')
        return old_kwargs

    def str_handler(self, code, kwargs):
        self.dprint(f'[str hndlr](start) code={code} | kwargs={kwargs}')
        code_vals = self.str_vals(code)
        self.dprint(f'[str hndlr] code_vals={code_vals}')
        _pfx_code = self.preffix_handlers.get(code_vals[0], False)
        if _pfx_code:
            kwargs = _pfx_code(code_vals[1], kwargs)
        else:
            _pfx_code = self.preffix_types.get(code_vals[0], False)
            if _pfx_code:
                kwargs = _pfx_code(code_vals[1], kwargs)
        self.dprint(f'[str hndlr](end) kwargs={kwargs}')
        return kwargs

    def eval_exec(self, code, kwargs=None):
        if kwargs is None:
            kwargs = {'scope': None,
                      'attr_name': None,
                      'attr_type': None,
                      'return_flag': False,
                      'attr_pos': (),
                      'cur_attr': None,
                      'prev_attr': None,
                      'assign_flag': False,
                      'tmp_indices': (),
                      'indices': ()}
        _val = self.eval_handlers[type(code)]
        return _val(code, kwargs)

    def eval_run(self, code):
        print('-Running H-hat code:\n')
        t_0 = time.process_time()
        self.eval_exec(code)
        t_f = time.process_time()
        print(f'\n- Finished.\n- Done in {round(t_f - t_0, 6)}s')


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
