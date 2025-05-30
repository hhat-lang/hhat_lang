from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from hhat_lang.core.data.core import WorkingData
from hhat_lang.core.error_handlers.errors import ErrorHandler
from hhat_lang.core.execution.abstract_base import BaseEvaluator
from hhat_lang.core.memory.core import BaseStack, IndexManager
from hhat_lang.core.utils import Result
from hhat_lang.dialects.heather.code.simple_ir_builder.ir import IRBlock


class BaseLowLevelQLang(ABC):
    """
    Hold H-hat quantum data to transform into low-level
    quantum-specific language.
    """

    _qdata: WorkingData
    _num_idxs: int
    _code: IRBlock
    _idx: IndexManager
    _executor: BaseEvaluator
    _qstack: BaseStack

    def __init__(
        self,
        qvar: WorkingData,
        code: IRBlock,
        idx: IndexManager,
        executor: BaseEvaluator,
        qstack: BaseStack,
        *_args: Any,
        **_kwargs: Any,
    ):
        self._qdata = qvar
        self._code = code
        self._idx = idx
        self._executor = executor
        self._qstack = qstack
        self._num_idxs = len(self._idx.in_use_by.get(self._qdata, []))

    @abstractmethod
    def init_qlang(self) -> tuple[str, ...]: ...

    @abstractmethod
    def gen_instrs(self, *args: Any, **kwargs: Any) -> Result | ErrorHandler: ...

    @abstractmethod
    def gen_program(self, *args: Any, **kwargs: Any) -> str: ...

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
