
from typing import Any
from abc import ABC, abstractmethod

from hhat_lang.core.code.ir import BlockIR
from hhat_lang.core.data.core import WorkingData
from hhat_lang.core.error_handlers.errors import ErrorHandler
from hhat_lang.core.execution.abstract_base import BaseEvaluator
from hhat_lang.core.memory.core import IndexManager
from hhat_lang.core.lowlevel.abstract_qlang import BaseLowLevelQLang


class BaseProgram(ABC):
    _qdata: WorkingData
    _idx: IndexManager
    _block: BlockIR
    _executor: BaseEvaluator
    _qlang: BaseLowLevelQLang

    @abstractmethod
    def run(self) -> Any | ErrorHandler:
        ...
