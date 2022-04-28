"""Symbolic for Pre Evaluation"""

"""
AST = tuple of objects (new_ast) 

FuncScopeTable - splits into 'main' and other functions funcs. i.e.: {'main': {}, 'funcs': {}}
VarScopeTable
BranchScopeTable



example:

func int Sum (int x, int y) ( return (add(x y)) )

main null X: ( 
 int a = (:3, :print('aoa'), :add(5), :print)
 int(3) b = (:10, 0:add(5), (1 2):add(-5), :print, (0 1):print('oi'))
 print(Sum(a b))
)

Program(
        Function(Token(function), (FuncTemplate(Symbol(Sum), Type(int), Params(...), Body(...)))),
        Function(Token(main), (FuncTemplate(Symbol(X), Type(null), Body(...)))),
        ...
        )

PreEvaluator -> 
(
    FST = {'main': {'X': (main's AST)},
           'funcs': {'Sum': (func's AST)}}
    VST = {'main': {'X': {'a': {'len': 1, 'type': 'int', 'data': {0: current_value}}},
                     {'b': {'len': 3, 'type': 'int', 'data': {0: cur, 1: cur, 2: cur}
                }},
            'funcs': {}}
    BST = {0: (AST body1 + exit_cond_body), ...}
)

Evaluator -> 
(
    AST = (FST(main(X)),)
)
"""

from copy import deepcopy
from enum import Enum, auto
from rply import Token
from hhat_lang.new_ast import (Function, FuncTemplate, Params, AThing, Body,
                               AttrDecl, Expr, ManyExprs, Entity, AttrAssign,
                               Call, Func, IfStmt, ElifStmt, ElseStmt, Tests,
                               ForLoop, Range, IndexAssign, ParamsSeq, TypeExpr,
                               AttrHeader, Args, ExitBody, SuperBox)


class Scope(Enum):
    NONE = None
    MAIN = 'main'
    FUNCS = 'func'
    SCOPE = auto()


class FuncScopeTable:
    table = {Scope.MAIN: {}, Scope.FUNCS: {}, Scope.SCOPE: {}}
    main_counter = 0

    def add(self, key):
        self.__setitem__(key, None)

    def __setitem__(self, key, value):
        if isinstance(key, (tuple, list)):
            if len(key) == 2:
                scope, name = key
                if name not in self.table[Scope.SCOPE].keys():
                    self.table[scope][name] = {'type': None, 'params': (), 'body': {}, 'return': {}}
                    self.table[Scope.SCOPE].update({name: scope})
                else:
                    raise ValueError(f"Only two values provided for {name} to be created.")
            elif len(key) == 3:
                scope, name, sec = key
                if name not in self.table[Scope.SCOPE].keys():
                    self.table[scope][name] = {'type': None, 'params': (), 'body': {}, 'return': {}}
                    self.table[Scope.SCOPE].update({name: scope})
                    if sec in self.table[scope][name].keys():
                        self.table[scope][name].update({sec: value})
                    else:
                        raise ValueError(f"Cannot find '{sec}' on {name} keys.")
                else:
                    if scope == self.table[Scope.SCOPE][name]:
                        if sec in self.table[scope][name].keys():
                            self.table[scope][name].update({sec: value})
                        else:
                            raise ValueError(f"Cannot find '{sec}' on {name} keys.")
                    else:
                        raise ValueError(f"Wrong function type ('{scope}') for '{name}'.")
            else:
                raise ValueError("FuncScopeTable needs 2 or 3 arguments.")
        else:
            if key in self.table[Scope.SCOPE].keys():
                if isinstance(value, dict):
                    self.table[self.table[Scope.SCOPE][key]][key].update(value)
                else:
                    self.table[self.table[Scope.SCOPE][key]][key] = value
            else:
                raise ValueError(f"No main or func '{key}' found.")

    def __getitem__(self, key):
        if key in self.table[Scope.SCOPE].keys():
            return self.table[self.table[Scope.SCOPE][key]][key]
        raise ValueError(f"No main or func '{key}' found.")

    def __repr__(self):
        return f"{self.table}"


