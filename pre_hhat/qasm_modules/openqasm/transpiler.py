"""Transpiling H-hat circuit type to OpenQASM (text) code"""

import json

from pre_hhat.types.builtin import ArrayCircuit, SingleInt
from pre_hhat.qasm_modules.base import BaseTranspiler


class Transpiler(BaseTranspiler):
    try:
        gates_conversion = json.loads(open('gates_conversion.json', 'r').read())
    except FileNotFoundError:
        raise ValueError(f"Transpiler: cannot open file for gates conversion.")

    def __init__(self, data: ArrayCircuit):
        self.data = data
        self.len = len(self.data)

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
            elif isinstance(k, SingleInt):
                res.append(str(k.value[0]))
        return res

    def unwrap_header(self) -> str:
        code = """OPENQASM 2.0;\ninclude "qelib1.inc";\n"""
        return code

    def unwrap_decl(self) -> str:
        return f"qreg q[{self.len}];\ncreg c[{self.len}];\n\n"

    def unwrap_gates(self) -> str:
        code = ""
        for g, i in zip(self.data, self.data.indices):
            gate = self.get_gate(g)
            indices = 'q[' + '], q['.join(self.get_indices(i)) + '];'
            code += f"{gate} {indices}\n"
        return code

    def unwrap_meas(self) -> str:
        code = "measure q -> c;\n"
        return code

    def transpile(self) -> str:
        code = self.unwrap_header()
        code += self.unwrap_decl()
        code += self.unwrap_gates()
        code += self.unwrap_meas()
        return code
