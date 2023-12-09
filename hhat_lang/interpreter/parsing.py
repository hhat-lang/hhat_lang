from hhat_lang.syntax_trees.ast import (
    Main,
    Assign,
    Extend,
    Array,
    ScopeToAll,
    ScopeToEach,
    ScopeCond,
    Expr,
    Operation,
    Id,
    Literal,
    ExprParadigm,
    DataTypeEnum,
    BehaviorATO,
    ASTType,
)
from hhat_lang.grammar import grammar_file
from arpeggio import visit_parse_tree, PTNodeVisitor
from arpeggio.cleanpeg import ParserPEG


class CST(PTNodeVisitor):
    def __init__(self, defaults=True, **kwargs):
        super().__init__(defaults=defaults, **kwargs)

    @staticmethod
    def unfold_exprs(k):
        scope = None
        new_k = ()
        for p in k:
            if isinstance(p, (ScopeCond, ScopeToEach, ScopeToAll)):
                scope = p.token
            elif isinstance(p, Array):
                p.node = scope
                scope = None
                new_k += p,
            elif isinstance(p, (Assign, Extend)):
                print(f"  -> assign/extend {p}")
            elif isinstance(p, Expr):
                new_k += p.edges
            elif isinstance(p, Id):
                new_k += Operation(p, None),
            else:
                new_k += p,
        return new_k

    def define_q_exprs(self, k, assign_q=False):
        res = ()
        for p in k:
            if isinstance(p, (Expr, Array)):
                self.define_q_exprs(p.edges[::-1], assign_q)
                res += p,
            elif isinstance(p, Operation):
                p.assign_q = assign_q
                if p.node.behavior in (BehaviorATO.ASSIGN, BehaviorATO.EXTEND):
                    assign_q = p.node.is_q
                self.define_q_exprs(p.edges[::-1], assign_q)
                if any(x.assign_q for x in p.edges):
                    assign_q = True
                    p.assign_q = True
                res += p,
            elif isinstance(p, (Assign, Extend)):
                continue
            elif isinstance(p, Id):
                p.assign_q = assign_q
                res += p,
            else:
                p.assign_q = assign_q
                res += p,
        return res

    def visit_program(self, n, k):
        res = Array(ExprParadigm.CONCURRENT, *k)
        return Main(res)

    def visit_exprs(self, n, k):
        new_k = self.unfold_exprs(k)
        new_k = self.define_q_exprs(new_k[::-1])[::-1]
        return Expr(*new_k)

    def visit_scope_id(self, n, k):
        if n.value == "?":
            return ScopeCond()
        if n.value == ".":
            return ScopeToAll()
        if n.value == "/":
            return ScopeToEach()
        raise ValueError(f"Wrong value for scope id: '{n.value}'.")

    def visit_assign(self, n, k):
        if n.value == "=":
            return Assign()
        if n.value == "=+":
            return Extend()
        raise ValueError(f"Unknown value {k}")

    def visit_parallel(self, n, k):
        assign_q = all(p.assign_q for p in k)
        return Array(ExprParadigm.PARALLEL, *k, assign_q=assign_q)

    def visit_concurrent(self, n, k):
        assign_q = all(p.assign_q for p in k)
        return Array(ExprParadigm.CONCURRENT, *k, assign_q=assign_q)

    def visit_sequential(self, n, k):
        assign_q = all(p.assign_q for p in k)
        return Array(ExprParadigm.SEQUENTIAL, *k, assign_q=assign_q)

    def visit_pipe(self, n, k):
        return

    def visit_operation(self, n, k):
        if len(k) == 2:
            if k[0].type in (ASTType.ASSIGN, ASTType.EXTEND):
                k[1].behavior = k[0].behavior
                return Operation(k[1], None)
            return Operation(k[0], k[1])
        if len(k) == 3:
            k[1].behavior = k[0].behavior
            return Operation(k[1], k[2])
        return Operation(k[0], None)

    def visit_id(self, n, k):
        return Id(token=n.value)

    def visit_literal(self, n, k):
        return k[0]

    def visit_ATOMIC(self, n, k):
        return Literal(token=n.value, lit_type=DataTypeEnum.ATOMIC)

    def visit_INT(self, n, k):
        return Literal(token=n.value, lit_type=DataTypeEnum.INT)

    def visit_FLOAT(self, n, k):
        return Literal(token=n.value, lit_type=DataTypeEnum.FLOAT)

    def visit_STR(self, n, k):
        return Literal(token=n.value, lit_type=DataTypeEnum.STR)

    def visit_BIN(self, n, k):
        return Literal(token=n.value, lit_type=DataTypeEnum.BIN)

    def visit_HEX(self, n, k):
        return Literal(token=n.value, lit_type=DataTypeEnum.HEX)

    def visit_BOOL(self, n, k):
        return Literal(token=n.value, lit_type=DataTypeEnum.BOOL)


def parse_code(code):
    peg_grammar = open(grammar_file, "r").read()
    parsed_code = ParserPEG(peg_grammar, "program", reduce_tree=True, comment_rule_name="comment")
    pt = parsed_code.parse(code)
    return visit_parse_tree(pt, CST())
