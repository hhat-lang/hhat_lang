"""Setting up the AST for evaluation"""
from pre_hhat.core.memory import SymbolTable
from pre_hhat.types.groups import BaseGroup
from pre_hhat.grammar.ast import AST


class PreEvaluator:
    def __init__(self, code):
        self.code = code
        self.table = SymbolTable()

    def walk_tree(self, code=None):
        if code is None:
            code = self.code
        res = None
        if isinstance(code, tuple):
            for k in code:
                res = self.walk_tree(k)
                if res is not None:
                    break
        if isinstance(code, AST):
            if code.name == 'main':
                self.table[code.name] = code.value
                res = self.table
            else:
                res = self.walk_tree(code.value)
        return res
