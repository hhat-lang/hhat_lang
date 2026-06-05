from __future__ import annotations

from pathlib import Path
from typing import Mapping

from hhat_lang.core.code.abstract import (
    IRHash,
    RefTable,
)
from hhat_lang.core.code.base import FnHeader
from hhat_lang.core.code.ir_graph import (
    IRGraph,
    IRNode,
)
from hhat_lang.core.data.core import (
    Symbol,
    CompositeSymbol,
)
from hhat_lang.core.data.fn_def import (
    FnDef,
    BuiltinFnDef,
)
from hhat_lang.core.types.abstract_base import BaseTypeDef


def get_type(
    node_key: IRHash, importing: Symbol | CompositeSymbol, ir_graph: IRGraph
) -> BaseTypeDef | None:
    """
    Import a type ``importing`` from an IR module's hash value ``node_key``. Return
    the type instance or ``None`` if not found.
    """

    node: IRNode | None = ir_graph.nodes[node_key]

    if node is not None:
        return node.ir.module.symbol_table.type.get(importing)

    return None


def get_fn(
    node_key: IRHash, importing: FnHeader, ir_graph: IRGraph
) -> FnDef | BuiltinFnDef | dict[FnHeader, FnDef | BuiltinFnDef] | None:
    """
    Import a function check instance ``importing`` from an IR module's hash value ``node_key``.

    Args:
        node_key: the ``IRHash`` instance
        importing: the function ``BaseFnCheck`` instance
        ir_graph: the program's ``IRGraph``

    Returns:
        A ``FnDef`` instance or ``None``, if no function is found.
    """

    node: IRNode | None = ir_graph.nodes[node_key]

    if node is not None:
        return node.ir.module.symbol_table.fn.get(importing)

    return None


def build_reftable(
    types: Mapping[Symbol | CompositeSymbol, Path] | None = None,
    fns: Mapping[FnHeader, Path] | None = None,
) -> RefTable:
    types = types or dict()
    fns = fns or dict()
    ref_table = RefTable()

    for type_name, ir_ref in types.items():
        ref_table.types.add_ref(type_name, ir_ref)

    for f_name, ir_ref in fns.items():
        ref_table.fns.add_ref(f_name, ir_ref)

    return ref_table
