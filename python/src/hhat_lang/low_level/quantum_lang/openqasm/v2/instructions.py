from __future__ import annotations

from typing import Any

from hhat_lang.core.code.instructions import QInstr, CInstr
from hhat_lang.core.code.utils import InstrStatus
from hhat_lang.core.execution.abstract_base import BaseEvaluator


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
        cond_test: tuple[str, ...],
        instrs: tuple[str, ...],
        **kwargs: Any
    ) -> tuple[tuple[str, ...], InstrStatus]:
        """
        Translate `If` instruction. Number of condition tests (`cond_test`) must
        match the number of instructions (`instrs`).
        """

        return (
            tuple(
                self._instr(c, i) for c, i in zip(cond_test, instrs)
            ),
            InstrStatus.DONE
        )

    def __call__(
        self,
        *,
        executor: BaseEvaluator,
        **kwargs: Any
    ) -> tuple[tuple[str, ...], InstrStatus]:
        """Transforms `if` instruction to openQASMv2.0 code."""

        self._instr_status = InstrStatus.RUNNING
        instrs, status = self._translate_instrs(**kwargs)
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
        self,
        idxs: tuple[int, ...]
    ) -> tuple[tuple[str, ...], InstrStatus]:
        return tuple(self._instr(k) for k in idxs), InstrStatus.DONE

    def __call__(
        self,
        *,
        idxs: tuple[int, ...],
        **_kwargs: Any
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
        self,
        idxs: tuple[tuple[int, ...], ...]
    ) -> tuple[tuple[str, ...], InstrStatus]:
        return tuple(self._instr(k) for k in idxs), InstrStatus.DONE

    def __call__(
        self,
        *,
        idxs: tuple[tuple[int, ...], ...],
        executor: BaseEvaluator,
        **_kwargs: Any
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
        self,
        *,
        idxs: tuple[int, ...],
        executor: BaseEvaluator,
        **kwargs: Any
    ) -> tuple[tuple[str, ...], InstrStatus]:
        """Transforms `@if` instruction to openQASMv2.0 code."""

        # TODO: implement this instruction; check documentation

        self._instr_status = InstrStatus.RUNNING
        raise NotImplementedError()
