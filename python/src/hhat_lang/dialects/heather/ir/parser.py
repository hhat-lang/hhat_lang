from __future__ import annotations

from typing import Any

from hhat_lang.dialects.heather.ir.ast_to_ir import IR
from hhat_lang.dialects.heather.syntax.ast import Program as ASTProgram


def parse_to_ir(parsed_code: ASTProgram) -> IR:
    ir = IR.load_ast(parsed_code)
    ir.build_ir()
    return ir
