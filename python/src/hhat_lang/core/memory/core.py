from __future__ import annotations

from collections import deque
from uuid import UUID

from hhat_lang.core.error_handlers.errors import (
    IndexAllocationError, ErrorHandler,
    IndexUnknownError, IndexVarHasIndexesError
)


class PIDManager:
    """
    Manages the PID for H-hat language, including all the dialects.
    """

    def new(self) -> UUID:
        pass

    def list(self) -> list[UUID]:
        pass


class IndexManager:
    def __init__(self, max_num_index: int):
        self._max_num_index: int = max_num_index
        self._available: deque = deque(
            *tuple(k for k in range(0, self._max_num_index)),
            maxlen=self._max_num_index
        )
        self._allocated: deque = deque(maxlen=self._max_num_index)
        self._in_use_by: dict[str, deque] = dict()

    def _alloc_idxs(self, num_idxs: int) -> deque | IndexAllocationError:
        available = len(self._available)

        if available <= num_idxs:
            return deque(self._available.pop() for _ in range(0, num_idxs))

        return IndexAllocationError(requested_idxs=num_idxs, max_idxs=available)

    def _alloc_var(self, var_name: str, idxs_deque: deque) -> None:
        self._in_use_by[var_name] = idxs_deque

    def _has_var(self, var_name: str) -> bool:
        return var_name in self._in_use_by

    def _free_var(self, var_name: str) -> deque:
        """
        Free variable's indexes and allocated deque with those indexes.
        """

        idxs = self._in_use_by.pop(var_name)

        for k in idxs:
            self._allocated.remove(k)

        return idxs

    def request(self, var_name: str, num_idxs: int) -> deque | ErrorHandler:
        """
        Request a number of indexes `num_idxs` for a variable `var_name`.
        """

        match x := self._alloc_idxs(num_idxs):

            case deque():
                if self._has_var(var_name):
                    return IndexVarHasIndexesError(var_name=var_name)

                self._alloc_var(var_name, x)

            case IndexAllocationError():
                return x

        return IndexUnknownError()

    def free(self, var_name: str) -> None:
        """
        Free indexes from a given variable `var_name`.
        """

        idxs = self._free_var(var_name)
        self._available.append(idxs)
