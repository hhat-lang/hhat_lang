"""Transpiling H-hat circuit type to OpenQASM (text) code"""

import os
from pre_hhat import behavior_type
import pre_hhat.types as types
import pre_hhat.core.ast_exec as ast_exec
import pre_hhat.grammar.ast as gast
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

    def decode_expr(self, data, pos=0):
        code = ""
        opers = ()
        for k in data:
            if isinstance(k, (types.Gate, types.GateArray, types.ArrayCircuit)):
                pass
            elif isinstance(k, gast.AST):
                if k.name == "id":
                    pass
                else:
                    pass
                res = self.decode_expr(k, pos)
                code += res[0]
                opers += res[1]
            else:
                pass
        return code, opers

    def unwrap_header(self) -> str:
        code = """OPENQASM 2.0;\ninclude "qelib1.inc";\n"""
        return code

    def unwrap_decl(self) -> str:
        return f"qreg q[{self.len}];\ncreg c[{self.len}];\n\n"

    def unwrap_gates(self) -> str:
        code = ""
        # # working code for simple quantum variable operations
        # for k in self.data:
        #     if isinstance(k, (types.Gate, types.GateArray, types.ArrayCircuit)):
        #         for g in k.name:
        #             gate = self.get_gate(g)
        #             if k.ct is None:
        #                 for p in self.get_indices(k.indices):
        #                     code += f"{gate} q[{p}];\n"
        #             else:
        #                 indices = "q[" + "], q[".join(self.get_indices(k.indices)) + "];"
        #                 code += f"{gate} {indices}\n"
        #     else:
        #         self.stack = self.ast_to_exec(k, self.stack, var=self.data.var)

        # to-be-working code for nested quantum variable operations
        cur_pos = 0
        for n, k in enumerate(zip(self.data, self.var_indices)):
            if isinstance(k[0], (types.Gate, types.GateArray, types.ArrayCircuit)):
                for g in k[0].name:
                    gate = self.get_gate(g)
                    if k[0].ct is None:
                        print(f'k -> {k[0].indices} {k[1]}')
                        for p, q in zip(self.get_indices(k[0].indices), k[1]):
                            print(f'indices? {p} {k[0].name} => {q}')
                            pass
                    else:
                        print('else indices')
                        indices = ""
            else:
                self.stack = self.ast_to_exec(k[0], self.stack, var=self.data.var)
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
