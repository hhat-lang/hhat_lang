from hhat_lang.syntax_trees.ast import (
    AST,
    Main,
    Expr,
    ManyExpr,
    Literal,
    Array,
    Operation
)
from hhat_lang.interpreter.memory import R


class Analysis:
    def __init__(self, parsed_code: AST):
        self.code = parsed_code

    def run(self):
        res = analyze(self.code)
        print(res)
        return res


def iter_analyze(code_: AST, role: str = ""):
    return tuple(analyze(code_=k, role=role) for k in code_)


def analyze(code_: AST, role: str = ""):
    match code_:
        case Expr():
            # print("* expr found; new concurrent task!")
            # print("  - expr start")
            res = iter_analyze(code_, role)
            # print("  - expr end")
            return R(
                ast_type=code_.type,
                value=res,
                is_concurrent=False,
                role="",
                execute_after=None,
            )
        case ManyExpr():
            # print(f"* entered many exprs ==> {code_}")
            # print("  - many-exprs enter")
            res = iter_analyze(code_, role)
            # print("  - many-exprs end")
            return R(
                ast_type=code_.type,
                value=res,
                is_concurrent=True,
                role="",
                execute_after=None,
            )
        case Literal():
            # print(f"* literal ==> {code_}")
            return code_
        case Array():
            # print(f"* array -> {code_}")
            # print("  - array start")
            res = iter_analyze(code_, role)
            # print("  - array end")
            return R(
                ast_type=code_.type,
                value=res,
                is_concurrent=False,
                role="",
                execute_after=None
            )
        case Operation():
            # print(f"* operation -> {code_}")
            res = iter_analyze(code_, role="callee")
            if res:
                return R(
                    ast_type="call",
                    value=(
                        R(
                            ast_type="oper",
                            value=code_.node,
                            is_concurrent=False,
                            role="caller",
                            execute_after=None
                        ),
                        R(
                            ast_type="args",
                            value=res,
                            is_concurrent=False,
                            role="callee",
                            execute_after=None
                        )
                    ),
                    is_concurrent=False,
                    role="",
                    execute_after=None,
                )
            return R(
                ast_type="call",
                value=(
                    R(
                        ast_type="oper",
                        value=code_.node,
                        is_concurrent=False,
                        role="caller" if not role else role,
                        execute_after=None
                    ),),
                is_concurrent=False,
                role="",
                execute_after=None,
            )
        case Main():
            res = iter_analyze(code_, role)
            return R(
                ast_type=code_.type,
                value=res,
                is_concurrent=True,
                role="",
                execute_after=None
            )
        case _:
            print(f"is {type(code_)}!")
