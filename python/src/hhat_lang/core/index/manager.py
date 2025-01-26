from __future__ import annotations

from collections import deque
from copy import deepcopy
from typing import Any, Iterable

from hhat_lang.core.type_system.utils import FullName, QSize
from hhat_lang.core.utils.result_handler import Result, ResultType


class ItemIndexes:
    """
    Provides a container for indexes of a quantum variable. It works basically
    as a deque of integers, but it pushes from the right and pops from the left.

    This class should be used in the context of `MappedIndexes`, as one of its
    base data.
    """

    def __init__(self):
        self._size: int = 0
        self._data: deque[int] = deque()

    @property
    def size(self) -> int:
        return self._size

    @property
    def data(self) -> str:
        return "[" + " ".join(str(k) for k in self._data) + "]"

    def push(self, item: int) -> Result:
        if item not in self._data:
            self._size += 1
            self._data.append(item)
            return Result(ResultType.OK)(None)
        return Result(ResultType.ERROR)(item)

    def push_many(self, items: deque[int]) -> Result:
        for k in items:
            r = self.push(k)
            if not r:
                return Result(ResultType.ERROR)(r.value)
        return Result(ResultType.OK)(None)

    def pop(self) -> int:
        self._size -= 1
        return self._data.popleft()

    def pop_many(self, num: int) -> deque[int]:
        self._size -= num
        return deque([self.pop() for _ in range(num)])

    def peek(self) -> list[int]:
        return list(self._data)

    def filter(self, mask: Iterable[int]) -> list[int]:
        return list(k for k in self.peek() if k in mask)

    def free(self) -> deque[int]:
        """
        Free index data and return it as deque of integers.

        Returns:
            The object data as deque of integers
        """
        res = deepcopy(self._data)
        self._size = 0
        self._data.clear()
        return res


class MappedIndexes:
    """
    Serves as a data container for variables and their indexes usage during program execution.
    """

    def __init__(self):
        self._data: dict[str, ItemIndexes] = dict()
        self._total: int = 0

    @property
    def total(self):
        return self._total

    def push(self, variable: str, value: int) -> Result:
        if variable not in self._data:
            self._data[variable] = ItemIndexes()
        res = self._data[variable].push(value)
        self._total += 1
        return res

    def push_many(self, variable: str, values: Iterable[int]) -> None:
        for value in values:
            r = self.push(variable, value)
            if not r:
                raise ValueError(f"value {r.value} duplicated on variable {variable}")

    def pop(self, variable: str) -> int:
        if variable in self._data:
            self._total -= 1
            return self._data[variable].pop()
        else:
            raise ValueError(f"variable '{variable}' seems to not contain any indexes")

    def pop_many(self, variable: str, num_indexes: int) -> deque[int]:
        self._total -= num_indexes
        return self._data[variable].pop_many(num_indexes)

    def free(self, variable: str) -> deque[int]:
        self._total -= self._data[variable].size
        if self._total == 0:
            return self._data.pop(variable).free()
        raise ValueError(
            f"tried to free indexes, but the total mapped indexes ({self._total}) is "
            f"different from the variable '{variable}' index data ({self._data[variable].size})"
        )

    def __setitem__(self, variable: str, value: int | Iterable[int]) -> None:
        if isinstance(value, int):
            self.push(variable, value)
        else:
            self.push_many(variable, value)

    def __getitem__(self, variable: str | tuple[str, int]) -> int | deque[int]:
        if isinstance(variable, str):
            return self.pop(variable)
        return self.pop_many(variable[0], variable[1])

    def __repr__(self) -> str:
        text = "#MappedIndexes\n"
        total_str = len(str(self._total))
        for k, v in self._data.items():
            text += f"  ({'0'*(total_str-len(str(v.size)))}{v.size}) {k}: {v.data}\n"
        text += "-" * (5 + total_str)
        text += f"\n   {self.total}\n#.\n"
        return text


class IndexKeeping:
    """
    To keep track of the minimum and maximum number of indexes that types will use
    during the execution of a quantum variable of a specific quantum datatype.
    """

    def __init__(self):
        self._data: dict[FullName, QSize] = dict()

    def add(self, name: FullName, qsize: QSize) -> Any:
        self._data[name] = qsize


class IndexManager:
    """
    Manages the index usage throughout the program execution.

    Indexes are qubits labelled differently to avoid unnecessary complexity and
    ambiguity for the user to build programs.
    """

    def __init__(self):
        self._mapped = MappedIndexes()
        self._keeping = IndexKeeping()
