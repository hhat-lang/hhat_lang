from __future__ import annotations

from collections import OrderedDict
from typing import Any, Iterable

from hhat_lang.core.data.core import CompositeSymbol, Symbol
from hhat_lang.core.data.fn_def import BaseFnCheck, BaseFnKey, FnDef
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure


class TypeTable:
    _table: OrderedDict[Symbol | CompositeSymbol, BaseTypeDataStructure]
    __slots__ = ("_table",)

    def __init__(self):
        self._table = OrderedDict()

    @property
    def table(self) -> OrderedDict[Symbol | CompositeSymbol, BaseTypeDataStructure]:
        return self._table

    def add(self, name: Symbol | CompositeSymbol, data: BaseTypeDataStructure) -> None:
        if isinstance(name, Symbol | CompositeSymbol) and isinstance(
            data, BaseTypeDataStructure
        ):
            if name not in self.table:
                self.table[name] = data

        else:
            raise ValueError(
                f"type {name} must be symbol/composite symbol and its data must be "
                f"known type structure"
            )

    def get(
        self, name: Symbol | CompositeSymbol, default: Any | None = None
    ) -> BaseTypeDataStructure | None:
        return self.table.get(name, default)

    def __hash__(self) -> int:
        return hash(self.table)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TypeTable):
            return hash(self) == hash(other)

        return False

    def __getitem__(
        self, item: Symbol | CompositeSymbol
    ) -> BaseTypeDataStructure | None:
        return self.get(item)

    def __contains__(self, item: Any) -> bool:
        return item in self.table

    def __len__(self) -> int:
        return len(self.table)

    def __iter__(self) -> Iterable:
        return iter(self.table.items())

    def __repr__(self) -> str:
        content = "\n        ".join(f"{v}" for v in self.table.values())
        return f"\n    - types:\n        {content}\n"


class FnTable:
    """
    This class holds functions definitions as ``BaseFnCheck`` for function
    entry (function name, type and argument types) and its body (content).

    Together with ``TypeTable``, ``SymbolTable`` and ``IRModule`` it provides
    the base for an IR object picturing the full code.
    """

    _table: OrderedDict[Symbol | CompositeSymbol, dict[BaseFnCheck, FnDef]]
    __slots__ = ("_table",)

    def __init__(self):
        self._table = OrderedDict()

    @property
    def table(
        self,
    ) -> OrderedDict[Symbol | CompositeSymbol, dict[BaseFnCheck, FnDef]]:
        return self._table

    def add(self, fn_entry: BaseFnCheck, data: FnDef) -> None:
        if isinstance(data, FnDef):
            if isinstance(fn_entry, BaseFnCheck):
                if fn_entry.name in self.table:
                    self.table[fn_entry.name].update({fn_entry: data})

                else:
                    self.table[fn_entry.name] = {fn_entry: data}

            elif isinstance(fn_entry, BaseFnKey):
                new_fn_entry = BaseFnCheck(
                    fn_name=fn_entry.name, args_types=fn_entry.args_types
                )
                if fn_entry.name in self.table:
                    self.table[fn_entry.name].update({new_fn_entry: data})

                else:
                    self.table[fn_entry.name] = {new_fn_entry: data}

            else:
                raise ValueError(f"fn_entry is of wrong type ({type(fn_entry)})")

    def get(
        self,
        fn_entry: Symbol | CompositeSymbol | BaseFnCheck,
        default: Any | None = None,
    ) -> FnDef | dict[BaseFnCheck, FnDef] | None:
        match fn_entry:
            case Symbol() | CompositeSymbol():
                return self.table.get(fn_entry, default)

            case BaseFnCheck():
                if fn_entry.name in self.table:
                    return self.table[fn_entry.name].get(fn_entry, default)

        raise ValueError(f"cannot retrieve fn {fn_entry}")

    def __hash__(self) -> int:
        return hash(self.table)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FnTable):
            return hash(self) == hash(other)

        return False

    def __contains__(self, item: Any) -> bool:
        match item:
            case Symbol() | CompositeSymbol():
                return item in self._table

            case BaseFnCheck():
                return item in self._table[item.name]

            case _:
                return False

    def __len__(self) -> int:
        return sum(len(k) for k in self.table.values())

    def __iter__(self) -> Iterable:
        return iter((p, q) for v in self.table.values() for p, q in v.items())

    def __repr__(self) -> str:
        content = "\n        ".join(
            f"{k}:\n          {v}" for h in self.table.values() for k, v in h.items()
        )
        return f"\n    - fns:\n        {content}"


class SymbolTable:
    """To store types and functions"""

    _types: TypeTable
    _fns: FnTable
    __slots__ = ("_types", "_fns")

    def __init__(self):
        self._types = TypeTable()
        self._fns = FnTable()

    @property
    def type(self) -> TypeTable:
        return self._types

    @property
    def fn(self) -> FnTable:
        return self._fns

    def __hash__(self) -> int:
        return hash((self._types, self._fns))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SymbolTable):
            return hash(self) == hash(other)

        return False
