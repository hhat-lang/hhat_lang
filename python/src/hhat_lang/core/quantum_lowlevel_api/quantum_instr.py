from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class QuantumInstr(ABC):
    @classmethod
    @abstractmethod
    def compile(cls, *args: Any, **kwargs: Any) -> Any:
        ...

    @classmethod
    @abstractmethod
    def execute(cls, *args: Any, **kwargs: Any) -> Any:
        ...


class QRedim(QuantumInstr, ABC):
    pass


class QSync(QuantumInstr, ABC):
    pass


class QIf(QuantumInstr, ABC):
    pass


class QNot(QuantumInstr, ABC):
    pass
