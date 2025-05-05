from __future__ import annotations

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
