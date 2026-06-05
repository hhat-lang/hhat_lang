"""
Quantum program is handler for quantum data/variable that executes
the quantum content done by a classical casting request. For example::

    u32*@2

casts a quantum data `@2` into a `u32` data type. The same as::

    u32*@redim(@1<@u3>)

will cast the resulting set of instructions from `@redim(@1<@u3>)`
into `u32`. It also is valid for quantum variables::

    @v1:@u3 = @redim(@0)
    number:u32 = u32*@v1


The quantum program workflow is as follows:

- Instructions are analyzed according to the low level language and target
backend support (lower level counterparts, LLC)

    - If classical instructions are supported, they will be handled by those
    - If not, they will fall back into this dialect's classical branch execution

- Memory is handled by the dialect and shared when appropriate to the LCC
- All the quantum-specific optimizations are handled by the LLC
- Quantum instructions are then executed and results are collected
- Casting protocols apply the according source type to target type at the results
- Results are sent back to the execution workflow as the target type data


"""

from __future__ import annotations

from typing import Any, Callable

from hhat_lang.core.code.ir_graph import IRNode, IRGraph
from hhat_lang.core.data.core import Literal
from hhat_lang.core.data.var_def import DataDef
from hhat_lang.core.error_handlers.errors import ErrorHandler
from hhat_lang.core.execution.abstract_base import BaseExecutor
from hhat_lang.core.execution.abstract_program import (
    QuantumProgram as CoreQuantumProgram,
)
from hhat_lang.core.lowlevel.abstract_qlang import BaseLLQManager, BaseLLQ
from hhat_lang.core.memory.core import MemoryManager

# TODO: the imports below must come from the config file, not hardcoded
from hhat_lang.low_level.target_backend.qiskit.aer_simulator.code_evaluator import (
    execute_program,
)


class QuantumProgram(CoreQuantumProgram):
    def __init__(
        self,
        *,
        qdata: DataDef | Literal,
        mem: MemoryManager,
        node: IRNode,
        ir_graph: IRGraph,
        executor: BaseExecutor,
        llq: Callable[
            [DataDef, MemoryManager, IRNode, IRGraph, BaseExecutor],
            BaseLLQManager,
        ],
    ):
        """
        Quantum program for Heather dialect.

        Args:
            qdata: a quantum literal or quantum variable
            mem: ``MemoryManager`` object
            node: ``IRNode`` object
            ir_graph: ``IRGraph`` object
            executor: dialect-specific code executor
            llq: Low-level quantum manager callable
        """
        super().__init__(
            qdata=qdata,
            mem=mem,
            node=node,
            ir_graph=ir_graph,
            base_llq=llq,
            executor=executor,
        )

    def run(self, debug: bool = False) -> Any | ErrorHandler:
        qlang_code: BaseLLQ = self._qlang.compile()

        if debug:
            print(qlang_code)

        return execute_program(qlang_code, self._qdata, debug)
