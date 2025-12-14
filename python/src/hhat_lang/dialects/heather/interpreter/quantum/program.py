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
    - If not, they will fall back into this dialect's classical branch interpreter

- Memory is handled by the dialect and shared when appropriate to the LCC
- All the quantum-specific optimizations are handled by the LLC
- Quantum instructions are then executed and results are collected
- Casting protocols apply the according source type to target type at the results
- Results are sent back to the execution workflow as the target type data


"""

from __future__ import annotations

from typing import Any, Type

from hhat_lang.core.code.ir import BlockIR
from hhat_lang.core.data.core import SimpleObj
from hhat_lang.core.error_handlers.errors import ErrorHandler
from hhat_lang.core.execution.abstract_base import BaseExecutor
from hhat_lang.core.execution.abstract_program import BaseQuantumProgram
from hhat_lang.core.lowlevel.abstract_qlang import BaseLLQManager
from hhat_lang.core.memory.core import BaseStack, IndexManager, Stack, SymbolTable
from hhat_lang.dialects.heather.code.simple_ir_builder.ir import IRBlock

# TODO: the imports below must come from the config file, not hardcoded
from hhat_lang.low_level.target_backend.qiskit.aer_simulator.code_evaluator import (
    execute_program,
)


class Program(BaseQuantumProgram):
    def __init__(
        self,
        *,
        qdata: SimpleObj,
        idx: IndexManager,
        block: IRBlock,
        executor: BaseExecutor,
        symboltable: SymbolTable,
        qlang: Type[  # type: ignore [type-arg]
            BaseLLQManager[
                SimpleObj,
                IRBlock | BlockIR,
                IndexManager,
                BaseExecutor,
                Stack,
                SymbolTable,
            ]
        ],
    ):
        if (
            isinstance(qdata, SimpleObj)
            and isinstance(idx, IndexManager)
            and isinstance(block, IRBlock)
        ):
            self._qdata = qdata
            self._idx = idx
            self._block = block
            self._executor = executor
            self._qstack = Stack()
            self._symbol = symboltable
            self._qlang = qlang(
                self._qdata,
                self._block,
                self._idx,
                self._executor,
                self._qstack,
                self._symbol,
            )

        else:
            raise ValueError(f"Quantum program got invalid parameters: {qdata=} | {idx=} {block=}")

    @property
    def qstack(self) -> BaseStack:
        return self._qstack

    def run(self, debug: bool = False) -> Any | ErrorHandler:
        qlang_code = self._qlang.gen_program()

        if debug:
            print(qlang_code)

        return execute_program(qlang_code, self._qdata, debug)
