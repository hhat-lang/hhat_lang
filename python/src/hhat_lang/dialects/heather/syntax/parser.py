from __future__ import annotations

from typing import Any
from pathlib import Path

from arpeggio import (
    PTNodeVisitor,
    Terminal,
    NonTerminal,
    SemanticActionResults,
    visit_parse_tree,
)
from arpeggio.cleanpeg import ParserPEG

from hhat_lang.core.utils.dialect_descriptor import DialectDescriptor, get_dialect_data

from .ast import (
    Struct,
    Enum,
    GenericTypeDef,
    GenericCall,
    GenericTypeCall,
    GenericFunctionDef,
    GenericArgs, Member, EnumsStruct, PropId, Declare, Assign, DeclareAssign, Call, Main, Body, Args,
    FunctionDef, TypeDef, Program,
)
from .base import QSymbol, CSymbol, Literal, CompositeLiteral, AST, Node, Terminal


def read_grammar() -> str:
    grammar_path = Path(__file__).parent / "grammar.peg"
    if grammar_path.exists():
        return open(grammar_path, "r").read()
    raise ValueError(f"No grammar found on {grammar_path} directory")


def parse_code(code: str, ws: str | None = None) -> Any:
    grammar = read_grammar()
    ws = ws if ws is not None else "\t\n\r ,"
    parser = ParserPEG(
        language_def=grammar,
        root_rule_name="program",
        comment_rule_name="comment",
        ws=ws
    )
    parse_tree = parser.parse(code)
    dialect = get_dialect_data(Path(__file__).parent.parent.parent, "heather")
    return visit_parse_tree(parse_tree, ParserVisitor(dialect))


class ParserVisitor(PTNodeVisitor):
    def __init__(self, dialect: DialectDescriptor):
        self.dialect = dialect
        super().__init__()

    def visit_program(self, node: NonTerminal, children: SemanticActionResults) -> AST:
        return Program(list(children), self.dialect)

    def visit_typedef(self, node: NonTerminal, children: SemanticActionResults) -> AST:
        if len(children) == 3:
            return GenericTypeDef(children[0], children[1], children[2], self.dialect)
        return TypeDef(children[0], children[1], self.dialect)

    def visit_generic(self, node: NonTerminal, children: SemanticActionResults) -> AST:
        return GenericArgs(children, self.dialect)

    def visit_struct(self, node: NonTerminal, children: SemanticActionResults) -> AST:
        return Struct(*children, dialect=self.dialect)

    def visit_elem(self, node: NonTerminal, children: SemanticActionResults) -> AST:
        return Member(children, self.dialect)

    def visit_enum(self, node: NonTerminal, children: SemanticActionResults) -> AST:
        return Enum(children, dialect=self.dialect)

    def visit_enums_struct(self, node: NonTerminal, children: SemanticActionResults) -> AST:
        return EnumsStruct(children[0], children[1], self.dialect)

    def visit_fndef(self, node: NonTerminal, children: SemanticActionResults) -> AST:
        if len(children) == 5:
            return GenericFunctionDef(
                fn_type=children[3],
                name=children[0],
                generic=children[1],
                args=children[2],
                body=children[4],
                dialect=self.dialect,
            )
        return FunctionDef(children[2], children[0], children[1], children[3], self.dialect)

    def visit_args(self, node: NonTerminal, children: SemanticActionResults) -> AST:
        return Args(list(children), self.dialect)

    def visit_main(self, node: NonTerminal, children: SemanticActionResults) -> AST:
        return Main(list(children), self.dialect)

    def visit_body(self, node: NonTerminal, children: SemanticActionResults) -> AST:
        return Body(list(children), self.dialect)

    def visit_id(self, node: Terminal, children: SemanticActionResults) -> AST:
        if node.value.startswith('?'):
            is_generic = True
            node.value = node.value[1:]
        else:
            is_generic = False

        if node.value.startswith('@'):
            return QSymbol(node.value, is_generic, self.dialect)
        return CSymbol(node.value, is_generic, self.dialect)

    def visit_declare_assign(self, node: NonTerminal, children: SemanticActionResults) -> AST:
        return DeclareAssign(children[1], children[0], children[2], self.dialect)

    def visit_declare(self, node: NonTerminal, children: SemanticActionResults) -> AST:
        return Declare(children[1], children[0], self.dialect)

    def visit_assign(self, node: NonTerminal, children: SemanticActionResults) -> AST:
        return Assign(*children, dialect=self.dialect)

    def visit_call(self, node: NonTerminal, children: SemanticActionResults) -> AST:
        if len(children) == 3:
            return GenericCall(children[1], children[0], children[2], self.dialect)
        return Call(*children, dialect=self.dialect)

    def visit_generic_call(self, node, children):
        return GenericTypeCall(list(children), self.dialect)

    def visit_call_args(self, node, children):
        return Args(children, self.dialect)

    def visit_prop_id(self, node, children):
        return PropId(*children, dialect=self.dialect)

    def visit_literal(self, node, children):
        return children[0]

    def visit_null(self, node, children):
        return Literal(node.value, "null", self.dialect)

    def visit_bin(self, node, children):
        return Literal(node.value, "bin", self.dialect)

    def visit_bool(self, node, children):
        return Literal(node.value, "bool", self.dialect)

    def visit_int(self, node, children):
        return Literal(node.value, "int", self.dialect)

    def visit_str(self, node, children):
        return Literal(node.value, "str", self.dialect)

    def visit_float(self, node, children):
        return Literal(node.value, "float", self.dialect)

    def visit_array(self, node, children):
        return CompositeLiteral(list(children), "array", self.dialect)

    def visit_hashmap(self, node, children):
        return CompositeLiteral(list(children), "hashmap", self.dialect)

    def visit_q__int(self, node, children):
        return Literal(node.value, "q__int", self.dialect)

    def visit_q__float(self, node, children):
        return Literal(node.value, "q__float", self.dialect)

    def visit_q__array(self, node, children):
        return CompositeLiteral(list(children), "q__array", self.dialect)

    def visit_q__bool(self, node, children):
        return Literal(node.value, "q__bool", self.dialect)

