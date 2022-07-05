"""Evaluator"""

import time
import ast
from copy import deepcopy
from typing import Any
import networkx as nx
from qiskit import QuantumCircuit
from qiskit.providers.aer import QasmSimulator
from rply.token import BaseBox, Token
from hhat_lang.tokens import tokens
from hhat_lang.lexer import lexer
from hhat_lang.parser import parser
from hhat_lang.symbolic import FST, Memory
from hhat_lang.data_types import (int_type, float_type, str_type,
                                  bool_type, circuit_type, literal_type)
from hhat_lang.new_ast import (Program, Function, FuncTemplate, ParamsSeq, AThing, Body,
                               AttrDecl, Expr, ManyExprs, Entity, AttrAssign, Call,
                               Func, IfStmt, ElifStmt, ElseStmt, Tests, ForLoop, ExitBody,
                               AttrHeader, TypeExpr, IndexAssign, Args, Caller, ExprAssign,
                               AType, ASymbol, AQSymbol, ABuiltIn, Range, LoopObj)
from hhat_lang.builtin import (btin_print, btin_and, btin_or, btin_not, btin_eq, btin_neq,
                               btin_gt, btin_gte, btin_lt, btin_lte, btin_add, btin_mult,
                               btin_div, btin_pow, btin_sqrt, btin_q_h, btin_q_x, btin_q_z,
                               btin_q_sync, btin_q_cnot, btin_q_toffoli, btin_q_init,
                               btin_q_and, btin_q_or, btin_abs)

SAMPLE_CODE_1 = """
func null f: ( int b =(:4) ) 

func int sum (int x, int y) (
    return (add(x y))
)

main null X: (
    int a =(:3)
    int b =(:5)
    if (eq(a b)): (
        print(a '=' b)
    ) 
    elif (gt(a b)): (
        print(a '>' b)
    ) 
    else: (
        print(a '<' b)
        if (eq(add(a b) 8)): ( print('yay!') )
        else: ( print('oh no') )
        
        if (and(eq(1 1) gt(b a))): ( print('worked') )
    )
    print('fin!')
)
"""

SAMPLE_CODE_2 = """
main null V: (
    circuit(2) @c1 = (1:@x)
    int a = (:5, :add(3 @c1), :print('test'))
    int(4) b = (0:1, 2:10, :add(100), :print, (1 3):print)
    circuit(3) @c2 = (0:@h, (0 1):@cnot)
    hashmap x = (0:1, 1:'oi', :print)
    measurement y = (:@c2, :print)
    circuit(4) @c3 = (:@h)
    circuit(8) @c4 = ((0 1 2 3):@c3)
    measurement z = (:@c4, :print('res:'))
    measurement z2 = (:@c4(1 2 7), :print('new res:'))
)
"""


