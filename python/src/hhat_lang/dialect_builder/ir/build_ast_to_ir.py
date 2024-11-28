"""
Use to build the ASTtoIR.
"""

from __future__ import annotations

from typing import Any

from hhat_lang.core.ast import BaseAST
from hhat_lang.dialect_builder.ir.ast_to_ir import ASTtoIR


class ASTtoIRBuilder:
    def resolve_macros(self, *args: Any, **kwargs: Any) -> Any:
        # to resolve the macros into the ASTtoIR
        pass

    def resolve_imports(self) -> Any:
        # to resolve the imports
        pass

    def resolve_functions(self) -> Any:
        # to resolve the functions
        pass

    def resolve_types(self, *args: Any, **kwargs: Any) -> Any:
        # to resolve the types
        pass

    def build(self, ast_code: BaseAST) -> Any:
        # TODO: implement it
        ast_to_ir = ASTtoIR()

        raise NotImplementedError()
