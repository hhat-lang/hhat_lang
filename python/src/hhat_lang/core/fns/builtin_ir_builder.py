from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from hhat_lang.core.code.abstract import BaseIR, BaseIRModule
from hhat_lang.core.code.ir_graph import IRGraph
from hhat_lang.core.code.symbol_table import SymbolTable
from hhat_lang.core.code.tools import build_reftable
from hhat_lang.core.fns.core import builtin_fns_path


def build_ir_module(
    builtin_path: Path,
    ir_module: Callable[[Path, SymbolTable, ...], BaseIRModule],
    **kwargs: Any,
) -> BaseIRModule:
    st = SymbolTable()

    for fn in builtin_fns_path[builtin_path]:
        st.fn.add(fn.fn_check, fn)

    return ir_module(builtin_path, st, **kwargs)


def build_ir(
    builtin_path: Path,
    ir_module: Callable[[Path, SymbolTable, ...], BaseIRModule],
    ir: type[BaseIR],
    **kwargs: Any,
) -> BaseIR:
    """
    Constructs built-in functions IR instance. The ``ir_module`` argument must
    be a dialect-specific IRModule class as well as the ``ir`` argument, a
    dialect-specific ``IR`` class. If extra arguments are needed for either
    ``ir_module`` or ``ir``, they must be placed as keyword arguments.
    """

    # TODO: if there is some function that depends on other references, place
    #   it in the reftable arguments below:
    ref_table = build_reftable()
    ir_module = build_ir_module(builtin_path=builtin_path, ir_module=ir_module, **kwargs)
    return ir(ref_table, ir_module, **kwargs)


def gen_builtin_ir(
    builtin_path: Path,
    ir_graph: IRGraph,
    ir_module: Callable[[Path, SymbolTable, ...], BaseIRModule],
    ir: type[BaseIR],
    **kwargs: Any,
) -> None:
    """
    Generates a specific built-in module IR instance.

    Args:
        builtin_path: built-in module path, usually located at the *__init__.py*
            from the dialect's target function folder, e.g. ``math.BUILTIN_FN_PATH``
        ir_graph: the IR graph
        ir_module: the dialect-specific IR module as a callable (expecting at least
            Path and SymbolTable objects)
        ir: the dialect-specific IR as a callable (expecting at least RefTable and
            IR module objects)
        **kwargs: any extra arguments for both ir_module and ir arguments
    """

    ir_obj = build_ir(builtin_path=builtin_path, ir_module=ir_module, ir=ir, **kwargs)
    ir_graph.add_node(ir_obj)


def gen_all_builtin_modules(
    ir_graph: IRGraph,
    ir_module: Callable[[Path, SymbolTable, ...], BaseIRModule],
    ir: type[BaseIR],
    **kwargs: Any,
) -> None:
    """
    Generates all the built-in modules at once.

    Args:
        ir_graph: the IR graph
        ir_module: the dialect-specific IR module as a callable (expecting at least
            Path and SymbolTable objects)
        ir: the dialect-specific IR as a callable (expecting at least RefTable and
            IR module objects)
        **kwargs: any extra arguments for both ir_module and ir arguments
    """

    for _path, _fn in builtin_fns_path.items():
        gen_builtin_ir(builtin_path=_path, ir_graph=ir_graph, ir_module=ir_module, ir=ir, **kwargs)
