from abc import ABC, abstractmethod

from pre_hhat.types.builtin import ArrayCircuit


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
    def transpile(self):
        ...
