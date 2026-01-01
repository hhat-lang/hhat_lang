from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from hhat_lang.core.code.abstract import BaseIR, BaseIRModule
from hhat_lang.core.code.ir_graph import IRGraph
from hhat_lang.core.code.symbol_table import SymbolTable
from hhat_lang.core.code.tools import build_reftable
from hhat_lang.core.fns.core import builtin_fns_path
from hhat_lang.core.types.new_builtin_core import builtin_types


def gen_builtin_modules(
    ir_graph: IRGraph,
    ir_module: Callable[[Path, SymbolTable, ...], BaseIRModule],
    ir: type[BaseIR],
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

    for mod_path, mod_fns in builtin_fns_path.items():
        st = SymbolTable()
        for name, fn in mod_fns.items():
            st.fn.add(name, fn)

        ref_table = build_reftable()
        ir_mod_fn = ir_module(mod_path, st, **kwargs)
        ir_obj = ir(ref_table, ir_mod_fn)
        ir_graph.add_node(ir_obj)

    for mod_path, mod_types in builtin_types.items():
        st = SymbolTable()
        for name, t in mod_types.items():
            st.type.add(name, t)

        # include any dependencies as ref tables below:
        ref_table = build_reftable()
        ir_mod_type = ir_module(mod_path, st, **kwargs)
        ir_obj = ir(ref_table, ir_mod_type)
        ir_graph.add_node(ir_obj)

    ir_graph.build()
