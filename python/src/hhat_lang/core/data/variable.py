from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable

from hhat_lang.core.data.core import CompositeSymbol, Symbol, WorkingData
from hhat_lang.core.data.utils import VariableKind, isquantum
from hhat_lang.core.error_handlers.errors import (
    ContainerVarError,
    ContainerVarIsImmutableError,
    ErrorHandler,
    VariableCreationError,
    VariableFreeingBorrowedError,
    VariableWrongMemberError,
)
from hhat_lang.core.utils import SymbolOrdered


class BaseDataContainer(ABC):
    """Data container for constant and variables definitions."""

    _name: Symbol
    _type: Symbol | CompositeSymbol
    _ds: SymbolOrdered
    """_ds: data from data structure, e.g. member types and names"""

    _data: SymbolOrdered
    """_data: where data will actually be stored"""

    _assigned: bool
    _is_constant: bool
    _is_mutable: bool
    _is_appendable: bool
    _is_quantum: bool

    _instr_counter: int
    """the counter for instructions so quantum instructions can be
    processed in ordered fashion; especially useful for quantum or
    appendable variables types. For instance, can be used on remote
    instructions for teleportation"""

    _transferred: bool
    """if the data container transferred data to other data container,
    in the same scope or to another scope, for instance, when a
    function returns the data container
    """

    _borrowed: bool
    """if the data is borrowed somewhere else"""

    @property
    def name(self) -> Symbol:
        """name of the variable"""
        return self._name

    @property
    def type(self) -> Symbol | CompositeSymbol:
        """type of the variable"""
        return self._type

    @property
    def is_assigned(self) -> bool:
        return self._assigned

    @property
    def is_constant(self) -> bool:
        return self._is_constant

    @property
    def is_mutable(self) -> bool:
        return self._is_mutable

    @property
    def is_appendable(self) -> bool:
        return self._is_appendable

    @property
    def is_quantum(self) -> bool:
        return self._is_quantum

    @property
    def data(self) -> SymbolOrdered:
        return self._data

    @property
    def value(self) -> SymbolOrdered:
        return self._data

    @property
    def counter(self) -> int:
        """
        The counter for instructions so quantum instructions can be
        processed in ordered fashion; especially useful for remote
        instructions on teleportation, for instance
        """

        return self._instr_counter

    @classmethod
    def _check_array_prop(cls, data: Any):
        """
        Check whether data has attribute `_array_type`.
        Usually related to data structures.
        """

        if hasattr(data, "_array_type"):
            return getattr(data, "_array_type")

        return False

    def _check_assign_ds_vals(
        self,
        data: Any,
        attr_type: Symbol,
        # tmp_container: SymbolOrdered
    ) -> bool:
        """
        Check data structure when passing values only (equivalent to `fn(*args)`) and
        assign value to container.


        Args:
            - data: literal, data structure or variable to be added to the variable data.
            - attr_type: The symbol that contains the type as attribute for the container.

        Returns:
            False if there is no attribute type. Otherwise, true.
        """

        if data.type == attr_type:

            # is quantum or array data structure
            if data.is_quantum or self._check_array_prop(data):

                if attr_type in self._ds:

                    if attr_type in self._data:
                        self._data[attr_type].append(data)

                    else:
                        self._data[attr_type] = [data]

                    self._instr_counter += 1
                    return True

                return False

            # not quantum
            self._data[attr_type] = data
            return True

        return False

    def _check_assign_ds_args_vals(
        self,
        key: Symbol,
        value: Any,
        # tmp_container: SymbolOrdered
    ) -> bool:
        """
        Check data structure when passing args and values, (equivalent to `fn(**args)`).
        Returns false if the key is not found, then cascading into a `ContainerVarError`.

        Args:
            - key: Symbol
            - value: literal, data structure or another variable to be added to the variable data.
            - tmp_container: SymbolOrdered (temporary container)
        """

        if key in self._ds:

            # is quantum or array data structure
            if key.is_quantum or self._check_array_prop(value):

                if key in self._data:
                    self._data[key].append(value)

                else:
                    self._data[key] = [value]

                self._instr_counter += 1
                return True

            # not quantum
            self._data[key] = value

            return True

        # key not in variable's attribute list
        return False

    @abstractmethod
    def assign(self, *args: Any, **kwargs: Any) -> None | ErrorHandler: ...

    @abstractmethod
    def get(self, *args: Any, **kwargs: Any) -> Any | ErrorHandler: ...

    def __call__(
        self,
        *args: Any,
        **kwargs: SymbolOrdered,
    ) -> None | ErrorHandler:
        return self.assign(*args, **kwargs)

    def __iter__(self) -> Iterable:
        yield from self._data.items()

    @abstractmethod
    def borrow(self, *args: Any, **kwargs: Any) -> None | ErrorHandler: ...

    @abstractmethod
    def transfer(self, *args: Any, **kwargs: Any) -> None | ErrorHandler: ...

    def free(self) -> None | ErrorHandler:
        """Freeing the container (program going out of container's scope)."""

        # it shouldn't be freed if data is borrowed somewhere else
        if self._borrowed:
            return VariableFreeingBorrowedError(self.name)

        del self
        return None


