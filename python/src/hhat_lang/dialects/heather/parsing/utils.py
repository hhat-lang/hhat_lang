from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Iterable, Iterator

from hhat_lang.core.data.core import Symbol, CompositeSymbol
from hhat_lang.core.data.fn_def import BaseFnKey, FnDef, BaseFnCheck
from hhat_lang.core.imports.utils import BaseImports
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure
from hhat_lang.dialects.heather.code.simple_ir_builder.new_ir import IRBlock, BodyBlock


class ImportDicts(BaseImports):
    def __init__(self, types: TypesDict, fns: FnsDict):
        if isinstance(types, TypesDict) and isinstance(fns, FnsDict):
            self.types = types
            self.fns = fns


class TypesDict(Mapping):
    """
    A special dict-like class that holds types definitions, with key as
    ``CompositeSymbol`` and value as ``BaseTypeDataStructure`` object.
    """

    _data: dict[CompositeSymbol, BaseTypeDataStructure]

    def __init__(self, data: dict | None = None):
        self._data = data if isinstance(data, dict) else dict()

    def __setitem__(self, key: CompositeSymbol, value: BaseTypeDataStructure) -> None:
        if isinstance(key, CompositeSymbol) and isinstance(value, BaseTypeDataStructure):
            self._data[key] = value

        else:
            raise ValueError(f"{key} ({type(key)}) is not valid key for types")

    def __getitem__(self, key: CompositeSymbol, /) -> BaseTypeDataStructure:
        if isinstance(key, CompositeSymbol):
            return self._data[key]

        raise KeyError(key)

    def __len__(self) -> int:
        return len(self._data)

    def items(self) -> Iterator:
        yield from self._data.items()

    def keys(self) -> Iterator:
        yield from self._data.keys()

    def values(self) -> Iterator:
        return iter(self._data.values())

    def update(self, data: Mapping) -> None:
        self._data.update({k: v for k, v in data.items()})

    def __iter__(self) -> Iterable:
        return iter(self._data.keys())

    def __repr__(self) -> str:
        return str(self._data)


class FnsDict(Mapping):
    """
    A special dict-like class that holds functions definitions, with key
    as ``BaseFnKey`` and value as ``FnDef`` object.
    """

    _data: dict[Symbol | CompositeSymbol, dict[BaseFnKey, FnDef]]

    def __init__(self, data: dict | None = None):
        self._data = data if isinstance(data, dict) else dict()

    def __setitem__(self, key: BaseFnKey, value: FnDef) -> None:
        if isinstance(key, BaseFnKey) and isinstance(value, FnDef):
            if key.name in self._data:
                self._data[key.name].update({key: value})

            else:
                self._data.update({key.name: {key: value}})

        else:
            raise ValueError(f"{key} ({type(key)}) is not valid key for types")

    def __getitem__(self, key: BaseFnKey | BaseFnCheck, /) -> FnDef:
        if isinstance(key, BaseFnKey | BaseFnCheck):
            return self._data[key.name].get(key)

        raise KeyError(key)

    def __len__(self) -> int:
        return len(self._data)

    def _items(self) -> Iterable:
        return iter((p,q) for v in self._data.values() for p, q in v.items())

    def items(self) -> Iterable:
        return iter(self._data.items())

    def keys(self) -> Iterator:
        return iter(self._data.keys())

    def values(self) -> Iterator:
        return iter(self._data.values())

    def update(self, data: Mapping) -> None:
        self._data.update({k: v for k, v in data.items()})

    def __iter__(self) -> Iterable:
        """Iterates over the (BaseFnKey, FnDef) pairs"""
        return iter(self._items())

    def __contains__(self, item: Any) -> bool:
        return item in self._data.keys()

    def __repr__(self) -> str:
        return str(self._data)
