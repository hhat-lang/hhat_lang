from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from hhat_lang.core.code.ir_graph import IRNode, IRGraph
from hhat_lang.core.data.var_def import DataDef
from hhat_lang.core.execution.abstract_base import BaseExecutor
from hhat_lang.core.memory.core import MemoryManager


class BaseLLQManager(ABC):
    """
    Manager to hold H-hat quantum data and transform it into low-level
    quantum-specific language.
    """

    _qdata: DataDef
    _mem: MemoryManager
    _node: IRNode
    _ir_graph: IRGraph
    _executor: BaseExecutor

    def __init__(
        self,
        qdata: DataDef,
        mem: MemoryManager,
        node: IRNode,
        ir_graph: IRGraph,
        executor: BaseExecutor,
        *_args: Any,
        **_kwargs: Any,
    ):
        self._qdata = qdata
        self._mem = mem
        self._executor = executor
        self._node = node
        self._ir_graph = ir_graph

    @abstractmethod
    def compile(self, *args: Any, **kwargs: Any) -> BaseLLQ:
        """
        The compile method should return a ``BaseQLang`` child class object. It then
        can be used inside a target backend evaluator to execute code on simulator/device.
        """

        raise NotImplementedError()


class BaseLLQ(ABC):
    """
    Base class for (low level) quantum language (aka OpenQASM, NetQASM, etc.) implementation.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        pass

    @abstractmethod
    def code(self) -> Any:
        """
        Use this method to implement code generation for specific quantum language.
        It should return the correct type for the target backend instance.
        """

        raise NotImplementedError()
