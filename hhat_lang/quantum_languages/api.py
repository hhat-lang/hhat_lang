from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class QASMAPI(ABC):
    @abstractmethod
    def parse_code(self, code: Any) -> Any:
        ...
