import os

from arpeggio import PTNodeVisitor, SemanticActionResults, visit_parse_tree
from arpeggio.cleanpeg import ParserPEG

from pre_hhat import examples_dir
from pre_hhat.operators import classical as poc
from pre_hhat.operators import quantum as poq
from pre_hhat.types import builtin as ptb
from pre_hhat.grammar.ast import AST
import pre_hhat.types.builtin as builtin
from pre_hhat.types.builtin import (SingleInt, SingleStr,
                                    ArrayInt, ArrayStr, ArrayCircuit)


examples = ['hello.hht',
            'simple_print.hht',
            'add_and_print.hht',
            'add_many_and_print.hht',
            'int_add_many_print.hht']


def parsing_code(example, print_code=False, debug=True):
    file_dir = os.path.dirname(__file__)
    grammar = open(os.path.join(file_dir, 'grammar.peg'), 'r').read()
    parser = ParserPEG(grammar, 'program', debug=debug, reduce_tree=True)
    code = open(os.path.join(examples_dir, example), 'r').readlines()
    if print_code:
        for k in code:
            print(f'      {k}')
    code = ''.join(code)
    pt = parser.parse(code)
    return visit_parse_tree(pt, CST())


def get_oper(value, kind='classical'):
    for k in dir(poq if kind == 'quantum' else poc):
        if isinstance(q := getattr(poq, k), type):
            if value.upper() == q.name:
                return q()


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
                    k[2] = AST('assign',
                               AST('assign_expr', (getattr(poc, val, None) or getattr(poq, val))()))
                else:
                    k[2] = AST('assign', AST('assign_expr', AST('id', k[2])))
        k[0], k[1] = k[1], k[0]
        return AST('var_decl', *k)

    def visit_type_expr(self, n, k):
        if isinstance(k[0], str):
            value = builtin.get_type(k[0].lower())
            if value:
                k[0] = value
            else:
                k[0] = AST('user_type', k[0])
        return AST('type_expr', *k)

    def visit_var_assign(self, n, k):
        return AST('var_assign', *k)

    def visit_gen_call(self, n, k):
        if isinstance(k[0], str):
            val = k[0].strip('@').capitalize()
            if getattr(poc, val, False) or getattr(poq, val, False):
                k[0] = (getattr(poc, val, None) or getattr(poq, val))()
            else:
                k[0] = AST('id', k[0])
        k = k[1], k[0]
        return AST('gen_call', *k)

    def visit_assign(self, n, k):
        return AST('assign', *k)

    def visit_assign_expr(self, n, k):
        if len(k) == 1:
            if isinstance(k[0], str):
                val = k[0].strip('@').capitalize()
                if getattr(poc, val, False) or getattr(poq, val, False):
                    k[0] = (getattr(poc, val, None) or getattr(poq, val))()
                else:
                    k[0] = AST('id', k[0])
        elif len(k) == 2:
            if isinstance(k[0], str):
                val = k[0].strip('@').capitalize()
                if getattr(poc, val, False) or getattr(poq, val, False):
                    k[0] = (getattr(poc, val, None) or getattr(poq, val))()
                else:
                    k[0] = AST('id', k[0])
            if isinstance(k[0], AST):
                k[0] = AST('index_expr', *k[0])
            else:
                k[0] = AST('index_expr', k[0])

            if isinstance(k[1], str):
                val = k[1].strip('@').capitalize()
                if getattr(poc, val, False) or getattr(poq, val, False):
                    k[1] = (getattr(poc, val, None) or getattr(poq, val))()
                else:
                    k[1] = AST('id', k[1])
        return AST('assign_expr', *k)

    def visit_index_expr(self, n, k):
        return AST('index_expr', *k)

    def visit_value_expr(self, n, k):
        return AST('value_expr', *k)

    def visit_expr(self, n, k):
        return AST('expr', *k)

    def visit_caller(self, n, k):
        if isinstance(k[0], str):
            val = k[0].strip('@').capitalize()
            if getattr(poc, val, False) or getattr(poq, val, False):
                k[0] = (getattr(poc, val, None) or getattr(poq, val))()
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
    for p in examples:
        res = parsing_code(p)
        print(res)
