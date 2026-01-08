from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from hhat_lang.core.code.abstract import BaseIR, BaseIRModule
from hhat_lang.core.code.base import CompositeSymbol, FnHeader, Symbol
from hhat_lang.core.code.ir_graph import IRGraph
from hhat_lang.core.code.symbol_table import BaseTable, SymbolTable
from hhat_lang.core.code.tools import build_reftable
from hhat_lang.core.data.fn_def import BuiltinFnDef
from hhat_lang.core.fns.core import builtin_fns_path
from hhat_lang.core.types.new_base_type import TypeDef
from hhat_lang.core.types.new_builtin_core import builtin_types


def _get_table(value: Any, st: SymbolTable) -> BaseTable:
    if isinstance(value, FnHeader) or (
        isinstance(value, dict) and isinstance(next(iter(value.keys())), FnHeader)
    ):
        return st.fn

    return st.type


def add_builtin_modules(
    ir_graph: IRGraph,
    ir_module: Callable[[Path, SymbolTable, ...], BaseIRModule],
    ir: type[BaseIR],
    builtin_dict: dict[
        Path, dict[Symbol | CompositeSymbol, TypeDef] | dict[FnHeader, BuiltinFnDef]
    ],
    **kwargs: Any,
) -> None:
    """

    Args:
        ir_graph: ``IRGraph`` instance
        ir_module: IR module class (to be instantiated)
        ir: IR class (to be instantiated)
        builtin_dict: the dictionary containing the objects to be built (functions or types)
    """

    for mod_path, mod_objs in builtin_dict.items():
        st = SymbolTable()
        table: BaseTable = _get_table(mod_objs, st)

        for name, obj in mod_objs.items():
            table.add(name, obj)

        # TODO: include any dependencies as ref tables below:
        ref_table = build_reftable()
        ir_mod = ir_module(mod_path, st, **kwargs)
        ir_obj = ir(ref_table, ir_mod)
        ir_graph.add_node(ir_obj)


def gen_builtin_modules(
    ir_graph: IRGraph,
    ir_module: Callable[[Path, SymbolTable, ...], BaseIRModule],
    ir: type[BaseIR],
    to_build: bool = False,
    **kwargs: Any,
) -> None:
    """
    Generate all the IR nodes containing the built-in functions and types.

    Args:
        ir_graph: the ``IRGraph`` instance
        ir_module: a dialect-specific callable that generates an IR module
            (expecting at least ``Path`` and ``SymbolTable`` instances)
        ir: a dialect-specific IR object to be instantiated (expecting at
            least ``RefTable`` and IR module instances)
        **kwargs: extra arguments to be used on the IR object
    """

    add_builtin_modules(ir_graph, ir_module, ir, builtin_fns_path, **kwargs)
    add_builtin_modules(ir_graph, ir_module, ir, builtin_types, **kwargs)

    if to_build:
        ir_graph.build()
