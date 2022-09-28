"""Transpiling H-hat circuit type to OpenQASM (text) code"""

import os
import pre_hhat.types as types
from pre_hhat.qasm_modules.base import BaseTranspiler


class Transpiler(BaseTranspiler):
    gate_json = os.path.join(os.path.dirname(__file__), "gates_conversion.json")

    def __init__(self, data):
        super().__init__(data)

    @staticmethod
    def get_pulse(value) -> bool:
        # TODO: implement something on pulses here
        return False

    def get_gate(self, value: str) -> str:
        res = self.gates_conversion.get(value, self.get_pulse(value))
        if res:
            return res
        raise ValueError(f"{self.__class__.__name__}: cannot find gate {value} in OpenQASM base.")

    @staticmethod
    def get_indices(value):
        res = []
        for k in value:
            if isinstance(k, int):
                res.append(str(k))
            elif isinstance(k, types.SingleInt):
                res.append(str(k.value[0]))
        return res

    def unwrap_header(self) -> str:
        code = """OPENQASM 2.0;\ninclude "qelib1.inc";\n"""
        return code

    def unwrap_decl(self) -> str:
        return f"qreg q[{self.len}];\ncreg c[{self.len}];\n\n"

    def unwrap_gates(self) -> str:
        code = ""
        for k in self.data:
            gate = self.get_gate(k[1])
            indices = "q[" + "], q[".join(self.get_indices(k[0])) + "];"
            code += f"{gate} {indices}\n"
        return code

    def unwrap_meas(self) -> str:
        code = "measure q -> c;\n"
        return code
