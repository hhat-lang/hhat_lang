from __future__ import annotations

from typing import Any

from hhat_lang.core.builtin.quantum_instr import (
    BaseQuantumInstr, QuantumInstrList, BaseQRedim,
    BaseQSync, BaseQIf, BaseQNot
)
from hhat_lang.core.index.manager import IndexSupport
from hhat_lang.core.interpreter.base import BaseEvaluate

from hhat_lang.core.memory.manager import MemoryManager



def q__not(mem: MemoryManager, idxs: list[int], **_options: Any) -> list[str]:
    """
    Implements `@not` quantum instruction for *OpenQASM* v2. It is equivalent
    to **X** gate.

    Args:
        mem (MemoryManager): memory manager object to handle possible
            extra operations.
        idxs (list[int]): list of indexes to apply the gate on.
        _options (dict): to ignore extra arguments for completeness.

    Returns:
        the openqasm v2 code as str
    """

    code = [f"x q[{idx}];\n" for idx in idxs]
    return code


def q__redim(mem: MemoryManager, idxs: list[int], **_options: Any) -> list[str]:
    """
    Implements `@redim` quantum instruction for *OpenQASM* v2. It is equivalent
    to **Hadamard** gate.

    Args:
        mem (MemoryManager): memory manager object to handle possible
            extra operations.
        idxs (list[int]): list of indexes to apply the gate on.
        _options (dict): to ignore extra arguments for completeness.

    Returns:
        the openqasm v2 code as str
    """

    code = [f"h q[{idx}];\n" for idx in idxs]
    return code


def q__sync(mem: MemoryManager, ctrls: list[int], tgts: list[int], **_options: Any) -> list[str]:
    """
    Implements `@sync` quantum instruction for *OpenQASM* v2. It is equivalent
    to:

    - a plain **CNOT** gate
    - ... [to insert the other options here]

    Args:
        mem (MemoryManager): memory manager object to handle possible
            extra operations.
        ctrls (list[int]): list of control indexes to apply the gate on.
        tgts (list[int]): list of target indexes to apply the gate on.
        _options (dict): to ignore extra arguments for completeness.

    Returns:
        the openqasm v2 code as str
    """

    # TODO: build a more complete implementation

    # simple case: just apply cnot gate on qubits
    code = [f"cx q[{c}], q[{t}];\n" for c, t in zip(ctrls, tgts)]
    return code


class QRedim(BaseQRedim):
    _name = "@redim"

    def _gen_instr(self, mem: MemoryManager, evaluate: BaseEvaluate) -> list[str]:
        return [f"h q[{idx}];\n" for idx in self.idxs.target]

    def apply(
        self,
        *,
        idxs: IndexSupport,
        mem: MemoryManager,
        evaluate: BaseEvaluate,
    ) -> BaseQuantumInstr:
        self._idxs = idxs
        self._instr = QuantumInstrList(*self._gen_instr(mem))
        return self

    def get_instr(self, **kwargs: Any) -> QuantumInstrList:
        return self._instr


class QSync(BaseQSync):
    _name = "@sync"

    def _gen_instr(self, mem: MemoryManager, evaluate: BaseEvaluate) -> list[str]:
        # TODO: build a more complete implementation
        # simple case: just apply cnot gate on qubits
        return [f"cx q[{c}], q[{t}];\n" for c, t in zip(self._idxs.control, self._idxs.target)]

    def apply(
        self,
        *,
        idxs: IndexSupport,
        mem: MemoryManager,
        evaluate: BaseEvaluate,
    ) -> BaseQuantumInstr:
        self._idxs = idxs
        self._instr = QuantumInstrList(*self._gen_instr(mem))
        return self

    def get_instr(self, **kwargs: Any) -> QuantumInstrList:
        return self._instr


class QIf(BaseQIf):
    _name = "@if"

    def _gen_instr(self, mem: MemoryManager, evaluate: BaseEvaluate) -> list[str]:
        raise NotImplementedError()

    def apply(
        self,
        *,
        idxs: IndexSupport,
        mem: MemoryManager,
        evaluate: BaseEvaluate,
    ) -> BaseQuantumInstr:
        raise NotImplementedError()

    def get_instr(self, **kwargs: Any) -> QuantumInstrList:
        return self._instr


class QNot(BaseQNot):
    _name = "@not"

    def _gen_instr(self, mem: MemoryManager, evaluate: BaseEvaluate) -> list[str]:
        return [f"x q[{idx}];\n" for idx in self.idxs.target]

    def apply(
        self,
        *,
        idxs: IndexSupport,
        mem: MemoryManager,
        evaluate: BaseEvaluate,
    ) -> BaseQuantumInstr:
        self._idxs = idxs
        self._instr = QuantumInstrList(*self._gen_instr(mem))
        return self

    def get_instr(self, **kwargs: Any) -> QuantumInstrList:
        return self._instr
