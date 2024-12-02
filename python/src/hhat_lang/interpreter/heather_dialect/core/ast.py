from __future__ import annotations

from hhat_lang.dialect_builder.ir.ast import AST


class Literal(AST):
    pass


class CompositeLiteral(AST):
    pass


class Id(AST):
    pass


class Expr(AST):
    pass


class Declare(AST):
    pass


class Assign(AST):
    pass


class DeclareAssign(AST):
    pass


class CallArgs(AST):
    pass


class Call(AST):
    pass


class Body(AST):
    pass


class IfTest(AST):
    pass


class IfStmt(AST):
    pass


class FnArgs(AST):
    pass


class Fn(AST):
    pass


class Main(AST):
    pass


class TypeBody(AST):
    pass


class Type(AST):
    pass


class Program(AST):
    pass