# noinspection PyArgumentList
class Eval:
    def __init__(self, code, debug=False):
        self.code = code
        self.symbolic = self.code
        self.debug = debug
        self.mem = Memory()
        self.mem.restart()
        self.func_dict_order = ['type', 'params', 'body', 'return']
        self.tasks = {dict: self.exec_dict,
                      tuple: self.exec_tuple,
                      str: self.exec_str,
                      ParamsSeq: self.ast_paramsseq,
                      AThing: self.ast_athing,
                      ASymbol: self.ast_asymbol,
                      AQSymbol: self.ast_aqsymbol,
                      AType: self.ast_atype,
                      ABuiltIn: self.ast_abuiltin,
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
                      LoopObj: self.ast_loopobj,
                      Range: self.ast_range,
                      AttrHeader: self.ast_attrheader,
                      TypeExpr: self.ast_typeexpr,
                      IndexAssign: self.ast_indexassign,
                      ExprAssign: self.ast_exprassign,
                      Args: self.ast_args,
                      Caller: self.ast_caller
                      }
        self.type_lookup = {
            # TODO: check if literal_type is valid then refactor calls below
            'INT_LITERAL': int_type,
            'STR_LITERAL': str_type,
            'FLOAT_LITERAL': float_type,
            'TRUE_LITERAL': bool_type,
            'FALSE_LITERAL': bool_type,
        }
        self.btin_funcs = {'print': btin_print,
                           'add': btin_add,
                           'and': btin_and,
                           'or': btin_or,
                           'not': btin_not,
                           'neq': btin_neq,
                           'eq': btin_eq,
                           'gt': btin_gt,
                           'lt': btin_lt,
                           'abs': btin_abs,
                           '@x': btin_q_x,
                           '@h': btin_q_h,
                           '@cnot': btin_q_cnot,
                           '@init': btin_q_init,
                           '@and': btin_q_and,
                           '@or': btin_q_or}
        self.trans_gates = {'@x': 'x',
                            '@h': 'h',
                            '@cnot': 'cx',
                            '@swap': 'swap',
                            '@toffoli': 'toffoli'}
        self.op_rules = {'add': self.morpher,
                         '@h': self.appender,
                         '@x': self.appender,
                         '@cnot': self.appender,
                         '@toffoli': self.appender,
                         '@and': self.appender,
                         '@or': self.appender,
                         'eq': self.morpher,
                         'gt': self.morpher,
                         'lt': self.morpher,
                         'abs': self.morpher,
                         'and': self.morpher,
                         'or': self.morpher,
                         'not': self.morpher,
                         'neq': self.morpher,
                         'print': self.nuller}

    ################
    # DEBUG PRINT #
    ###############

    def dp(self, scope, depth=None, *msg, **msgs):
        if self.debug:
            if depth is not None:
                depth_str = f'*[{depth}]'
            else:
                depth_str = f'* - '
            scope_str = f'[{scope}]: '
            print(f'{depth_str}{scope_str}')
            for k in msg:
                if isinstance(k, str):
                    if '\n' in k:
                        for p in k.split('\n'):
                            print(f'{" " * (len(depth_str) - 2)}> {p}')
                    else:
                        print(f'{" " * (len(depth_str) - 2)}|_ {k}')
                else:
                    print(f'{" " * (len(depth_str) - 2)}|_ {k}')
            print(**msgs)

    ###################
    # STATS CREATION #
    ##################

    def start_stats(self):
        stats = {'type': None,
                 'var': None,
                 'func': None,
                 'scope': None,
                 'key': None,
                 'obj': None,
                 'depth': 0,
                 'skip': 0,
                 'res': (),
                 'idx': (),
                 'loop_range': (),
                 'loop_var_list': [],
                 'loop_var': dict(),
                 'in_loop': False,
                 'is_new_loop': False,
                 'mode': None}
        return stats

    ###################
    # MAIN FUNCTIONS #
    ##################

    def exec_dict(self, code, stats):
        if stats['scope'] is None:
            if 'main' in code.keys():
                stats['scope'] = 'main'
                stats = self.tasks[type(code['main'])](code['main'], stats)
            elif 'func' in code.keys():
                stats['scope'] = 'func'
                stats = self.tasks[type(code['func'])](code['func'], stats)
            else:
                if len(code.keys()) == 1:
                    print('??')

        elif stats['scope'] == 'main':
            if not stats['func']:
                stats['func'] = list(code.keys())[0]
                self.mem.create(scope=stats['scope'], name=stats['func'])
                stats = self.tasks[type(code[stats['func']])](code[stats['func']], stats)
            else:
                if not set(self.func_dict_order).symmetric_difference(code.keys()):
                    for k in self.func_dict_order:
                        if k in code.keys():
                            stats['key'] = k
                            stats = self.tasks[type(code[k])](code[k], stats)

        elif stats['scope'] == 'func':
            self.dp('dict', stats['depth'], 'scope: func', stats['func'], f'code: {code.keys()}')
            if not stats['func']:
                stats['func'] = list(code.keys())[0]
                self.mem.create(scope=stats['scope'], name=stats['func'])
                stats = self.tasks[type(code[stats['func']])](code[stats['func']], stats)
            else:
                if not set(self.func_dict_order).symmetric_difference(code.keys()):
                    for k in self.func_dict_order:
                        stats['key'] = k
                        if k == 'return':
                            self.dp('FUNCTION_RETURN',
                                    stats['depth'],
                                    f'stats: {stats}')
                            stats['obj'] = None
                        stats = self.tasks[type(code[k])](code[k], stats)

        return stats

    def exec_tuple(self, code, stats):
        new_stats = deepcopy(stats)
        tmp_res = ()
        tmp_idx = ()
        if stats['key'] == 'params':
            self.prepare_params(stats['scope'], stats['func'], stats)
            stats['res'] = ()
            return stats

        if stats['skip'] == 0:
            for k in code:
                if new_stats['skip'] == 0:
                    new_stats = self.tasks[type(k)](k, stats)

                if new_stats['skip'] > 0:
                    if type(k) == ExitBody:
                        self.dp('tuple',
                                new_stats['depth'],
                                'conditional -> skipping',
                                f'stats: {stats}',
                                f'old_obj: {stats["obj"]}',
                                f'cur: {type(k)}')
                        new_stats['skip'] -= 1
                        new_stats['obj'] = stats['obj']
                        stats['skip'] = new_stats['skip']
                        break
                else:
                    self.dp('tuple',
                            new_stats['depth'],
                            f'obj: {new_stats["obj"]}',
                            f'old_obj: {stats["obj"]}',
                            f'stats: {new_stats}')
                    #
                    if stats['obj'] == AttrHeader:
                        if stats['type'] is None and new_stats['res']:
                            stats['type'] = new_stats['res'][0]

                    elif stats['obj'] == Call:
                        tmp_res = new_stats['res']
                        tmp_idx = new_stats['idx']

                    elif stats['obj'] == Args:
                        tmp_res = new_stats['res']
                        tmp_idx = new_stats['idx']
                        stats['idx'] = tmp_idx

                    elif stats['obj'] in [Caller, ABuiltIn, Func, AttrAssign]:
                        self.dp('tuple',
                                stats['depth'],
                                f'obj: {stats["obj"]}',
                                f'stats: {new_stats}')
                        if stats['obj'] == AttrAssign:
                            stats['var'] = new_stats['var']
                            stats['type'] = new_stats['type']
                        tmp_res = new_stats['res']
                        tmp_idx = new_stats['idx']
                        stats['idx'] = tmp_idx

                    elif stats['obj'] == IndexAssign:
                        tmp_idx = new_stats['idx']
                        tmp_idx += new_stats['res']
                        tmp_res = ()
                        stats['idx'] = tmp_idx

                    elif stats['obj'] in [ExprAssign, Entity]:
                        tmp_res += new_stats['res']
                        tmp_idx = new_stats['idx']

                    elif stats['obj'] == TypeExpr:
                        tmp_res += new_stats['res']

                    elif stats['type'] is None and stats['obj'] == AType and new_stats['res']:
                        stats['type'] = new_stats['res'][0]

                    elif stats['obj'] == Tests:
                        tmp_res = new_stats['res']
                        tmp_idx = new_stats['idx']

                    elif stats['obj'] in [Range, ForLoop, LoopObj]:
                        tmp_res = new_stats['res']
                        stats['loop_var'] = new_stats['loop_var']
                        stats['loop_range'] = new_stats['loop_range']

                    elif stats['obj'] is None and stats['key'] == 'return':
                        tmp_res = new_stats['res']

            stats['res'] = tmp_res
            stats['idx'] = tmp_idx
        else:
            if stats['obj'] == ExitBody:
                stats['skip'] -= 1

        self.dp('tuple', stats['depth'], f'exit-tuple stats: {stats}')
        return stats

    def exec_str(self, code, stats):
        if stats['key'] == 'type':
            res = self.resolve_literal(code, stats)
            self.mem.write(scope=stats['scope'],
                           name=stats['func'],
                           var=stats['var'],
                           prop='type',
                           value=res)

        elif stats['key'] == 'params':
            pass

        elif stats['key'] == 'body':
            if code == '*all*' and stats['func'] and stats['var'] and stats['type']:
                stats['idx'] = self.mem.get_idx(scope=stats['scope'],
                                                name=stats['func'],
                                                var=stats['var'])
                self.dp('str', stats['depth'], f'got all {stats["idx"]}')
            else:
                stats = self.resolve_ast(code, stats)

        elif stats['key'] == 'return':
            self.dp('str', stats['depth'], f'key: return', f'stats: {stats}')
            stats = self.resolve_ast(code, stats)

        return stats

    ##########################
    # AST OBJECTS FUNCTIONS #
    #########################

    def ast_paramsseq(self, code, stats):
        stats = self.tasks[type(code.value)](code.value, stats)
        return stats

    def ast_athing(self, code, stats):
        stats = self.tasks[type(code.value)](code.value, stats)
        return stats

    def ast_body(self, code, stats):
        stats['obj'] = Body
        stats['depth'] += 1
        stats = self.tasks[type(code.value)](code.value, stats)
        stats['depth'] -= 1
        return stats

    def ast_attrdecl(self, code, stats):
        self.dp('attrdecl', stats['depth'], 'entered')
        old_obj = stats['obj']
        stats['obj'] = AttrDecl
        stats['depth'] += 1
        stats['res'] = ()
        stats['idx'] = ()
        stats = self.tasks[type(code.value)](code.value, stats)
        if stats['res']:
            self.dp('attrdecl',
                    stats['depth'],
                    f'to_var: T',
                    f'to_var: {stats["res"]}',
                    f'idx: {stats["idx"]}')
        stats['var'] = None
        stats['type'] = None
        stats['obj'] = old_obj
        stats['depth'] -= 1
        self.dp('attrdel', stats['depth'], 'left')
        return stats

    def ast_attrassign(self, code, stats):
        old_obj = stats['obj']
        stats['obj'] = AttrAssign
        stats['depth'] += 1
        old_new_loop = stats['is_new_loop']
        stats['is_new_loop'] = False
        stats = self.tasks[type(code.value)](code.value, stats)
        if stats['res']:
            self.dp('attrassign', stats['depth'], f'args: T')
        stats['obj'] = old_obj
        stats['is_new_loop'] = old_new_loop
        stats['var'] = None
        stats['type'] = None
        stats['depth'] -= 1
        return stats

    def ast_expr(self, code, stats):
        stats = self.tasks[type(code.value)](code.value, stats)
        return stats

    def ast_manyexprs(self, code, stats):
        stats = self.tasks[type(code.value)](code.value, stats)
        return stats

    def ast_entity(self, code, stats):
        old_obj = stats['obj']
        stats['obj'] = Entity
        stats = self.tasks[type(code.value)](code.value, stats)
        self.dp('entity', stats['depth'], f'post-stats: {stats}')
        stats['obj'] = old_obj
        res = stats['res']
        self.dp('entity',
                stats['depth'],
                f'obj: {stats["obj"]}',
                f'res: {res}',
                f'idx: {stats["idx"]}')
        if stats['var'] is not None and stats['type'] is not None:
            if not stats['is_new_loop']:
                if len(res) == len(stats['idx']):
                    if stats['type'] != 'circuit':
                        for k, v in zip(stats['idx'], res):
                            self.dp('entity',
                                    stats['depth'],
                                    f'len val: idx',
                                    f'idx: {k}',
                                    f'val: {v}')
                            sub_v = self.resolve_literal(v, stats)[0]
                            self.mem.write(scope=stats['scope'],
                                           name=stats['func'],
                                           var=stats['var'],
                                           index=k,
                                           value=sub_v)
                            self.dp('entity',
                                    stats['depth'],
                                    f'memory: write',
                                    f'MEMORY: {self.mem}')
                    else:
                        for k in res:
                            self.mem.write(scope=stats['scope'],
                                           name=stats['func'],
                                           var=stats['var'],
                                           value=k)
                        self.dp('entity',
                                stats['depth'],
                                f'memory: write',
                                f'MEMORY: {self.mem}')
                elif len(res) == 1:
                    if stats['type'] != 'circuit':
                        for k in stats['idx']:
                            self.mem.write(scope=stats['scope'],
                                           name=stats['func'],
                                           var=stats['var'],
                                           index=k,
                                           value=res[0])
                        self.dp('entity',
                                stats['depth'],
                                f'memory: write',
                                f'MEMORY: {self.mem}')
                    else:
                        self.mem.write(scope=stats['scope'],
                                       name=stats['func'],
                                       var=stats['var'],
                                       value=res[0])
                        self.dp('entity',
                                stats['depth'],
                                f'memory: write',
                                f'MEMORY: {self.mem}')
                else:
                    if stats['type'] == 'circuit':
                        for k in res:
                            self.mem.write(scope=stats['scope'],
                                           name=stats['func'],
                                           var=stats['var'],
                                           value=k)
                        self.dp('entity',
                                stats['depth'],
                                f'memory: write',
                                f'MEMORY: {self.mem}')

            else:
                # loop true
                if len(stats['idx']) > 0:
                    self.dp('entity', stats['depth'], 'forloop--entered')
                    # stats['loop_range'] = stats['idx'][0]
                    # stats['idx'] = ()

        else:
            if stats['obj'] == ForLoop or (stats['in_loop'] and stats['is_new_loop']):
                if len(stats['idx']) > 0:
                    self.dp('entity', stats['depth'], 'forloop--entered')
                    # stats['loop_range'] = stats['idx'][0]
                    # stats['idx'] = ()
            else:
                self.dp('entity', stats['depth'], 'no var, no forloop')
        stats['res'] = ()
        stats['idx'] = ()
        return stats

    def ast_call(self, code, stats):
        self.dp('call', stats['depth'], 'entered', f'stats: {stats}')
        old_obj = stats['obj']
        stats['obj'] = Call
        stats['depth'] += 1
        tmp_res = stats['res']
        stats['res'] = ()
        stats = self.tasks[type(code.value)](code.value, stats)
        new_res = stats['res']
        stats['res'] = tmp_res + new_res
        stats['obj'] = old_obj
        stats['depth'] -= 1
        self.dp('call', stats['depth'], 'left', f'stats: {stats}')
        return stats

    def ast_func(self, code, stats):
        old_obj = stats['obj']
        stats['obj'] = Func
        stats = self.tasks[type(code.value)](code.value, stats)
        stats['obj'] = old_obj
        return stats

    def ast_ifstmt(self, code, stats):
        self.dp('if-stmt', stats['depth'], 'entered')
        stats['skip'] = 0
        stats = self.tasks[type(code.value)](code.value, stats)
        stats['skip'] = 0
        self.dp('if-stmt', stats['depth'], 'left')
        return stats

    def ast_elifstmt(self, code, stats):
        self.dp('elif-stmt', stats['depth'], 'entered')
        stats = self.tasks[type(code.value)](code.value, stats)
        self.dp('elif-stmt', stats['depth'], 'left')
        return stats

    def ast_elsestmt(self, code, stats):
        self.dp('else-stmt', stats['depth'], 'entered')
        stats = self.tasks[type(code.value)](code.value, stats)
        self.dp('else-stmt', stats['depth'], 'left')
        return stats

    def ast_tests(self, code, stats):
        old_obj = stats['obj']
        stats['obj'] = Tests
        stats['depth'] += 1
        stats = self.tasks[type(code.value)](code.value, stats)
        self.dp('tests', stats['depth'], f'stats: {stats}')
        if len(stats['res']) > 0:
            for k in stats['res']:
                if k == False:
                    stats['skip'] = 1
                    break
        else:
            raise ValueError('Something went wrong while trying to test conditional')
        stats['res'] = ()
        stats['depth'] -= 1
        return stats

    def ast_exitbody(self, code, stats):
        stats['obj'] = ExitBody
        stats['skip'] = 2
        self.dp('exitbody', stats['depth'], f'exit body reached, skip={stats["skip"]}')
        return stats

    def ast_forloop(self, code, stats):
        old_obj = stats['obj']
        stats['obj'] = ForLoop
        stats['depth'] += 1
        old_res = stats['res']
        stats['res'] = ()
        old_loop = stats['in_loop']
        old_new_loop = stats['is_new_loop']
        stats['in_loop'] = True
        stats['is_new_loop'] = True
        stats = self.tasks[type(code.value)](code.value, stats)
        stats['in_loop'] = old_loop
        stats['is_new_loop'] = old_new_loop
        if len(stats['loop_var_list']) > 0:
            last_loop_var = stats['loop_var_list'].pop(-1)
            if len(stats['loop_var'].keys()) > 0:
                stats['loop_var'].pop(last_loop_var)
        stats['loop_range'] = ()
        stats['depth'] -= 1
        stats['res'] = old_res
        stats['obj'] = old_obj
        return stats

    def ast_loopobj(self, code, stats):
        old_obj = stats['obj']
        stats['obj'] = LoopObj
        stats['depth'] += 1
        stats = self.tasks[type(code.value)](code.value, stats)
        if len(stats['res']) > 0 and not stats['loop_range']:
            stats['loop_range'] = stats['res'][0]
            stats['res'] = ()
        stats['depth'] -= 1
        stats['obj'] = old_obj
        return stats

    def ast_range(self, code, stats):
        old_obj = stats['obj']
        stats['obj'] = Range
        stats['depth'] += 1
        stats = self.tasks[type(code.value)](code.value, stats)
        if isinstance(stats['res'], tuple):
            if len(stats['res']) == 2:
                stats['res'] = range(*stats['res'])
        stats['loop_range'] = stats['res']
        stats['res'] = ()
        stats['obj'] = old_obj
        stats['depth'] -= 1
        return stats

    def ast_attrheader(self, code, stats):
        old_obj = stats['obj']
        stats['obj'] = AttrHeader
        stats['depth'] += 1
        stats = self.tasks[type(code.value)](code.value, stats)
        stats['depth'] -= 1
        _scope = stats['scope']
        _func = stats['func']
        _type = stats['type']
        _var = stats['var']
        self.dp('attrheader', stats['depth'], f'res: {stats}')
        self.dp('attrheader',
                stats['depth'],
                f'scope: {_scope}',
                f'func: {_func}',
                f'var: {_var}',
                f'type: {_type}')
        if _scope and _func and _type and _var:
            self.dp('attrheader', stats['depth'], 'ok!')
            self.mem.create(scope=_scope,
                            name=_func,
                            var=_var,
                            type_data=_type)
            if stats['res']:
                self.mem.write(scope=_scope,
                               name=_func,
                               var=_var,
                               prop='len',
                               value=stats['res'][0])
                stats['res'] = ()
            self.dp('memory', stats['depth'], f'MEMORY: {self.mem}')
            # stats['obj'] = AttrAssign
        else:
            stats['obj'] = old_obj
        return stats

    def ast_typeexpr(self, code, stats):
        stats['obj'] = TypeExpr
        stats['depth'] += 1
        stats = self.tasks[type(code.value)](code.value, stats)
        stats['depth'] -= 1
        return stats

    def ast_indexassign(self, code, stats):
        old_obj = stats['obj']
        stats['obj'] = IndexAssign
        stats['depth'] += 1
        stats = self.tasks[type(code.value)](code.value, stats)
        stats['depth'] -= 1
        stats['obj'] = old_obj
        stats['idx'] += stats['res']
        stats['res'] = ()
        self.dp('indexassign', stats['depth'], f'post-stats: {stats}')
        return stats

    def ast_exprassign(self, code, stats):
        old_obj = stats['obj']
        stats['obj'] = ExprAssign
        stats['depth'] += 1
        if stats['in_loop'] and stats['is_new_loop']:
            self.dp('exprassign',
                    stats['depth'],
                    f'loop-entedered',
                    f'loop idxs: {tuple(stats["loop_var"].keys())}',
                    f'code: {code}',
                    f'stats: {stats}')
            _iter = stats['loop_range']
            if len(stats['loop_var']) > 0:
                cur_loop_var = [p for p, v in stats['loop_var'].items() if v is None][0]
                for k in _iter:
                    stats['loop_var'][cur_loop_var] = k
                    stats = self.tasks[type(code.value)](code.value, stats)
        else:
            self.dp('exprassign', stats['depth'], f'code: {code}', f'stats: {stats}')
            stats = self.tasks[type(code.value)](code.value, stats)
        stats['depth'] -= 1
        stats['obj'] = old_obj
        self.dp('exprassign', stats['depth'], f'post-stats: {stats}')
        return stats

    def ast_args(self, code, stats):
        old_obj = stats['obj']
        stats['obj'] = Args
        stats['depth'] += 1
        stats = self.tasks[type(code.value)](code.value, stats)
        stats['obj'] = old_obj
        stats['depth'] -= 1
        return stats

    def ast_caller(self, code, stats):
        old_obj = stats['obj']
        stats['obj'] = Caller
        stats['depth'] += 1
        stats = self.tasks[type(code.value)](code.value, stats)
        stats['obj'] = old_obj
        stats['depth'] -= 1
        return stats

    def ast_asymbol(self, code, stats):
        stats = self.tasks[type(code.value)](code.value, stats)
        return stats

    def ast_aqsymbol(self, code, stats):
        stats = self.tasks[type(code.value)](code.value, stats)
        return stats

    def ast_atype(self, code, stats):
        stats['obj'] = AType
        stats = self.tasks[type(code.value)](code.value, stats)
        return stats

    def ast_abuiltin(self, code, stats):
        old_obj = stats['obj']
        stats['obj'] = ABuiltIn
        stats = self.tasks[type(code.value)](code.value, stats)
        stats['obj'] = old_obj
        return stats

    ##########################
    # AST RESOLVER FUNCTION #
    #########################

    def resolve_ast(self, code, stats):
        self.dp('resolver',
                stats['depth'],
                f'{code}',
                f'obj: {stats["obj"]}',
                f'stats: {stats}')

        if stats['obj'] == None:
            if stats['key'] == 'return':
                stats['res'] += self.resolve_literal(code, stats)

        elif stats['obj'] == AttrHeader:
            if not stats['var']:
                stats['var'] = code
            elif not stats['type']:
                stats['type'] = code

        elif stats['obj'] == AType:
            stats['type'] = code

        elif stats['obj'] == IndexAssign:
            stats['idx'] += self.resolve_literal(code, stats)
            stats['res'] = ()

        elif stats['obj'] == ExprAssign:
            res = self.resolve_literal(code, stats)
            self.dp('resolver',
                    stats['depth'],
                    f'exprassign res: {res}',
                    f'type: {type(res)}')
            stats['res'] += res

        elif stats['obj'] == Args:
            res = self.resolve_literal(code, stats)
            stats['res'] += res

        elif stats['obj'] == Call:
            self.dp('resolver',
                    stats['depth'],
                    f'obj: call (any call?)', f'code: {code}')
            stats['res'] += self.resolve_literal(code, stats)

        elif stats['obj'] == Tests:
            self.dp('resolver', stats['depth'], 'obj: tests')

        elif stats['obj'] == TypeExpr:
            self.dp('resolver',
                    stats['depth'],
                    f'obj: typeexpr',
                    f'symbol: {code}')
            stats['res'] += self.resolve_literal(code, stats)

        elif stats['obj'] == AttrAssign:
            if self.mem.is_var(scope=stats['scope'], name=stats['func'], var=code):
                stats['var'] = code
                stats['type'] = self.mem.read(scope=stats['scope'],
                                              name=stats['func'],
                                              var=code,
                                              prop='type')
            else:
                raise ValueError(f"{code} is not a var")

        elif stats['obj'] == ForLoop:
            pass

        elif stats['obj'] == LoopObj:
            pass

        elif stats['obj'] == Range:
            if self.mem.is_var(scope=stats['scope'], name=stats['func'], var=code):
                res = ()
                for k in stats['res']:
                    res += (self.mem.read(scope=stats['scope'],
                                          name=stats['func'],
                                          var=code,
                                          index=k),)
                stats['res'] = res

            elif code in self.symbolic['func'].keys():
                func_data_body = self.symbolic['func'][code]
                new_stats = self.start_stats()
                new_stats['scope'] = 'func'
                new_stats['func'] = code
                new_stats['res'] = stats['res']
                new_stats = self.tasks[type(func_data_body)](func_data_body,
                                                             new_stats)
                stats['res'] += new_stats['res']
            elif code in stats['loop_var'].keys():
                stats['res'] += (stats['loop_var'][code],)
            else:
                stats['res'] += self.resolve_literal(code, stats)

            if len(stats['res']) == 2:
                stats['res'] = range(*stats['res'])
            elif len(stats['res']) > 2:
                raise ValueError("Range has more than two parameters")

        elif stats['obj'] in [Caller, ABuiltIn]:
            self.dp('resolver',
                    stats['depth'],
                    f'obj: caller',
                    f'code: {code}',
                    f'stats: {stats}')
            if stats['var']:
                if stats['type'] is None and stats['var'] is not None:
                    stats['res'] += self.resolve_literal(code, stats)
                else:
                    if code in self.op_rules.keys():
                        new_stats_data = self.op_rules[code](code, stats)
                    else:
                        if code.startswith('@'):
                            new_stats_data = self.qsymbol_caller(code, stats)
                        else:
                            new_stats_data = ()
                            if self.mem.is_var(scope=stats['scope'],
                                               name=stats['func'],
                                               var=code):
                                if len(stats['res']) > 0:
                                    for k in stats['res']:
                                        tmp_res = self.mem.return_prop_or_idx(scope=stats['scope'],
                                                                              name=stats['func'],
                                                                              var=code,
                                                                              data=k)
                                        new_stats_data += (tmp_res,) if not isinstance(tmp_res,
                                                                                       tuple) else tmp_res
                                else:
                                    tmp_res = self.mem.read(scope=stats['scope'],
                                                            name=stats['func'],
                                                            var=code)
                                    new_stats_data += (tmp_res,) if not isinstance(tmp_res,
                                                                                   tuple) else tmp_res

                            elif code in self.symbolic['func'].keys():
                                self.dp('resolver',
                                        stats['depth'],
                                        f'call func: {code}')
                                func_data_body = self.symbolic['func'][code]
                                new_stats = self.start_stats()
                                new_stats['scope'] = 'func'
                                new_stats['func'] = code
                                new_stats['res'] = stats['res']
                                stats['res'] = ()
                                new_stats = self.tasks[type(func_data_body)](func_data_body,
                                                                             new_stats)
                                new_stats_data += new_stats['res']

                            # TODO: implement external function (import) check and call here
                            # elif external_function:
                            #    pass

                            elif code in stats['loop_var'].keys():
                                new_stats_data += (stats['loop_var'][code],)

                            else:
                                res = self.resolve_literal(code, stats)
                                if "'" not in res[0] or '"' not in res[0]:
                                    stats['loop_var'].update({res[0]: None})
                                    stats['loop_var_list'].append(res[0])
                                else:
                                    new_stats_data += res
                                self.dp('resolver', stats['depth'], f'what is {code}')
                                new_stats_data = ()

                    if isinstance(new_stats_data, dict):
                        stats = deepcopy(new_stats_data)
                    elif isinstance(new_stats_data, tuple):
                        stats['res'] = new_stats_data
                    else:
                        raise ValueError('No valid data found.')
                    self.dp('resolver',
                            stats['depth'],
                            f'obj: caller',
                            f'stats: {stats}')
            else:
                if stats['type'] is None:
                    if code in self.btin_funcs.keys():
                        btin_res = self.btin_funcs[code](*stats['res'])
                        if btin_res is not None and not (btin_res == ()):
                            stats['res'] = (btin_res,)
                        else:
                            stats['res'] = ()
                    else:
                        if code in self.mem.data[stats['scope']][stats['func']].keys():
                            self.dp('resolver', stats['depth'], f'mem: {self.mem}')

                            if self.mem.is_var(scope=stats['scope'],
                                               name=stats['func'],
                                               var=code):
                                new_stats_data = ()
                                if len(stats['res']) > 0:
                                    for k in stats['res']:
                                        tmp_res = self.mem.return_prop_or_idx(scope=stats['scope'],
                                                                              name=stats['func'],
                                                                              var=code,
                                                                              data=k)
                                        new_stats_data += (tmp_res,) if not isinstance(tmp_res,
                                                                                       tuple) else tmp_res
                                else:
                                    tmp_res = self.mem.read(scope=stats['scope'],
                                                            name=stats['func'],
                                                            var=code)
                                    new_stats_data += (tmp_res,) if not isinstance(tmp_res,
                                                                                   tuple) else tmp_res
                            else:
                                self.dp('resolver', stats['depth'], f'what is {code}')
                                new_stats_data = self.mem.read(stats['scope'],
                                                               stats['func'],
                                                               code)
                            self.dp('resolver', stats['depth'], f'new res: {new_stats_data}')
                            stats['res'] = new_stats_data
                            self.dp('resolver', stats['depth'], f'now stats: {stats}')

                        elif code in self.symbolic['func'].keys():
                            self.dp('resolver',
                                    stats['depth'],
                                    f'call func: {code}')
                            func_data_body = self.symbolic['func'][code]
                            new_stats = self.start_stats()
                            new_stats['scope'] = 'func'
                            new_stats['func'] = code
                            new_stats['res'] = stats['res']
                            stats['res'] = ()
                            new_stats = self.tasks[type(func_data_body)](func_data_body,
                                                                         new_stats)
                            stats['res'] += new_stats['res']

                        elif code in stats['loop_var'].keys():
                            stats['res'] += (stats['loop_var'][code],)

                        else:
                            res = self.resolve_literal(code, stats)
                            if "'" not in res[0] or '"' not in res[0]:
                                stats['loop_var'].update({res[0]: None})
                                stats['loop_var_list'].append(res[0])
                            else:
                                stats['res'] += res
        else:
            self.dp('token', stats['depth'], f'anything else {code}', f'obj: {stats["obj"]}')
        return stats

    ##########################################
    # MORPHER - APPENDER - NULLER FUNCTIONS #
    #########################################

    def morpher(self, code, stats):
        self.dp('morpher',
                stats['depth'],
                f'caller: {code}',
                f'stats: {stats}')
        to_var = ()
        for k0, k in enumerate(stats['idx']):
            res2 = stats['res']
            res2 += (self.mem.read(scope=stats['scope'],
                                   name=stats['func'],
                                   var=stats['var'],
                                   index=k),)
            self.dp('morpher',
                    stats['depth'],
                    f'res2 value: {res2}')
            if code in self.btin_funcs.keys():
                args = res2  # self.resolve_args(res2, stats)
                if k0 + 1 < len(stats['idx']):
                    btin_res = self.btin_funcs[code](*args, buffer=True)
                else:
                    btin_res = self.btin_funcs[code](*args, buffer=False)
                self.dp('morpher', stats['depth'], f'btin_res: {btin_res}')
                if btin_res:
                    to_var += (btin_res,)
        return to_var

    def appender(self, code, stats):
        self.dp('appender',
                stats['depth'],
                f'caller: {code}',
                f'stats: {stats}')
        to_var = ()
        if len(stats['idx']) > 0:
            if code in self.btin_funcs.keys():
                if code in ['@cnot', '@swap', '@cz']:
                    if len(stats['res']) == len(stats['idx']) and stats['res'] % 2 == 0:
                        for arg, idx in zip(stats['res'], stats['idx']):
                            self.dp('appender',
                                    stats['depth'],
                                    f'2-gate {code} ({arg}, {idx})')
                            btin_res = self.btin_funcs[code](arg, idx)
                            if btin_res:
                                to_var += (btin_res,)
                    else:
                        if len(stats['res']) > 0:
                            for arg in stats['res']:
                                for idx in stats['idx']:
                                    if arg != idx:
                                        self.dp('appender',
                                                stats['depth'],
                                                f'2-gate {code} ({arg}, {idx})')
                                        btin_res = self.btin_funcs[code](stats['res'], idx)
                                        if btin_res:
                                            to_var += (btin_res,)
                        else:
                            if len(stats['idx']) % 2 == 0:
                                idxs = ()
                                for idx in stats['idx']:
                                    if len(idxs) < 2:
                                        idxs += (idx,)
                                    if len(idxs) == 2:
                                        self.dp('appender',
                                                stats['depth'],
                                                f'2-gate {code} {idxs}')
                                        btin_res = self.btin_funcs[code](*idxs)
                                        if btin_res:
                                            stats['res'] += (btin_res,)
                                        idxs = ()
                elif code in ['@toffoli', '@and', '@or']:
                    if len(stats['idx']) % 3 == 0:
                        idxs = ()
                        for idx in stats['idx']:
                            if len(idxs) < 3:
                                idxs += (idx,)
                            if len(idxs) == 3:
                                self.dp('appender',
                                        stats['depth'],
                                        f'3-gate {code} {idxs}')
                                btin_res = self.btin_funcs[code](*idxs)
                                if btin_res:
                                    to_var += (btin_res,)
                    else:
                        if len(stats['res']) % 2 == 0:
                            args = ()
                            for arg in stats['res']:
                                if len(args) < 2:
                                    args += (arg,)
                                else:
                                    new_args = args
                                    for idx in stats['idx']:
                                        if len(new_args) == 2:
                                            new_args += (idx,)
                                        if arg not in idx and len(new_args) == 3:
                                            self.dp('appender',
                                                    stats['depth'],
                                                    f'3-gate {code} {new_args}')
                                            btin_res = self.btin_funcs[code](*new_args)
                                            self.dp('appender',
                                                    stats['depth'],
                                                    f'btin_res={btin_res}')
                                            if btin_res:
                                                stats['res'] += (btin_res,)
                                            new_args = ()
                else:
                    args = stats['idx']  # self.resolve_args(stats['idx'], stats)
                    args += stats['res']
                    btin_res = self.btin_funcs[code](*args)
                    if btin_res:
                        to_var += (btin_res,)
        else:
            self.dp('appender', stats['depth'], 'len idx == 0')
        self.dp('appender',
                stats['depth'],
                f'output',
                f'stats: {stats}')
        return to_var

    def nuller(self, code, stats):
        self.dp('nuller',
                stats['depth'],
                f'caller: {code}',
                f'stats: {stats}')
        to_var = ()
        btin_res = self.btin_funcs[code](*stats['res'], buffer=True)
        for k0, idx in enumerate(sorted(stats['idx'])):
            if stats['type'] not in ['hashmap', 'measurement']:
                res = (self.mem.read(scope=stats['scope'],
                                     name=stats['func'],
                                     var=stats['var'],
                                     index=idx),)
            else:
                res = (self.mem.read(scope=stats['scope'],
                                     name=stats['func'],
                                     var=stats['var'],
                                     index=idx),)
            if code in self.btin_funcs.keys():
                args = res  # self.resolve_args(res, stats)
                if k0 + 1 < len(stats['idx']):
                    btin_res = self.btin_funcs[code](*args, buffer=True)
                else:
                    btin_res = self.btin_funcs[code](*args, buffer=False)
                self.dp('nuller', stats['depth'], f'btin_res={btin_res}')
                if btin_res:
                    to_var += (btin_res,)
        return to_var

    def qsymbol_caller(self, code, stats):
        self.dp('qsymbol-caller',
                stats['depth'],
                f'caller: {code}',
                f'type: {stats["type"]}',
                f'stats: {stats}')
        if stats['type'] == 'circuit':
            code_type = self.mem.read(scope=stats['scope'],
                                      name=stats['func'],
                                      var=code, prop='type')
            if code_type == 'circuit':
                self.dp('qsymbol-caller',
                        stats['depth'],
                        'current variable and external variable are circuits')
                if len(stats['res']) > 0:
                    self.dp('qsymbol-caller',
                            stats['depth'],
                            'len stats args > 0')
                else:
                    self.dp('qsymbol-caller',
                            stats['depth'],
                            'len stats args == 0')
                    data = {'data': None, 'len': 0}
                    data['data'] = self.mem.read(scope=stats['scope'],
                                                 name=stats['func'],
                                                 var=code)
                    data['len'] = range(self.mem.read(scope=stats['scope'],
                                                      name=stats['func'],
                                                      var=code,
                                                      prop='len'))
                    res = self.resolve_circuit_idx(data, stats)
                    stats['res'] += res
            else:
                self.dp('qsymbol-caller',
                        stats['depth'],
                        f'variable is circuit, external var {code} is not')
                res = ()
                for k in stats['idx']:
                    res2 = self.mem.read(scope=stats['scope'],
                                         name=stats['func'],
                                         var=code,
                                         index=k)
                    res += res2 if isinstance(res2, tuple) else (res2,)
                    stats['res'] = res
        else:
            circuit_data = self.mem.read(scope=stats['scope'],
                                         name=stats['func'],
                                         var=code,
                                         prop='data')
            circuit_len = self.mem.read(scope=stats['scope'],
                                        name=stats['func'],
                                        var=code,
                                        prop='len')
            q_args = stats['res'] if stats['res'] else None
            circuit_qasm = self.circuit_to_qasm(circuit_data, circuit_len, q_args)
            simu = QasmSimulator()
            sim_run = simu.run(circuit_qasm, shots=2048)
            sim_res = sim_run.result()
            sim_counts = sim_res.data()['counts']
            self.dp('quantum data',
                    stats['depth'],
                    f'counts: {sim_counts}')
            if stats['type'] != 'measurement':
                if stats['type'] == 'hashmap':
                    raise ValueError(
                        f"Use measurement type instead of hashmap for circuits.")

                if len(sim_counts) == 1:
                    fin_res = int(list(sim_counts.keys())[0], 16)
                    self.dp('quantum data',
                            stats['depth'],
                            f'result: {fin_res}')
                    stats['res'] = (fin_res,)
                else:
                    iq_res = (self.interpret_qdata(sim_counts, stats['type']),)
                    stats['res'] = iq_res if isinstance(iq_res, tuple) else (iq_res,)
            else:
                stats['idx'] = tuple(sim_counts.keys())
                stats['res'] = tuple(sim_counts.values())
                self.dp('qsymbol-caller',
                        stats['depth'],
                        f'meas data: ({stats["idx"]}',
                        f'{stats["res"]})')
        return stats

    ###########################
    # QUANTUM DATA COMPUTING #
    ##########################

    @staticmethod
    def simple_trans_gates(gate):
        transl_gates = {'@x': 'x',
                        '@h': 'h',
                        '@cnot': 'cx',
                        '@swap': 'swap',
                        '@toffoli': 'ccx'}
        res = transl_gates.get(gate)
        if res:
            return res
        raise ValueError(f"Simple translated gates has no {gate} gate.")

    def display_gates_circuit(self, data):
        tmp_data = {}
        res = ''
        for line in data:
            for k in line.edges.data():
                ga = k[2]['data']
                if ga not in tmp_data.keys():
                    tmp_data.update({ga: []})
                if k[0] not in tmp_data[ga]:
                    tmp_data[ga].append(k[0])
                if k[1] not in tmp_data[ga]:
                    tmp_data[ga].append(k[1])

            tmp_data = {k: sorted(v,
                                  key=lambda y: line.nodes[y]['data']) for k, v in tmp_data.items()}
            for k, v in tmp_data.items():
                res += f'{self.simple_trans_gates(k)} '
                res += ', '.join([f'q[{p}]' for p in v])
                res += ';\n'
        res += '\n'
        return res

    def interpret_circuit(self, data):
        # circuit_code = ""
        # for k in data:
        #     for p in data[k]:
        #         if 'data' in data.edges[k, p]:
        #             circuit_code += ''.join(self.composed_trans_gates(k.edges[k, p]['data']))
        #         else:
        circuit_code = ""
        for node in data.nodes.data():
            if 'data' in node[1].keys():
                circuit_code += f"{self.trans_gates[node[1]['data']]} q[{node[0]}];\n"
        for edge in data.edges.data():
            if 'data' in edge[-1].keys():
                circuit_code += f"{self.trans_gates[edge[-1]['data']]}"
                for k0, k in enumerate(range(len(edge) - 1)):
                    circuit_code += f" q[{edge[k]}]"
                    if k0 + 2 < len(edge):
                        circuit_code += ", "
                circuit_code += ";\n"
        return circuit_code

    def circuit_to_qasm(self, data, data_len, args=None):
        circuit_code = """OPENQASM 2.0;\ninclude "qelib1.inc";\n"""
        circuit_code += f"qreg q[{data_len}];\ncreg c[{data_len}];\n\n"
        # for k in data:
        #     circuit_code += self.interpret_circuit(k)
        circuit_code += self.display_gates_circuit(data)
        if args is not None:
            for k in args:
                circuit_code += f"\nmeasure q[{k}] -> c[{k}];\n"
        else:
            circuit_code += "\nmeasure q -> c;\n"
        self.dp('qasm',
                None,
                f'file: \n\"{circuit_code}\"')
        qc = QuantumCircuit.from_qasm_str(circuit_code)
        return qc

    @staticmethod
    def interpret_qdata(data, data_type='int'):
        total_counts = 0
        final_value = 0
        for k, v in data.items():
            final_value += int(k, 16) * v
            total_counts += v
        final_value /= total_counts
        if data_type == 'int':
            return int(final_value)
        if data_type == 'str':
            return chr(int(final_value))
        if data_type == 'float':
            return final_value
        raise ValueError(f"No algorithm found for '{data_type}' process of quantum data.")

    def resolve_circuit_idx(self, data, stats):
        idx = {p: k for k, p in zip(stats['idx'], data['len'])}
        self.dp('resolve-circuit-idx',
                stats['depth'],
                f'idx: {idx}')
        new_data = []
        for k in data['data']:
            self.dp('resolve-circuit-idx',
                    stats['depth'],
                    f'nodes: {[(p[0], p[1]["data"]) for p in k.nodes.data()]}')
            self.dp('resolve-circuit-idx',
                    stats['depth'],
                    f'edges: {[(p[0], p[1], p[2]["data"]) for p in k.edges.data()]}')
            new_data.extend(
                [self.btin_funcs[node[1]['data']](*(idx[node[0]],)) for node in k.nodes.data()])
            new_data.extend(
                [self.btin_funcs[edge[2]['data']](*(idx[edge[0]], idx[edge[1]])) for edge in
                 k.edges.data()])
        return new_data,

    ########################
    # RESOLVING FUNCTIONS #
    #######################

    def resolve_literal(self, code, stats):
        if code in self.btin_funcs.keys():
            return code,
        if self.mem.is_var(scope=stats['scope'], name=stats['func'], var=code):
            return code,
        if code in self.symbolic['func'].keys():
            return code,
        if code == '*all*':
            return code,
        if isinstance(code, dict):
            return tuple(f'{p[0]}:{p[1]}' for p in code.items())
        try:
            res = ast.literal_eval(code)
            if isinstance(res, str):
                if (code.startswith('"') or code.startswith("'")) and (
                        code.endswith('"') or code.endswith("'")):
                    return res,
                else:
                    return res,
            return res,
        except ValueError:
            return code,

    def resolve_args(self, code, stats):
        if isinstance(code, tuple):
            args = ()
            for k in code:
                if isinstance(k, (int, float, str)):
                    args += self.resolve_literal(k, stats)
                elif isinstance(k, (tuple, list)):
                    new_args = self.resolve_args(k, stats)
                    args += new_args
                elif isinstance(k, (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph)):
                    args += (k,)
                    """
                elif isinstance(k, Token):
                    new_args = ()
                    for p in stats['idx']:
                        new_args += (self.mem.read(stats['scope'], stats['func'], stats['var'], p),)
                    if new_args:
                        args += (new_args,)
                    """
                elif isinstance(k, dict):
                    args += tuple(f'{p[0]}:{p[1]}' for p in k.items())
            return args

        if isinstance(code, list):
            self.dp('resolve-args',
                    stats['depth'],
                    f'code: {code}')
            args = ()
            for k in code:
                if isinstance(k,
                              (nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph, int, float)):
                    args += (k,)
                if isinstance(k, str):
                    args += self.resolve_literal(k, stats)
            return args
        if isinstance(code, str):
            return self.resolve_literal(code)

    ################################
    # FUNCTION HANDLING FUNCTIONS #
    ###############################

    def prepare_params(self, scope, func_name, stats):
        func_params = self.symbolic[scope][func_name]['params']
        self.dp('params',
                stats['depth'],
                f'scope: {scope}',
                f'func: {func_name}',
                f'func params: {func_params}',
                f'stats: {stats}')
        lfp = len(func_params)
        lsr = len(stats['res'])
        if lfp == lsr:
            for fp, sr in zip(func_params, stats['res']):
                is_var = self.mem.is_var(scope=stats['scope'], name=stats['func'], var=sr)
                is_func = sr in self.symbolic['func'].keys()
                if is_var or is_func:
                    self.mem.create(scope='func',
                                    name=func_name,
                                    var=fp['symbol'],
                                    type_data=fp['type'])
                    from_var = dict(scope=stats['scope'],
                                    name=stats['func'],
                                    var=sr,
                                    type=self.mem.read(scope=stats['scope'],
                                                       name=stats['func'],
                                                       var=sr,
                                                       prop='type'),
                                    len=self.mem.read(scope=stats['scope'],
                                                      name=stats['func'],
                                                      var=sr,
                                                      prop='len'),
                                    data=self.mem.read(scope=stats['scope'],
                                                       name=stats['func'],
                                                       var=sr,
                                                       prop='data'))
                    to_var = dict(scope='func',
                                  name=func_name,
                                  var=fp['symbol'],
                                  type=fp['type'],
                                  len=None,
                                  data={})
                    self.mem.copy(from_var, to_var)
                else:
                    self.mem.create(scope='func',
                                    name=func_name,
                                    var=fp['symbol'],
                                    type_data=fp['type'])
                    if 'len' in fp.keys():
                        self.mem.write(scope='func',
                                       name=func_name,
                                       var=fp['symbol'],
                                       prop='len',
                                       value=self.resolve_literal(fp['len'][0], stats)[0])
                    if isinstance(sr, (tuple, list)):
                        for k0, k in enumerate(sr):
                            self.mem.write(scope='func',
                                           name=func_name,
                                           var=fp['symbol'],
                                           value=k,
                                           index=k0)
                    else:
                        self.mem.write(scope='func',
                                       name=func_name,
                                       var=fp['symbol'],
                                       value=sr)
        else:
            raise ValueError("Func params and assigned data does not match in length.")

    ##################
    # WALK FUNCTION #
    #################

    def walk(self, code, stats=None):
        if stats is None:
            stats = self.start_stats()
        stats = self.tasks[type(code)](code, stats)
        return stats


