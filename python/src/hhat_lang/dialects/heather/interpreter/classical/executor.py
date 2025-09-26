"""
Execute classical branch instructions. Quantum branch may use it
to execute classical instructions that are not supported by the
quantum low level language and/or the target backend.
"""

from __future__ import annotations

from typing import Any

from hhat_lang.core.code.ir import BaseFnIR, BlockIR, BodyIR, TypeIR
from hhat_lang.core.execution.abstract_base import BaseEvaluator
from hhat_lang.core.memory.core import MemoryManager


class Evaluator(BaseEvaluator):
    def __init__(self, mem: MemoryManager, type_table: TypeIR, fn_table: BaseFnIR):
        self._mem = mem
        self._type_table = type_table
        self._fn_table = fn_table

    def run(self, code: BodyIR | BlockIR, **kwargs: Any) -> Any:
        pass

    def __call__(self, code: BodyIR | BlockIR, **kwargs: Any) -> Any:
        pass
