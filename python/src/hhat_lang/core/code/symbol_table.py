from __future__ import annotations

from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Generic, Iterable, TypeVar

from hhat_lang.core.code.base import FnHeader, FnHeaderDef
from hhat_lang.core.data.core import CompositeSymbol, Symbol
from hhat_lang.core.data.fn_def import BuiltinFnDef, FnDef, ModifierDef
from hhat_lang.core.data.var_def import DataDef
from hhat_lang.core.types.new_base_type import TypeDef

K = TypeVar("K")
V = TypeVar("V")


class BaseTable(ABC, Generic[K, V]):
    @abstractmethod
    @property
    def table(self) -> OrderedDict[K, V]:
        raise NotImplementedError()

    @abstractmethod
    def add(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def get(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def __hash__(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def __getitem__(self, item: Any) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def __contains__(self, item: Any) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError()

    @abstractmethod
    def __iter__(self) -> Iterable:
        raise NotImplementedError()

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError()


class TypeTable(BaseTable[Symbol | CompositeSymbol, TypeDef]):
    _table: OrderedDict[Symbol | CompositeSymbol, TypeDef]
    __slots__ = ("_table",)

    def __init__(self):
        self._table = OrderedDict()

    @property
    def table(self) -> OrderedDict[Symbol | CompositeSymbol, TypeDef]:
        return self._table

    def add(self, name: Symbol | CompositeSymbol, data: TypeDef) -> None:
        if isinstance(name, Symbol | CompositeSymbol) and isinstance(data, TypeDef):
            if name not in self.table:
                self.table[name] = data

        else:
            raise ValueError(
                f"type {name} must be symbol/composite symbol and its data must be "
                f"known type structure"
            )

    def get(
        self, name: Symbol | CompositeSymbol, default: Any | None = None
    ) -> TypeDef | Any | None:
        return self.table.get(name, default)

    def __hash__(self) -> int:
        return hash(self.table)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TypeTable):
            return hash(self) == hash(other)

        return False

    def __getitem__(self, item: int | Symbol | CompositeSymbol) -> TypeDef | Any | None:
        if isinstance(item, int):
            return tuple(self.table.items())[item]

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


class FnTable(
    BaseTable[Symbol | CompositeSymbol, dict[FnHeader, FnDef | BuiltinFnDef]]
):
    """
    This class holds functions definitions as ``BaseFnCheck`` for function
    entry (function name, type and argument types) and its body (content).

    Together with ``TypeTable``, ``SymbolTable`` and ``IRModule`` it provides
    the base for an IR object picturing the full code.
    """

    _table: OrderedDict[Symbol | CompositeSymbol, dict[FnHeader, FnDef | BuiltinFnDef]]
    __slots__ = ("_table",)

    def __init__(self):
        self._table = OrderedDict()

    @property
    def table(
        self,
    ) -> OrderedDict[Symbol | CompositeSymbol, dict[FnHeader, FnDef | BuiltinFnDef]]:
        return self._table

    def add(self, fn_entry: FnHeader, data: FnDef | BuiltinFnDef) -> None:
        if isinstance(data, FnDef | BuiltinFnDef):
            if isinstance(fn_entry, FnHeader):
                if fn_entry.name in self.table:
                    self.table[fn_entry.name].update({fn_entry: data})

                else:
                    self.table[fn_entry.name] = {fn_entry: data}

            elif isinstance(fn_entry, FnHeaderDef):
                new_fn_entry = FnHeader(
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
        fn_entry: Symbol | CompositeSymbol | FnHeader,
        default: Any | None = None,
    ) -> FnDef | BuiltinFnDef | dict[FnHeader, FnDef | BuiltinFnDef] | None:
        match fn_entry:
            case Symbol() | CompositeSymbol():
                return self.table.get(fn_entry, default)

            case FnHeader():
                if fn_entry.name in self.table:
                    return self.table[fn_entry.name].get(fn_entry, default)

        raise ValueError(f"cannot retrieve fn {fn_entry}")

    def __hash__(self) -> int:
        return hash(self.table)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FnTable):
            return hash(self) == hash(other)

        return False

    def __getitem__(
        self, item: int | Symbol | CompositeSymbol | FnHeader
    ) -> FnDef | BuiltinFnDef | dict[FnHeader, FnDef | BuiltinFnDef | None]:
        if isinstance(item, int):
            return tuple(self.table.items())[item]

        return self.get(item)

    def __contains__(self, item: Any) -> bool:
        match item:
            case Symbol() | CompositeSymbol():
                return item in self._table

            case FnHeader():
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


class ConstTable(BaseTable[Symbol | CompositeSymbol, DataDef]):
    """
    This class holds all constants in a module
    """

    _table: OrderedDict[Symbol | CompositeSymbol, DataDef]
    __slots__ = ("_table",)

    def __init__(self):
        self._table = OrderedDict()

    @property
    def table(self) -> OrderedDict[Symbol | CompositeSymbol, DataDef]:
        return self._table

    def add(self, item: DataDef) -> None:
        if isinstance(item, DataDef) and item.is_constant:
            self._table[item.name] = item

        raise ValueError(
            f"data must be constant to be added to ConstTable; {item.name} ({item.type}) is not."
        )

    def get(
        self, item: Symbol | CompositeSymbol, default: Any | None = None
    ) -> DataDef | Any | None:
        return self._table.get(item, default)

    def __getitem__(self, item: Symbol | CompositeSymbol) -> DataDef | Any | Any:
        return self.get(item)

    def __hash__(self) -> int:
        return hash(self.table)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ConstTable):
            return hash(self) == hash(other)

        return False

    def __contains__(self, item: Any) -> bool:
        return item in self.table

    def __len__(self) -> int:
        return len(self.table)

    def __iter__(self) -> Iterable:
        return iter(self.table.items())

    def __repr__(self) -> str:
        content = "\n        ".join(
            f"{k}:\n          {v}" for h in self.table.values() for k, v in h.items()
        )
        return f"\n    - consts:\n        {content}"


