"""
Functions and factories to convert FirstIR to CoreIR.
"""

from __future__ import annotations

from typing import Any

from hhat_lang.dialect_builder.ir.core_ir import CoreIR
from hhat_lang.dialect_builder.ir.first_ir import FirstIR


class CoreIRBuilder:
    def build(self, first_ir: FirstIR, **kwargs: Any) -> CoreIR:
        # TODO: implement it
        raise NotImplementedError()