class GenAST:
    def __init__(self, code=None):
        self.code = SAMPLE_CODE_2 if code is None else code
        self.lc = lexer.lex(self.code)
        self.pc = parser.parse(self.lc)
        self.st = self.pc.symbolic.table

    def get_ast(self):
        return self.pc


class Code:
    """
    Execution the code from text to evaluation/interpreting code
    """

    def __init__(self, code, debug=False, keep=False):
        """

        Parameters
        ----------
        code : code str
        debug : whether to print interpreter debugging message or not
        keep : whether to keep the interpreter's access memory for later investigation
        """
        self.code = code
        self.debug = debug
        self.keep = keep
        self.lex_code = self.lex()
        self.parsed_code = self.parse()
        self.mem = None

    def lex(self, code=None):
        """
        Provides the tokens sequence for the given code.

        Returns
        -------
        iterable containing the tokens
        """
        code = self.code if code is None else code
        lex_code = lexer.lex(code)
        return lex_code

    def parse(self, lcode=None):
        """
        Parse the data, structuring the tokens into data.

        Returns
        -------
        tuple of dictionaries, tuples and tokens
        """
        lcode = self.lex_code if lcode is None else lcode
        lex_code = deepcopy(lcode)
        parse_code = parser.parse(lex_code)
        parsed_code = parse_code.symbolic.table
        return parsed_code

    def eval(self, pcode=None):
        """
        Evaluate the intermediate representation code
        and execute the code
        """
        pcode = self.parsed_code if pcode is None else pcode
        ev = Eval(code=pcode, debug=self.debug)
        ev.walk(pcode)
        if self.keep:
            self.mem = ev.mem
        else:
            del ev.mem

    def run(self):
        """
        Bundle function to run all the previous functions
        """
        self.eval()
        print()
        if self.keep:
            print('Memory:')
            print(self.mem)
