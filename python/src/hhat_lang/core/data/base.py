from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseData(ABC):
    @abstractmethod
    def set(self, data: Any) -> None:
        pass

    @abstractmethod
    def get(self) -> Any:
        pass
