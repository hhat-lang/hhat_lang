import json
from abc import ABC, abstractmethod

from pre_hhat.types import ArrayCircuit


class BaseQasm(ABC):
    """
    class to provide base specification for QASM modules.
    """

    name = "base for QASM"

    @abstractmethod
    def run(self, data: ArrayCircuit, **kwargs) -> dict:
        ...

    @abstractmethod
    def circuit_to_str(self, data: ArrayCircuit) -> str:
        ...

    @abstractmethod
    def str_to_qasm(self, code: str):
        ...

    @abstractmethod
    def circuit_to_qasm(self, data: ArrayCircuit, **kwargs):
        ...


class BaseTranspiler(ABC):
    gate_json = ""

    def __init__(self, data: ArrayCircuit):
        try:
            self.gates_conversion = json.loads(open(self.gate_json, "r").read())
        except FileNotFoundError:
            raise ValueError(f"Transpiler: cannot open file for gates conversion.")
        else:
            self.data = data
            self.len = len(self.data)

    @abstractmethod
    def unwrap_header(self):
        ...

    @abstractmethod
    def unwrap_decl(self):
        ...

    @abstractmethod
    def unwrap_gates(self):
        ...

    @abstractmethod
    def unwrap_meas(self):
        ...

    def transpile(self) -> str:
        code = self.unwrap_header()
        code += self.unwrap_decl()
        code += self.unwrap_gates()
        code += self.unwrap_meas()
        return code
