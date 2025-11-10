from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseCompiler(ABC):
    """
    Abstract class for the compiler that holds all compilation information, such
    as: the list of other compilers used (classical, for other dialects, and
    quantum), the list of executors (that evaluate the IR code for classical
    and quantum) the compiler can use, quantum specs for available devices,
    backends, quantum languages
    """

    @abstractmethod
    def parse(self) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def evaluate(self) -> Any:
        raise NotImplementedError()
