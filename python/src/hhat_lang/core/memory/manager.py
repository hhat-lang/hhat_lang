from __future__ import annotations

from collections import deque
from typing import Any


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


class MemoryManager:
    pass
