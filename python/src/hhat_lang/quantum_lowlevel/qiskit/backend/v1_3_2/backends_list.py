from __future__ import annotations

from qiskit_aer import AerSimulator


DEFAULT_BACKEND = AerSimulator


backends = {
    "aersimulator": AerSimulator,
}
