import json
from abc import ABC, abstractmethod
import pre_hhat.core.ast_exec as ast_exec


class BaseQasm(ABC):
    """
    class to provide base specification for QASM modules.
    """

    name = "base for QASM"

    @abstractmethod
    def run(self, data, stack, **kwargs):
        ...

    @abstractmethod
    def circuit_to_str(self, data, stack) -> str:
        ...

    @abstractmethod
    def str_to_qasm(self, code: str):
        ...

    @abstractmethod
    def circuit_to_qasm(self, data, stack, **kwargs):
        ...


class BaseTranspiler(ABC):
    gate_json = ""

    def __init__(self, data, stack):
        try:
            self.gates_conversion = json.loads(open(self.gate_json, "r").read())
        except FileNotFoundError:
            raise ValueError(f"Transpiler: cannot open file for gates conversion.")
        else:
            self.data = data
            self.len = len(self.data)
            self.stack = stack

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

    @abstractmethod
    def ast_to_exec(self, code, stack, **kwargs):
        ...

    def transpile(self) -> str:
        code = self.unwrap_header()
        code += self.unwrap_decl()
        code += self.unwrap_gates()
        code += self.unwrap_meas()
        return code
