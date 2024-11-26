from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AST(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def value(self) -> Any: ...
