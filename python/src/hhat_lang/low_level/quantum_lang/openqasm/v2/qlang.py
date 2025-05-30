from __future__ import annotations

import importlib
import inspect
from typing import Any, Callable

from hhat_lang.core.code.ir import BlockIR, InstrIR, InstrIRFlag, TypeIR
from hhat_lang.core.code.utils import InstrStatus
from hhat_lang.core.data.core import (
    CompositeLiteral,
    CompositeMixData,
    CompositeSymbol,
    CoreLiteral,
    Symbol,
)
from hhat_lang.core.data.variable import BaseDataContainer
from hhat_lang.core.error_handlers.errors import (
    ErrorHandler,
    InstrNotFoundError,
    InstrStatusError,
)
from hhat_lang.core.execution.abstract_base import BaseEvaluator
from hhat_lang.core.lowlevel.abstract_qlang import BaseLowLevelQLang
from hhat_lang.core.memory.core import IndexManager, MemoryManager
from hhat_lang.core.utils import Error, Ok, Result
from hhat_lang.dialects.heather.code.ast import Literal
from hhat_lang.dialects.heather.code.simple_ir_builder.ir import (
    IRArgs,
    IRBlock,
    IRInstr,
)


class LowLeveQLang(BaseLowLevelQLang):
    def init_qlang(self) -> tuple[str, ...]:
        code_list = (
            "OPENQASM 2.0;",
            'include "qelib1.inc";',
            f"qreg q[{self._num_idxs}];",
            f"creg c[{self._num_idxs}];",  # for now, creg num == qreg num
        )

        return code_list

    def end_qlang(self) -> tuple[str, ...]:
        """Provides the end of the code"""

        # TODO: check whether some qubits were previously measured and
        #  handle the rest appropriately

        return ("measure q -> c;",)

    def gen_literal(
        self, literal: CoreLiteral, **_kwargs: Any
    ) -> tuple[str, ...] | ErrorHandler:
        """Generate QASM code from literal data"""

        return tuple(f"x q[{n}];" for n, k in enumerate(literal.bin) if k == "1")

    def gen_var(
        self, var: BaseDataContainer | Symbol, executor: BaseEvaluator
    ) -> tuple[str, ...] | ErrorHandler:
        """Generate QASM code from variable data"""

        var_data = executor.mem.heap[var if isinstance(var, Symbol) else var.name]
        code_tuple: tuple[str, ...] = ()

        for member, data in var_data:

            match data:
                case Symbol():
                    d_res = self.gen_var(data, executor=self._executor)

                    if isinstance(d_res, tuple):
                        code_tuple += d_res

                    else:
                        return d_res

                case CoreLiteral():
                    d_res = self.gen_literal(data)

                    if isinstance(d_res, tuple):
                        code_tuple += d_res

                    else:
                        return d_res

                case CompositeSymbol():
                    # TODO: implement it
                    raise NotImplementedError()

                case CompositeLiteral():
                    # TODO: implement it
                    raise NotImplementedError()

                case CompositeMixData():
                    # TODO: implement it
                    raise NotImplementedError()

                case InstrIR():

                    match res := self.gen_instrs(instr=data, executor=self._executor):
                        case Ok():
                            code_tuple += res.result()

                        case Error():
                            return res.result()

                        case ErrorHandler():
                            return res

        return code_tuple

    def gen_args(self, args: tuple[Any, ...], **kwargs: Any) -> Result | ErrorHandler:
        code_tuple: tuple[str, ...] = ()

        for k in args:

            match k:
                case Symbol():
                    res = self.gen_var(k, executor=self._executor)

                    if isinstance(res, tuple):
                        code_tuple += res

                    else:
                        return res

                case CoreLiteral():
                    res = self.gen_literal(k)

                    if isinstance(res, tuple):
                        code_tuple += res

                    else:
                        return res

                case CompositeSymbol():
                    # TODO: implement it
                    raise NotImplementedError()

                case CompositeLiteral():
                    # TODO: implement it
                    raise NotImplementedError()

                case CompositeMixData():
                    # TODO: implement it
                    raise NotImplementedError()

                case InstrIR():

                    match instr_res := self.gen_instrs(instr=k, **kwargs):
                        case Ok():
                            code_tuple += instr_res.result()

                        case Error():
                            return instr_res.result()

                        case ErrorHandler():
                            return instr_res

                case _:
                    # unknown case, needs investigation
                    raise NotImplementedError()

        return Ok(code_tuple)

    def gen_instrs(
        self, *, instr: InstrIR | BlockIR, **kwargs: Any
    ) -> Result | ErrorHandler:
        """
        Transforms each of the instructions into an OpenQASM v2 code or
        evaluate the code using the `executor` (H-hat dialect native
        executor) if it is classical instruction not supported by OpenQASM v2.

        Args:
            instr: InstrIR or BlockIR
            **kwargs: anything else

        Returns:
            A tuple with OpenQASM v2 code strings
        """

        instr_module = importlib.import_module(
            name="hhat_lang.low_level.quantum_lang.openqasm.v2.instructions",
        )

        for name, obj in inspect.getmembers(instr_module, inspect.isclass):

            if (x := getattr(obj, "name", False)) and x == instr.name:
                res_instr, res_status = obj()(
                    idxs=self._idx.in_use_by[self._qdata],
                    executor=self._executor,
                )

                if res_status == InstrStatus.DONE:
                    return Ok(res_instr)

                return InstrStatusError(instr.name)

            # if openQASMv2.0 does not have the instruction, then falls
            # back to H-hat dialect to execute it
            else:
                # TODO: falls back to dialect execution
                pass

        return InstrNotFoundError(instr.name)

    def gen_program(self, **kwargs: Any) -> str:
        """
        Produces the program as a string code written in OpenQASM v2.

        Args:
            **kwargs: any metadata that can be useful

        Returns:
            A string with the OpenQASM v2 code.
        """

        code = ""
        code += "\n".join(self.init_qlang()) + "\n\n"

        for instr in self._code:  # type: ignore [attr-defined]

            if instr.args:

                match gen_args := self.gen_args(instr.args):

                    case Ok():
                        if gen_args.result():
                            code += "\n".join(gen_args.result()) + "\n"

                    # TODO: implement it better
                    case Error():
                        raise ValueError(gen_args.result())

                    case ErrorHandler():
                        raise gen_args

            match gen_instr := self.gen_instrs(
                instr=instr, idx=self._idx, executor=self._executor
            ):

                case Ok():
                    code += "\n".join(gen_instr.result())

                case Error():
                    raise gen_instr.result()

                # TODO: implement it better
                case ErrorHandler():
                    raise gen_instr

        code += "\n"
        code += "\n".join(self.end_qlang()) + "\n"
        return code

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        pass
