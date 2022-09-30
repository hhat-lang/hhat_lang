"""Transpiling H-hat circuit type to OpenQASM (text) code"""

import os
from pre_hhat import behavior_type
import pre_hhat.types as types
import pre_hhat.core.ast_exec as ast_exec
from pre_hhat.qasm_modules.base import BaseTranspiler


class Transpiler(BaseTranspiler):
    gate_json = os.path.join(os.path.dirname(__file__), "gates_conversion.json")

    def __init__(self, data, stack):
        super().__init__(data, stack)

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
        # print(f"** data: {self.data} {self.data.var}")
        for k in self.data:
            # print(f"gates? {k} {type(k)}")
            if isinstance(k, (types.Gate, types.GateArray, types.ArrayCircuit)):
                for g in k.name:
                    gate = self.get_gate(g)
                    if k.ct is None:
                        for p in self.get_indices(k.indices):
                            code += f"{gate} q[{p}];\n"
                    else:
                        indices = "q[" + "], q[".join(self.get_indices(k.indices)) + "];"
                        code += f"{gate} {indices}\n"
            else:
                # print(f"ast type? {self.stack['var']} {self.stack['res']} {k} {type(k)}")
                self.stack = self.ast_to_exec(k, self.stack, var=self.data.var)
        return code

    def unwrap_meas(self) -> str:
        code = "measure q -> c;\n"
        return code

    @staticmethod
    def ast_to_exec(code, stack, **kwargs):
        if behavior_type == "static":
            res = stack["res"]
            index = stack["index"]
            var = stack["var"]
            stack["res"] = ()
            stack["index"] = ()
            stack["var"] = kwargs.get("var", stack["var"])
            stack = ast_exec.Exec().walk_tree(code, stack)
            stack["res"] = res
            stack["index"] = index
            stack["var"] = var
            return stack
