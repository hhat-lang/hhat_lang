from __future__ import annotations

from typing import Any
from abc import ABC, abstractmethod


class AST(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def value(self) -> Any: ...
