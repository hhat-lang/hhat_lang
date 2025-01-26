from __future__ import annotations

from typing import Any

from hhat_lang.core.memory.manager import MemoryManager


def qnot(_mem: MemoryManager, idxs: list[int], **_options: Any) -> str:
    """
    Implements `@not` quantum instruction for *OpenQASM* v2. It is equivalent
    to **X** gate.

    Args:
        _mem (MemoryManager): memory manager object to handle possible
            extra operations.
        idxs (list[int]): list of indexes to apply the gate on.
        _options (dict): to ignore extra arguments for completeness.

    Returns:
        the openqasm v2 code as str
    """

    code = "".join(f"x q[{idx}];\n" for idx in idxs)
    return code


def qredim(_mem: MemoryManager, idxs: list[int], **_options: Any) -> str:
    """
    Implements `@redim` quantum instruction for *OpenQASM* v2. It is equivalent
    to **Hadamard** gate.

    Args:
        _mem (MemoryManager): memory manager object to handle possible
            extra operations.
        idxs (list[int]): list of indexes to apply the gate on.
        _options (dict): to ignore extra arguments for completeness.

    Returns:
        the openqasm v2 code as str
    """

    code = "".join(f"h q[{idx}];\n" for idx in idxs)
    return code


def qsync(_mem: MemoryManager, ctrls: list[int], tgts: list[int], **_options: Any) -> str:
    """
    Implements `@sync` quantum instruction for *OpenQASM* v2. It is equivalent
    to:

    - a plain **CNOT** gate
    - ... [to insert the other options here]

    Args:
        _mem (MemoryManager): memory manager object to handle possible
            extra operations.
        ctrls (list[int]): list of control indexes to apply the gate on.
        tgts (list[int]): list of target indexes to apply the gate on.
        _options (dict): to ignore extra arguments for completeness.

    Returns:
        the openqasm v2 code as str
    """

    # TODO: build a more complete implementation

    # simple case: just apply cnot gate on qubits
    code = "".join(f"cx q[{c}], q[{t}];\n" for c, t in zip(ctrls, tgts))
    return code
