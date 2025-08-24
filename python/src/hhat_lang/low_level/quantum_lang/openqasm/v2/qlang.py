from __future__ import annotations

import importlib
import inspect
from typing import Any, Callable, Iterable, cast

from hhat_lang.core.code.instructions import QInstrFlag
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
from hhat_lang.core.utils import Error, Ok, Result
from hhat_lang.dialects.heather.code.simple_ir_builder.new_ir import IRBlock, IRInstr


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

    def _gen_literal_int(self, literal: CoreLiteral) -> tuple[str, ...]:
        if literal in self._idx:
            (literal.type)
            return tuple(f"x q[{n}];" for n, k in enumerate(literal.bin) if k == "1")

        return ("",)

    def _gen_literal_bool(self, literal: CoreLiteral) -> tuple[str, ...]:
        return tuple("x q[")

    def gen_literal(
        self, literal: CoreLiteral, **_kwargs: Any
    ) -> tuple[str, ...] | ErrorHandler:
        """Generate QASM code from literal data"""

        match literal.type:
            case "@int" | "@u2" | "@u3" | "@u4":
                return self._gen_literal_int(literal)

            case "@bool":
                return self._gen_literal_bool(literal)

            case _:
                raise NotImplementedError(
                    "Generating quantum literal not implemented yet."
                )

        return tuple(f"x q[{n}];" for n, k in enumerate(literal.bin) if k == "1")

    def gen_var(
        self, var: BaseDataContainer | Symbol, executor: BaseEvaluator
    ) -> tuple[str, ...] | ErrorHandler:
        """Generate QASM code from variable data"""

        var_data = executor.mem.heap[var if isinstance(var, Symbol) else var.name]
        code_tuple: tuple[str, ...] = ()

        for member, data in cast(Iterable[tuple[Any, Any]], var_data):

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

                case IRInstr():
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

                case IRInstr():

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
        self, *, instr: IRInstr | IRBlock, **kwargs: Any
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

        if not isinstance(instr, IRInstr):
            return InstrNotFoundError(getattr(instr, "name", None))

        instr_module = importlib.import_module(
            name="hhat_lang.low_level.quantum_lang.openqasm.v2.instructions",
        )

        for name, obj in inspect.getmembers(instr_module, inspect.isclass):

            if (x := getattr(obj, "name", False)) and x == instr.name:

                skip_gen = (
                    getattr(obj, "flag", QInstrFlag.NONE) == QInstrFlag.SKIP_GEN_ARGS
                )

                if skip_gen:
                    args: tuple[Any, ...] = tuple(cast(Iterable[Any], instr.args))
                    if len(args) != 2:
                        return InstrStatusError(instr.name)

                    mask, body = args

                    body_cls = None
                    for n, o in inspect.getmembers(instr_module, inspect.isclass):
                        if getattr(o, "name", False) == body:
                            body_cls = o
                            break

                    if body_cls is None:
                        return InstrNotFoundError(body)

                    res_instr, res_status = obj()(
                        idxs=self._idx.in_use_by[self._qdata],
                        mask=mask,
                        body_instr=body_cls(),
                        executor=self._executor,
                    )
                else:
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
                raise NotImplementedError(
                    f"low-level qlang instr error: {x} ({type(x)})"
                )

        return InstrNotFoundError(instr.name)

    def gen_program(self, **kwargs: Any) -> str:
        """
        Produces the program as a string code written in OpenQASM v2.

        Args:
            **kwargs: any metadata that can be useful

        Returns:
            A string with the OpenQASM v2 code.
        """

        body_code = ""

        instr_module = importlib.import_module(
            "hhat_lang.low_level.quantum_lang.openqasm.v2.instructions"
        )

        for instr in self._code:  # type: ignore [attr-defined]

            instr_cls = None
            for name, obj in inspect.getmembers(instr_module, inspect.isclass):
                if getattr(obj, "name", False) == instr.name:
                    instr_cls = obj
                    break

            skip_gen = False
            if instr_cls is not None:
                skip_gen = (
                    getattr(instr_cls, "flag", QInstrFlag.NONE)
                    == QInstrFlag.SKIP_GEN_ARGS
                )

            if instr.args and not skip_gen:

                match gen_args := self.gen_args(instr.args):

                    case Ok():
                        if gen_args.result():
                            body_code += "\n".join(gen_args.result()) + "\n"

                    # TODO: implement it better
                    case Error():
                        raise ValueError(gen_args.result())

                    case ErrorHandler():
                        raise gen_args

            match gen_instr := self.gen_instrs(
                instr=instr, idx=self._idx, executor=self._executor
            ):

                case Ok():
                    body_code += "\n".join(gen_instr.result())

                case Error():
                    raise gen_instr.result()

                # TODO: implement it better
                case ErrorHandler():
                    raise gen_instr

        if not body_code:
            return ""

        code = ""
        code += "\n".join(self.init_qlang()) + "\n\n"
        code += body_code
        code += "\n"
        code += "\n".join(self.end_qlang()) + "\n"
        return code

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        pass
