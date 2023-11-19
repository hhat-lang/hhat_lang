from __future__ import annotations
from typing import Any, Callable


qubit_register  = "qreg"
bit_register    = "creg"
qubit_label     = "q"
bit_label       = "c"

x        = "x"
y        = "y"
z        = "z"
hadamard = "h"
cnot     = "cx"
cz       = "cz"

measurement = "measure"


def header_expr() -> str:
    code = "OPENQASM 2.0;\ninclude \"qelib1.inc\";\n"
    return code


def oper_expr(operations: tuple, qubits: tuple) -> str:
    code = ""
    for o, qs in zip(operations, qubits):
        code += f"{o} "
        code += ", ".join(f"{qubit_label}[{q}]" for q in qs)
        code += ";\n"
    return code


def measurement_expr(qubit: tuple, bit: tuple) -> str:
    code = ""
    for q, b in zip(qubit, bit):
        code += f"{measurement} {qubit_register}[{q}] -> {bit_label}[{b}];\n"
    return code


