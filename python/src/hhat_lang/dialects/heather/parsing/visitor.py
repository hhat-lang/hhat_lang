from __future__ import annotations

from arpeggio import PTNodeVisitor, NonTerminal, SemanticActionResults

from hhat_lang.core.code.ast import AST

from hhat_lang.dialects.heather.code.ast import (
    Program,
    Main,
    Imports,
    TypeImport,
    TypeDef,
    TypeMember,
    Id,
    CompositeId,
    ArgValuePair,
    ArgTypePair,
    SingleTypeMember,
    EnumTypeMember,
)


class ParserVisitor(PTNodeVisitor):
    def visit_program(self, node: NonTerminal, child: SemanticActionResults) -> AST:
        pass
