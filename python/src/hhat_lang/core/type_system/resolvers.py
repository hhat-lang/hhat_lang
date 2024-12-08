from __future__ import annotations

from typing import Any

from hhat_lang.core.memory.code_manager import CodeReference
from hhat_lang.core.type_system import QSize
from hhat_lang.core.type_system.base import BaseDataType


def resolve_types() -> Any:
    pass


def register_type_mem() -> Any:
    pass


def pre_compute_qsize(mem_ref: CodeReference[BaseDataType]) -> None:
    """
    Computes and resolves qsize min and max values for composite types at
    "compilation" time.
    """

    for _, data in mem_ref:
        resolve_qsize(mem_ref, data)


def resolve_qsize(mem_ref: CodeReference[BaseDataType], data: BaseDataType) -> QSize:
    new_data: BaseDataType = mem_ref[data.name]

    if new_data.qsize.defined:
        return new_data.qsize

    total_qsize = QSize()
    for name, member in new_data.members():
        new_qsize = resolve_qsize(mem_ref, member)
        total_qsize.inc_min(new_qsize.min)
        total_qsize.inc_max(new_qsize.max)

    return total_qsize


def runtime_compute_qsize(
    mem_ref: CodeReference[BaseDataType], data: BaseDataType
) -> None:
    """
    Computes qsize min and max values for composite types at runtime.
    """

    qsize: QSize = resolve_qsize(mem_ref, data)

    if qsize.max is None:
        raise ValueError(f"cannot compute index size (qsize) for type {data.name}")
