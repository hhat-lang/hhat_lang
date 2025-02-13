from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable

from hhat_lang.core.index.manager import IndexSupport
from hhat_lang.core.interpreter.base import BaseEvaluate
from hhat_lang.core.memory.manager import MemoryManager


class BaseCompileQuantumInstr(ABC):
    @classmethod
    @abstractmethod
    def compile(cls, *args: Any, **kwargs: Any) -> Any:
        ...

    @classmethod
    @abstractmethod
    def execute(cls, *args: Any, **kwargs: Any) -> Any:
        ...


class QuantumInstrList:
    _instrs: tuple[str, ...]

    def __init__(self, *instrs: str):
        self._instrs = instrs

    def peek(self) -> str:
        return f"#QuantumInstrList({' '.join(str(k) for k in self._instrs)})"

    def __iter__(self) -> Iterable:
        yield from self._instrs


class BaseQuantumInstr(ABC):
    _name: str
    _idxs: IndexSupport
    _instr: QuantumInstrList

    @property
    def name(self) -> str:
        return self._name

    @property
    def size(self) -> int:
        return len(self._idxs)

    @property
    def idxs(self) -> IndexSupport:
        return self._idxs

    @property
    def instr(self) -> QuantumInstrList:
        return self._instr

    @abstractmethod
    def _gen_instr(self, mem: MemoryManager, evaluate: BaseEvaluate) -> list[str]:
        pass

    @abstractmethod
    def apply(
        self,
        *,
        idxs: IndexSupport,
        mem: MemoryManager,
        evaluate: BaseEvaluate,
    ) -> BaseQuantumInstr:
        pass

    @abstractmethod
    def get_instr(self, **kwargs: Any) -> QuantumInstrList:
        pass


class BaseQRedim(BaseQuantumInstr, ABC):
    pass


class BaseQSync(BaseQuantumInstr, ABC):
    pass


class BaseQIf(BaseQuantumInstr, ABC):
    pass


class BaseQNot(BaseQuantumInstr, ABC):
    pass
