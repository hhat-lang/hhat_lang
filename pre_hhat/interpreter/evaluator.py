"""Interpreter/Evaluator"""
from .pre_evaluator import PreEvaluator
from pre_hhat.core.memory import Memory, SymbolTable
from pre_hhat.grammar.ast import AST
from pre_hhat.operators.classical import (Add, Print)
from pre_hhat.operators.quantum import (X, H)
from pre_hhat.types.groups import (ArrayType, SingleType)
from pre_hhat.types.builtin import (SingleNull, SingleBool, SingleInt, SingleStr,
                                    ArrayBool, ArrayInt, ArrayStr, ArrayCircuit)


class Evaluator:
    def __init__(self, pre_eval_ast):
        if isinstance(pre_eval_ast, SymbolTable):
            self.code = pre_eval_ast
            self.main = Memory('main')
            self._ast_nodes = {'id': self.node_id,
                               'args': self.node_args,
                               'caller': self.node_caller,
                               'value_expr': self.node_value_expr,
                               'index_expr': self.node_index_expr,
                               'assign_expr': self.node_assign_expr,
                               'assign': self.node_assign,
                               'gen_call': self.node_gen_call,
                               'var_assign': self.node_var_assign,
                               'type_expr': self.node_type_expr,
                               'var_decl': self.node_var_decl}
            self._roles = {AST: self._ast_nodes,
                           ArrayType: self.data_types,
                           SingleType: self.literals}
        else:
            raise ValueError(f"{self.__class__.__name__}: ast must be of SymbolTable type (from PreEvaluator).")

    def literals(self, code, stats):

        return stats

    def data_types(self, code, stats):

        return stats

    def node_id(self, code, stats):
        return stats

    def node_args(self, code, stats):
        return stats

    def node_caller(self, code, stats):
        return stats

    def node_value_expr(self, code, stats):
        return stats

    def node_index_expr(self, code, stats):

        return stats

    def node_assign_expr(self, code, stats):

        return stats

    def node_assign(self, code, stats):

        return stats

    def node_gen_call(self, code, stats):

        return stats

    def node_var_assign(self, code, stats):

        return stats

    def node_type_expr(self, code, stats):

        return stats

    def node_var_decl(self, code, stats):

        return stats

    def walk_tree(self, code):
        pass


def run(code):
    ev = Evaluator()
