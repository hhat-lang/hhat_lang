"""Interpreter/Evaluator"""
from copy import deepcopy

from pre_hhat.core.memory import Memory, SymbolTable
from pre_hhat.grammar.ast import AST
from pre_hhat.operators.builtin import Operators
from pre_hhat.operators.classical import (Add, Print)
from pre_hhat.operators.quantum import (X, H)
from pre_hhat.types.groups import (ArrayType, SingleType)
from pre_hhat.types.builtin import (SingleNull, SingleBool, SingleInt, SingleStr,
                                    ArrayBool, ArrayInt, ArrayStr, ArrayCircuit)


class EvalStack:
    pass


# noinspection PyArgumentList,PyStatementEffect
class Evaluator:
    def __init__(self, pre_eval_ast):
        if isinstance(pre_eval_ast, SymbolTable):
            self.code = pre_eval_ast
            self.main = self.code['main']
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
            self._roles = {ArrayType: self.data_types,
                           SingleType: self.literals,
                           tuple: self.role_tuple,
                           dict: self.role_dict}
        else:
            raise ValueError(f"{self.__class__.__name__}: ast must be of SymbolTable type (from PreEvaluator).")

    @staticmethod
    def _new_stack():
        return {'var': None,
                'res': (),
                'index': (),
                'scope': None,
                'mem': Memory(),
                'upstream': False}

    def init_main(self, stack):
        stack['scope'] = 'main'
        stack['mem'].init('main')
        return self.main

    def get_node(self, node, stack):
        return self._roles.get(type(node), self._get_ast_node(node))(node, stack)

    def _get_ast_node(self, node):
        return self._ast_nodes[node.name] if isinstance(node, AST) else None

    def role_dict(self, code, stack):
        print('got into role dict')
        for k, v in code.items():
            if k == 'main':
                stack['scope'] = 'main'
                stack['mem'].init('main')
                stack = self.get_node(v, stack)
            else:
                break
        return stack

    def role_tuple(self, code, stack):
        old_stack = deepcopy(stack)
        for k in code:
            stack = self.get_node(k, stack)

        if stack['upstream']:
            return stack
        return old_stack

    def literals(self, code, stack):

        return stack

    def data_types(self, code, stack):

        return stack

    def node_id(self, code, stack):

        return stack

    def node_args(self, code, stack):
        stack['res'] += code.value
        return stack

    def node_caller(self, code, stack):
        args = self.get_node(code.value[0], stack)['res']
        if not stack['index']:
            stack['index'] = stack['mem'][stack['var']]
        res = code.value[1](*(stack['res'], stack['index']))
        if res:
            stack['mem'][stack['var']] = res
        stack['res'] = ()
        stack['index'] = ()
        return stack

    def node_value_expr(self, code, stack):
        return stack

    def node_index_expr(self, code, stack):

        return stack

    def node_assign_expr(self, code, stack):
        if len(code.value) == 1:
            stack['index'] = stack['mem'][stack['var']]
            if isinstance(code.value[0], Operators):
                res = code.value[0](*stack['index'])
                if res:
                    stack['mem'][stack['var']] = res
            else:
                stack = self.get_node(code.value[0], stack)
        elif len(code.value) == 2:
            print('hoi')
        else:
            pass
        return stack

    def node_assign(self, code, stack):
        for k in code:
            stack = self.get_node(k, stack)
        return stack

    def node_gen_call(self, code, stack):
        args = self.get_node(code.value[0], stack)
        code.value[1](*(stack['res']))
        return stack

    def node_var_assign(self, code, stack):

        return stack

    def node_type_expr(self, code, stack):

        return stack

    def node_var_decl(self, code, stack):
        for n, k in enumerate(code):
            if n == 0:
                stack['var'] = k
            elif n == 1:
                stack['mem'][stack['var'], k]
            else:
                stack = self.get_node(k, stack)
        return stack

    def walk_tree(self, code=None, stack=None):
        stack = self._new_stack() if stack is None else stack
        code = self.init_main(stack) if code is None else code
        return self.get_node(code, stack)


def run(code):
    ev = Evaluator(code)
    ev.walk_tree()
