from __future__ import annotations

from typing import Any

from qiskit import qasm2, QuantumCircuit, transpile
from qiskit.providers import Backend

from hhat_lang.core.quantum_lowlevel_api.quantum_instr import BaseQuantumInstrList


def parse_instr():
    pass


def str_to_lowlevel(
    quantum_instr: QuantumInstrList,
    backend: Backend,
    **options: Any
) -> QuantumCircuit:
    code = f"""
    OPENQASM 2.0;
    include "qelib1.inc";
    {quantum_instr.build()}
    """
    circuit = qasm2.loads(code)  # include more options later if needed
    return transpile(circuit, backend)


class QuantumInstrList(BaseQuantumInstrList):
    def build(self) -> str:
        self.init = [f"qreg q[{self.num_qubits}];\ncreg c[{self.num_qubits}];"]
        self.meas = [f"measure q[{k}] -> c[{k}];\n" for k in range(self.num_qubits)]
        return "\n".join(k for k in self.init + self.instr + self.meas)

