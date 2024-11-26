"""
Use to build the FirstIR.
"""

from __future__ import annotations

from typing import Any

from hhat_lang.core.ast import AST
from hhat_lang.dialect_builder.ir.first_ir import FirstIR


class FirstIRBuilder:
    def resolve_macros(self, *args: Any, **kwargs: Any) -> Any:
        # to resolve the macros into the FirstIR
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

    def build(self, ast_code: AST) -> Any:
        # TODO: implement it
        first_ir = FirstIR()

        raise NotImplementedError()