class MetaModTable(BaseTable[Symbol | CompositeSymbol, dict[FnHeader, FnDef]]):
    """
    This class holds all meta modules in a module.
    """

    _table: OrderedDict[Symbol | CompositeSymbol, dict[FnHeader, FnDef]]
    __slots__ = ("_table",)

    def __init__(self):
        self._table = OrderedDict()

    @property
    def table(self) -> OrderedDict[Symbol | CompositeSymbol, dict[FnHeader, FnDef]]:
        return self._table

    def add(self, fn_entry: FnHeader, data: FnDef) -> None:
        # TODO: check whether it needs more specific information (copied from FnTable)

        if isinstance(data, FnDef):
            if isinstance(fn_entry, FnHeader):
                if fn_entry.name in self.table:
                    self.table[fn_entry.name].update({fn_entry: data})

                else:
                    self.table[fn_entry.name] = {fn_entry: data}

            elif isinstance(fn_entry, FnHeaderDef):
                new_fn_entry = FnHeader(
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
        fn_entry: Symbol | CompositeSymbol | FnHeader,
        default: Any | None = None,
    ) -> FnDef | dict[FnHeader, FnDef] | None:
        # TODO: check if it needs more information (copied from FnTable)

        match fn_entry:
            case Symbol() | CompositeSymbol():
                return self.table.get(fn_entry, default)

            case FnHeader():
                if fn_entry.name in self.table:
                    return self.table[fn_entry.name].get(fn_entry, default)

        raise ValueError(f"cannot retrieve fn {fn_entry}")

    def __hash__(self) -> int:
        return hash(self.table)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, MetaModTable):
            return hash(self) == hash(other)

        return False

    def __getitem__(
        self, item: int | Symbol | CompositeSymbol | FnHeader
    ) -> FnDef | dict[FnHeader, FnDef] | None:
        if isinstance(item, int):
            return tuple(self.table.items())[item]

        return self.get(item)

    def __contains__(self, item: Any) -> bool:
        match item:
            case Symbol() | CompositeSymbol():
                return item in self._table

            case FnHeader():
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
        return f"\n    - metamods:\n        {content}"


class ModifierTable(BaseTable[Symbol | CompositeSymbol, dict[FnHeader, ModifierDef]]):
    """
    This class holds all modifiers in a module
    """

    _table: OrderedDict[Symbol | CompositeSymbol, dict[FnHeader, ModifierDef]]
    __slots__ = ("_table",)

    def __init__(self):
        self._table = OrderedDict()

    @property
    def table(
        self,
    ) -> OrderedDict[Symbol | CompositeSymbol, dict[FnHeader, ModifierDef]]:
        return self._table

    def add(self, fn_entry: FnHeader, data: ModifierDef) -> None:
        if isinstance(data, ModifierDef) and isinstance(fn_entry, FnHeader):
            if fn_entry.name in self.table:
                self.table[fn_entry.name].update({fn_entry: data})

            else:
                self.table[fn_entry.name] = {fn_entry: data}

    def get(
        self, item: Symbol | CompositeSymbol | FnHeader, default: Any | None = None
    ) -> ModifierDef | dict[FnHeader, ModifierDef] | None:
        match item:
            case Symbol() | CompositeSymbol():
                return self.table.get(item, default)

            case FnHeader():
                if item.name in self.table:
                    return self.table[item.name].get(item, default)

        raise ValueError(f"cannot retrieve fn {item}")

    def __hash__(self) -> int:
        return hash(self.table)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ModifierTable):
            return hash(self) == hash(other)

        return False

    def __getitem__(
        self, item: int | Symbol | CompositeSymbol | FnHeader
    ) -> ModifierDef | dict[FnHeader, ModifierDef] | None:
        if isinstance(item, int):
            return tuple(self.table.items())[item]

        return self.get(item)

    def __contains__(self, item: Any) -> bool:
        match item:
            case Symbol() | CompositeSymbol():
                return item in self._table

            case FnHeader():
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
        return f"\n    - modifiers:\n        {content}"


class SymbolTable:
    """To store types and functions"""

    _types: TypeTable
    _fns: FnTable
    _consts: ConstTable
    _metamods: MetaModTable
    _modifiers: ModifierTable
    __slots__ = ("_types", "_fns", "_consts", "_metamods", "_modifiers")

    def __init__(self):
        self._types = TypeTable()
        self._fns = FnTable()
        self._consts = ConstTable()
        self._metamods = MetaModTable()
        self._modifiers = ModifierTable()

    @property
    def type(self) -> TypeTable:
        return self._types

    @property
    def fn(self) -> FnTable:
        return self._fns

    @property
    def const(self) -> ConstTable:
        return self._consts

    @property
    def metamod(self) -> MetaModTable:
        return self._metamods

    @property
    def modifier(self) -> ModifierTable:
        return self._modifiers

    def __hash__(self) -> int:
        return hash(
            (self._types, self._fns, self._consts, self._metamods, self._modifiers)
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SymbolTable):
            return hash(self) == hash(other)

        return False
