from __future__ import annotations

from typing import Any

from hhat_lang.core.code.ir_graph import IRGraph, IRNode
from hhat_lang.core.execution.abstract_base import (
    BaseExecutor,
    BaseClassicalEvaluator,
    BaseQuantumEvaluator,
)
from hhat_lang.core.memory.core import MemoryManager


class Executor(BaseExecutor):
    def __init__(self):
        self._cexec = CExecutor()
        self._qexec = QExecutor()

    def run(
        self,
        *,
        code: Any,
        mem: MemoryManager,
        node: IRNode,
        ir_graph: IRGraph,
        **kwargs: Any,
    ) -> None:
        self.walk(code, mem, node, ir_graph)

    def walk(
        self,
        code: Any,
        mem: MemoryManager,
        node: IRNode,
        ir_graph: IRGraph,
        **kwargs: Any,
    ) -> Any:
        pass

    def __call__(self, *args: Any, **kwargs: Any):
        pass


class CExecutor(BaseClassicalEvaluator):
    pass


class QExecutor(BaseQuantumEvaluator):
    pass
