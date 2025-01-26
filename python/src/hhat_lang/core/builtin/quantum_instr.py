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
    name: str = "@redim"


class QSync(QuantumInstr, ABC):
    name: str = "@sync"


class QIf(QuantumInstr, ABC):
    name: str = "@if"


class QNot(QuantumInstr, ABC):
    name: str = "@not"
