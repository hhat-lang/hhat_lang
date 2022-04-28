"""Pre Eval"""


from copy import deepcopy
from rply.token import Token
try:
    from new_ast import (SuperBox, Function, FuncTemplate, Params,
                         Body, ManyExprs, IfStmt, ElifStmt, ElseStmt, Tests)
    from symbolic import Scope, FuncScopeTable, BranchScopeTable
except ImportError:
    from hhat_lang.new_ast import (SuperBox, Function, FuncTemplate, Params,
                                   Body, ManyExprs, IfStmt, ElifStmt, ElseStmt, Tests)
    from hhat_lang.symbolic import Scope, FuncScopeTable, BranchScopeTable


# noinspection PyArgumentList
class PreEval:
    def __init__(self):
        self.fst = FuncScopeTable()
        self.stats = {'cur_scope': Scope.NONE, 'cur_attr': '', 'cur_func': None, 'cur_expr': ''}
        self.walk_handler = {tuple: self.walk_tuple,
                             SuperBox: self.walk_superbox,
                             Token: self.walk_token}

    def walk_tuple(self, code):
        old_stats = deepcopy(self.stats)
        for k in code:
            self.walk(k)
        self.stats = old_stats

    def walk_superbox(self, code):
        if isinstance(code, Function):
            pass
        elif isinstance(code, FuncTemplate):
            pass
        elif isinstance(code, Params):
            pass
        elif isinstance(code, Body):
            pass
        elif isinstance(code, ManyExprs):
            if isinstance(self.stats['cur_func'], Token):
                if self.stats['cur_func'].value == 'return':
                    self.stats['cur_expr'] = 'return'
        elif isinstance(code, (IfStmt, ElifStmt, ElseStmt)):
            pass
        elif isinstance(code, Tests):
            pass

    def walk_token(self, code):
        if code.name == 'MAIN':
            self.stats['cur_scope'] = Scope.MAIN
        elif code.name == 'FUNCTION':
            self.stats['cur_scope'] = Scope.FUNCS
        elif code.name == 'SYMBOL':
            if self.stats['cur_func'] == FuncTemplate:
                self.fst.add([self.stats['cur_scope'], code.value])
                self.stats['cur_attr'] = code.value
        elif 'TYPE' in code.name:
            self.fst[self.stats['cur_scope'], self.stats['cur_attr'], 'type'] = code.value
        elif code.name == 'RETURN':
            self.stats['cur_func'] = code


    def walk(self, code):
        if isinstance(code, SuperBox):
            self.walk_handler[SuperBox](code)
        elif isinstance(code, tuple):
            self.walk_handler[tuple](code)
        elif isinstance(code, Token):
            self.walk_handler[Token](code)

    def code_exec(self, code):
        self.walk(code)
