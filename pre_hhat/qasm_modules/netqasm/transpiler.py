"""Transpiling H-hat circuit type to NetQASM (text) code"""

from pre_hhat.types import ArrayCircuit, SingleInt
from pre_hhat.qasm_modules.base import BaseTranspiler


class Transpiler(BaseTranspiler):
    gate_json = "gates_conversion.json"

    def __init__(self, data: ArrayCircuit):
        super().__init__(data=data)

    def unwrap_header(self):
        return ""

    def unwrap_decl(self):
        return ""

    def unwrap_gates(self):
        return ""

    def unwrap_meas(self):
        return ""
