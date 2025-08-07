from __future__ import annotations

from functools import lru_cache
from typing import Any, Iterable

from hhat_lang.core.code.abstract_new_ir import BaseIRBlock
from hhat_lang.core.data.core import Symbol, CompositeSymbol


class BaseFnKey:
    """
    Base class for functions definition on memory's SymbolTable.
    Provide functions a signature.

    Given a function::

        fn sum (a:u64 b:u64) u64 { ::add(a b) }

    The function key object is as follows::

        BaseFnKey(
            name=Symbol("sum"),
            type=Symbol("u64"),
            args_names=(Symbol("a"), Symbol("b"),),
            args_types=(Symbol("u64"), Symbol("u64"),)
        )

    When trying to retrieve the function data, use ``BaseFnCheck``
    parent instance instead:

    """

    _name: Symbol
    _type: Symbol | CompositeSymbol
    _args_types: tuple | tuple[Symbol | CompositeSymbol, ...]
    _args_names: tuple | tuple[Symbol, ...]
    _hash_value: int

    # TODO: implement code for comparison of out of order args_names

    def __init__(
        self,
        fn_name: Symbol,
        fn_type: Symbol | CompositeSymbol,
        args_names: tuple | tuple[Symbol, ...],
        args_types: tuple | tuple[Symbol | CompositeSymbol, ...],
    ):

        # check correct types for each argument before proceeding
        assert (
            isinstance(fn_name, Symbol)
            and isinstance(fn_type, Symbol | CompositeSymbol)
            and all(isinstance(k, Symbol) for k in args_names)
            and all(isinstance(p, Symbol | CompositeSymbol) for p in args_types),
            f"Wrong types provided for function definition on SymbolTable:\n"
            f"  name: {fn_name}\n  type: {fn_type}\n  args types: {args_types}\n"
            f"  args names: {args_names}\n",
        )

        self._name = fn_name
        self._type = fn_type
        self._args_names = args_names
        self._args_types = args_types
        self._hash_value = hash((hash(self._name), hash(self._args_types)))

    @property
    def name(self) -> Symbol:
        return self._name

    @property
    def type(self) -> Symbol | CompositeSymbol:
        return self._type

    @property
    def args_types(self) -> tuple | tuple[Symbol | CompositeSymbol, ...]:
        return self._args_types

    @property
    def args_names(self) -> tuple | tuple[Symbol, ...]:
        return self._args_names

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BaseFnKey | BaseFnCheck):
            return hash(self) == hash(other)

        return False

    def has_args(self, args: tuple[Symbol, ...]) -> bool:
        return set(self._args_names) == set(args)

    def __iter__(self) -> Iterable:
        return iter(zip(self.args_names, self.args_types))

    def __repr__(self) -> str:
        return (
            f"{self.name}:{self.type}("
            f"{' '.join(f'{k}:{v}' for k, v in zip(self.args_names, self.args_types))})"
        )


class BaseFnCheck:
    """
    Base function class to check and retrieve a given function from the SymbolTable.
    """

    _name: Symbol
    _args_types: tuple | tuple[Symbol | CompositeSymbol, ...]
    _hash_value: int
    __slots__ = ("_name", "_args_types", "_hash_value")

    def __init__(
        self,
        fn_name: Symbol,
        args_types: tuple | tuple[Symbol | CompositeSymbol, ...],
    ):

        # checks types correctness
        assert (
            isinstance(fn_name, Symbol)
            and all(isinstance(p, Symbol | CompositeSymbol) for p in args_types),
            f"Wrong types provided for function retrieval on SymbolTable:\n"
            f"  name: {fn_name}\n  args types: {args_types}\n",
        )

        self._name = fn_name
        self._args_types = args_types
        self._hash_value = hash((hash(self._name), hash(self._args_types)))

    @property
    def name(self) -> Symbol:
        return self._name

    def transform(
        self,
        fn_type: Symbol | CompositeSymbol,
        args_names: tuple[Symbol, ...]
    ) -> BaseFnKey:
        if (
            all(isinstance(p, Symbol) for p in args_names)
            and isinstance(fn_type, Symbol | CompositeSymbol)
        ):
            return BaseFnKey(
                fn_name=self.name,
                fn_type=fn_type,
                args_types=self._args_types,
                args_names=args_names,
            )
        raise ValueError(f"cannot transform FnKey with fn type {fn_type} and args {args_names}")

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BaseFnKey | BaseFnCheck):
            return hash(self) == hash(other)

        return False

    def __repr__(self) -> str:
        args = ", ".join(f"{t}" for t in self._args_types)
        return f"fn(name={self.name}, args=({args}))"


class FnDef:
    """
    Function definition class
    """

    _name: Symbol | BaseIRBlock
    _type: Symbol | CompositeSymbol | None
    _body: BaseIRBlock
    _args: BaseIRBlock
    """
    function definition arguments must be a special kind of IRBlock
    that has ``arg`` and ``value`` attributes and is iterable through
    them.
    """

    def __init__(
        self,
        fn_name: Symbol | BaseIRBlock,
        fn_args: BaseIRBlock,
        fn_body: BaseIRBlock,
        fn_type: Symbol | CompositeSymbol | None = None,
    ):
        if (
            isinstance(fn_name, Symbol | BaseIRBlock)
            and isinstance(fn_args, BaseIRBlock)
            and isinstance(fn_body, BaseIRBlock)
            and isinstance(fn_type, Symbol | CompositeSymbol) or fn_type is None
        ):
            self._name = fn_name
            self._args = fn_args
            self._body = fn_body
            self._type = fn_type or Symbol("null")

        else:
            raise ValueError(
                f"some fn definition type is wrong: "
                f"{type(fn_name)} {type(fn_args)} {type(fn_body)} {type(fn_body)}"
            )
    @property
    def name(self) -> Symbol | BaseIRBlock:
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
    def arg_names(self) -> tuple[Symbol, ...]:
        return tuple(k.arg for k in self.args)

    @property
    @lru_cache
    def arg_values(self) -> tuple[Symbol | CompositeSymbol, ...]:
        return tuple(k.value for k in self.args)

    def get_fn_entry(self) -> BaseFnKey:
        return BaseFnKey(
            fn_name=self.name,
            fn_type=self.type,
            args_types=self.arg_values,
            args_names=self.arg_names,
        )

    def get_fn_check(self) -> BaseFnCheck:
        return BaseFnCheck(
            fn_name=self.name,
            args_types=self.arg_values
        )

    def __repr__(self) -> str:
        args = " ".join(str(k) for k in self.args)
        fn_header = f"FN-DEF#:NAME#[{self.name}] ARGS#[{args}] TYPE#[{self.type or 'null'}]"
        body = "\n            ".join(str(k) for k in self.body)
        return f"{fn_header}" + "\n            " + f"{body}" + "\n"
