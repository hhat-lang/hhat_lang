"""Evaluator"""

import time
import ast
from copy import deepcopy
from typing import Any
from rply.token import BaseBox, Token
from hhat_lang.tokens import tokens
from hhat_lang.lexer import lexer
from hhat_lang.parser import parser
from hhat_lang.new_ast import (Program, Function, FuncTemplate, Params, AThing, Body,
                               AttrDecl, Expr, ManyExprs, Entity, AttrAssign, Call,
                               Func, IfStmt, ElifStmt, ElseStmt, Tests, ForLoop)
from hhat_lang.builtin import (btin_print, btin_and, btin_or, btin_not, btin_eq, btin_neq,
                               btin_gt, btin_gte, btin_lt, btin_lte, btin_add, btin_mult,
                               btin_div, btin_pow, btin_sqrt, btin_q_h, btin_q_x, btin_q_z)


# noinspection PyArgumentList
class PreEval:
    def __init__(self, debug=True):
        self.debug = debug
        self.p = {'funcs': {}, 'main': {}, 'storage': {}}
        self.tasks = {tuple: self.exec_tuple,
                      Token: self.exec_token,
                      Program: self.exec_program,
                      Function: self.exec_func,
                      FuncTemplate: self.exec_functemplate,
                      Params: self.exec_params,
                      AThing: self.exec_athing,
                      Body: self.exec_body,
                      AttrDecl: self.exec_attrdecl,
                      Expr: self.exec_expr,
                      ManyExprs: self.exec_manyexprs,
                      Entity: self.exec_entity,
                      AttrAssign: self.exec_attrassign,
                      Call: self.exec_call,
                      Func: self.exec_func,
                      IfStmt: self.exec_ifstmt,
                      ElifStmt: self.exec_elifstmt,
                      ElseStmt: self.exec_elsestmt,
                      Tests: self.exec_tests,
                      ForLoop: self.exec_forloop
                      }
        self.methods = {'func': self.handle_func, 'main': self.handle_main}

    @staticmethod
    def init_data():
        return {}

    def build(self):
        pass

    def handle_func(self, state=None):
        res = None
        return res

    def handle_main(self, state=None):
        res = None
        return res

    def exec_token(self, code, state=None):
        res = None
        if code.value in self.methods.keys():
            res = self.methods[code.value]()
        return res

    def exec_tuple(self, code, state=None):
        old_state = deepcopy(state)
        for k in code:
            state = self.tasks[type(k)](k, state)
            if not state:
                break
        return old_state

    def exec_program(self, code, state=None):
        state = self.tasks[type(code)](code, state)
        return state

    def exec_function(self, code, state=None):
        state = self.tasks[type(code)](code, state)
        return state

    def exec_functemplate(self, code, state=None):
        return state

    def exec_params(self, code, state=None):
        return state

    def exec_athing(self, code, state=None):
        return state

    def exec_body(self, code, state=None):
        return state

    def exec_attrdecl(self, code, state=None):
        return state

    def exec_expr(self, code, state=None):
        return state

    def exec_manyexprs(self, code, state=None):
        return state

    def exec_entity(self, code, state=None):
        return state

    def exec_attrassign(self, code, state=None):
        return state

    def exec_call(self, code, state=None):
        return state

    def exec_func(self, code, state=None):
        return state

    def exec_ifstmt(self, code, state=None):
        return state

    def exec_elifstmt(self, code, state=None):
        return state

    def exec_elsestmt(self, code, state=None):
        return state

    def exec_tests(self, code, state=None):
        return state

    def exec_forloop(self, code, state=None):
        return state

    def walk(self, code, state=None):
        state = self.tasks[type(code)](code, state)

    def dprint(self, *msg, **msgs):
        if self.debug:
            print('1-[debug-pre_eval]', *msg, **msgs)


class Eval:
    def __init__(self):
        pass
