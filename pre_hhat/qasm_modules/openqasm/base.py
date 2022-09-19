"""Base to provide common ground for all QASM and dummy QASM devices"""

from abc import abstractmethod

from qiskit import QuantumCircuit, converters as qiskit_conv
from qiskit.qasm import Qasm

from pre_hhat.qasm_modules.base import BaseQasm
from pre_hhat.qasm_modules.openqasm.transpiler import Transpiler
from pre_hhat.types import ArrayCircuit


class DummyDevice:
    """
    class provided to serve as a dummy template
    """

    def __init__(self, **kwargs):
        pass

    def run(self, data, **kwargs):
        return self

    @staticmethod
    def result() -> dict:
        from pre_hhat import execute_mode

        if execute_mode == "all":
            return {"0x0": 1024}
        if execute_mode == "one":
            return {"0x0": 1}


class OpenQasmBase(BaseQasm):
    @abstractmethod
    def run(self, *args, **kwargs):
        ...

    def circuit_to_str(self, data: ArrayCircuit) -> str:
        return Transpiler(data).transpile()

    def str_to_qasm(self, code: str) -> QuantumCircuit:
        qasm = Qasm(data=code)
        code_ast = qasm.parse()
        code_dag = qiskit_conv.ast_to_dag(code_ast)
        return qiskit_conv.dag_to_circuit(code_dag)

    def circuit_to_qasm(self, data: ArrayCircuit, **kwargs) -> QuantumCircuit:
        code = self.circuit_to_str(data)
        return self.str_to_qasm(code)
