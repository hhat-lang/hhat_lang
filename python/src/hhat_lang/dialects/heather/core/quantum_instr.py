from __future__ import annotations

from typing import Any

from hhat_lang.core.quantum_lowlevel_api.quantum_instr import (
    QRedim as BaseQRedim,
    QSync as BaseQSync,
    QIf as BaseQIf,
    QNot as BaseQNot,
)


class QRedim(BaseQRedim):
    @classmethod
    def compile(cls, *args: Any, **kwargs: Any) -> Any:
        pass

    @classmethod
    def execute(cls, *args: Any, **kwargs: Any) -> Any:
        pass


class QSync(BaseQSync):
    @classmethod
    def compile(cls, *args: Any, **kwargs: Any) -> Any:
        pass

    @classmethod
    def execute(cls, *args: Any, **kwargs: Any) -> Any:
        pass


class QIf(BaseQIf):
    @classmethod
    def compile(cls, *args: Any, **kwargs: Any) -> Any:
        pass

    @classmethod
    def execute(cls, *args: Any, **kwargs: Any) -> Any:
        pass


class QNot(BaseQNot):
    @classmethod
    def compile(cls, *args: Any, **kwargs: Any) -> Any:
        pass

    @classmethod
    def execute(cls, *args: Any, **kwargs: Any) -> Any:
        pass
