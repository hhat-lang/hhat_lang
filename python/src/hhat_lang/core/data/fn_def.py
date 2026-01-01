from __future__ import annotations

from typing import Any, Callable

from hhat_lang.core.code.base import FnHeader, BaseIRBlock
from hhat_lang.core.code.ir_custom import ArgsBlock, ArgsValuesBlock
from hhat_lang.core.data.core import (
    CompositeSymbol,
    Literal,
    ObjArray,
    SimpleObj,
    Symbol,
)
from hhat_lang.core.data.var_def import DataDef
from hhat_lang.core.memory.core import MemoryManager


class FnDef:
    """
    Function definition class
    """

    _name: Symbol | CompositeSymbol
    _type: Symbol | CompositeSymbol
    _body: BaseIRBlock
    _fn_check: FnHeader
    _args: ArgsBlock
    """
    function definition arguments must be a special kind of IRBlock
    that has ``arg`` and ``value`` attributes and is iterable through
    them.
    """

    def __init__(
        self,
        fn_name: Symbol | CompositeSymbol,
        fn_args: ArgsBlock,
        fn_body: BaseIRBlock,
        fn_type: Symbol | CompositeSymbol | None = None,
    ):
        if (
            isinstance(fn_name, Symbol | CompositeSymbol)
            and isinstance(fn_args, ArgsBlock)
            and isinstance(fn_body, BaseIRBlock)
            and isinstance(fn_type, Symbol | CompositeSymbol)
            or fn_type is None
        ):
            self._name = fn_name
            self._args = fn_args
            self._body = fn_body
            self._type = fn_type or Symbol("null")
            self._fn_check = FnHeader(fn_name=self.name, args_types=self.arg_values)

        else:
            raise ValueError(
                f"some fn definition type is wrong: "
                f"{type(fn_name)} {type(fn_args)} {type(fn_type)} {type(fn_body)}"
            )

    @property
    def name(self) -> Symbol | CompositeSymbol:
        return self._name

    @property
    def type(self) -> Symbol | CompositeSymbol:
        return self._type

    @property
    def args(self) -> ArgsBlock:
        return self._args

    @property
    def body(self) -> BaseIRBlock:
        return self._body

    @property
    def arg_names(self) -> tuple[SimpleObj | ObjArray, ...]:
        if hasattr(self._args, "args"):
            return self._args.args  # type: ignore [return-value]

        raise ValueError(f"wrong arg names from function definition {self._name}")

    @property
    def arg_values(self) -> tuple[Symbol | CompositeSymbol | BaseIRBlock, ...]:
        if hasattr(self._args, "values"):
            return self._args.values[0]

        return tuple(v.values[0] for v in self._args.args)

    @property
    def fn_check(self) -> FnHeader:
        return self._fn_check

    def __repr__(self) -> str:
        args = " ".join(str(k) for k in self.args)
        fn_header = f"FN-DEF NAME[{self.name}] ARGS[{args}] {f'TYPE[{self.type}]' if self.type else ''}"
        body = "\n            ".join(str(k) for k in self.body)
        return f"{fn_header}" + "\n            " + f"{body}" + "\n"


class BuiltinFnDef:
    """
    Built-in function class definition
    """

    _name: Symbol | CompositeSymbol
    _type: Symbol | CompositeSymbol
    _body: Callable
    """``BuiltinFnDef`` callable"""
    _fn_header: FnHeader
    _args: ArgsValuesBlock
    """
    function definition arguments must be a special kind of IRBlock
    that has ``arg`` and ``value`` attributes and is iterable through
    them.
    """

    def __init__(
        self,
        fn_name: Symbol | CompositeSymbol,
        fn_args: ArgsValuesBlock,
        fn_body: Callable | None,
        fn_type: Symbol | CompositeSymbol | None = None,
    ):
        if (
            isinstance(fn_name, Symbol | CompositeSymbol)
            and isinstance(fn_args, ArgsValuesBlock)
            and (isinstance(fn_body, Callable) or fn_body is None)
            and isinstance(fn_type, Symbol | CompositeSymbol)
            or fn_type is None
        ):
            self._name = fn_name
            self._args = fn_args
            self._body = fn_body
            self._type = fn_type or Symbol("null")
            self._fn_header = FnHeader(fn_name=self.name, args_types=self.arg_values)

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
    def args(self) -> ArgsValuesBlock:
        return self._args

    @property
    def body(self) -> Callable:
        """``BuiltinFnDef`` callable"""
        return self._body

    @property
    def arg_names(self) -> tuple[SimpleObj | ObjArray, ...]:
        if hasattr(self._args, "args"):
            return self._args.args  # type: ignore [return-value]

        raise ValueError(f"wrong arg names from function definition {self._name}")

    @property
    def arg_values(self) -> tuple[Symbol | CompositeSymbol | BaseIRBlock, ...]:
        if hasattr(self._args, "values"):
            return self._args.values

        raise ValueError(f"wrong arg values from function definition {self._name}")

    @property
    def fn_header(self) -> FnHeader:
        return self._fn_header

    def __call__(self, *args: Any, mem: MemoryManager) -> Literal | DataDef:
        return self._body(*args, mem=mem)

    def __repr__(self) -> str:
        args = " ".join(f"{k}:{v}" for k, v in self.args)
        fn_header = (
            f"FN-DEF<built-in> NAME[{self.name}] ARGS[{args}]"
            f" {f'TYPE[{self.type}]' if self.type else ''}"
        )
        body = "\n            <internal implementation>"
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


class ModifierDef:
    """
    Modifier function
    """

    # TODO: implement it
