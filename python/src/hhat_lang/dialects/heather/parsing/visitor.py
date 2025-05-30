from __future__ import annotations

from arpeggio import NonTerminal, PTNodeVisitor, SemanticActionResults

from hhat_lang.core.code.ast import AST
from hhat_lang.dialects.heather.code.ast import (
    ArgTypePair,
    ArgValuePair,
    CompositeId,
    EnumTypeMember,
    Id,
    Imports,
    Main,
    Program,
    SingleTypeMember,
    TypeDef,
    TypeImport,
    TypeMember,
)


class ParserVisitor(PTNodeVisitor):
    def visit_program(self, node: NonTerminal, child: SemanticActionResults) -> AST:
        raise NotImplementedError()
