from __future__ import annotations

from collections import deque
from typing import Any

from hhat_lang.core.constructors import FullName


class DataTable:
    def __init__(self):
        self._data = deque()

    def add(self, value: Any) -> int:
        return self.append(value)

    def append(self, value: Any) -> int:
        self._data.append(value)
        return len(self._data)

    def get(self, ref: int) -> Any:
        return self.__getitem__(ref)

    def __getitem__(self, ref: int) -> Any:
        return self._data[ref]

    def __repr__(self) -> str:
        return "DataTable[ " + "\n ".join(map(str, self._data)) + "]\n"


class ReferenceKeeping:
    def __init__(self):
        self._data: dict = dict()

    def add(self, type_name: FullName, index: int) -> None:
        self.__setitem__(type_name, index)

    def get(self, type_name: FullName) -> Any:
        return self.__getitem__(type_name)

    def __getitem__(self, key: FullName) -> int:
        return self._data[key]

    def __setitem__(self, key: FullName, index: int) -> None:
        self._data[key] = index

    def __repr__(self) -> str:
        return "Ref{" + " ".join(f"{k}:{v}" for k,v in self._data.items()) + "}"


class MemoryData:
    def __init__(self, name: str):
        self._name: str = name
        self._data: DataTable = DataTable()
        self._ref: ReferenceKeeping = ReferenceKeeping()

    @property
    def name(self) -> str:
        return self._name

    def get_index(self, type_name: FullName) -> int:
        return self._ref[type_name]

    def get_data(self, index: int) -> Any:
        return self._data[index]

    def add(self, type_name: FullName, data: Any) -> None:
        index = self._data.add(data)
        self._ref.add(type_name, index)

    def get(self, type_name: FullName) -> Any:
        return self.get_data(self.get_index(type_name))

    def ref_view(self) -> str:
        return self.name +str(self._ref)

    def data_view(self) -> str:
        return self.name + str(self._data)


class MemoryManager:
    def __init__(self, scope: Any):
        self._scope = scope
        self._type_mem: MemoryData = MemoryData()
        self._fn_mem: MemoryData = MemoryData()
        self._var_mem: MemoryData = MemoryData()

    @classmethod
    def _add(cls, name: FullName, data: Any, table_type: MemoryData) -> None:
        table_type.add(name, data)

    @classmethod
    def _get(cls, name: FullName, table_type: MemoryData) -> Any:
        return table_type.get(name)

    @classmethod
    def _view(cls, table_type: MemoryData) -> str:
        ref = table_type.ref_view()
        data = table_type.data_view()
        return f"#{table_type.name}MemoryView:\n {ref}\n{data}\n" + "-" * 30

    def add_type(self, type_name: FullName, data: Any) -> None:
        self._add(type_name, data, self._type_mem)

    def add_fn(self, fn_name: FullName, data: Any) -> None:
        self._add(fn_name, data, self._fn_mem)

    def add_var(self, var_name: FullName, data: Any) -> None:
        self._add(var_name, data, self._var_mem)

    def get_type(self, type_name: FullName) -> Any:
        return self._get(type_name, self._type_mem)

    def get_fn(self, fn_name: FullName) -> Any:
        return self._get(fn_name, self._fn_mem)

    def get_var(self, var_name: FullName) -> Any:
        return self._get(var_name, self._var_mem)

    def type_mem_view(self) -> str:
        return self._view(self._type_mem)

    def fn_mem_view(self) -> str:
        return self._view(self._fn_mem)

    def var_mem_view(self) -> str:
        return self._view(self._var_mem)

    def mem_view(self) -> str:
        return self._view(self._type_mem) + self._view(self._fn_mem) + self._view(self._var_mem)
