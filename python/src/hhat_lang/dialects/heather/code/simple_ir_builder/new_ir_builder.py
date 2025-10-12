from __future__ import annotations

from pathlib import Path

from hhat_lang.core.code.base import BaseFnCheck
from hhat_lang.core.code.new_ir import build_reftable
from hhat_lang.core.code.symbol_table import SymbolTable
from hhat_lang.core.data.core import CompositeSymbol, Symbol
from hhat_lang.core.data.fn_def import FnDef
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure
from hhat_lang.dialects.heather.code.simple_ir_builder.new_ir import (
    IR,
    BodyBlock,
    IRModule,
)
from hhat_lang.dialects.heather.parsing.utils import FnsDict, TypesDict

TypesTyping = TypesDict | dict[Symbol | CompositeSymbol, Path]
FnsTyping = FnsDict | dict[BaseFnCheck, Path]


def build_ir_module(
    *,
    path: Path | str,
    types: tuple[BaseTypeDataStructure, ...] | None = None,
    fns: tuple[FnDef, ...] | None = None,
    main: BodyBlock | None = None,
) -> IRModule:
    """
    Build an ``IRModule`` instance from types, functions and/or main body block.

    Args:
        path: the ``IRModule`` path instance or str
        types: tuple of ``BaseTypeDataStructure`` elements or ``None``. Default ``None``
        fns: tuple of ``FnDef`` elements or ``None``. Default ``None``
        main: a ``BodyBlock`` instance or ``None``. Default ``None``

    Returns:
        The ``IRModule`` instance
    """

    types = types or ()
    fns = fns or ()
    st = SymbolTable()
    path = path if isinstance(path, Path) else Path(path)

    for t in types:
        st.type.add(t.name, t)

    for f in fns:
        st.fn.add(f.fn_check, f)

    return IRModule(path=path, symboltable=st, main=main)


def build_ir(
    *,
    path: Path | str,
    ref_types: TypesTyping | None = None,
    ref_fns: FnsTyping | None = None,
    types: tuple[BaseTypeDataStructure, ...] | None = None,
    fns: tuple[FnDef, ...] | None = None,
    main: BodyBlock | None = None,
) -> IR:
    ref_table = build_reftable(types=ref_types, fns=ref_fns)
    ir_module = build_ir_module(path=path, types=types, fns=fns, main=main)
    return IR(ref_table=ref_table, ir_module=ir_module)
