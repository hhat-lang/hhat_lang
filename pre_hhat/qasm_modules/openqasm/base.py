"""Base to provide common ground for all QASM and dummy QASM devices"""

from abc import abstractmethod

from qiskit import QuantumCircuit, converters as qiskit_conv
from qiskit.qasm import Qasm

import pre_hhat.core.ast_exec as ast_exec
from pre_hhat import behavior_type
from pre_hhat.qasm_modules.base import BaseQasm
from pre_hhat.qasm_modules.openqasm.transpiler import Transpiler


class DummyDevice:
    """
    class provided to serve as a dummy template
    """

    def __init__(self, **kwargs):
        pass

    def run(self, data, stack, **kwargs):
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
    def run(self, data, stack, **kwargs):
        ...

    def circuit_to_str(self, data) -> str:
        return Transpiler(data).transpile()

    def str_to_qasm(self, code: str) -> QuantumCircuit:
        qasm = Qasm(data=code)
        code_ast = qasm.parse()
        code_dag = qiskit_conv.ast_to_dag(code_ast)
        return qiskit_conv.dag_to_circuit(code_dag)

    def circuit_to_qasm(self, data, stack, **kwargs) -> QuantumCircuit:
        code = ""
        print("veio aqui?")
        if isinstance(data, (tuple, list)):
            for k in data:
                code = self.circuit_to_str(k)
        else:
            code = self.circuit_to_str(data)
        print(f"show me de code:\n{code}")
        now_qasm = self.str_to_qasm(code)
        print(f"now show qasm:\n{now_qasm}")
        print("chetau")
        return now_qasm

    def ast_to_qasm(self, code, stack):
        if behavior_type == "static":
            stack = ast_exec.Exec().walk_tree(code, stack)
            return stack