class VarScopeTable:
    table = {Scope.MAIN: {}, Scope.FUNCS: {}, Scope.SCOPE: {}}

    def __setitem__(self, key, value):
        if isinstance(key, (tuple, list)):
            if len(key) == 3:
                scope, name, attr = key
                if name not in self.table[Scope.SCOPE].keys():
                    if scope in [Scope.MAIN, Scope.FUNCS]:
                        self.table[Scope.SCOPE].update({name: scope})
                    else:
                        raise ValueError("Wrong scope name. Should be from 'main' or 'func'.")
                else:
                    self.table[scope][name].update({attr: value})

            elif len(key) == 2:
                name, attr = key
                if name not in self.table[Scope.SCOPE].keys():
                    raise ValueError(
                        f"No main or func parameter found. Cannot decide where to put '{name}'.")
                else:
                    self.table[self.table[Scope.SCOPE][name]][name].update({attr: value})

        else:
            raise ValueError("Should be at least two parameters: function name and attribute.")

    def __getitem__(self, key):
        if isinstance(key, tuple):
            if len(key) == 3:
                scope, name, attr = key
                return self.table[scope][name][attr]
            if len(key) == 2:
                name, attr = key
                return self.table[self.table[Scope.SCOPE][name]][name][attr]
        raise ValueError("Wrong type or number os arguments for key.")

    def __repr__(self):
        return f"{self.table}"


class BranchScopeTable:
    table = {}
    count = 0

    def __init__(self):
        pass

    def __iadd__(self, value):
        self.table[self.count] = value
        self.count += 1
        return self

    def __getitem__(self, key):
        try:
            return self.table[key]
        except ValueError:
            raise ValueError(f"No key '{key}' found.")

    def __setitem__(self, key, value):
        if key in self.table.keys():
            self.table[key] = value
        else:
            raise ValueError(f"Cannot set a key not present in the table.")

    def add(self, value):
        return self.__iadd__(value)

    def get(self, key):
        return self.__getitem__(key)


