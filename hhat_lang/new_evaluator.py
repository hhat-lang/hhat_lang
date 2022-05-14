"""Evaluator"""

import time
import ast
from copy import deepcopy
from typing import Any
from rply.token import BaseBox, Token
from hhat_lang.tokens import tokens
from hhat_lang.lexer import lexer
from hhat_lang.parser import parser
from hhat_lang.symbolic import FST, Memory
from hhat_lang.new_ast import (Program, Function, FuncTemplate, ParamsSeq, AThing, Body,
                               AttrDecl, Expr, ManyExprs, Entity, AttrAssign, Call,
                               Func, IfStmt, ElifStmt, ElseStmt, Tests, ForLoop, ExitBody,
                               AttrHeader, TypeExpr, IndexAssign, Args, Caller)
from hhat_lang.builtin import (btin_print, btin_and, btin_or, btin_not, btin_eq, btin_neq,
                               btin_gt, btin_gte, btin_lt, btin_lte, btin_add, btin_mult,
                               btin_div, btin_pow, btin_sqrt, btin_q_h, btin_q_x, btin_q_z)

SAMPLE_CODE_2 = """
func null f: ( int b =(:4) ) 

func int sum (int x, int y) (
    return (add(x y))
)

main null X: (
    int a =(:3) 
    if (eq(a b)): (
        print('eq')
    ) 
    elif (gt(a b)): (
        print('gt')
    ) 
    else: (
        print('lt')
    )
)
"""


