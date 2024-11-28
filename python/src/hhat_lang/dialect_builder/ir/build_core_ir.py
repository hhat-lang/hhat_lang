"""
Functions and factories to convert ASTtoIR to CoreIR.
"""

from __future__ import annotations

from typing import Any

from hhat_lang.dialect_builder.ir.ast_to_ir import ASTtoIR
from hhat_lang.dialect_builder.ir.core_ir import CoreIR


class CoreIRBuilder:
    def build(self, first_ir: ASTtoIR, **kwargs: Any) -> CoreIR:
        # TODO: implement it
        raise NotImplementedError()