# noinspection PyArgumentList
class Symbolic:
    def __init__(self):
        self.stats = {'cur_branch': None,
                      'cur_var': None,
                      'cur_scope': None,
                      'cur_seq': None,
                      'cur_token': None,
                      'cur_attr': None,
                      'after_type': None,
                      'call_funcs': None,
                      'branch': False,
                      'var': False,
                      'scope': False}
        self.count = 0
        self.branch = BranchScopeTable()
        self.var = VarScopeTable()
        self.funcs = FuncScopeTable()
        self.sym_dict = {Function: self.ast_function,
                         FuncTemplate: self.ast_func_template,
                         Params: self.ast_params,
                         AThing: self.ast_athing,
                         Body: self.ast_body,
                         AttrDecl: self.ast_attr_decl,
                         Expr: self.ast_expr,
                         ManyExprs: self.ast_many_exprs,
                         Entity: self.ast_entity,
                         AttrAssign: self.ast_attr_assign,
                         Call: self.ast_call,
                         Func: self.ast_func,
                         IfStmt: self.ast_if_stmt,
                         ElifStmt: self.ast_elif_stmt,
                         ElseStmt: self.ast_else_stmt,
                         Tests: self.ast_tests,
                         ForLoop: self.ast_for_loop,
                         Token: self.ast_token,
                         Range: self.aux_range,
                         IndexAssign: self.aux_index_assign,
                         ParamsSeq: self.aux_param_seq,
                         TypeExpr: self.aux_type_expr,
                         AttrHeader: self.aux_attr_header,
                         Args: self.aux_args,
                         ExitBody: self.aux_exit_body,
                         tuple: self.tuple_handler,
                         str: self.str_handler
                         }
        self.token_dict = {'MAIN': self.main_handler,
                           'FUNCTION': self.func_handler,
                           'SYMBOL': self.symbol_handler,
                           'QSYMBOL': self.qsymbol_handler,
                           'BUILTIN': self.builtin_handler,
                           'GATE': self.gate_handler,
                           'LITERAL': self.literal_handler,
                           'TYPE': self.type_handler,
                           'LOGOP': self.logop_handler,
                           'OP': self.op_handler}

    ###################
    # MISC FUNCTIONS #
    ##################

    @staticmethod
    def get_token_name(code):
        res = code.name.split('_')
        if len(res) == 1:
            return res[0]
        if len(res) == 2:
            return res[1]

    #############################
    # DATA STRUCTURE FUNCTIONS #
    ############################

    def tuple_handler(self, code):
        old_stats = deepcopy(self.stats)
        new_code = {'after_type': deepcopy(code)}
        for k in new_code['after_type']:
            if self.stats['scope']:
                if self.stats['cur_token'] == 'TYPE':
                    if self.stats['cur_seq'] == Params:
                        self.funcs[self.stats['cur_scope'],
                                   self.stats['cur_attr']].update({'params': {}})
                    elif self.stats['cur_seq'] == Body:
                        self.funcs[self.stats['cur_scope'],
                                   self.stats['cur_attr']].update({'body': {}})
                self.funcs[self.stats['cur_scope'], self.stats['cur_attr']] = k
                new_k = self.funcs[self.stats['cur_scope'], self.stats['cur_attr']]
                self.stats['scope'] = False
                self.sym_dict[type(new_k)](new_k)
            else:
                self.sym_dict[type(k)](k)
        self.stats = old_stats

    def str_handler(self, code):
        pass

    ####################
    # TOKEN FUNCTIONS #
    ###################

    def main_handler(self, code):
        self.stats['cur_scope'] = Scope.MAIN
        self.stats['scope'] = True
        self.stats['cur_token'] = self.get_token_name(code)

    def func_handler(self, code):
        self.stats['cur_scope'] = Scope.FUNCS
        self.stats['scope'] = True
        self.stats['cur_token'] = self.get_token_name(code)

    def symbol_handler(self, code):
        self.stats['cur_attr'] = code.value
        self.stats['cur_token'] = self.get_token_name(code)
        if self.stats['cur_seq'] == Function:
            self.stats['scope'] = True
        elif self.stats['cur_seq'] == AttrDecl:
            # self.var[self.stats['cur_scope'], code.value] = {}
            pass

    def qsymbol_handler(self, code):
        self.symbol_handler(code)
        self.stats['cur_token'] = self.get_token_name(code)

    def builtin_handler(self, code):
        self.stats['cur_token'] = self.get_token_name(code)

    def gate_handler(self, code):
        self.stats['cur_token'] = self.get_token_name(code)

    def literal_handler(self, code):
        self.stats['cur_token'] = self.get_token_name(code)

    def type_handler(self, code):
        self.stats['cur_token'] = self.get_token_name(code)
        if self.stats['cur_seq'] == Function:
            self.stats['scope'] = True
        elif self.stats['cur_seq'] == AttrDecl:
            self.funcs[self.stats['cur_scope'], self.stats['cur_attr']]['type'] = code.value

    def logop_handler(self, code):
        self.stats['cur_token'] = self.get_token_name(code)

    def op_handler(self, code):
        self.stats['cur_token'] = self.get_token_name(code)

    ##################
    # AST FUNCTIONS #
    #################

    def ast_token(self, code):
        self.token_dict[self.get_token_name(code)](code)

    def ast_function(self, code):
        self.stats['cur_seq'] = Function
        self.sym_dict[type(code.value)](code.value)

    def ast_func_template(self, code):
        self.sym_dict[type(code.value)](code.value)

    def ast_params(self, code):
        self.stats['cur_seq'] = Params
        self.sym_dict[type(code.value)](code.value)

    def ast_athing(self, code):
        self.sym_dict[type(code.value)](code.value)

    def ast_body(self, code):
        self.stats['cur_seq'] = Body
        self.sym_dict[type(code.value)](code.value)

    def ast_attr_decl(self, code):
        self.stats['cur_seq'] = AttrDecl
        self.sym_dict[type(code.value)](code.value)
        self.stats['cur_var'] = None

    def ast_expr(self, code):
        self.sym_dict[type(code.value)](code.value)

    def ast_many_exprs(self, code):
        self.sym_dict[type(code.value)](code.value)

    def ast_entity(self, code):
        self.sym_dict[type(code.value)](code.value)

    def ast_attr_assign(self, code):
        self.sym_dict[type(code.value)](code.value)

    def ast_call(self, code):
        self.stats['cur_seq'] = Call
        self.sym_dict[type(code.value)](code.value)

    def ast_func(self, code):
        pass

    def ast_if_stmt(self, code):
        pass

    def ast_elif_stmt(self, code):
        pass

    def ast_else_stmt(self, code):
        pass

    def ast_tests(self, code):
        pass

    def ast_for_loop(self, code):
        pass

    ########################
    # AUXILIARY FUNCTIONS #
    #######################

    def aux_range(self, code):
        pass

    def aux_index_assign(self, code):
        pass

    def aux_param_seq(self, code):
        pass

    def aux_type_expr(self, code):
        pass

    def aux_attr_header(self, code):
        pass

    def aux_args(self, code):
        pass

    def aux_exit_body(self, code):
        pass


