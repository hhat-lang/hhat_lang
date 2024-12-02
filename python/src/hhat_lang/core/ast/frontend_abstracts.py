from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generator


class BaseAST(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def value(self) -> tuple[Any, ...]: ...

    def __iter__(self) -> Generator:
        yield from self.value
