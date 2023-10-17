from abc import ABC
from typing import Any
from hhat_literal_define import (literal_bool_define, literal_int_define)


literal_dict = dict(
    bool=literal_bool_define,
    int=literal_int_define
)


class AOT(ABC):
    def __init__(self, token: str, aot_type: str = ""):
        self.token = token
        self.type = aot_type

    def __repr__(self) -> str:
        return self.token


class AST(ABC):
    def __init__(
            self,
            *args: Any,
            node: AOT | None = None,
            ast_type: str = "",
            is_concurrent: bool = False,
    ):
        self.node = node or ""
        self.type = ast_type
        self.edges = args
        self.is_concurrent = is_concurrent

    def __len__(self):
        return len(self.edges)

    def __iter__(self):
        yield from self.edges

    def __repr__(self) -> str:
        token = self.node.token if self.node else ""
        args = " ".join(str(k) for k in self.edges)
        return token + (f"({args})" if args else "")


class Literal(AOT):
    def __init__(self, token: str, lit_type: str = ""):
        super().__init__(token, lit_type)
        self.value = literal_dict[self.type](self.token)


class Id(AOT):
    def __init__(self, token: str, aot_type: str = "id"):
        super().__init__(token, aot_type)
        self.value = self.token


class Array(AST):
    def __init__(self, *values: Any):
        super().__init__(ast_type="array", *values)


class Expr(AST):
    def __init__(self, *values: Any):
        super().__init__(ast_type="expr", is_concurrent=True, *values)


class ManyExpr(AST):
    def __init__(self, *values: Any):
        super().__init__(ast_type="many-expr", is_concurrent=False, *values)


class Operation(AST):
    def __init__(self, oper_token: AOT | str, *args: Any):
        if isinstance(oper_token, Id):
            oper_token.type = "oper"
        else:
            oper_token = Id(token=oper_token, aot_type="oper")
        super().__init__(node=oper_token, ast_type="oper", *args)


class Main(AST):
    def __init__(self, *exprs: Any):
        super().__init__(ast_type="main", is_concurrent=True, *exprs)


class Program(AST):
    def __init__(self, *super_exprs: Any):
        super().__init__(ast_type="program", *super_exprs)
