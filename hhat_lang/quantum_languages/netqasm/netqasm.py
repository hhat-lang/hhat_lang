from __future__ import annotations

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
