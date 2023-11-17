from hhat_lang.syntax_trees.ast import (
    Main,
    Assign,
    Extend,
    Array,
    Conditional,
    Expr,
    Operation,
    Id,
    Literal,
    ExprParadigm,
    DataTypeEnum,
    BehaviorATO,
)
from hhat_lang.grammar import grammar_file
from arpeggio import visit_parse_tree, PTNodeVisitor
from arpeggio.cleanpeg import ParserPEG


class CST(PTNodeVisitor):
    def __init__(self, defaults=True, **kwargs):
        super().__init__(defaults=defaults, **kwargs)

    def set_behavior(self, behavior: BehaviorATO) -> BehaviorATO:
        return (
            behavior
            if behavior in (BehaviorATO.ASSIGN, BehaviorATO.EXTEND)
            else BehaviorATO.CALL
        )

    def visit_program(self, n, k):
        res = Array(ExprParadigm.CONCURRENT, *k)
        return Main(res)

    def visit_exprs(self, n, k):
        print(f"exprs -> {k}")
        new_k = ()
        has_q_var = any(p.has_q for p in k if not isinstance(p, str))
        behavior = BehaviorATO.CALL
        for p in k:
            if isinstance(p, Expr):
                if behavior:
                    p.edges[0].behavior = behavior
                    behavior = self.set_behavior(behavior)
                new_k += p.edges
            elif isinstance(p, (Assign, Extend)):
                behavior = p.behavior
            elif isinstance(p, Id):
                p.behavior = behavior
                new_k += p,
                behavior = self.set_behavior(behavior)
            elif isinstance(p, str):
                continue
            else:
                new_k += p,
        return Expr(*new_k, has_q=has_q_var)

    def visit_scope_id(self, n, k):
        print(f"scope id {n.value=}")
        if n.value == "?":
            return Conditional()
        return n.value

    def visit_pipe_assign(self, n, k):
        print(f"pipe/assign {n=} {k=}")
        if n.value == ":=":
            return Assign()
        if n.value == ":=+":
            return Extend()
        return

    def visit_parallel(self, n, k):
        has_q_var = all(p.has_q for p in k)
        return Array(ExprParadigm.PARALLEL, *k, has_q=has_q_var)

    def visit_concurrent(self, n, k):
        has_q_var = all(p.has_q for p in k)
        return Array(ExprParadigm.CONCURRENT, *k, has_q=has_q_var)

    def visit_sequential(self, n, k):
        has_q_var = all(p.has_q for p in k)
        return Array(ExprParadigm.SEQUENTIAL, *k, has_q=has_q_var)

    def visit_expr(self, n, k):
        print("EXPR!")
        if len(k) > 1:
            return Expr(*k)
        return k

    def visit_single(self, n, k):
        print("SINGLE!")
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