class VariableTemplate:
    """
    A template for all the types of variables. It will instantiate to the correct
    container type given flag. By the default it will produce an immutable variable.
    """

    def __new__(
        cls,
        var_name: Symbol,
        type_name: Symbol | CompositeSymbol,
        type_ds: SymbolOrdered,
        flag: VariableKind = VariableKind.IMMUTABLE,
    ) -> BaseDataContainer | ErrorHandler:

        # quantum variables are, at least for now, always appendable and thus mutable
        if isquantum(var_name) and isquantum(type_name):
            return AppendableVariable(var_name, type_name, type_ds, True)

        if not isquantum(var_name) and not isquantum(type_name):

            match flag:

                # constant, at least for now, cannot be quantum
                case VariableKind.CONSTANT:
                    return ConstantData(var_name, type_name, type_ds)

                case VariableKind.APPENDABLE:
                    return AppendableVariable(var_name, type_name, type_ds, False)

                case VariableKind.MUTABLE:
                    return MutableVariable(var_name, type_name, type_ds)

                case VariableKind.IMMUTABLE:
                    return ImmutableVariable(var_name, type_name, type_ds)

                # default for now is immutable
                case _:
                    return ImmutableVariable(var_name, type_name, type_ds)

        return VariableCreationError(var_name, type_name)


class ConstantData(BaseDataContainer):
    def __init__(
        self,
        var_name: Symbol,
        type_name: Symbol | CompositeSymbol,
        type_ds: SymbolOrdered,
    ):
        self._name = var_name
        self._type = type_name
        self._ds = type_ds
        self._data = SymbolOrdered()
        self._assigned = False
        self._is_constant = True
        self._is_mutable = False
        self._is_appendable = False
        self._is_quantum = False

        self._transferred = False
        self._borrowed = False

        self._instr_counter = 0

    def assign(self, *args: Any, **kwargs: Any) -> None | ErrorHandler:
        raise NotImplementedError()

    def get(self, member: Symbol | None = None) -> Any | ErrorHandler:
        member = next(iter(self._ds.keys())) if member is None else member

        if member in self._data:
            return self._data[member]

        return VariableWrongMemberError(self.name)

    def borrow(self, *args: Any, **kwargs: Any) -> None | ErrorHandler:
        raise NotImplementedError()

    def transfer(self, *args: Any, **kwargs: Any) -> None | ErrorHandler:
        raise NotImplementedError()


