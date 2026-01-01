from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Iterable, Iterator

from hhat_lang.core.data.core import (
    CompositeSymbol,
    ObjArray,
    SimpleObj,
    Symbol,
    Tmp,
)


class FnHeaderDef:
    """
    Base class for functions header definition on memory's SymbolTable.
    Provide functions a signature.

    Given a function::

        fn sum (a:u64 b:u64) u64 { ::add(a b) }

    The function key object is as follows::

        FnHeaderDef(
            name=Symbol("sum"),
            type=Symbol("u64"),
            args_names=(Symbol("a"), Symbol("b"),),
            args_types=(Symbol("u64"), Symbol("u64"),)
        )

    When trying to retrieve the function data, use ``BaseFnHeader``
    parent instance instead:

    """

    _name: Symbol | CompositeSymbol
    _type: Symbol | CompositeSymbol
    _args_types: tuple | tuple[Symbol | CompositeSymbol, ...]
    _args_names: tuple | tuple[Symbol, ...]
    _hash_value: int

    # TODO: implement code for comparison of out of order args_names

    def __init__(
        self,
        fn_name: Symbol | CompositeSymbol,
        fn_type: Symbol | CompositeSymbol,
        args_names: tuple | tuple[Symbol, ...],
        args_types: tuple | tuple[Symbol | CompositeSymbol, ...],
    ):
        # check correct types for each argument before proceeding
        assert (
            isinstance(fn_name, Symbol | CompositeSymbol)
            and isinstance(fn_type, Symbol | CompositeSymbol)
            and all(isinstance(k, Symbol) for k in args_names)
            and all(isinstance(p, Symbol | CompositeSymbol) for p in args_types)
        ), (
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
    def name(self) -> Symbol | CompositeSymbol:
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

    def complement_name(self, text: str) -> None:
        """
        To finish off the function name for temporary 'variables', aka ``Tmp`` instances.
        """

        if isinstance(self._name, Tmp):
            self._name.append_to_name(text)

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FnHeaderDef | FnHeader):
            return hash(self) == hash(other)

        return False

    def has_args(self, args: tuple[Symbol, ...]) -> bool:
        return set(self._args_names) == set(args)

    def __iter__(self) -> Iterator[tuple[Symbol, Symbol | CompositeSymbol]]:
        return iter(zip(self.args_names, self.args_types))

    def __repr__(self) -> str:
        return (
            f"{self.name}:{self.type}("
            f"{' '.join(f'{k}:{v}' for k, v in zip(self.args_names, self.args_types))})"
        )


class FnHeader:
    """
    Base function header class to check and retrieve a given function from the SymbolTable.
    """

    _name: Symbol | CompositeSymbol
    _args_types: tuple | tuple[Symbol | CompositeSymbol, ...]
    _hash_value: int
    __slots__ = ("_name", "_args_types", "_hash_value")

    def __init__(
        self,
        fn_name: Symbol | CompositeSymbol,
        args_types: tuple | tuple[Symbol | CompositeSymbol, ...],
    ):
        # checks types correctness
        assert isinstance(fn_name, Symbol | CompositeSymbol) and all(
            isinstance(p, Symbol | CompositeSymbol) for p in args_types
        ), (
            f"Wrong types provided for function retrieval on SymbolTable:\n"
            f"  name: {fn_name}\n  args types: {args_types}\n",
        )

        self._name = fn_name
        self._args_types = args_types
        self._hash_value = hash((hash(self._name), hash(self._args_types)))

    @property
    def name(self) -> Symbol | CompositeSymbol:
        return self._name

    def transform(
        self, fn_type: Symbol | CompositeSymbol, args_names: tuple[Symbol, ...]
    ) -> FnHeaderDef:
        if all(
            isinstance(p, Symbol | CompositeSymbol) for p in args_names
        ) and isinstance(fn_type, Symbol | CompositeSymbol):
            return FnHeaderDef(
                fn_name=self.name,
                fn_type=fn_type,
                args_types=self._args_types,
                args_names=args_names,
            )
        raise ValueError(
            f"cannot transform FnKey with fn type {fn_type} and args {args_names}"
        )

    def check_args_types(self, *values: Symbol | CompositeSymbol) -> bool:
        """Check whether ``*values`` have the same values as in function args types"""

        return len(values) == len(self._args_types) and all(
            k == v for k, v in zip(values, self._args_types)
        )

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FnHeader):
            return hash(self) == hash(other)

        return False

    def __repr__(self) -> str:
        args = ", ".join(f"{t}" for t in self._args_types)
        return f"fn(name={self.name}, args=({args}))"


class BaseOptnCheck:
    """
    Base function with arguments as options (optn) class to check
    a given optn from the SymbolTable.
    """

    # TODO: implement it


class BaseBdnCheck:
    """
    Base function with arguments and body (bdn) class to check
    a given bdn from the SymbolTable.
    """


class BaseOptBdnCheck:
    """
    Base function with arguments and options in the body (optbdn) class to check
    a given optbdn from the SymbolTable
    """


class BaseIRBlock(ABC):
    """
    Base for IR block classes.
    """

    _name: BaseIRBlockFlag
    args: tuple[SimpleObj | ObjArray | BaseIRBlock | BaseIRInstr, ...]

    @property
    def name(self) -> BaseIRBlockFlag:
        return self._name

    @abstractmethod
    def append(self, data: Any, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("base IRBlock append method must be implemented")

    def __hash__(self) -> int:
        return hash((hash(self._name), hash(self.args)))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BaseIRBlock):
            return hash(self) == hash(other)

        return False

    def __iter__(self) -> Iterator:
        return iter(self.args)

    def __len__(self) -> int:
        return len(self.args)

    def __getitem__(self, item: Any) -> Any:
        return self.args[item]

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError()


class BaseIRBlockFlag(Enum):
    """
    Base for IR block flag classes. Should be used to define types of IR blocks.
    """


class BaseIRFlag(Enum):
    """
    Base for IR flag classes. It should be used to create enums for instructions,
    such as ``CALL``, ``DECLARE``, ``ASSIGN``, ``RETURN``, etc.
    """


class BaseIRInstr(ABC):
    """
    Base IR instruction classes.
    """

    _name: BaseIRFlag
    args: tuple[BaseIRBlock | SimpleObj | ObjArray, ...] | tuple
    _hash_value: int

    def __init__(self, *args: Any, **kwargs: Any):
        self._hash_value = hash((hash(self.name), hash(self.args)))

    @property
    def name(self) -> Any:
        return self._name

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BaseIRInstr):
            return hash(self) == hash(other)

        return False

    def __iter__(self) -> Iterable:
        return iter(self.args)

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError()
