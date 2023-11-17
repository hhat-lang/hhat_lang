from __future__ import annotations
from typing import Any

from abc import ABC, abstractmethod

from hhat_lang.interpreter.post_ast import R


class QLangLinkerAPI(ABC):
    pass


class QuantumBackendAPI(ABC):
    @abstractmethod
    def load_qasm(self, ) -> Any:
        ...

    @abstractmethod
    def transpile(self, code: R, **kwargs: Any) -> Any:
        ...

    @abstractmethod
    def execute(self) -> Any:
        ...


