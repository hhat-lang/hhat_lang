import json
from abc import ABC, abstractmethod
import pre_hhat.types as types
import pre_hhat.grammar.ast as gast
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
            self.stack = stack
            # self.len = len(self.data)
            self.var_indices, self.len = self.count_indices()

    def count_indices(self):
        index_track = ()
        total_index = 0
        print(self.data)
        print(self.stack["mem"])
        for n, k in enumerate(self.data):
            if isinstance(k, (types.Gate, types.GateArray)):
                total_index += len(k)
                index_track += tuple((self.data.var, p) for p in k.indices)
                print(f"-[{n}] got some gate {k} with indices {k.indices} or {len(k)}")
            elif isinstance(k, types.ArrayCircuit):
                index_track += tuple((k.var, p) for p in k.indices)
                total_index += len(k)
                print(f"-[{n}] got some var {k} with indices {k.indices} or {len(k)}")
            elif isinstance(k, gast.AST):
                if k.name == "id":
                    indices = self.stack["mem"][k, "indices"]
                    total_index += len(indices)
                    index_track += tuple((k, p) for p in indices)
                else:
                    index_track += ((),)
                print(f"-[{n}] got some AST {k}")
            else:
                print(f"{self.__class__.__name__}: unexpected type {type(k)}.")
        print(f">> index track={index_track} | total index={total_index}")
        return index_track, total_index

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
