from __future__ import annotations
from typing import Any, Callable

from enum import StrEnum


class QasmKeyword(StrEnum):
    QUBIT_REGISTER  = "qreg"
    BIT_REGISTER    = "creg"

    QUBIT_LABEL     = "q"
    BIT_LABEL       = "c"

    X_OPER          = "x"
    Y_OPER          = "y"
    Z_OPER          = "z"
    HADAMARD_OPER   = "h"
    CNOT_OPER       = "cx"
    CZ_OPER         = "cz"

    MEASUREMENT     = "measure"


def header_expr() -> str:
    code = "OPENQASM 2.0;\ninclude \"qelib1.inc\";\n"
    return code


def init_expr(num_qubits: int, num_bits: int) -> str:
    return f"qreg q[{num_qubits}];\ncreg c[{num_bits}];\n"


def oper_expr(operations: tuple, qubits: tuple) -> str:
    code = ""
    for o, qs in zip(operations, qubits):
        code += f"{o} "
        if isinstance(qs, int):
            code += f"{QasmKeyword.QUBIT_LABEL}[{qs}]"
        else:
            code += ", ".join(f"{QasmKeyword.QUBIT_LABEL}[{q}]" for q in qs)
        code += ";\n"
    return code


def measurement_expr(qubit: tuple, bit: tuple) -> str:
    code = ""
    for q, b in zip(qubit, bit):
        code += f"{QasmKeyword.MEASUREMENT} {QasmKeyword.QUBIT_REGISTER}[{q}] -> {QasmKeyword.BIT_REGISTER}[{b}];\n"
    return code
