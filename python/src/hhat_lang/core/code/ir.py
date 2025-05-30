from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Callable, Iterable

from hhat_lang.core.data.core import CompositeSymbol, Symbol
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure


class BlockIRFlag(Enum):
    INSTR_BLOCK = auto()
    CONTROLFLOW_BLOCK = auto()
    CLOSURE_BLOCK = auto()
    CALL_BLOCK = auto()


class InstrIRFlag(Enum):
    ASSIGN = auto()
    DECLARE = auto()
    DECLARE_ASSIGN = auto()
    CALL = auto()
    CONTROLFLOW = auto()
    TEST_COND = auto()
    LOOP = auto()
    LOOP_COND = auto()
    RETURN = auto()


class InstrIR(ABC):
    """
    To hold individual instructions and their arguments (if any).
    """

    _name: Symbol | CompositeSymbol
    _args: ArgsIR
    _flag: InstrIRFlag

    @property
    def name(self) -> Symbol | CompositeSymbol:
        return self._name

    @property
    def args(self) -> ArgsIR:
        return self._args

    @property
    def flag(self) -> InstrIRFlag:
        return self._flag


class BlockIR(ABC):
    """
    To hold tuple of instructions (`InstrIR`) and blocks (`BlockIR`).
    """

    name: str
    _instrs: tuple[InstrIR | BlockIR, ...]

    def __getitem__(self, item: int) -> InstrIR | BlockIR:
        return self._instrs[item]

    def __iter__(self) -> Iterable:
        yield from self._instrs


class ArgsIR(ABC):
    """
    To hold instructions arguments.
    """

    _args: tuple[Any, ...]

    def __contains__(self, arg: Any) -> bool:
        return arg in self._args

    def __iter__(self) -> Iterable:
        yield from self._args


class BodyIR:
    """
    Body IR for functions body and `main`.
    """

    _data: list[InstrIR | BlockIR] | list

    def __init__(self):
        self._data = []

    def push(self, new_item: Any, to_instr_fn: Callable | None = None) -> None:
        if not isinstance(new_item, InstrIR | BlockIR):

            if to_instr_fn is not None:
                new_item = to_instr_fn(new_item)

            else:
                raise ValueError(
                    "'to_instr_fn' argument must not be None if the item is not 'InstrIR'."
                )

        self._data.append(new_item)

    def __iter__(self) -> Iterable:
        yield from self._data


####################
# type annotations #
####################

TypeTable = dict[Symbol | CompositeSymbol, BaseTypeDataStructure]
"""
Type annotation for `TypeTable`. It holds all the types used throughout the program.

A dictionary where the keys are the type names (`Symbol`, `CompositeSymbol`) and the
 values are their data structure (`BaseTypeDataStructure`).
"""

FnTable = dict[
    tuple[  # key: define the function header
        Symbol | CompositeSymbol,  # first element: function name
        Symbol | CompositeSymbol,  # second element: function type
        tuple
        | tuple[
            Symbol | CompositeSymbol | tuple[Symbol, Symbol | CompositeSymbol], ...
        ],  # third element: args; empty args, only types args, name and type pairs
    ],
    BodyIR,
]  # value: the function body
"""
Type annotation for `FnTable`, a function table that holds all the program functions.

It consists in a dictionary where the key is:

- first element: function name (`Symbol`, `CompositeSymbol`)
- second element: function type (`Symbol`, `CompositeSymbol`)
- third element: args, which can be empty, only types or name-type pairs
  (tuple of `Symbol`, `CompositeSymbol` or tuple pairs with `Symbol` and
  `Symbol` or `CompositeSymbol`)

and the dictionary value is body of the function.
"""


#############
# IR TABLES #
#############


class TypeIR:
    """To format, store and retrieve all types used in the program."""

    _data: TypeTable

    def __init__(self):
        self._data = dict()

    @property
    def table(self) -> TypeTable:
        return self._data

    def push(self, new_type: BaseTypeDataStructure):
        self[new_type.name] = new_type

    def get(self, name: Symbol | CompositeSymbol) -> BaseTypeDataStructure:
        return self[name]

    def __setitem__(
        self, key: Symbol | CompositeSymbol, value: BaseTypeDataStructure
    ) -> None:
        if isinstance(key, (Symbol, CompositeSymbol)) and isinstance(
            value, BaseTypeDataStructure
        ):
            if key not in self._data:
                self._data[key] = value

            else:
                print("[[LOG:IR]] ignore adding the same type in the type table.")

        else:
            raise ValueError(
                "type table needs symbol/composite symbol as key and data structure as value."
            )

    def __getitem__(self, key: Symbol | CompositeSymbol) -> BaseTypeDataStructure:
        return self._data[key]

    def __contains__(self, key: Symbol | CompositeSymbol) -> bool:
        return key in self._data


class BaseFnIR(ABC):
    """
    Function IR class: handles the function table data. It is an abstract class, because
    it's up to the dialect to implement how it wants to handle function call, e.g.
    whether arguments can be passed in order, a name and value pair in any order, etc.
    """

    _data: FnTable

    @property
    def table(self) -> FnTable:
        return self._data

    @abstractmethod
    def push(self, *ags: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    def get(self, item: Any) -> Any:
        pass

    @abstractmethod
    def __setitem__(self, key: Any, value: Any) -> None:
        pass

    @abstractmethod
    def __getitem__(self, key: Any) -> Any:
        pass

    @abstractmethod
    def __contains__(self, item: Any) -> bool:
        pass


class BaseIR(ABC):
    """
    Where the IR code lies. It contains `TypeIR` (type table), `FnIR` (function table),
    and the `main` code.
    """

    _data: BodyIR
    _type_table: TypeIR
    _fn_table: BaseFnIR

    def __init__(self):
        self._data = BodyIR()
        self._type_table = TypeIR()
        self._fn_table = BaseFnIR()

    @property
    def types(self) -> TypeIR:
        return self._type_table

    @property
    def fns(self) -> BaseFnIR:
        return self._fn_table

    @property
    def main(self) -> BodyIR:
        return self._data

    def add_type(
        self, name: Symbol | CompositeSymbol, data: BaseTypeDataStructure
    ) -> None:
        self._type_table[name] = data

    @abstractmethod
    def add_fn(
        self,
        *,
        fn_name: Symbol,
        fn_type: Symbol | CompositeSymbol,
        fn_args: Any,
        body: Any,
    ) -> None: ...

    def add_body(self, body: Any) -> None:
        for k in body:
            self._data.push(k)
