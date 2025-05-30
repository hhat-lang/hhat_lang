"""
Simple IR implementation. Intended to be simple for AST conversion and
readiness for the evaluator.
"""

from __future__ import annotations

import uuid
from typing import Any, Iterable

from hhat_lang.core.code.ast import AST
from hhat_lang.core.code.ir import (
    ArgsIR,
    BaseFnIR,
    BaseIR,
    BlockIR,
    InstrIR,
    InstrIRFlag,
)
from hhat_lang.core.data.core import (
    CompositeLiteral,
    CompositeSymbol,
    CoreLiteral,
    Symbol,
)


class IRInstr(InstrIR):
    def __init__(self, name: Symbol | CompositeSymbol, args: IRArgs, flag: InstrIRFlag):
        if (
            isinstance(name, (Symbol, CompositeSymbol))
            and isinstance(args, IRArgs)
            and isinstance(flag, InstrIRFlag)
        ):
            self._name = name
            self._args = args
            self._flag = flag


class IRArgs(ArgsIR):
    def __init__(
        self, *args: Symbol | CompositeSymbol | CoreLiteral | CompositeLiteral
    ):
        if (
            all(
                isinstance(k, (Symbol, CompositeSymbol, CoreLiteral, CompositeLiteral))
                for k in args
            )
            or len(args) == 0
        ):
            self._args = args


class IRBlock(BlockIR):
    def __init__(self):
        self._instrs = tuple()
        self.name = str(uuid.uuid4())

    def add_instr(self, instr: IRInstr | IRBlock) -> None:
        if isinstance(instr, IRInstr | IRBlock):
            self._instrs += (instr,)


################
# IR BASE CODE #
################


def compile_to_ir(code: AST) -> IR:
    raise NotImplementedError()


class FnIR(BaseFnIR):
    def __init__(self):
        self._data = dict()

    def push(self, *ags: Any, **kwargs: Any) -> Any:
        pass

    def get(self, item: Any) -> Any:
        pass

    def __setitem__(self, key: Any, value: Any) -> None:
        pass

    def __getitem__(self, key: Symbol | CompositeSymbol) -> Any:
        pass

    def __contains__(self, item: Any) -> bool:
        raise NotImplementedError()


class IR(BaseIR):
    """
    The IR class that contains all the relevant code to be evaluated, including
    types, functions and `main` body. An evaluator class must use this one to
    execute classical instructions.
    """

    def __init__(self):
        super().__init__()

    def add_fn(
        self,
        *,
        fn_name: Symbol,
        fn_type: Symbol | CompositeSymbol,
        fn_args: Any,
        body: IRBlock,
    ) -> None: ...