""" 
AST = (Function(main), FuncTemplate(Symbol(X), Type(int), Body(....)))
FuncTemplate.value = (...)
tuple1 = (0, (FuncTemplate(...))...
for k in tuple[1]:
    k.value = 'o'
tuple[1] -> FST['main']['X']['data'][VST(0)]

FST['funcs']['F1']...
"""

FST = FuncScopeTable()
VST = VarScopeTable()


def walk0(code, stats=None):
    """
    - cur_stack = params, body, return
    - scope =
    Parameters
    ----------
    code
    stats

    Returns
    -------

    """
    if stats is None:
        stats = {'cur_obj': None,
                 'cur_attr': None,
                 'scope': None,
                 'cur_func': None,
                 'cur_stack': None}

    if isinstance(code, tuple):
        if stats['scope'] == 'FST':
            FST[stats['cur_func'], stats['cur_attr'], stats['cur_stack']] = code
            stats['scope'] = None

        old_stats = deepcopy(stats)
        for k in code:
            stats = walk0(k, stats)
        stats = old_stats

    elif isinstance(code, Token):
        if code.name == 'SYMBOL':
            if stats['cur_obj'] == FuncTemplate:
                stats['cur_attr'] = code.value

        elif code.name == 'MAIN':
            stats['cur_func'] = 'main'
            stats['scope'] = 'FST'

        elif code.name == 'FUNCTION':
            stats['cur_func'] = 'funcs'

        else:
            if stats['cur_obj'] == FuncTemplate:
                if 'TYPE' in code.name:
                    FST[stats['cur_func'], stats['cur_attr'], 'type'] = code.value


    elif isinstance(code, SuperBox):
        if isinstance(code, Function):
            stats['cur_obj'] = Function
        elif isinstance(code, FuncTemplate):
            stats['cur_obj'] = FuncTemplate
        elif isinstance(code, Body):
            stats['cur_obj'] = Body
        elif isinstance(code, AttrDecl):
            stats['cur_obj'] = AttrDecl
        elif isinstance(code, AttrAssign):
            stats['cur_obj'] = AttrAssign

    else:
        print('fudeu')
    return stats


# CÓDIGO:
# main null X: (
#   int a = (:3, :add(5))
#   int b
#   a (:add(10))
# )
#

""" 
# ANTES
AST = Program((Function(Token('main'), FuncTemplate((Symbol('X'), Type('null')),
                                                    Body(AttrDecl(Symbol('a'), Type('int'),
                                                                  AttrAssign(Call(Int(3)))))))), )

# DEPOIS
AST = Program((FST['main', 'X', 'params'], FST['main', 'X', 'body'], FST['main', 'X', 'return'],))

FST = {'main':
           {'X':
                {'type': 'null',
                 'params': (),
                 'body': (AttrDecl((Symbol('a'), Type('int'), (AttrAssign(Call(Int(3))),
                                                               AttrAssign(Call(Args((Int(5),)),
                                                                               Token('add'))),
                                                               AttrAssign(Call(Token('print')))
                                                               )
                                    )),
                          ),
                 'return': ()}
            }
       }

VST = {'X':}
->
"""