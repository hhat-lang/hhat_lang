from qiskit_aer import QasmSimulator, AerJob
from qiskit import QuantumCircuit

from hhat_lang.datatypes.builtin_datatype import Hashmap
from hhat_lang.interpreter.shots_estimator import get_num_shots
from hhat_lang.quantum_backends.qiskit.q_lang_support import supported_lang


class Simulator:
    @staticmethod
    def get_result(backend_run: AerJob) -> dict:
        return backend_run.result().get_counts()

    @staticmethod
    def cast2hasmap(result: dict) -> Hashmap:
        return Hashmap(*result.items())

    def run(self, transpiled_code: QuantumCircuit) -> Hashmap:
        backend = QasmSimulator().from_backend('qasm_simulator')
        job = backend.run(transpiled_code)
        counts = job.result().get_counts()
        return self.cast2hasmap(counts)
