from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable

from hhat_lang.core.code.ir_graph import IRGraph, IRNode
from hhat_lang.core.data.core import Literal
from hhat_lang.core.data.var_def import DataDef
from hhat_lang.core.error_handlers.errors import ErrorHandler
from hhat_lang.core.execution.abstract_base import BaseExecutor
from hhat_lang.core.lowlevel.abstract_qlang import BaseLLQManager
from hhat_lang.core.memory.core import MemoryManager


class BaseQuantumProgram(ABC):
    """Base abstract class to handle quantum programs"""

    _qdata: DataDef | Literal
    _executor: BaseExecutor
    _qlang: BaseLLQManager
    _mem: MemoryManager
    _node: IRNode
    _ir_graph: IRGraph

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any | ErrorHandler:
        raise NotImplementedError()


class QuantumProgram(BaseQuantumProgram):
    """
    Class to handle quantum programs.

    It is intended to be used when casting quantum data to classical types::

        @some-var*some-type

    The program coordinates code execution related to hybrid quantum and
    classical instructions. If classical instructions are not present on
    the target backend, it fallbacks to the H-hat's dialect implementation
    of them; if not present, an error must be raised. For quantum instructions
    they must be present on target backend, otherwise an error must be raised.
    """

    def __init__(
        self,
        qdata: DataDef | Literal,
        mem: MemoryManager,
        node: IRNode,
        ir_graph: IRGraph,
        base_llq: Callable[
            [DataDef, MemoryManager, IRNode, IRGraph, BaseExecutor],
            BaseLLQManager,
        ],
        executor: BaseExecutor,
    ):
        if (
            isinstance(qdata, DataDef | Literal)
            and isinstance(mem, MemoryManager)
            and isinstance(node, IRNode)
            and isinstance(ir_graph, IRGraph)
            and isinstance(base_llq, type)
            and isinstance(executor, BaseExecutor)
        ):
            self._mem = mem
            self._node = node
            self._ir_graph = ir_graph
            self._qdata = qdata
            self._executor = executor
            self._qlang = base_llq(qdata, mem, node, ir_graph, executor)

        else:
            raise ValueError(
                f"some type is invalid:\n"
                f"  - {qdata}: {type(qdata)}\n"
                f"  - {mem}: {type(mem)}\n"
                f"  - {node}: {type(node)}\n"
                f"  - {ir_graph}: {type(ir_graph)}"
            )

    @property
    def mem(self) -> MemoryManager:
        return self._mem

    @property
    def executor(self) -> BaseExecutor:
        return self._executor

    @property
    def node(self) -> IRNode:
        return self._node

    @property
    def ir_graph(self) -> IRGraph:
        return self._ir_graph

    @property
    def qlang(self) -> BaseLLQManager:
        return self._qlang

    def run(self, *args: Any, **kwargs: Any) -> Any | ErrorHandler:
        """
        Dialects must implement their own ``Program`` class with this method.
        """

        raise NotImplementedError(
            "dialect must implement 'run' method from (quantum) `Program` class."
        )
