from __future__ import annotations

import sys
from enum import IntEnum, auto


class InstrStatus(IntEnum):
    NOT_STARTED = auto()
    RUNNING = auto()
    TIMEOUT = auto()
    INTERRUPTED = auto()
    DONE = auto()
    ERROR = auto()


def check_quantum_type_correctness(names: tuple[str, ...]) -> None:
    """
    Check whether the quantum and classical symbols follow the rules:
    - a quantum data can have classical data
    - a classical data cannot have a quantum one
    """

    prev_quantum = False
    cur_quantum = False
    for n, name in enumerate(names):
        if n != 0 and cur_quantum and not prev_quantum:
            raise ValueError(
                f"{name} is an attribute from a non-quantum symbol. "
                f"Cannot have a quantum attribute from a classical symbol."
            )

        prev_quantum = True if cur_quantum else False
        cur_quantum = True if name.startswith("@") else False


#######################################
# PERFECT HASH FUNCTION (PHF) SECTION #
#######################################

def get_phf_prime(tuple_len: int) -> int:
    """
    Retrieve a prime for the perfect hash function (PHF) algorithm. Use the tuple length
    to check which primer number to use, which must be bigger than ``tuple_len``.

    Probably a relatively good size project may have a few hundreds items (types and
    functions combined). By that time, python will not be useful to interpret the code
    anyway, but we never know what things will come out of it.
    """

    if tuple_len <= 2**5:
        return 37

    if tuple_len <= 2**6:
        return 67

    if tuple_len <= 2**8:
        return 257

    if tuple_len <= 2**12:
        return 4_099

    if tuple_len <= 2**14:
        return 16_411

    # I don't think this number below will ever be needed, but for future references
    return 1_048_583


PHF_A_LIMIT = 1_000_000
"""perfect hash function (PHF) parameter ``a`` limit"""

# only compatible with 64- or 128-bit systems
PHF_R_LIMIT = 127 if sys.maxsize > 2**64 else 61
"""perfect hash function (PHF) parameter ``r`` limit"""


class ResultPHF:
    """Hold PHF result values"""

    _a: int
    _r: int
    __slots__ = ("_a", "_r")

    def __init__(self, *, a: int, r: int):
        self._a = a
        self._r = r

    @property
    def a(self) -> int:
        return self._a

    @property
    def r(self) -> int:
        return self._r
