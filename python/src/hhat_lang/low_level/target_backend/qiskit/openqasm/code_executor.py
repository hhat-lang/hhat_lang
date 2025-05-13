from __future__ import annotations

from typing import Any

from qiskit import qasm2, QuantumCircuit, transpile
from qiskit.primitives.containers.pub_result import PubResult, DataBin

# TODO: to set the configuration's simulator instead of a fixed simulator
from qiskit_aer import AerSimulator
from qiskit_aer.primitives import SamplerV2 as Sampler

from hhat_lang.core.data.core import Symbol, WorkingData
from hhat_lang.core.error_handlers.errors import (
    InvalidQuantumComputedResult,
    ErrorHandler
)


def load_qasm(code: str) -> QuantumCircuit:
    return qasm2.loads(code)


def sample_circuit(
    circuit: QuantumCircuit,
    qdata: str | Symbol,
    metadata: dict[str, Any] | None = None,
) -> Any | ErrorHandler:
    """
    Generate the counts from a given qdata containing instructions turned into a circuit.
    """

    metadata = metadata or dict()

    # this should be replaced by a config backend, not a hardcoded one
    backend = AerSimulator()
    tcirc = transpile(circuit, backend=backend)

    sample = Sampler()
    n_shots = metadata.get("shots", None) or (len(circuit.qregs) * 888)
    job = sample.run([tcirc], shots=n_shots)

    job_res = job.result()

    if job_res:
        pub_res: PubResult = job_res[0]
        databin: DataBin = pub_res.data
        res = (getattr(databin, "c", None) or getattr(databin, "meas", None)).get_counts()
        return res

    # job_res is None, then something went wrong
    return InvalidQuantumComputedResult(qdata)


def execute_program(
    code: str,
    qdata: str | WorkingData,
    debug: bool = False
) -> Any | ErrorHandler:
    """
    Execute the quantum program from a quantum data `qdata`. First, it is passed as a
    string of code as a plain OpenQASM v2.0 code, then transformed into a qiskit's
    QuantumCircuit to be executed on a sampler instance to retrieve the bitstring
    distribution or an error.
    """

    circ = load_qasm(code)
    res = sample_circuit(circ, qdata)

    match res:

        # in case it had an error
        case InvalidQuantumComputedResult():
            # TODO: define properly what to do next
            return res

        # should contain the counts with bitstrings as keys (`Counter`?)
        case _:

            if debug:
                print(res)

            return res
