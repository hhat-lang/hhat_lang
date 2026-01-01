from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Iterable

from hhat_lang.core.code.base import FnHeader, BaseIRBlock
from hhat_lang.core.code.symbol_table import SymbolTable
from hhat_lang.core.data.core import CompositeSymbol, Symbol


class IRHash:
    """
    IR key class to handle the nodes for the IRGraph.

    Use ``key`` attribute when comparing between ``IRModule``. It is also hashable.

    Use ``uid`` attribute when comparing between type or function name
    and an ``IRHash``, ``IRNode`` or ``IRModule``. This is the default when applying
    ``hash`` function to this class instance.
    """

    _key: Path
    _uid: int
    __slots__ = ("_key", "_uid")

    def __init__(self, ir_path: Path):
        if isinstance(ir_path, Path):
            self._key = ir_path
            self._uid = hash(ir_path)

        else:
            raise ValueError("ir_path must be of type Path")

    @property
    def key(self) -> Path:
        return self._key

    @property
    def uid(self) -> int:
        return self._uid

    def __hash__(self) -> int:
        return self._uid

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, IRHash):
            return hash(self) == hash(other)

        if isinstance(other, BaseIRModule):
            return hash(self) == hash(other.path)

        return False

    def __repr__(self) -> str:
        txt = Path()

        for p in reversed(self._key.parts):
            if p == "src":
                break

            txt = Path(p) / txt

        return f"[{txt}#{str(self._uid)[-8:]}]"


###################
# IR BASE CLASSES #
###################


class BaseIRModule(ABC):
    """Base abstract class for IR module definitions."""

    _path: Path
    _symbol_table: SymbolTable
    _main: BaseIRBlock

    @property
    def path(self) -> Path:
        return self._path

    @property
    def uid(self) -> int:
        return hash(self._path)

    @property
    def symbol_table(self) -> SymbolTable:
        return self._symbol_table

    @property
    def main(self) -> BaseIRBlock:
        return self._main

    def __hash__(self) -> int:
        return hash((hash(self._path), hash(self._symbol_table), hash(self._main)))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)

        return False

    def __contains__(
        self, item: Symbol | CompositeSymbol | FnHeader | Path | Any
    ) -> bool:
        return item in self._symbol_table.type or item in self._symbol_table.fn

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError()


class BaseIR(ABC):
    """
    Base class for the IR.

    IR holds information about the main code execution (as an IR block), or a symbol
    table containing type definitions or function definitions, and a reference table
    to point the definitions of types or functions from other IRs.
    """

    _ref_table: RefTable
    _module: BaseIRModule

    def __init__(self, ref_table: RefTable, module: BaseIRModule, **kwargs: Any):
        self._ref_table = ref_table
        self._module = module

    @property
    def module(self) -> BaseIRModule:
        return self._module

    @property
    def ref_table(self) -> RefTable:
        return self._ref_table

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError()


###########################
# REFERENCE TABLE CLASSES #
###########################


class RefTypeTable:
    """Reference to types from another IR"""

    _table: dict[Symbol | CompositeSymbol, IRHash]
    __slots__ = ("_table",)

    def __init__(self):
        self._table = dict()

    def add_ref(self, type_name: Symbol | CompositeSymbol, ir_path: Path) -> None:
        if isinstance(type_name, Symbol | CompositeSymbol) and isinstance(
            ir_path, Path
        ):
            self._table[type_name] = IRHash(ir_path)

        else:
            raise ValueError(f"wrong reference type table input ({type_name})")

    def get_irpath(self, type_name: Symbol | CompositeSymbol) -> Path:
        return self.get_irhash(type_name).key

    def get_irhash(self, type_name: Symbol | CompositeSymbol) -> IRHash:
        return self._table[type_name]

    def __hash__(self) -> int:
        return hash(self._table)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, RefTypeTable):
            return hash(self) == hash(other)

        return False

    def __contains__(self, item: Symbol | CompositeSymbol | Any) -> bool:
        return item in self._table

    def __len__(self) -> int:
        return len(self._table)

    def __iter__(self) -> Iterable[tuple[Symbol | CompositeSymbol, IRHash]]:
        return iter(self._table.items())


class RefFnTable:
    """Reference to functions from another IR"""

    _table: dict[FnHeader, IRHash]
    __slots__ = ("_table",)

    def __init__(self):
        self._table = dict()

    def add_ref(self, fn_name: FnHeader, ir_path: Path) -> None:
        if isinstance(fn_name, FnHeader) and isinstance(ir_path, Path):
            self._table[fn_name] = IRHash(ir_path)

        else:
            raise ValueError(f"wrong reference type table input ({fn_name})")

    def get_irpath(self, fn_name: FnHeader) -> Path:
        return self.get_irhash(fn_name).key

    def get_irhash(self, fn_name: FnHeader) -> IRHash:
        return self._table[fn_name]

    def __hash__(self) -> int:
        return hash(self._table)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, RefFnTable):
            return hash(self) == hash(other)

        return False

    def __contains__(self, item: Symbol | CompositeSymbol | FnHeader) -> bool:
        match item:
            case FnHeader():
                return item in self._table

            case Symbol() | CompositeSymbol():
                for k in self._table:
                    if item == k.name:
                        return True

                return False

            case _:
                return False

    def __len__(self) -> int:
        return len(self._table)

    def __iter__(self) -> Iterable[tuple[FnHeader, IRHash]]:
        return iter(self._table.items())


class RefTable:
    """To store reference for types and functions from another IR"""

    _types: RefTypeTable
    _fns: RefFnTable
    __slots__ = ("_types", "_fns")

    def __init__(
        self, *, type_ref: RefTypeTable | None = None, fn_ref: RefFnTable | None = None
    ):
        self._types = type_ref or RefTypeTable()
        self._fns = fn_ref or RefFnTable()

    @property
    def types(self) -> RefTypeTable:
        return self._types

    @property
    def fns(self) -> RefFnTable:
        return self._fns

    def __hash__(self) -> int:
        return hash(hash(self._types) + hash(self._fns))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, RefTable):
            return hash(self) == hash(other)

        return False

    def __contains__(self, item: Symbol | CompositeSymbol | FnHeader) -> bool:
        return item in self._types or item in self._fns