# noinspection PyArgumentList
class Eval:
    def __init__(self, debug=False):
        self.debug = debug
        self.mem = Memory()
        self.mem.restart()
        self.func_dict_order = ['type', 'params', 'body', 'return']
        self.tasks = {dict: self.exec_dict,
                      tuple: self.exec_tuple,
                      str: self.exec_str,
                      ParamsSeq: self.ast_paramsseq,
                      AThing: self.ast_athing,
                      Body: self.ast_body,
                      AttrDecl: self.ast_attrdecl,
                      AttrAssign: self.ast_attrassign,
                      Expr: self.ast_expr,
                      ManyExprs: self.ast_manyexprs,
                      Entity: self.ast_entity,
                      Call: self.ast_call,
                      Func: self.ast_func,
                      IfStmt: self.ast_ifstmt,
                      ElifStmt: self.ast_elifstmt,
                      ElseStmt: self.ast_elsestmt,
                      Tests: self.ast_tests,
                      ExitBody: self.ast_exitbody,
                      ForLoop: self.ast_forloop,
                      AttrHeader: self.ast_attrheader,
                      TypeExpr: self.ast_typeexpr,
                      IndexAssign: self.ast_indexassign,
                      Args: self.ast_args,
                      Caller: self.ast_caller,
                      Token: self.ast_token
                      }
        self.btin_funcs = {'print': btin_print,
                           'add': btin_add}

    # DEBUG PRINT

    def dp(self, scope, *msg, **msgs):
        if self.debug:
            print(f'* [{scope}]:', *msg, **msgs)

    # MAIN EXECUTER FUNCTIONS

    def exec_dict(self, code, stats):
        if stats['scope'] is None:
            # old_stats = deepcopy(stats)
            if 'main' in code.keys():
                stats['scope'] = 'main'
                stats = self.tasks[type(code['main'])](code['main'], stats)
            elif 'func' in code.keys():
                stats['scope'] = 'func'
                stats = self.tasks[type(code['func'])](code['func'], stats)
            else:
                if len(code.keys()) == 1:
                    print('??')

            # stats = old_stats
        elif stats['scope'] == 'main':
            if not stats['func']:
                stats['func'] = list(code.keys())[0]
                stats = self.tasks[type(code[stats['func']])](code[stats['func']], stats)
            else:
                if not set(self.func_dict_order).symmetric_difference(code.keys()):
                    self.dp('dict', 'executing inside function (main)')
                    for k in self.func_dict_order:
                        if k in code.keys():
                            self.dp('dict', f'code: key={k} | code={code[k]}')
                            stats['key'] = k
                            stats = self.tasks[type(code[k])](code[k], stats)

        elif stats['scope'] == 'func':
            if not stats['func']:
                stats['func'] = list(code.keys())[0]
                stats = self.tasks[type(code[stats['func']])](code[stats['func']], stats)
            if not set(self.func_dict_order).symmetric_difference(code.keys()):
                self.dp('dict', 'executing inside function (func)')
                for k in self.func_dict_order:
                    if k in code.keys():
                        stats['key'] = k
                        stats = self.tasks[type(code[k])](code[k], stats)

        return stats

    def exec_tuple(self, code, stats):
        # old_stats = deepcopy(stats)
        for k in code:
            self.dp('tuple', f'code: key/code={k}')
            if stats['skip'] == 0:
                stats = self.tasks[type(k)](k, stats)
                if stats['skip'] > 0:
                    stats['skip'] -= 1
                    break
        # stats = old_stats
        return stats

    def exec_str(self, code, stats):
        if stats['key'] == 'type':
            res = self.resolve_literal(code)
            self.mem.write(scope=stats['scope'], name=stats['func'], var=stats['var'], prop='type',
                           value=res)

        elif stats['key'] == 'params':
            pass

        elif stats['key'] == 'body':
            self.dp('str', 'body')
            if code == 'all' and stats['func'] and stats['var'] and stats['type']:
                stats['idx'] = self.mem.get_idx(scope=stats['scope'], name=stats['func'],
                                                var=stats['var'])
                self.dp('str', f'got all {stats["idx"]}')

        elif stats['key'] == 'return':
            pass

        self.dp('str', f'- str={code} | key={stats["key"]}')
        return stats

    # AST OBJECTS FUNCTIONS

    def ast_paramsseq(self, code, stats):
        stats = self.tasks[type(code.value)](code.value, stats)
        return stats

    def ast_athing(self, code, stats):
        stats = self.tasks[type(code.value)](code.value, stats)
        return stats

    def ast_body(self, code, stats):
        stats['obj'] = Body
        stats = self.tasks[type(code.value)](code.value, stats)
        if stats['obj'] == AttrDecl:
            stats['obj'] = None
        return stats

    def ast_attrdecl(self, code, stats):
        self.dp('attrdecl', 'entered')
        stats['obj'] = AttrDecl
        stats = self.tasks[type(code.value)](code.value, stats)
        if stats['to_var']:
            res = stats['to_var']
            if len(res) == len(stats['idx']):
                for k, r in zip(stats['idx'], res):
                    sub_r = self.resolve_literal(r)
                    self.mem.write(scope=stats['scope'], name=stats['func'], var=stats['var'],
                                   index=k, value=sub_r)
            elif len(res) == 1:
                for k in stats['idx']:
                    self.mem.write(scope=stats['scope'], name=stats['func'], var=stats['var'],
                                   index=k, value=res[0])
        stats['var'] = None
        stats['type'] = None
        stats['obj'] = None
        self.dp('attrdel', 'left')
        return stats

    def ast_attrassign(self, code, stats):
        stats['obj'] = AttrAssign
        stats = self.tasks[type(code.value)](code.value, stats)
        if stats['to_var']:
            res = stats['to_var']
            if len(res) == len(stats['idx']):
                for k, r in zip(stats['idx'], res):
                    sub_r = self.resolve_literal(r)
                    self.mem.write(scope=stats['scope'], name=stats['func'], var=stats['var'],
                                   index=k, value=sub_r)
            elif len(res) == 1:
                for k in stats['idx']:
                    self.mem.write(scope=stats['scope'], name=stats['func'], var=stats['var'],
                                   index=k, value=res[0])
        stats['obj'] = None
        return stats

    def ast_expr(self, code, stats):
        # stats['obj'] = Expr
        stats = self.tasks[type(code.value)](code.value, stats)
        return stats

    def ast_manyexprs(self, code, stats):
        stats = self.tasks[type(code.value)](code.value, stats)
        return stats

    def ast_entity(self, code, stats):
        stats = self.tasks[type(code.value)](code.value, stats)
        res = self.resolve_args(stats['to_var'], stats)
        if len(res) == len(stats['idx']):
            for k, v in zip(stats['idx'], res):
                sub_v = self.resolve_literal(v)
                self.mem.write(scope=stats['scope'], name=stats['func'], var=stats['var'], index=k,
                               value=sub_v)
        elif len(res) == 1:
            for k in stats['idx']:
                self.mem.write(scope=stats['scope'], name=stats['func'], var=stats['var'], index=k,
                               value=res[0])
        stats['to_var'] = ()
        stats['args'] = ()
        stats['idx'] = ()
        stats['from_var'] = ()
        return stats

    def ast_call(self, code, stats):
        self.dp('call', 'entered')
        prev_obj = stats['obj']
        stats['obj'] = Call
        stats = self.tasks[type(code.value)](code.value, stats)
        if prev_obj == Tests:
            pass
        stats['obj'] = None
        self.dp('call', 'left')
        return stats

    def ast_func(self, code, stats):
        stats = self.tasks[type(code.value)](code.value, stats)
        return stats

    def ast_ifstmt(self, code, stats):
        self.dp('if-stmt', 'entered')
        stats = self.tasks[type(code.value)](code.value, stats)
        self.dp('if-stmt', 'left')
        return stats

    def ast_elifstmt(self, code, stats):
        self.dp('elif-stmt', 'entered')
        stats = self.tasks[type(code.value)](code.value, stats)
        self.dp('elif-stmt', 'left')
        return stats

    def ast_elsestmt(self, code, stats):
        self.dp('else-stmt', 'entered')
        stats = self.tasks[type(code.value)](code.value, stats)
        self.dp('else-stmt', 'left')
        return stats

    def ast_tests(self, code, stats):
        stats['obj'] = Tests
        stats = self.tasks[type(code.value)](code.value, stats)
        return stats

    def ast_exitbody(self, code, stats):
        stats['skip'] += 2
        return stats

    def ast_forloop(self, code, stats):
        stats['obj'] = ForLoop
        stats = self.tasks[type(code.value)](code.value, stats)
        return stats

    def ast_attrheader(self, code, stats):
        stats['obj'] = AttrHeader
        stats = self.tasks[type(code.value)](code.value, stats)
        _scope = stats['scope']
        _func = stats['func']
        _type = stats['type']
        _var = stats['var']
        self.dp('attrheader', f'res: {stats}')
        self.dp('attrheader', f'- scope={_scope} func={_func} var={_var} type={_type}')
        if _scope and _func and _type and _var:
            self.dp('attrheader', '... ok!')
            self.mem.create(scope=_scope, name=_func, var=_var, type_data=_type)
            if stats['args']:
                self.mem.write(scope=_scope, name=_func, var=_var, prop='len',
                               value=stats['args'][0])
                stats['args'] = ()
            self.dp('memory', f'** MEMORY={self.mem} **')
            stats['obj'] = AttrAssign
        return stats

    def ast_typeexpr(self, code, stats):
        old_obj = stats['obj']
        stats['obj'] = TypeExpr
        stats = self.tasks[type(code.value)](code.value, stats)
        stats['obj'] = old_obj
        return stats

    def ast_indexassign(self, code, stats):
        prev_obj = stats['obj']
        stats['obj'] = IndexAssign
        stats = self.tasks[type(code.value)](code.value, stats)
        stats['obj'] = prev_obj
        return stats

    def ast_args(self, code, stats):
        stats['obj'] = Args
        stats = self.tasks[type(code.value)](code.value, stats)
        return stats

    def ast_caller(self, code, stats):
        stats['obj'] = Caller
        stats = self.tasks[type(code.value)](code.value, stats)
        return stats

    def ast_token(self, code, stats):
        self.dp('token', f'token got={code} | obj={stats["obj"]}')

        if stats['obj'] == AttrHeader:
            if not stats['var']:
                if code.name.endswith('SYMBOL'):
                    stats['var'] = code.value
            elif not stats['type']:
                if code.name.endswith('TYPE') or code.name.endswith('SYMBOL'):
                    stats['type'] = code.value

        elif stats['obj'] == IndexAssign:
            res = self.resolve_literal(code)
            stats['idx'] += (res,)

        elif stats['obj'] == Args:
            res = self.resolve_literal(code)
            stats['args'] += (res,)

        elif stats['obj'] == Call:
            self.dp('token', 'obj=call')
            if stats['var'] and stats['type']:
                res = ()
                for k in stats['args']:
                    res += (k,)
                for k in stats['idx']:
                    res += (
                    self.mem.read(scope=stats['scope'], name=stats['func'], var=stats['var'],
                                  index=k),)
                self.dp('token', f'obj=call res={res}')
            else:
                res = stats['args']
            args = self.resolve_args(res, stats)
            res = self.btin_funcs[code.value](*args)
            if stats['var'] and stats['type'] and res:
                stats['to_var'] += (res,)

        elif stats['obj'] == Tests:
            pass

        elif stats['obj'] == TypeExpr:
            self.dp('token', 'obj=typeexpr')
            if code.name.endswith('LITERAL'):
                stats['args'] += (self.resolve_literal(code),)
                self.dp('token',
                        f'obj=typeexpr | args={stats["args"]} type args={type(stats["args"])}')
            elif code.name.endswith('SYMBOL'):
                pass
            else:
                stats['args'] += self.resolve_args(code.value, stats)

        elif stats['obj'] == AttrAssign:
            res = self.resolve_literal(code)
            self.dp('token', f'attrassign res={res} type={type(res)}')
            stats['to_var'] += (res,)

        elif stats['obj'] == Caller:
            self.dp('token', 'obj=caller')
            if stats['var'] and stats['type']:
                res = ()
                for k in stats['args']:
                    res += (k,)
                for k0, k in enumerate(stats['idx']):
                    res2 = res
                    res2 += (
                    self.mem.read(scope=stats['scope'], name=stats['func'], var=stats['var'],
                                  index=k),)
                    args = self.resolve_args(res2, stats)
                    if code.value in self.btin_funcs.keys():
                        self.dp('token', f'obj=caller code={code.value} args={args}')
                        if k0 + 1 < len(stats['idx']):
                            btin_res = self.btin_funcs[code.value](*args, buffer=True)
                        else:
                            btin_res = self.btin_funcs[code.value](*args, buffer=False)

                    if stats['var'] and stats['type'] and btin_res:
                        stats['to_var'] += (btin_res,)
            else:
                if not stats['type']:
                    if not stats['var']:
                        res = self.resolve_args(stats['args'], stats)
                        if code.value in self.btin_funcs.keys():
                            btin_res = self.btin_funcs[code.value](*stats['args'])
                            if stats['var'] and stats['type'] and btin_res:
                                stats['to_var'] += (res,)
                        elif code.value in ['int', 'float', 'str']:
                            self.dp('token', 'int, float, str - here modafoca?')
                        else:
                            self.dp('token', self.mem)
                            self.dp('token',
                                    self.mem.data[stats['scope']][stats['func']][code.value][
                                        'data'])
                            stats['args'] += self.mem.read(stats['scope'], stats['func'],
                                                           code.value)
                            self.dp('token', f'else={stats}')
                    else:
                        self.dp('token', 'no type... assigning')
                        stats['type'] = code.value
                        res = self.resolve_args(stats['args'], stats)
                        if code.value in self.btin_funcs.keys():
                            btin_res = self.btin_funcs[code.value](*stats['args'])
                            if stats['var'] and stats['type'] and btin_res:
                                stats['to_var'] += (res,)

        else:
            print(f'token, obj={stats["obj"]}')
        return stats

    # RESOLVING FUNCTIONS

    def resolve_literal(self, code):
        if isinstance(code, Token):
            if code.name.endswith('LITERAL'):
                return ast.literal_eval(code.value)
            return code.value
        return code

    def resolve_args(self, code, stats):
        if isinstance(code, tuple):
            args = ()
            for k in code:
                if isinstance(k, (int, float, str)):
                    args += (k,)
                elif isinstance(k, tuple):
                    new_args = self.resolve_args(k, stats)
                    args += (new_args,)
                elif isinstance(k, Token):
                    new_args = ()
                    for p in stats['idx']:
                        new_args += (self.mem.read(stats['scope'], stats['func'], stats['var'], p),)
                    if new_args:
                        args += (new_args,)
            return args
        if isinstance(code, str):
            return (code,)

    # FIRST WALK

    def walk(self, code, stats=None):
        if stats is None:
            stats = {'type': None,
                     'var': None,
                     'func': None,
                     'scope': None,
                     'key': None,
                     'obj': None,
                     'skip': 0,
                     'args': (),
                     'idx': (),
                     'to_var': (),
                     'from_var': ()}
        stats = self.tasks[type(code)](code, stats)
        return stats


class GenAST:
    def __init__(self, code=None):
        if code is None:
            self.code = SAMPLE_CODE_2
        self.lc = lexer.lex(self.code)
        self.pc = parser.parse(self.lc)

    def get_ast(self):
        return self.pc
