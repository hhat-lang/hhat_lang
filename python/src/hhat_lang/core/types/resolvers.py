"""
Collection of functions to resolve types and sizes (``Size`` and ``QSize``).

This is the step after all the types are stored in the ``SymbolTable``'s ``TypeTable``
of all the modules. It will look up for unresolved type members inside types, that is
types that are not built-in.

It checks for the right types definitions and sizes so all types are defined and
ready to be used during program execution.
"""

from __future__ import annotations

from typing import Any

from hhat_lang.core.code.ir_graph import IRGraph, IRNode
from hhat_lang.core.code.tools import get_type
from hhat_lang.core.code.symbol_table import TypeTable, SymbolTable
from hhat_lang.core.error_handlers.errors import (
    ErrorHandler,
    TypeMemberNotResolvedError,
)
from hhat_lang.core.types.abstract_base import BaseTypeDef


#################
# Resolve types #
#################


def resolve_members(
    table: TypeTable,
) -> None | ErrorHandler:
    """
    To resolve type members so everything is defined when the program is executed
    """

    # return TypeMemberNotResolvedError()


#################
# Resolve sizes #
#################


def _size_resolver():
    pass


def _qsize_resolver(ds: BaseTypeDef, node: IRNode, ir_graph: IRGraph) -> int | None:
    if ds.qsize is not None:
        if ds.qsize.max is None:
            qsize_max = 0

            for _, member_type in ds:
                if t := get_type(node.irhash, member_type, ir_graph):
                    res = _qsize_resolver(ds=t, node=node, ir_graph=ir_graph)

                    if res:
                        qsize_max += res

            ds.qsize.add_max(qsize_max)

        return ds.qsize.max

    raise ValueError("Quantum type must have QSize defined.")


def ct_size() -> Any:
    """Compile-time size resolver."""

    pass


def ct_qsize(ds: BaseTypeDef, type_table: TypeTable) -> Any:
    """Compile-time qsize resolver."""

    pass


def runtime_size() -> Any:
    """Runtime size resolver."""

    pass


def runtime_qsize() -> Any:
    """Runtime qsize resolver."""

    pass
