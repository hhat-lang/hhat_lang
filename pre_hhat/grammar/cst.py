import os

from arpeggio import PTNodeVisitor, SemanticActionResults, visit_parse_tree
from arpeggio.cleanpeg import ParserPEG

from pre_hhat import examples_dir
from pre_hhat.operators import classical as poc
from pre_hhat.operators import quantum as poq
from pre_hhat.grammar.ast import AST
from pre_hhat.types import get_type
from pre_hhat.types import SingleInt, SingleStr, SingleHashmap

examples = [
    "hello.hht",
    "simple_print.hht",
    "add_and_print.hht",
    "add_many_and_print.hht",
    "int_add_many_print.hht",
]


def parsing_code(example_name, print_code=False, debug=True):
    file_dir = os.path.dirname(__file__)
    grammar = open(os.path.join(file_dir, "grammar.peg"), "r").read()
    parser = ParserPEG(grammar, "program", debug=debug, reduce_tree=True)
    code = open(os.path.join(examples_dir, example_name), "r").readlines()
    if print_code:
        for k in code:
            print(f"      {k}")
    code = "".join(code)
    pt = parser.parse(code)
    return visit_parse_tree(pt, CST())


def get_oper(value, kind="classical"):
    for k in dir(poq if kind == "quantum" else poc):
        if isinstance(q := getattr(poq, k), type):
            if value.upper() == q.name:
                return q()


class CST(PTNodeVisitor):
    def __init__(self, defaults=True, **kwargs):
        super().__init__(defaults=defaults, **kwargs)

    def visit_program(self, n, k):
        return AST("program", *k)

    def visit_protocols(self, n, k):
        print(f"protocol = {k}")
        k[0] = AST("protocol", *tuple(q for q in k if not isinstance(example, str)))

    def visit_main(self, n, k):
        return AST("main", *k)

    def visit_var_decl(self, n, k):
        if len(k) > 2:
            if isinstance(k[2], str):
                val = k[2].strip("@").capitalize()
                if getattr(poc, val, False) or getattr(poq, val, False):
                    k[2] = AST(
                        "assign",
                        AST("assign_expr", (getattr(poc, val, None) or getattr(poq, val))()),
                    )
                else:
                    k[2] = AST("assign", AST("assign_expr", AST("id", k[2])))
        k[0], k[1] = k[1], k[0]
        return AST("var_decl", *k)

    def visit_type_expr(self, n, k):
        if isinstance(k[0], str):
            value = get_type(k[0].lower())
            if value:
                k[0] = value
            else:
                k[0] = AST("user_type", k[0])
        return AST("type_expr", *k)

    def visit_var_assign(self, n, k):
        return AST("var_assign", *k)

    def visit_gen_call(self, n, k):
        if isinstance(k[0], str):
            val = k[0].strip("@").capitalize()
            if getattr(poc, val, False) or getattr(poq, val, False):
                k[0] = (getattr(poc, val, None) or getattr(poq, val))()
            else:
                k[0] = AST("id", k[0])
            k = k[1], k[0]
        elif isinstance(k[0], AST) and isinstance(k[1], str):
            val = k[1].strip("@").capitalize()
            if getattr(poc, val, False) or getattr(poq, val, False):
                k[1] = (getattr(poc, val, None) or getattr(poq, val))()
            else:
                k[1] = AST("id", k[1])
            k = k[-1], k[-2]
            k = (AST("collect", *k),)
        return AST("gen_call", *k)

    def visit_assign(self, n, k):
        return AST("assign", *k)

    def visit_assign_expr(self, n, k):
        if len(k) == 1:
            if isinstance(k[0], str):
                val = k[0].strip("@").capitalize()
                if getattr(poc, val, False) or getattr(poq, val, False):
                    k[0] = (getattr(poc, val, None) or getattr(poq, val))()
                else:
                    k[0] = AST("id", k[0])
        elif len(k) == 2:
            if isinstance(k[0], str):
                val = k[0].strip("@").capitalize()
                if getattr(poc, val, False) or getattr(poq, val, False):
                    k[0] = (getattr(poc, val, None) or getattr(poq, val))()
                else:
                    k[0] = AST("id", k[0])
            if isinstance(k[0], AST):
                k[0] = AST("index_expr", *k[0])
            else:
                k[0] = AST("index_expr", k[0])

            if isinstance(k[1], str):
                val = k[1].strip("@").capitalize()
                if getattr(poc, val, False) or getattr(poq, val, False):
                    k[1] = (getattr(poc, val, None) or getattr(poq, val))()
                else:
                    k[1] = AST("id", k[1])
        return AST("assign_expr", *k)

    def visit_index_expr(self, n, k):
        return AST("index_expr", *k)

    def visit_value_expr(self, n, k):
        return AST("value_expr", *k)

    def visit_expr(self, n, k):
        return AST("expr", *k)

    def visit_caller(self, n, k):
        if len(k) < 3:
            if isinstance(k[0], str):
                val = k[0].strip("@").capitalize()
                if getattr(poc, val, False) or getattr(poq, val, False):
                    k[0] = (getattr(poc, val, None) or getattr(poq, val))()
                else:
                    k[0] = AST("id", k[0])
            k = k[1], k[0]
        else:
            if k[0] == "collect":
                k[0] = AST("collect", *(k[2], k[1]))
            k = (k[0],)
        return AST("caller", *k)

    def visit_args(self, n, k):
        return AST("args", *k)

    def visit_collect(self, n, k):
        return AST("collect", *k)

    def visit_id(self, n, k):
        return AST("id", n.value)

    def visit_INT(self, n, k):
        return SingleInt(n.value)

    def visit_STR(self, n, k):
        return SingleStr(n.value)

    def visit_HASHMAP(self, n, k):
        print(f"hashmap = {k}")
        return SingleHashmap(k)

    def visit_hash_expr(self, n, k):
        return k[0], k[2]


if __name__ == "__main__":
    for example in examples:
        res = parsing_code(example)
        print(res)
