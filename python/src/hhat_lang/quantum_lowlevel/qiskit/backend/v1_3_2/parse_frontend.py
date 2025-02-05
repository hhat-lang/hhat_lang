from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit.providers import BackendV2

from hhat_lang.quantum_lowlevel.qiskit.frontend.openqasm.v2.base import str_to_lowlevel

from hhat_lang.quantum_lowlevel.qiskit.backend.v1_3_2.shots_estimation import ShotsEstimator


from hhat_lang.quantum_lowlevel.qiskit.backend.v1_3_2.backends_list import (
    backends,
    DEFAULT_BACKEND,
)


def load_backend(name: str) -> BackendV2:
    return backends.get(name, DEFAULT_BACKEND)()


def run_backend(backend_name: str, instr: str, shots: int) -> dict[str, int]:
    backend = load_backend(backend_name)
    circuit = str_to_lowlevel(instr, backend)
    result = backend.run(circuit, shots=shots).result()
    return result.get_counts(circuit)
