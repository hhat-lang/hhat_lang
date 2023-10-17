from hhat_ast import (Program, Expr, Operation, Array, Id, Literal)
from hhat_new_ast import (
    Main as NewMain,
    Expr as NewExpr,
    ManyExpr as NewManyExpr,
    Operation as NewOperation,
    Array as NewArray,
    Id as NewId,
    Literal as NewLiteral
)
from arpeggio import visit_parse_tree, PTNodeVisitor
from arpeggio.cleanpeg import ParserPEG


class CST(PTNodeVisitor):
    def __init__(self, defaults=True, **kwargs):
        super().__init__(defaults=defaults, **kwargs)

    def visit_program(self, n, k):
        # return Program(*k)
        # return NewMain(*k)
        res = tuple(NewManyExpr(p) for p in k)
        return NewMain(*res)

    def visit_exprs(self, n, k):
        # return Expr(*k)
        return NewExpr(*k)

    def visit_expr(self, n, k):
        if len(k) > 1:
            # return Expr(*k)
            return NewManyExpr(*k)  # NewExpr(*k)
        return k[0]

    def visit_operation(self, n, k):
        if len(k) > 1:
            # return Operation(k[0], *k[1:])
            return NewOperation(k[0], *k[1:])
        # return Operation(k[0])
        return NewOperation(k[0])

    def visit_array(self, n, k):
        # return Array(*k)
        return NewArray(*k)

    def visit_id(self, n, k):
        # return Id(n.value)
        return NewId(n.value)

    def visit_literal(self, n, k):
        return k[0]

    def visit_BOOL(self, n, k):
        # return Literal(n.value, "bool")
        return NewLiteral(n.value, "bool")

    def visit_INT(self, n, k):
        # return Literal(n.value, "int")
        return NewLiteral(n.value, "int")


def parse_code(code):
    peg_grammar = open("grammar.peg", "r").read()
    parsed_code = ParserPEG(peg_grammar, "program", reduce_tree=False)
    pt = parsed_code.parse(code)
    return visit_parse_tree(pt, CST())
