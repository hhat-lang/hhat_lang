from hhat_lang.syntax_trees.ast import (
    ATO,
    AST,
    Main,
    Expr,
    Literal,
    Id,
    Array,
    Operation,
    ASTType,
    ExprParadigm,
)
from hhat_lang.builtins.functions import builtin_fn_dict
from hhat_lang.interpreter.post_ast import R


class Analysis:
    def __init__(self, parsed_code: AST):
        self.code = parsed_code

    def run(self) -> R:
        res = analyze(self.code)
        print(res)
        return res


def iter_analyze(code_: AST, role: str = "") -> tuple[R | AST]:
    return tuple(analyze(code_=k, role=role) for k in code_)


def analyze(code_: AST | ATO, role: str = ""):
    match code_:
        case Expr():
            res = iter_analyze(code_, role)
            return R(
                ast_type=code_.type,
                value=res,
                paradigm_type=code_.paradigm,
                role="",
                execute_after=None,
            )
        case Literal():
            return code_
        case Id():
            # TODO: implement a broader check for imported functions
            if code_.token in builtin_fn_dict.keys():
                return R(
                    ast_type=ASTType.OPERATION,
                    value=code_,
                    paradigm_type=ExprParadigm.SINGLE,
                    role="caller",
                    execute_after=None,
                )
            return R(
                ast_type=ASTType.ID,
                value=code_,
                paradigm_type=ExprParadigm.SINGLE,
                role="",
                execute_after=None,
            )
        case Array():
            res = iter_analyze(code_, role)
            return R(
                ast_type=code_.type,
                value=res,
                paradigm_type=code_.paradigm,
                role="",
                execute_after=None
            )
        case Operation():
            res = iter_analyze(code_, role="callee")
            if res:
                return R(
                    ast_type=ASTType.CALL,
                    value=(
                        code_.node,
                        R(
                            ast_type=ASTType.ARGS,
                            value=res,
                            paradigm_type=code_.edges.paradigm,
                            role="callee",
                            execute_after=None
                        )
                    ),
                    paradigm_type=ExprParadigm.SINGLE,
                    role="",
                    execute_after=None,
                )
            return R(
                ast_type=ASTType.CALL,
                value=(
                    R(
                        ast_type=ASTType.OPERATION,
                        value=code_.node,
                        paradigm_type=code_.paradigm,
                        role="caller" if not role else role,
                        execute_after=None
                    ),),
                paradigm_type=code_.paradigm,
                role="",
                execute_after=None,
            )
        case Main():
            res = iter_analyze(code_, role)
            return R(
                ast_type=code_.type,
                value=res,
                paradigm_type=code_.paradigm,
                role="",
                execute_after=None
            )
        case _:
            print(f"!! no match on previous cases: is {type(code_)}!")
