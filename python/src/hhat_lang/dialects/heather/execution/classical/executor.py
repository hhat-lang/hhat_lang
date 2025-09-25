"""
Execute classical branch instructions. Quantum branch may use it
to execute classical instructions that are not supported by the
quantum low level language and/or the target backend.
"""

from __future__ import annotations

from typing import Any

from hhat_lang.core.execution.abstract_base import BaseEvaluator
from hhat_lang.core.memory.core import MemoryManager
from hhat_lang.dialects.heather.code.simple_ir_builder.new_ir import IRBlock


class Evaluator(BaseEvaluator):
    def __init__(self, mem: MemoryManager, **_kwargs: Any):
        self._mem = mem

    def walk(self, code: Any, mem: MemoryManager, **kwargs: Any) -> Any:
        pass

    def run(self, code: IRBlock, **kwargs: Any) -> Any:
        pass

    def __call__(self, code: IRBlock, **kwargs: Any) -> Any:
        pass
