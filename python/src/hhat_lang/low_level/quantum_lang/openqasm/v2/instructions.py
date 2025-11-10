from __future__ import annotations

from typing import Any

from hhat_lang.core.code.instructions import CInstr, QInstr, QInstrFlag
from hhat_lang.core.code.utils import InstrStatus
from hhat_lang.core.data.core import (
    CompositeLiteral,
    CompositeMixData,
    CoreLiteral,
    Symbol,
)
from hhat_lang.core.data.variable import BaseDataContainer
from hhat_lang.core.error_handlers.errors import (
    HeapInvalidKeyError,
    IndexUnknownError,
)
from hhat_lang.core.execution.abstract_base import BaseExecutor
from hhat_lang.core.memory.core import MemoryDataTypes
from hhat_lang.core.utils import Error, Ok, Result

##########################
# CLASSICAL INSTRUCTIONS #
##########################


class If(CInstr):
    name = "if"

    @staticmethod
    def _instr(cond_test: str | tuple[str, ...], instr: str | tuple[str, ...]) -> str:
        return f"if({cond_test}) {instr};"

    def _translate_instrs(
        self,
        cond_test: tuple[MemoryDataTypes],
        instrs: tuple[MemoryDataTypes],
        **kwargs: Any,
    ) -> tuple[tuple[str, ...], InstrStatus]:
        """
        Translate `If` instruction. Number of condition tests (`cond_test`) must
        match the number of instructions (`instrs`).
        """

        transformed_instrs: tuple[str, ...] = ()

        for c, i in zip(cond_test, instrs):
            c_value: str | tuple[str, ...]

            match c:
                case BaseDataContainer():
                    c_value = c.name.value

                case CoreLiteral() | Symbol():
                    c_value = c.value

                case CompositeLiteral() | CompositeMixData():
                    raise NotImplementedError()

                case _:
                    raise NotImplementedError()

            i_value: str | tuple[str, ...]

            match i:
                case BaseDataContainer():
                    i_value = i.name.value

                case CoreLiteral() | Symbol():
                    i_value = i.value

                case CompositeLiteral() | CompositeMixData():
                    raise NotImplementedError()

                case _:
                    raise NotImplementedError()

            transformed_instrs += (self._instr(c_value, i_value),)

        return transformed_instrs, InstrStatus.DONE

    def __call__(
        self, *, executor: BaseExecutor, **kwargs: Any
    ) -> tuple[tuple[str, ...], InstrStatus]:
        """Transforms `if` instruction to openQASMv2.0 code."""

        self._instr_status = InstrStatus.RUNNING

        # conditional test must be in the first position of the stack
        cond_test = executor.mem.stack.pop()
        cond_test_tuple = cond_test if isinstance(cond_test, tuple) else (cond_test,)

        # instructions must be in the following position of the stack
        if_instrs = executor.mem.stack.pop()
        if_instrs_tuple = if_instrs if isinstance(if_instrs, tuple) else (if_instrs,)

        instrs, status = self._translate_instrs(
            cond_test=cond_test_tuple, instrs=if_instrs_tuple
        )
        self._instr_status = status
        return instrs, status


########################
# QUANTUM INSTRUCTIONS #
########################


class QRedim(QInstr):
    name = "@redim"

    @staticmethod
    def _instr(idx: int) -> str:
        return f"h q[{idx}];"

    def _translate_instrs(
        self, idxs: tuple[int, ...]
    ) -> tuple[tuple[str, ...], InstrStatus]:
        return tuple(self._instr(k) for k in idxs), InstrStatus.DONE

    def __call__(
        self, *, idxs: tuple[int, ...], **_kwargs: Any
    ) -> tuple[tuple[str, ...], InstrStatus]:
        """Transforms `@redim` instruction to openQASMv2.0 code"""

        self._instr_status = InstrStatus.RUNNING
        instrs, status = self._translate_instrs(idxs)
        self._instr_status = status
        return instrs, status


class QSync(QInstr):
    name = "@sync"

    @staticmethod
    def _instr(idxs: tuple[int, ...]) -> str:
        return f"cx q[{idxs[0]}], q[{idxs[1]}];"

    def _translate_instrs(
        self, idxs: tuple[tuple[int, ...], ...]
    ) -> tuple[tuple[str, ...], InstrStatus]:
        return tuple(self._instr(k) for k in idxs), InstrStatus.DONE

    def __call__(
        self,
        *,
        idxs: tuple[tuple[int, ...], ...],
        executor: BaseExecutor,
        **_kwargs: Any,
    ) -> tuple[tuple[str, ...], InstrStatus]:
        """Transforms `@sync` instruction to openQASMv2.0 code."""

        self._instr_status = InstrStatus.RUNNING

        # TODO: implement this instruction with all the range of capabilities;
        #  check documentation

        instrs, status = self._translate_instrs(idxs)

        self._instr_status = status
        return instrs, status


