from __future__ import annotations

from typing import Any

from hhat_lang.core.code.ir import TypeTable
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure


def _size_resolver():
    pass


def _qsize_resolver(ds: BaseTypeDataStructure, table: TypeTable) -> int | None:
    if ds.qsize is not None:

        if ds.qsize.max is None:
            qsize_max = 0

            for _, member_type in ds:
                res = _qsize_resolver(table[member_type], table)

                if res:
                    qsize_max += res

            ds.qsize.add_max(qsize_max)

        return ds.qsize.max

    raise ValueError("Quantum type must have QSize defined.")


def ct_size() -> Any:
    """Compile-time size resolver."""

    pass


def ct_qsize(ds: BaseTypeDataStructure, type_table: TypeTable) -> Any:
    """Compile-time qsize resolver."""

    pass


def runtime_size() -> Any:
    """Runtime size resolver."""

    pass


def runtime_qsize() -> Any:
    """Runtime qsize resolver."""

    pass
