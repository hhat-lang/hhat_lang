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
        options: dict[Any, Any],  # Mapping of condition value (int/str) to body instruction(s)
        cond_size: int = 1,      # Number of qubits/bits for the condition (default 1 for @bool)
        **kwargs: Any
    ) -> tuple[tuple[str, ...], InstrStatus]:
        """Transforms `@if` instruction to openQASM v2.0 code (call with options)."""
        self._instr_status = InstrStatus.RUNNING
        code = []
        cond_idxs = idxs[:cond_size]  # The indices of the qubits for the condition
        body_idxs = idxs[cond_size:]  # The rest are for the body
        # 1. Measure all condition qubits into corresponding classical bits
        for qidx in cond_idxs:
            code.append(f"measure q[{qidx}] -> c[{qidx}];")
        # 2. For each option, emit an if statement
        handled_else = False
        for cond_val, body in options.items():
            if cond_val in ("else", "default"):
                handled_else = True
                continue  # Handle after all other options
            # cond_val: expected classical value (int or str representing bits)
            # Convert cond_val to bitstring if needed
            if isinstance(cond_val, int):
                bitstr = format(cond_val, f"0{cond_size}b")
            elif isinstance(cond_val, str) and cond_val.isdigit():
                bitstr = format(int(cond_val), f"0{cond_size}b")
            else:
                bitstr = cond_val  # Assume already a bitstring
            # Build the OpenQASM if condition (e.g., c[0]==1 && c[1]==0)
            cond_expr = " && ".join(
                f"c[{cond_idxs[i]}]=={bitstr[i]}" for i in range(cond_size)
            )
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
            code.append(f"if ({cond_expr}) {body_code_str}")
        # Handle else/default option if present
        if handled_else:
            body = options.get("else") or options.get("default")
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
            # The else branch: if none of the above, so negate all previous conditions
            prev_conds = []
            for cond_val in options:
                if cond_val in ("else", "default"): continue
                if isinstance(cond_val, int):
                    bitstr = format(cond_val, f"0{cond_size}b")
                elif isinstance(cond_val, str) and cond_val.isdigit():
                    bitstr = format(int(cond_val), f"0{cond_size}b")
                else:
                    bitstr = cond_val
                cond_expr = " && ".join(
                    f"c[{cond_idxs[i]}]=={bitstr[i]}" for i in range(cond_size)
                )
                prev_conds.append(f"({cond_expr})")
            if prev_conds:
                else_expr = "! (" + " || ".join(prev_conds) + ")"
            else:
                else_expr = "1"  # Always true if no previous conditions
            code.append(f"if ({else_expr}) {body_code_str}")
        self._instr_status = InstrStatus.DONE
        return tuple(code), self._instr_status