class QIf(QInstr):
    name = "@if"

    def __call__(
        self, *, idxs: tuple[int, ...], executor: BaseExecutor, **kwargs: Any
    ) -> tuple[tuple[str, ...], InstrStatus]:
        """Transforms `@if` instruction to openQASMv2.0 code."""

        # TODO: implement this instruction; check documentation

        self._instr_status = InstrStatus.RUNNING
        raise NotImplementedError()


class QNot(QInstr):
    name = "@not"

    @staticmethod
    def _instr(idx: int) -> str:
        return f"x q[{idx}];"

    def _translate_instrs(
        self, idxs: tuple[int, ...]
    ) -> tuple[tuple[str, ...], InstrStatus]:
        return tuple(self._instr(k) for k in idxs), InstrStatus.DONE

    def __call__(
        self, *, idxs: tuple[int, ...], **_kwargs: Any
    ) -> tuple[tuple[str, ...], InstrStatus]:
        """Transforms `@not` instruction to openQASMv2.0 code"""
        self._instr_status = InstrStatus.RUNNING
        instrs, status = self._translate_instrs(idxs)
        self._instr_status = status
        return instrs, status


class QNez(QInstr):
    """Quantum not-equal-zero instruction."""

    name = "@nez"
    flag = QInstrFlag.SKIP_GEN_ARGS

    @staticmethod
    def _get_mask_idxs(
        mask: CoreLiteral | BaseDataContainer | Symbol,
        num_idxs: int,
        executor: BaseExecutor | None = None,
    ) -> Result:
        """Return indexes from ``mask`` that are non-zero.

        If ``mask`` is a variable or a symbol reference to a variable, the
        current value is fetched from ``executor``'s memory manager.
        """

        match mask:
            case CoreLiteral():
                lit = mask

            case Symbol() if mask.value in ("@true", "@false"):
                bool_val = "@1" if mask.value == "@true" else "@0"
                lit = CoreLiteral(bool_val, "@bool")

            case BaseDataContainer() | Symbol():
                if executor is None:
                    return Error(IndexUnknownError())

                var = executor.mem.heap[mask if isinstance(mask, Symbol) else mask.name]

                if isinstance(var, HeapInvalidKeyError):
                    return Error(var)

                val = var.get(var.type if hasattr(var, "type") else None)

                if isinstance(val, list):
                    val = val[-1]

                if not isinstance(val, CoreLiteral):
                    return Error(IndexUnknownError())

                lit = val

            case _:
                return Error(IndexUnknownError())

        mask_bits = lit.bin[::-1]
        idxs: tuple[int, ...] = tuple(
            i for i, bit in enumerate(mask_bits) if bit == "1" and i < num_idxs
        )

        return Ok(idxs)

    @staticmethod
    def _instr(idx: int, body_instr: QInstr) -> str:
        if hasattr(body_instr, "_instr"):
            return body_instr._instr(idx)  # type: ignore[attr-defined]
        raise NotImplementedError("body instruction missing '_instr' method")

    def _translate_instrs(
        self,
        idxs: tuple[int, ...],
        mask: CoreLiteral | BaseDataContainer | Symbol,
        body_instr: QInstr,
        executor: BaseExecutor | None = None,
        **kwargs: Any,
    ) -> tuple[tuple[str, ...], InstrStatus]:
        """Translate ``@nez`` instruction."""

        mask_res = self._get_mask_idxs(mask, len(idxs), executor)

        match mask_res:
            case Ok():
                mask_idxs = mask_res.result()

            case Error():
                # error while obtaining mask indexes
                return (mask_res.result(),), InstrStatus.ERROR  # type: ignore[return-value]

            case _:
                return tuple(), InstrStatus.ERROR

        if not mask_idxs:
            return tuple(), InstrStatus.DONE

        selected = tuple(idxs[i] for i in mask_idxs)
        return (
            tuple(self._instr(i, body_instr) for i in selected),
            InstrStatus.DONE,
        )

    def __call__(
        self,
        *,
        idxs: tuple[int, ...],
        mask: CoreLiteral | BaseDataContainer | Symbol,
        body_instr: QInstr,
        executor: BaseExecutor | None = None,
        **kwargs: Any,
    ) -> tuple[tuple[str, ...], InstrStatus]:
        """Transforms ``@nez`` instruction to OpenQASM v2.0 code."""

        self._instr_status = InstrStatus.RUNNING
        instrs, status = self._translate_instrs(
            idxs=idxs,
            mask=mask,
            body_instr=body_instr,
            executor=executor,
            **kwargs,
        )
        self._instr_status = status
        return instrs, status
