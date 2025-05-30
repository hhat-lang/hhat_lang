from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from hhat_lang.core import DataParadigm
from hhat_lang.core.code.utils import InstrStatus


class BaseInstr(ABC):
    """Base instruction class"""

    name: str
    _instr_status: InstrStatus

    @property
    def status(self) -> InstrStatus:
        return self._instr_status

    @property
    @abstractmethod
    def is_quantum(self) -> bool: ...

    @property
    @abstractmethod
    def paradigm(self) -> DataParadigm: ...

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


class QInstr(BaseInstr, ABC):
    """Quantum instruction base class"""

    def __init__(self):
        self._instr_status = InstrStatus.NOT_STARTED

    @property
    def is_quantum(self) -> bool:
        return True

    @property
    def paradigm(self) -> DataParadigm:
        return DataParadigm.QUANTUM


class CInstr(BaseInstr, ABC):
    """Classical instruction base class"""

    def __init__(self):
        self._instr_status = InstrStatus.NOT_STARTED

    @property
    def is_quantum(self) -> bool:
        return False

    @property
    def paradigm(self) -> DataParadigm:
        return DataParadigm.CLASSICAL
