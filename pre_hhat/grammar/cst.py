import os

from arpeggio import PTNodeVisitor, SemanticActionResults, visit_parse_tree, RegExMatch as reg
from arpeggio.cleanpeg import ParserPEG

from pre_hhat import examples_files as examples
import pre_hhat.types as types
from pre_hhat import examples_dir
from pre_hhat.operators import classical as poc
from pre_hhat.operators import quantum as poq
from pre_hhat.grammar.ast import AST


def parsing_code(example_name, print_code=False, debug=True, reduce_tree=True):
    file_dir = os.path.dirname(__file__)
    grammar = open(os.path.join(file_dir, "grammar.peg"), "r").read()
    parser = ParserPEG(grammar, "program", debug=debug, reduce_tree=reduce_tree)
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

    @staticmethod
    def _define_str(value):
        new_value = value.strip("@").capitalize()
        if getattr(poc, new_value, False) or getattr(poq, new_value, False):
            return (getattr(poc, new_value, None) or getattr(poq, new_value))()
        return AST("id", value)

    def visit_program(self, n, k):
        return AST("program", *k)

    def visit_protocols(self, n, k):
        print(f"protocol = {k}")
        k[0] = AST("protocol", *tuple(q for q in k if not isinstance(example, str)))
        return k

    def visit_funcs(self, n, k):
        if k[2].name == "params":
            if len(k) > 2:
                k = k[1], k[0], k[2], AST("func_body", *k[3:])
            else:
                k = k[1], k[0], k[2]
        else:
            k = k[1], k[0], AST("func_body", *k[2:])
        return AST("func", *k)

    def visit_params(self, n, k):
        vals = ()
        for p in range(0, len(k), 2):
            k[p] = (k[p].value[0], k[p].value[1]) if len(k[p].value) == 2 else k[p].value
            vals += (k[p+1], k[p]),
        return AST("params", *vals)

    def visit_func_body(self, n, k):
        return AST("func_body", *k)

    def visit_main(self, n, k):
        return AST("main", *k)

    def visit_var_decl(self, n, k):
        if len(k) > 2:
            for n, p in enumerate(k):
                if isinstance(p, str):
                    k[n] = AST("assign", AST("assign_expr", AST("value_expr", self._define_str(p))))
                elif isinstance(p, types.SingleType):
                    k[n] = AST("assign", AST("assign_expr", AST("value_expr", p)))
                elif isinstance(p, AST):
                    if p.name in ["caller", "expr"]:
                        k[n] = AST("assign", AST("assign_expr", AST("value_expr", p)))
        k[0], k[1] = k[1], k[0]
        return AST("var_decl", *k)

    def visit_type_expr(self, n, k):
        if isinstance(k[0], str):
            value = types.get_type(k[0].lower())
            if value:
                k[0] = value
            else:
                k[0] = AST("user_type", k[0])
        return AST("type_expr", *k)

    def visit_var_assign(self, n, k):
        return AST("var_assign", *k)

    def visit_gen_call(self, n, k):
        for n, p in enumerate(k):
            if isinstance(p, str):
                if p != "collect":
                    k[n] = self._define_str(p)
        if k[0] == "collect":
            k[0] = AST("collect", *(k[2], k[1], *k[3:]))
            k = [k[0]]
        else:
            k = [k[1], k[0], *k[2:]]
        return AST("gen_call", *k)

    def visit_assign(self, n, k):
        return AST("assign", *k)

    def visit_assign_expr(self, n, k):
        # print('assign expr...')
        for n, p in enumerate(k):
            if isinstance(p, str):
                k[n] = AST("value_expr", self._define_str(p))
            else:
                if n == 0 and len(k) >= 2:
                    # print(p, type(p), *p, isinstance(p, AST), k[n])
                    if isinstance(p, AST):
                        if not p.name == "id":
                            k[n] = AST("index_expr", *p)
                        else:
                            k[n] = AST("index_expr", p)
                    else:
                        k[n] = AST("index_expr", p)
                    # k[n] = AST("index_expr", *p if isinstance(p, AST) else (p,))
                    # print(k[n], type(k[n]), k[n].value, type(k[n].value[0]))
                if (n != 0 and len(k) >= 2) or (n == 0 and len(k) == 1) and p.name != "value_expr":
                    k[n] = AST("value_expr", p)
        return AST("assign_expr", *k if len(k) > 1 else k)

    def visit_index_expr(self, n, k):
        # print(['index_expr'], k, type(k), [type(p) for p in k])
        return AST("index_expr", *k)

    def visit_value_expr(self, n, k):
        # print(f'value expr?! {k}')
        ast_seq = []
        pipe = []
        for p in k:
            if isinstance(p, str):
                ast_seq.append(AST("pipe", *pipe)) if pipe else ast_seq.extend(pipe)
                ast_seq.append(self._define_str(p))
                pipe = []
            else:
                if isinstance(p, AST):
                    if p.name == "pipe":
                        pipe.append(*p.value)
                    else:
                        ast_seq.append(p)
        ast_seq.append(AST("pipe", *pipe)) if pipe else res.extend(pipe)
        k = ast_seq if len(ast_seq) > 0 else k
        # print(f"value expr after pipe: {k}")
        return AST("value_expr", *k)

    def visit_pipe(self, n, k):
        # print(f"pipe? {k}")
        return AST("pipe", *k)

    def visit_expr(self, n, k):
        # print('expr', k, type(k), [type(p) for p in k])
        return AST("expr", *k)

    def visit_caller(self, n, k):
        for n, p in enumerate(k):
            if n < len(k) - 1:
                if isinstance(p, str):
                    k[n] = self._define_str(p)
            else:
                if p == "collect":
                    k[n] = AST("collect", *(k[2], k[1], *k[3:]))
                    k = [k[n]]
                else:
                    k = [k[1], k[0], *k[2:]]
        return AST("caller", *k)

    def visit_args(self, n, k):
        return AST("args", *k)

    def visit_args2(self, n, k):
        vals = ()
        for p in range(0, len(k), 2):
            # kp0 = (k[p].value[0], k[p].value[1]) if len(k[p]) == 2 else (k[p].value[0],)
            # kp1 = (k[p+1].value[0], k[p+1].value[1]) if len(k[p + 1]) == 2 else (k[p+1].value[0],)
            vals += (AST("value", k[p+1]), AST("key_arg", k[p])),
        return AST("args2", *vals)

    def visit_collect(self, n, k):
        pass

    def visit_id(self, n, k):
        return AST("id", n.value)

    def visit_INT(self, n, k):
        return types.SingleInt(n.value)

    def visit_STR(self, n, k):
        return types.SingleStr(n.value)

    def visit_HASHMAP(self, n, k):
        # print(f"hashmap = {k}")
        return types.SingleHashmap(k)

    def visit_hash_expr(self, n, k):
        return k[0], k[2]


if __name__ == "__main__":
    for example in examples:
        res = parsing_code(example)
        print(res)
