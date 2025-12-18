from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from collections import deque
from enum import auto
from typing import Any, Iterable

from hhat_lang.core.code.base import (
    BaseIRBlock,
    BaseIRBlockFlag,
    BaseIRFlag,
    BaseIRInstr,
)
from hhat_lang.core.data.core import (
    Literal,
    LiteralArray,
    ObjArray,
    SimpleObj,
)
from hhat_lang.core.error_handlers.errors import RetrieveAppendableDataError


# IR INSTR SECTION #
####################


class IRFlag(BaseIRFlag):
    """
    Used to identify the ``IRBaseInstr`` child class purpose. Ex: a ``CallInstr``
    class is defined with its name as ``IRFlag.FN_CALL``.
    """

    NULL = auto()
    BUILTIN_FN_CALL = auto()
    BUILTIN_OPTN_CALL = auto()
    BUILTIN_BDN_CALL = auto()
    BUILTIN_OPTBDN_CALL = auto()

    FN_CALL = auto()
    """function with arguments (fn), defined as ``caller(args*)``"""

    CAST = auto()
    """casting some data to a type, defined as ``data*type``"""

    ASSIGN = auto()
    """assigning a variable as ``var=expr``"""

    DECLARE = auto()
    """declaring a variable, defined as ``var:type``"""

    DECLARE_ASSIGN = auto()
    """declaring and assigning a variable in one step, defined as ``var:type=expr``"""

    ARGS = auto()
    """simple arguments (variables, literals, etc)"""

    ARG_VALUE = auto()
    """argument names with values, defined as ``arg=value`` or ``arg:value``"""

    OPTION_EXPR = auto()
    """option expression ``option:expr``"""
    # COND = auto()
    # MATCH = auto()

    BDN_CALL = auto()
    """function body-ion (bdn), defined as ``caller(args*){body*}``"""

    OPTBDN_CALL = auto()
    """
    function with arguments and options in the body (optbdn), defined as
    ``caller(args*){option_expr*}``
    """

    OPTN_CALL = auto()
    """function with arguments as options (optn), defined as ``caller(option_expr*)"""

    RETURN = auto()
    """returning something (variable, literal, expr) from a function, defined as ``::expr``"""


####################
# IR BLOCK SECTION #
####################


class IRBlockFlag(BaseIRBlockFlag):
    """Define all valid IR block flags for IR blocks"""

    BODY = auto()
    EXPRESSION = auto()
    ARGS = auto()
    ARGS_VALUES = auto()
    OPTION = auto()
    RETURN = auto()
    MODIFIER = auto()
    MODIFIER_ARGS = auto()


class IRBlock(BaseIRBlock, ABC):
    """
    IR blocks
    """

    _name: IRBlockFlag

    def append(self, data: Any, *args: Any, **kwargs: Any) -> None:
        match data:
            case IRBlock() | IRInstr() | Literal():
                self.args += (data,)

            case _:
                raise NotImplementedError(f"data of type {type(data)} not imeplemented")


class IRInstr(BaseIRInstr):
    """
    Base class for IR instructions. Custom IR instructions names must adhere to
    IRFlag enum attributes. For example::


        class DeclareInstr(IRInstr):
            def __init__(self, ...):
                ...
                super().__init__(..., name=IRFlag.DECLARE)
    """

    _name: IRFlag
    args: tuple[IRBlock | SimpleObj | ObjArray, ...] | tuple

    def __init__(
        self,
        *args: IRBlock | BaseIRInstr | SimpleObj | ObjArray,
        name: IRFlag,
    ):
        if all(
            isinstance(k, IRBlock | BaseIRInstr | SimpleObj | ObjArray) for k in args
        ) and isinstance(name, IRFlag):
            self._name = name
            self.args = args
            super().__init__()

        else:
            raise ValueError(
                f"IR instr {self.__class__.__name__} must received name as {type(name)},"
                f" args as {[type(k) for k in args]}. Check for correct types."
            )

    def __repr__(self) -> str:
        return f"{self.name}({', '.join(str(k) for k in self.args)})"


##############################
# APPENDABLE OBJECTS SECTION #
##############################


class AppendableData:
    """
    Appendable data, to be used on appendable data kind, such as quantum data.
    All quantum data (variables, expressions) are appendable. Ex::

        // appendable variable @q
        @q:@bool = @false

        // appendable expression '@redim(@0)'
        @redim(@0)

        // appendable expression '@redim(@3)' inside appendable variable @v
        @v:@u3 = @redim(@3)

    Any other combination, for instance applying a functions to a variable, will
    be incorporated as appendable as well. Under the hood, it considers everything
    as ir blocks or ir instructions.

    Note: this object is not hashable.
    """

    # use Queue in the future for threading/asynchronous queueing
    _value: deque[IRBlock | IRInstr | LiteralArray | Literal]

    def __init__(self, *values: Any):
        self._value = deque(*values)

    def insert(self, value: IRBlock | IRInstr | Literal | LiteralArray) -> None:
        self._value.append(value)

    def get(self, item: int | Any) -> IRBlock | IRInstr | Literal | LiteralArray:
        return self.__getitem__(item)

    def __getitem__(self, item: int | Any) -> IRBlock | IRInstr | Literal | LiteralArray:
        if isinstance(item, int):
            return self._value[item]

        sys.exit(RetrieveAppendableDataError(item)())

    def __iter__(self) -> Iterable:
        return iter(self._value)
