from hhat_lang.syntax_trees.ast import (
    Main,
    Array,
    Expr,
    Operation,
    Id,
    Literal,
    ExprParadigm,
    DataTypeEnum,
)
from hhat_lang.grammar import grammar_file
from arpeggio import visit_parse_tree, PTNodeVisitor
from arpeggio.cleanpeg import ParserPEG


class CST(PTNodeVisitor):
    def __init__(self, defaults=True, **kwargs):
        super().__init__(defaults=defaults, **kwargs)

    def visit_program(self, n, k):
        res = Array(ExprParadigm.CONCURRENT, *k)
        return Main(res)

    def visit_exprs(self, n, k):
        new_k = ()
        for p in k:
            if isinstance(p, Expr):
                new_k += p.edges
            else:
                new_k += p,
        return Expr(*new_k)

    def visit_parallel(self, n, k):
        return Array(ExprParadigm.PARALLEL, *k)

    def visit_concurrent(self, n, k):
        return Array(ExprParadigm.CONCURRENT, *k)

    def visit_sequential(self, n, k):
        return Array(ExprParadigm.SEQUENTIAL, *k)

    def visit_expr(self, n, k):
        if len(k) > 1:
            return Expr(*k)
        return k

    def visit_single(self, n, k):
        return Expr(*k)

    def visit_operation(self, n, k):
        if len(k) > 1:
            return Operation(k[0], k[1])
        return Operation(k[0], None)

    def visit_id(self, n, k):
        return Id(token=n.value)

    def visit_literal(self, n, k):
        return k[0]

    def visit_INT(self, n, k):
        return Literal(token=n.value, lit_type=DataTypeEnum.INT)

    def visit_BOOL(self, n, k):
        return Literal(token=n.value, lit_type=DataTypeEnum.BOOL)


def parse_code(code):
    peg_grammar = open(grammar_file, "r").read()
    parsed_code = ParserPEG(peg_grammar, "program", reduce_tree=True)
    pt = parsed_code.parse(code)
    return visit_parse_tree(pt, CST())
