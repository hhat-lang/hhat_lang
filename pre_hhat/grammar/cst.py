import os

from arpeggio import PTNodeVisitor, SemanticActionResults, visit_parse_tree
from arpeggio.cleanpeg import ParserPEG

import pre_hhat.operators.classical as poc
import pre_hhat.operators.quantum as poq
import pre_hhat.types.builtin as ptb
from pre_hhat.grammar.ast import AST
from pre_hhat.types.builtin import (SingleInt, ArrayInt, SingleStr, ArrayStr, ArrayCircuit)


def parsing_code():
    file_dir = os.path.dirname(__file__)
    grammar = open(os.path.join(file_dir, 'grammar.peg'), 'r').read()
    parser = ParserPEG(grammar, 'program', debug=True, reduce_tree=True)
    code = open('../../examples/quantum_add_int.hht', 'r').read()
    pt = parser.parse(code)
    return visit_parse_tree(pt, CST())


def get_oper(value, kind='classical'):
    for k in dir(poq if kind == 'quantum' else poc):
        if isinstance(p := getattr(poq, k), type):
            if value.upper() == p.name:
                return p()


class CST(PTNodeVisitor):
    def __init__(self, defaults=True, **kwargs):
        super().__init__(defaults=defaults, **kwargs)

    def visit_program(self, n, k):
        return AST('program', *k)

    def visit_main(self, n, k):
        return AST('main', *k)

    def visit_var_decl(self, n, k):
        if len(k) > 2:
            if isinstance(k[2], str):
                val = k[2].strip('@').capitalize()
                if getattr(poc, val, False) or getattr(poq, val, False):
                    k[2] = AST('assign', AST('assign_expr', AST('builtin_func', k[2])))
                else:
                    k[2] = AST('assign', AST('assign_expr', AST('id', k[2])))
        k[0], k[1] = k[1], k[0]
        return AST('var_decl', *k)

    def visit_type_expr(self, n, k):
        if isinstance(k[0], str):
            if getattr(ptb, k[0].capitalize(), False):
                k[0] = AST('builtin_type', k[0])
            else:
                k[0] = AST('user_type', k[0])
        return AST('type_expr', *k)

    def visit_var_assign(self, n, k):
        return AST('var_assign', *k)

    def visit_gen_call(self, n, k):
        pass

    def visit_assign(self, n, k):
        return AST('assign', *k)

    def visit_assign_expr(self, n, k):
        if isinstance(k[0], str):
            val = k[0].strip('@').capitalize()
            if getattr(poc, val, False) or getattr(poq, val, False):
                k[0] = AST('builtin_func', k[0])
            else:
                k[0] = AST('id', k[0])
        return AST('assign_expr', *k)

    def visit_index_expr(self, n, k):
        return AST('index_expr', *k)

    def visit_value_expr(self, n, k):
        return AST('value_expr', *k)

    def visit_caller(self, n, k):
        if isinstance(k[0], str):
            val = k[0].strip('@').capitalize()
            if getattr(poc, val, False) or getattr(poq, val, False):
                k[0] = AST('builtin_func', k[0])
            else:
                k[0] = AST('id', k[0])
        k = k[1], k[0]
        return AST('caller', *k)

    def visit_args(self, n, k):
        return AST('args', *k)

    def visit_id(self, n, k):
        return AST('id', n.value)

    def visit_INT(self, n, k):
        return SingleInt(n.value)

    def visit_STR(self, n, k):
        return SingleStr(n.value)


if __name__ == '__main__':
    res = parsing_code()
    print(res)
