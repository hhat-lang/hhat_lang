from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from hhat_lang.core.code.abstract import BaseIR
from hhat_lang.core.code.ir_graph import IRGraph, IRNode
from hhat_lang.core.data.core import CompositeSymbol, Symbol
from hhat_lang.core.memory.core import MemoryManager


###################
# BASE IR SECTION #
###################


class BaseIRManager(ABC):
    """
    To manage IR code in a graph way, where nodes are IR from files and edges are the
    connection between them (uni- or bidirectional).
    """

    _graph: IRGraph

    @property
    def ir_graph(self) -> IRGraph:
        return self._graph

    @abstractmethod
    def add_ir(self, *args: Any, **kwargs: Any) -> Any:
        """To add IR objects to the IR manager"""

        raise NotImplementedError()

    @abstractmethod
    def link_ir(
        self,
        *refs: Symbol | CompositeSymbol,
        ir_importing: BaseIR,
        ir_imported: BaseIR,
        **kwargs: Any,
    ) -> Any:
        """
        To link IR objects. When a file (``A``, importing) imports types or functions from
        another file (``B``, imported), a directed edge is created from ``A`` to ``B``, that
        is ``A`` holds a reference to ``B``, but not the other way around.
        """

        raise NotImplementedError()

    @abstractmethod
    def update_ir(self, prev_ir: BaseIR, new_ir: BaseIR) -> Any:
        """
        Update IR object to a new one.
        """

        raise NotImplementedError()


############################
# BASE INTERPRETER SECTION #
############################


class BaseInterpreter(ABC):
    """
    An abstract execution class. The execution class must hold basic execution
    attributes and functionalities, such as parsing and evaluating code.

    Each execution object holds information regarding available quantum devices specs,
    quantum target backend and its quantum language as well as their specs, and the H-hat
    dialect specs to parse the code and to evaluate it.
    """

    _depth_counter: int
    """to count code depth, for memory and scope management; it must be >= 0"""

    @property
    def depth_counter(self) -> int:
        """
        To count code depth, especially on recursive function calls.

        Returns:
            The current integer of the depth counter
        """

        return self._depth_counter

    def inc_depth_counter(self) -> None:
        self._depth_counter += 1

    def dec_depth_counter(self) -> None:
        self._depth_counter -= 1
        if self._depth_counter < 0:
            raise ValueError("execution depth counter is < 0")

    @abstractmethod
    def parse(self, *args: Any, code: str, **kwargs: Any) -> Any:
        """
        Parsing the source code to some intermediate representation,
        e.g. AST, IR, etc.
        """

        raise NotImplementedError()

    @abstractmethod
    def evaluate(self, *args: Any, **kwargs: Any) -> Any:
        """
        Evaluates the code using the evaluator instance defined by the
        execution specs.
        """

        raise NotImplementedError()


#########################
# BASE EXECUTOR SECTION #
#########################


class BaseExecutor(ABC):
    """
    An abstract executor class.
    """

    _cexec: BaseClassicalEvaluator
    _qexec: BaseQuantumEvaluator

    @property
    def cexec(self) -> BaseClassicalEvaluator:
        """Classical executor instance."""

        return self._cexec

    @property
    def qexec(self) -> BaseQuantumEvaluator:
        """Quantum executor instance."""

        return self._qexec

    @abstractmethod
    def run(
        self,
        *,
        code: Any,
        mem: MemoryManager,
        node: IRNode,
        ir_graph: IRGraph,
        **kwargs: Any,
    ) -> Any:
        """To be called only once, when calling the instance to execute the code."""

        raise NotImplementedError()

    @abstractmethod
    def walk(
        self,
        code: Any,
        mem: MemoryManager,
        node: IRNode,
        ir_graph: IRGraph,
        **kwargs: Any,
    ) -> Any:
        """
        To run recursively and execute the code. Should not be called directly be
        the user, but rather through `run` and internal methods.
        """

        raise NotImplementedError()

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any):
        raise NotImplementedError()


class BaseClassicalEvaluator(ABC):
    """Base evaluator for overall classical instructions"""


class BaseQuantumEvaluator(ABC):
    """Base evaluator for quantum programs"""