class ImmutableVariable(BaseDataContainer):
    def __init__(
        self,
        var_name: Symbol,
        type_name: Symbol | CompositeSymbol,
        type_ds: SymbolOrdered,
    ):
        self._name = var_name
        self._type = type_name
        self._ds = type_ds
        self._data = SymbolOrdered()
        self._assigned = False
        self._is_constant = False
        self._is_mutable = False
        self._is_quantum = False

        self._transferred = False
        self._borrowed = False

        self._instr_counter = 0

    def assign(
        self,
        *args: Any,
        **kwargs: SymbolOrdered,
    ) -> None | ErrorHandler:

        if not self._assigned:

            if len(args) == len(self._ds):

                for k, d in zip(args, self._ds):

                    if not self._check_assign_ds_vals(k, d):
                        return ContainerVarError(self.name)

            elif len(kwargs) == len(self._ds):

                for k, v in kwargs.items():

                    if not self._check_assign_ds_args_vals(Symbol(k), v):
                        return ContainerVarError(self.name)

            self._assigned = True
            return None

        return ContainerVarIsImmutableError(self.name)

    def get(self, member: Symbol | None = None) -> Any | ErrorHandler:
        member = next(iter(self._ds.keys())) if member is None else member

        if member in self._data:
            return self._data[member]

        return VariableWrongMemberError(self.name)

    def borrow(self, *args: Any, **kwargs: Any) -> None | ErrorHandler:
        raise NotImplementedError()

    def transfer(self, *args: Any, **kwargs: Any) -> None | ErrorHandler:
        raise NotImplementedError()


class MutableVariable(BaseDataContainer):
    def __init__(
        self,
        var_name: Symbol,
        type_name: Symbol | CompositeSymbol,
        type_ds: SymbolOrdered,
    ):
        self._name = var_name
        self._type = type_name
        self._ds = type_ds
        self._data = SymbolOrdered()
        self._assigned = False
        self._is_constant = False
        self._is_mutable = True
        self._is_quantum = False

        self._transferred = False
        self._borrowed = False

        self._instr_counter = 0

    def assign(
        self, *args: Any, **kwargs: dict[WorkingData, WorkingData | BaseDataContainer]
    ) -> None | ErrorHandler:

        if len(args) == len(self._ds):

            for k, d in zip(args, self._ds):

                if not self._check_assign_ds_vals(k, d):
                    return ContainerVarError(self.name)

        elif len(kwargs) == len(self._ds):

            for k, v in kwargs.items():

                if not self._check_assign_ds_args_vals(Symbol(k), v):
                    return ContainerVarError(self.name)

        self._assigned = True
        return None

    def get(self, member: Symbol | None = None) -> Any | ErrorHandler:
        member = next(iter(self._ds.keys())) if member is None else member

        if member in self._data:
            return self._data[member]

        return VariableWrongMemberError(self.name)

    def borrow(self, *args: Any, **kwargs: Any) -> None | ErrorHandler:
        raise NotImplementedError()

    def transfer(self, *args: Any, **kwargs: Any) -> None | ErrorHandler:
        raise NotImplementedError()


class AppendableVariable(BaseDataContainer):
    def __init__(
        self,
        var_name: Symbol,
        type_name: Symbol | CompositeSymbol,
        type_ds: SymbolOrdered,
        is_quantum: bool,
    ):
        self._name = var_name
        self._type = type_name
        self._ds = type_ds
        self._data = SymbolOrdered()
        self._assigned = False
        self._is_constant = False
        self._is_mutable = True
        self._is_quantum = is_quantum

        self._transferred = False
        self._borrowed = False

        self._instr_counter = 0

    def assign(
        self,
        *args: Any,
        **kwargs: SymbolOrdered,
    ) -> None | ErrorHandler:

        if len(args) == len(self._ds):

            for k, d in zip(args, self._ds):

                if not self._check_assign_ds_vals(k, d):
                    return ContainerVarError(self.name)

        elif len(kwargs) == len(self._ds):

            for k, v in kwargs.items():

                if not self._check_assign_ds_args_vals(Symbol(k), v):
                    return ContainerVarError(self.name)

        self._assigned = True
        return None

    def get(self, member: Symbol | None = None) -> Any | ErrorHandler:
        member = next(iter(self._ds.keys())) if member is None else member

        if member in self._data:
            return self._data[member]

        return VariableWrongMemberError(self.name)

    def borrow(self, *args: Any, **kwargs: Any) -> None | ErrorHandler:
        raise NotImplementedError()

    def transfer(self, *args: Any, **kwargs: Any) -> None | ErrorHandler:
        raise NotImplementedError()
