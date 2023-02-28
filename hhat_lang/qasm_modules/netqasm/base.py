from abc import abstractmethod

from hhat_lang.qasm_modules.base import BaseQasm
from hhat_lang.qasm_modules.netqasm.transpiler import Transpiler
from hhat_lang.types import ArrayCircuit


class DummyDevice:
    def __init__(self, **kwargs):
        pass

    def run(self, data, **kwargs):
        return self


class NetQasmBase(BaseQasm):
    def run(self, data: ArrayCircuit, **kwargs) -> dict:
        pass

    def circuit_to_str(self, data: ArrayCircuit) -> str:
        pass

    def str_to_qasm(self, code: str):
        pass

    def circuit_to_qasm(self, data: ArrayCircuit, **kwargs):
        pass
