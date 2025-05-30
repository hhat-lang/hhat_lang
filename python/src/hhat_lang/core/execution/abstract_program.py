from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from hhat_lang.core.code.ir import BlockIR
from hhat_lang.core.data.core import WorkingData
from hhat_lang.core.error_handlers.errors import ErrorHandler
from hhat_lang.core.execution.abstract_base import BaseEvaluator
from hhat_lang.core.lowlevel.abstract_qlang import BaseLowLevelQLang
from hhat_lang.core.memory.core import BaseStack, IndexManager


class BaseProgram(ABC):
    _qdata: WorkingData
    _idx: IndexManager
    _block: BlockIR
    _executor: BaseEvaluator
    _qlang: BaseLowLevelQLang
    _qstack: BaseStack

    @abstractmethod
    def run(self) -> Any | ErrorHandler: ...
