from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Iterable, Iterator

from hhat_lang.core.code.base import FnHeader
from hhat_lang.core.data.core import Symbol
from hhat_lang.core.imports.utils import BaseImports


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

    _data: dict[Symbol, Path]

    def __init__(self, data: dict | None = None):
        self._data = data if isinstance(data, dict) else dict()

    def __setitem__(self, key: Symbol, value: Path) -> None:
        if isinstance(key, Symbol) and isinstance(value, Path):
            self._data[key] = value

        else:
            raise ValueError(f"{key} ({type(key)}) is not valid key for types")

    def __getitem__(self, key: Symbol, /) -> Path:
        if isinstance(key, Symbol):
            return self._data[key]

        raise KeyError(key)

    def __len__(self) -> int:
        return len(self._data)

    def items(self) -> Iterator:
        yield from self._data.items()

    def keys(self) -> Iterator:
        return iter(self._data.keys())

    def values(self) -> Iterator:
        return iter(self._data.values())

    def update(self, data: Mapping) -> None:
        self._data.update({k: v for k, v in data.items()})

    def __iter__(self) -> Iterable:
        yield from self._data.keys()

    def __repr__(self) -> str:
        return str(self._data)


class FnsDict(Mapping):
    """
    A special dict-like class that holds functions definitions, with key
    as ``BaseFnKey`` and value as ``FnDef`` or ``BuiltinFnDef`` object.
    """

    _data: dict[FnHeader, Path]

    def __init__(self, data: dict | None = None):
        self._data = data if isinstance(data, dict) else dict()

    def __setitem__(self, key: FnHeader, value: Path) -> None:
        if isinstance(key, FnHeader) and isinstance(value, Path):
            if key.name in self._data:
                self._data[key] = value

            else:
                self._data.update({key: value})

        else:
            raise ValueError(f"{key} ({type(key)}) is not valid key for types")

    def __getitem__(self, key: FnHeader, /) -> Path:
        if isinstance(key, FnHeader):
            return self._data[key]

        raise KeyError(key)

    def __len__(self) -> int:
        return len(self._data)

    def _items(self) -> Iterable:
        return iter(self._data.items())

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
        yield from self._items()

    def __contains__(self, item: Any) -> bool:
        return item in self._data.keys()

    def __repr__(self) -> str:
        return str(self._data)
