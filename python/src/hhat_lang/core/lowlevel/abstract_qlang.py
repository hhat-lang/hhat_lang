from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from hhat_lang.core.data.core import Symbol
from hhat_lang.core.execution.abstract_base import BaseEvaluator
from hhat_lang.core.memory.core import IndexManager
from hhat_lang.dialects.heather.code.simple_ir_builder.ir import IRBlock


class BaseLowLevelQLang(ABC):
    _qvar: Symbol
    _num_idxs: int
    _code: IRBlock
    _idx: IndexManager
    _executor: BaseEvaluator

    def __init__(
        self,
        qvar: Symbol,
        code: IRBlock,
        idx: IndexManager,
        executor: BaseEvaluator,
        *_args: Any,
        **_kwargs: Any
    ):
        self._qvar = qvar
        self._code = code
        self._idx = idx
        self._executor = executor
        self._num_idxs = len(self._idx.in_use_by.get(self._qvar, []))

    @abstractmethod
    def init_qlang(self) -> tuple[str, ...]:
        ...

    @abstractmethod
    def end_qlang(self) -> tuple[str, ...]:
        ...

    @abstractmethod
    def gen_instrs(self, *args: Any, **kwargs: Any) -> tuple[str, ...]:
        ...

    @abstractmethod
    def gen_program(self, *args: Any, **kwargs: Any) -> str:
        ...

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...
