from __future__ import annotations

from functools import lru_cache
from typing import Sized, cast

from hhat_lang.core.code.base import BaseFnCheck, BaseIRBlock
from hhat_lang.core.data.core import (
    CompositeSymbol,
    CompositeWorkingData,
    Symbol,
    WorkingData,
)


class FnDef:
    """
    Function definition class
    """

    _name: Symbol | CompositeSymbol
    _type: Symbol | CompositeSymbol
    _body: BaseIRBlock
    _fn_check: BaseFnCheck
    _args: BaseIRBlock
    """
    function definition arguments must be a special kind of IRBlock
    that has ``arg`` and ``value`` attributes and is iterable through
    them.
    """

    def __init__(
        self,
        fn_name: Symbol | CompositeSymbol,
        fn_args: BaseIRBlock,
        fn_body: BaseIRBlock,
        fn_type: Symbol | CompositeSymbol | None = None,
    ):
        if (
            isinstance(fn_name, Symbol | CompositeSymbol)
            and isinstance(fn_args, BaseIRBlock)
            and isinstance(fn_body, BaseIRBlock)
            and isinstance(fn_type, Symbol | CompositeSymbol)
            or fn_type is None
        ):
            self._name = fn_name
            self._args = self._unwrap_args(cast(Sized, fn_args))
            self._body = fn_body
            self._type = fn_type or Symbol("null")
            self._fn_check = BaseFnCheck(fn_name=self.name, args_types=self.arg_values)

        else:
            raise ValueError(
                f"some fn definition type is wrong: "
                f"{type(fn_name)} {type(fn_args)} {type(fn_body)} {type(fn_body)}"
            )

    @property
    def name(self) -> Symbol | CompositeSymbol:
        return self._name

    @property
    def type(self) -> Symbol | CompositeSymbol:
        return self._type

    @property
    def args(self) -> BaseIRBlock:
        return self._args

    @property
    def body(self) -> BaseIRBlock:
        return self._body

    @property
    @lru_cache
    def arg_names(self) -> tuple[WorkingData | CompositeWorkingData, ...]:
        if hasattr(self._args, "args"):
            return self._args.args  # type: ignore [return-value]

        raise ValueError(f"wrong arg names from function definition {self._name}")

    @property
    @lru_cache
    def arg_values(self) -> tuple[Symbol | CompositeSymbol | BaseIRBlock, ...]:
        if hasattr(self._args, "values"):
            return self._args.values

        raise ValueError(f"wrong arg values from function definition {self._name}")

    @property
    def fn_check(self) -> BaseFnCheck:
        return self._fn_check

    def _unwrap_args(self, args: Sized) -> BaseIRBlock:
        if len(args) == 1:
            if hasattr(args, "args"):
                if hasattr(args.args[0], "values"):
                    return args.args[0]

        raise ValueError("function definition must contain arg-value pairs")

    def __repr__(self) -> str:
        args = " ".join(str(k) for k in self.args)
        fn_header = f"FN-DEF NAME[{self.name}] ARGS[{args}] TYPE[{self.type or 'null'}]"
        body = "\n            ".join(str(k) for k in self.body)
        return f"{fn_header}" + "\n            " + f"{body}" + "\n"


class OptnDef:
    """
    Function with arguments as options (optn) definition class
    """
    # TODO: implement it


class BdnDef:
    """
    Function with arguments and body (bdn) definition class
    """
    # TODO: implement it


class OptBdnDef:
    """
    Function with arguments and options in the body (optbdn) definition class
    """
    # TODO: implement it
