from __future__ import annotations

from typing import Any

from hhat_lang.core.code.instructions import CInstr, QInstr
from hhat_lang.core.code.utils import InstrStatus
from hhat_lang.core.data.core import (
    CompositeLiteral,
    CompositeMixData,
    CoreLiteral,
    Symbol,
)
from hhat_lang.core.data.variable import BaseDataContainer
from hhat_lang.core.execution.abstract_base import BaseEvaluator
from hhat_lang.core.memory.core import MemoryDataTypes

##########################
# CLASSICAL INSTRUCTIONS #
##########################


class If(CInstr):
    name = "if"

    @staticmethod
    def _instr(cond_test: str, instr: str) -> str:
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

            c_value: str

            match c:
                case BaseDataContainer():
                    c_value = c.name.value
                case CoreLiteral() | Symbol():
                    c_value = c.value
                case CompositeLiteral() | CompositeMixData():
                    raise NotImplementedError()
                case _:
                    raise NotImplementedError()

            i_value: str

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
        self, *, executor: BaseEvaluator, **kwargs: Any
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
        executor: BaseEvaluator,
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
        self, *, idxs: tuple[int, ...], executor: BaseEvaluator, **kwargs: Any
    ) -> tuple[tuple[str, ...], InstrStatus]:
        """Transforms `@if` instruction to openQASM v2.0 code (call with options)."""
        self._instr_status = InstrStatus.RUNNING
        code = []
        cond_size = kwargs["cond_size"]
        options = kwargs["options"]
        cond_idxs = idxs[:cond_size]  # The indices of the qubits for the condition
        body_idxs = idxs[cond_size:]  # The rest are for the body
        # 1. Measure all condition qubits into a dedicated creg 'cond'
        for i, qidx in enumerate(cond_idxs):
            code.append(f"measure q[{qidx}] -> cond[{i}];")
        # 2. For each option, emit an OpenQASM if statement
        handled_values = set()
        for cond_val, body in options.items():
            if cond_val in ("else", "default"):
                continue  # Handle after all other options
            # cond_val: expected classical value (int or str representing bits)
            if isinstance(cond_val, int):
                int_val = cond_val
            elif isinstance(cond_val, str) and cond_val.isdigit():
                int_val = int(cond_val)
            else:
                # If bitstring, convert to int
                int_val = int(cond_val, 2)
            handled_values.add(int_val)
            # Generate the body code
            if isinstance(body, list):
                body_code = []
                for instr in body:
                    instr_code, _ = instr(
                        idxs=body_idxs, executor=executor, **kwargs
                    )
                    body_code.extend(instr_code)
                body_code_str = " ".join(body_code)
            else:
                body_code, _ = body(
                    idxs=body_idxs, executor=executor, **kwargs
                )
                body_code_str = " ".join(body_code)
            code.append(f"if (cond=={int_val}) {body_code_str}")
        # Handle else/default option if present
        if "else" in options or "default" in options:
            body = options.get("else") or options.get("default")
            # For all possible values not handled above
            max_val = 2 ** cond_size
            for int_val in range(max_val):
                if int_val in handled_values:
                    continue
                if isinstance(body, list):
                    body_code = []
                    for instr in body:
                        instr_code, _ = instr(
                            idxs=body_idxs, executor=executor, **kwargs
                        )
                        body_code.extend(instr_code)
                    body_code_str = " ".join(body_code)
                else:
                    body_code, _ = body(
                        idxs=body_idxs, executor=executor, **kwargs
                    )
                    body_code_str = " ".join(body_code)
                code.append(f"if (cond=={int_val}) {body_code_str}")
        self._instr_status = InstrStatus.DONE
        return tuple(code), self._instr_status
