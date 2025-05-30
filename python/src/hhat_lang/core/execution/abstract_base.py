from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from hhat_lang.core.code.ir import BaseFnIR, TypeIR
from hhat_lang.core.memory.core import MemoryManager


class BaseEvaluator(ABC):
    _mem: MemoryManager
    _type_table: TypeIR
    _fn_table: BaseFnIR

    @property
    def mem(self) -> MemoryManager:
        return self._mem

    @property
    def type_table(self) -> TypeIR:
        return self._type_table

    @property
    def fn_table(self) -> BaseFnIR:
        return self._fn_table

    @abstractmethod
    def run(self, code: Any, **kwargs: Any) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any):
        raise NotImplementedError()
