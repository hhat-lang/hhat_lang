from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from collections import OrderedDict, deque
from copy import deepcopy
from enum import Enum, auto
from idlelib.configdialog import is_int
from typing import Any, Hashable, Iterator, cast
from uuid import UUID

from hhat_lang.core.code.new_ir import BaseIRBlock
from hhat_lang.core.data.core import (
    CompositeLiteral,
    CompositeMixData,
    CompositeSymbol,
    CompositeWorkingData,
    CoreLiteral,
    Symbol,
    WorkingData,
)
from hhat_lang.core.data.fn_def import BaseFnCheck
from hhat_lang.core.data.variable import BaseDataContainer
from hhat_lang.core.error_handlers.errors import (
    ErrorHandler,
    FnWrongArgsTypesError,
    HeapInvalidKeyError,
    IndexAllocationError,
    IndexInvalidVarError,
    IndexUnknownError,
    IndexVarHasIndexesError,
    StackFrameGetError,
    StackFrameNotFnError,
)
from hhat_lang.core.utils import gen_uuid


class PIDManager:
    """
    Manages the PID for H-hat language, including all the dialects.
    """

    def new(self) -> UUID:
        raise NotImplementedError()

    def list(self) -> list[UUID]:
        raise NotImplementedError()


class IndexManager:
    """
    Holds and manages information about the indexes (qubits) availability and allocation.

    Properties
        ``max_number``: maximum number of allowed indexes

        ``available``: deque with all the available indexes

        ``allocated``: deque with all the allocated indexes

        ``resources``: variable members and literals with respective number of indexes
        requested

        ``in_use_by``: dictionary containing the allocator variable member as key and
        deque with allocated indexes as value

    Methods
        ``add``: add a variable member or literal with a requested number of indexes to
        the resources dictionary

        ``request``: given a variable member (``Symbol``) and the number of indexes
        (``int``), allocate the number if it has enough space

        ``free``: given a variable member (``Symbol``), free all the allocated indexes
    """

    _max_num_index: int
    _num_allocated: int
    _available: deque
    _allocated: deque
    _resources: dict[WorkingData | CompositeWorkingData, int]
    _in_use_by: dict[WorkingData | CompositeWorkingData, deque]

    def __init__(self, max_num_index: int):
        self._max_num_index = max_num_index
        self._num_allocated = 0
        self._available = deque(
            iterable=tuple(k for k in range(0, self._max_num_index)),
            maxlen=self._max_num_index,
        )
        self._allocated = deque(maxlen=self._max_num_index)
        self._resources = dict()
        self._in_use_by = dict()

    @property
    def max_number(self) -> int:
        return self._max_num_index

    @property
    def available(self) -> deque:
        return self._available

    @property
    def allocated(self) -> deque:
        return self._allocated

    @property
    def resources(self) -> dict[WorkingData | CompositeWorkingData, int]:
        """
        Dictionary containing the variable members/literal(s) and
        the index amount requested.
        """

        return self._resources

    @property
    def in_use_by(self) -> dict[WorkingData | CompositeWorkingData, deque]:
        """
        Dictionary containing the variable members/literal(s) with
        the deque of indexes provided.
        """

        return self._in_use_by

    def __getitem__(
        self, item: WorkingData | CompositeWorkingData
    ) -> deque | IndexInvalidVarError:
        """Return the deque of indexes from a quantum data."""

        if res := self._in_use_by.get(item, False):
            return res  # type: ignore [return-value]

        return IndexInvalidVarError(var_name=item)

    def __contains__(self, item: WorkingData | CompositeWorkingData) -> bool:
        """Checks whether there is item in the IndexManager."""

        return item in self._in_use_by

    def _alloc_idxs(self, num_idxs: int) -> deque | IndexAllocationError:
        available = self._max_num_index - self._num_allocated

        if available >= num_idxs:
            _data: tuple = tuple()

            for _ in range(0, num_idxs):
                _data += (self._available.popleft(),)
                self._num_allocated += 1

            return deque(
                iterable=_data,
                maxlen=num_idxs,
            )

        return IndexAllocationError(requested_idxs=num_idxs, max_idxs=available)

    def _alloc_var(
        self, member_name: WorkingData | CompositeWorkingData, idxs_deque: deque
    ) -> None:
        self._in_use_by[member_name] = idxs_deque
        self._allocated.extend(idxs_deque)

    def _has_var(self, member_name: WorkingData | CompositeWorkingData) -> bool:
        return member_name in self._resources

    def _free_var(self, member_name: WorkingData | CompositeWorkingData) -> deque:
        """
        Free variable member's indexes and allocated deque with those indexes.
        """

        idxs = self._in_use_by.pop(member_name)

        for k in idxs:
            self._allocated.remove(k)

        return idxs

    def add(
        self, member_name: WorkingData | CompositeWorkingData, num_idxs: int
    ) -> None | ErrorHandler:
        """
        Add a variable member/literal with a given number of indexes required for it.
        The amount will be used upon request through the `request` method.
        """

        if (self._num_allocated + num_idxs) <= self._max_num_index:
            if member_name not in self._resources:
                self._resources[member_name] = num_idxs
                return None

            return IndexVarHasIndexesError(member_name)

        return IndexAllocationError(
            requested_idxs=num_idxs, max_idxs=self._num_allocated
        )

    def request(
        self, member_name: WorkingData | CompositeWorkingData
    ) -> deque | ErrorHandler:
        """
        Request a number of indexes given by the `resources` property for
        a variable member `var_name`.
        """

        if not (num_idxs := self._resources.get(member_name, False)):
            return IndexInvalidVarError(member_name)

        match x := self._alloc_idxs(num_idxs):
            case deque():
                if not self._has_var(member_name):
                    return IndexInvalidVarError(var_name=member_name)

                self._alloc_var(member_name, x)
                return x

            case IndexAllocationError():
                return x

        return IndexUnknownError()

    def free(self, member_name: WorkingData | CompositeWorkingData) -> None:
        """
        Free indexes from a given variable member `var_name`.
        """

        idxs = self._free_var(member_name)
        self._available.extend(idxs)
        self._num_allocated -= len(idxs)


#########################
# DATA STORAGE MANAGERS #
#########################


class StackFrame:
    """Stack memory frame. To be used inside ``Stack`` instance whenever a new scope is needed"""

    _data: OrderedDict[
        WorkingData | CompositeSymbol | BaseFnCheck,
        BaseDataContainer | CoreLiteral | None,
    ]
    _fn_header: BaseFnCheck | None
    _for_fn_use: bool

    def __init__(self, for_fn_use: bool = False):
        self._data = OrderedDict()
        self._for_fn_use = for_fn_use

    @property
    def keys(
        self,
    ) -> tuple[WorkingData | CompositeWorkingData | BaseFnCheck, ...] | tuple:
        return tuple(self._data.keys())

    @property
    def for_fn_use(self) -> bool:
        return self._for_fn_use

    def add_no_assign(self, key: Symbol | CompositeSymbol) -> None:
        if key not in self._data and isinstance(key, WorkingData):
            self._data[key] = None

    def add(
        self,
        key: Symbol | CompositeSymbol | CoreLiteral,
        value: BaseDataContainer | CoreLiteral,
    ) -> None:
        if (
            isinstance(key, Symbol | CompositeSymbol | CoreLiteral)
            and (key not in self._data or self._data[key] is None)  # type: ignore [index]
            and isinstance(value, BaseDataContainer | CoreLiteral)
        ):
            self._data[key] = value

    def add_fn_header(self, header: BaseFnCheck) -> None:
        """First thing to be added on the stack frame instance if it is used for a function."""

        if isinstance(header, BaseFnCheck):
            self._fn_header = header

    def _check_fn_args_types(
        self, *values_types: BaseDataContainer | CoreLiteral
    ) -> bool:
        if self._for_fn_use:
            return all(
                cast(BaseFnCheck, self._fn_header).check_args_types(
                    k.type
                    if isinstance(k, BaseDataContainer)
                    else (
                        Symbol(k.type)
                        if isinstance(k.type, str)
                        else CompositeSymbol(k.type)
                    )
                )
                for k in values_types
            )

        sys.exit(StackFrameNotFnError()())

    def add_ordered(self, *values: BaseDataContainer | CoreLiteral) -> None:
        """
        **Note**: to be used only for functions, on its startup parameters declaration.

        Use when no argument name is provided and the ``*values`` are assumed to be in
        the correct order
        """

        if self._for_fn_use:
            if self._check_fn_args_types(*values):
                for k, v in zip(self._data, values):
                    self._data[k] = v

                return

            sys.exit(
                FnWrongArgsTypesError(
                    values=values,
                    expected=cast(BaseFnCheck, self._fn_header)._args_types,
                )()
            )

        # if no function-use stack frame defined, error is raised
        sys.exit(StackFrameNotFnError()())

    def get(
        self, item: WorkingData | CompositeSymbol | BaseFnCheck
    ) -> BaseDataContainer | CoreLiteral | ErrorHandler:
        return self._data.get(item) or StackFrameGetError(item)

    def __contains__(self, item: Any) -> bool:
        return item in self._data


class Stack:
    """
    Stack memory handling data inside frames according to scopes that appears in Lifo order.
    """

    class EntryType(Enum):
        VALUE_ONLY = auto()
        ARG_VALUE = auto()

    _data: list[StackFrame] | list
    _entry_stack: (
        list[
            BaseDataContainer
            | CoreLiteral
            | tuple[Symbol, BaseDataContainer | CoreLiteral]
        ]
        | list
    )
    _entry_type: Stack.EntryType
    _return_stack: list[BaseDataContainer | CoreLiteral] | list

    def __init__(self):
        self._data = []
        self._entry_stack = []
        self._return_stack = []

    def new(self, for_fn_use: bool = False) -> None:
        """Push a new ``StackFrame`` instance to the stack"""

        self._data.append(StackFrame(for_fn_use))

    def push(self, data: BaseDataContainer | CoreLiteral) -> None:
        """Push ``data`` into current stack's frame as its new last item"""

        if isinstance(data, BaseDataContainer):
            self._data[-1].add(data.name, data)  # type: ignore [arg-type]

        else:
            self._data[-1].add(data, data)

    def get(
        self, item: WorkingData | CompositeWorkingData
    ) -> BaseDataContainer | CoreLiteral:
        """Retrieves data from the current stack frame"""

        match res := self._data[-1].get(item):
            case ErrorHandler():
                sys.exit(res())

            case _:
                return res

    def set_fn_entry(
        self,
        *values: BaseDataContainer | CoreLiteral,
        fn_header: BaseFnCheck,
        **args_values: BaseDataContainer | CoreLiteral,
    ) -> None:
        """
        Set the function entry, i.e. it's arguments. It can be through only
        arguments (``*values``) or through keyword arguments (``**args_values``).

        It will be consumed by the function once the stack frame is initialized
        for it.

        Args:
            *values: ``BaseDataContainer`` or ``CoreLiteral`` data
            fn_header: ``BaseFnCheck`` instance
            **args_values: ``BaseDataContainer`` or ``CoreLiteral`` data
        """

        assert (values and not args_values) or (
            not values and args_values
        ), "stack frame cannot have both values and args values-pair"

        if isinstance(fn_header, BaseFnCheck):
            self._data[-1].add_fn_header(fn_header)

        if values:
            self._entry_stack.extend(value for value in values)
            self._entry_type = Stack.EntryType.VALUE_ONLY
            return

        self._entry_stack.extend(
            (Symbol(arg), value) for arg, value in args_values.items()
        )
        self._entry_type = Stack.EntryType.ARG_VALUE

    def get_fn_entry(self) -> None:
        """
        Retrieve function entry for the function stack frame.
        """

        if self._data[-1].for_fn_use:
            match self._entry_type:
                case Stack.EntryType.ARG_VALUE:
                    for arg, value in self._entry_stack:
                        self._data[-1].add(arg, value)

                case Stack.EntryType.VALUE_ONLY:
                    self._data[-1].add_ordered(*self._entry_stack)

        sys.exit(StackFrameNotFnError()())

    def set_fn_return(self, item: BaseDataContainer | CoreLiteral) -> None:
        """
        Add a function return to a special space in the stack; to be
        retrieved by the newest last stack frame
        """

        self._return_stack = [item]

    def get_fn_return(self) -> BaseDataContainer | CoreLiteral:
        """
        After the function is finished and its return value is properly
        addressed, this method must be used to clean the queue from
        function returns. Its output is the value being hold (possibly
        to be used by another stack frame).
        """

        return_res = deepcopy(self._return_stack)[0]
        self._return_stack = []
        return return_res

    def free(self) -> None:
        """Free last frame from stack"""

        self._data.pop()

    def __contains__(self, item: Any) -> bool:
        """Always check in the last stack frame added"""
        return item in self._data[-1]


class Heap:
    """Heap memory handling data of dynamic size"""

    _data: dict[Symbol, BaseDataContainer]

    def __init__(self):
        self._data = dict()

    def set(self, key: Symbol, value: BaseDataContainer) -> None | HeapInvalidKeyError:
        if not (isinstance(key, Symbol) and isinstance(value, BaseDataContainer)):
            return HeapInvalidKeyError(key=key)

        self._data[key] = value
        return None

    def get(self, key: Symbol) -> BaseDataContainer | HeapInvalidKeyError:
        """
        Given a key, returns its data which can be a variable container (variable content),
        a working data (symbol, literal) or composite working data.
        """

        if (var_data := self._data.get(key, None)) is None:
            return HeapInvalidKeyError(key=key)

        return var_data  # type: ignore [return-value]

    def free(self, key: Symbol) -> HeapInvalidKeyError | None:
        """
        To free a given key from the heap. It must be called every time the heap goes out of scope
        """

        if not self._data.pop(key, False):
            return HeapInvalidKeyError(key=key)

        return None

    def __contains__(self, item: Symbol) -> bool:
        return item in self._data

    def __getitem__(self, item: Symbol) -> BaseDataContainer:
        match res := self.get(item):
            case BaseDataContainer():
                return res

            case HeapInvalidKeyError():
                sys.exit(res())

            case _:
                raise ValueError("could not get heap value")


class ScopeValue:
    """Holds a value for scopes"""

    _value: int
    _counter: int

    def __init__(self, obj: Hashable, *, counter: int):
        """
        Hold a value for scope.

         Args:
             obj: object must be hashable
             counter: from the execution counter, to keep track of scope nesting
        """

        self._value = gen_uuid(gen_uuid(obj) + counter)
        self._counter = counter

    @property
    def value(self) -> int:
        return self._value

    @property
    def counter(self) -> int:
        return self._counter

    def __hash__(self) -> int:
        return self._value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ScopeValue):
            return self._value == other._value

        if isinstance(other, int):
            return self._value == other

        return False

    def __repr__(self) -> str:
        return f"S#{self._value}"


class Scope:
    """Defines a scope for stack and heap memory allocation"""

    _table: OrderedDict[ScopeValue, Heap]

    def __init__(self):
        self._heap = dict()

    @property
    def table(self) -> OrderedDict[ScopeValue, Heap]:
        return self._table

    def new(self, scope: ScopeValue) -> Any:
        """Define a new scope"""
        if isinstance(scope, ScopeValue):
            self._table[scope] = Heap()

        else:
            # TODO: maybe create a error handler for it?
            raise ValueError(f"value scope must be ScopeValue, got {type(scope)}")

    def last(self) -> ScopeValue:
        """
        Get the last ``ScopeValue``, having an ``OrderedDict`` object, will always
        return the key-value pairs in insertion order.
        """

        return next(reversed(self._table))

    def free(self, scope: ScopeValue) -> ScopeValue | None:
        """
        Free scope heap memory. Must be called every time the scope is finished.

        Returns:
            The ``ScopeValue`` object where the return data was placed,
            if ``to_return`` is set to ``True``. ``False`` by default. Otherwise,
            ``None`` is returned
        """

        self._table.pop(scope)
        return None

    def __len__(self) -> int:
        return len(self._table)

    def __contains__(self, item: ScopeValue) -> bool:
        return item in self._table


########################
# MEMORY MANAGER CLASS #
########################


class BaseMemoryManager(ABC):
    _heap: Scope
    _stack: Stack
    _cur_scope: ScopeValue

    @property
    def heap(self) -> Scope:
        return self._heap

    @property
    def stack(self) -> Stack:
        return self._stack

    @property
    def cur_scope(self) -> ScopeValue:
        return self._cur_scope


class MemoryManager(BaseMemoryManager):
    """Manages the stack and heap per scope, pid, and indexes."""

    def __init__(self, *, ir_block: BaseIRBlock, depth_counter: int):
        if isinstance(ir_block, BaseIRBlock) and isinstance(depth_counter, int):
            self._stack = Stack()
            self._heap = Scope()
            self._cur_scope = ScopeValue(obj=ir_block, counter=depth_counter)
            self._heap.new(self._cur_scope)

        else:
            raise ValueError(
                "memory manager needs IR block object, and execution code depth counter"
            )

    def new_scope(self, ir_block: BaseIRBlock, depth_counter: int) -> ScopeValue:
        scope_value = ScopeValue(ir_block, counter=depth_counter)
        self._heap.new(scope_value)
        self._cur_scope = scope_value
        return scope_value

    def free_scope(self, scope: ScopeValue, to_return: bool = False) -> None:
        self._heap.free(scope=scope)

        if scope == self._cur_scope:
            if len(self._heap) > 0:
                self._cur_scope = self._heap.last()

            else:
                # no more scope, the execution should have reached the end of the code
                # TODO: double check later what to do in this case
                pass

    def free_last_scope(self, to_return: bool = False) -> None:
        if len(self._heap) > 0:
            last_scope = self._heap.last()
            self._heap.free(scope=last_scope)

            if len(self._heap) > 0:
                self._cur_scope = self._heap.last()

            else:
                # TODO: what to do next
                pass

        else:
            raise ValueError(
                "trying to free last scope, but no more scope is left; mind is empty"
            )


class QuantumMemoryManager(MemoryManager):
    """
    A quantum version of memory manager to execute quantum programs containing both classical
    and quantum instructions. It is a superset of ``MemoryManager`` because it includes
    ``IndexManager``.
    """

    _idx: IndexManager

    def __init__(
        self, *, ir_block: BaseIRBlock, max_num_index: int, depth_counter: int = 0
    ):
        if isinstance(max_num_index, int):
            self._idx = IndexManager(max_num_index)
            super().__init__(ir_block=ir_block, depth_counter=depth_counter)

        else:
            raise ValueError(
                f"max num index must be integer, got {type(max_num_index)}"
            )

    @property
    def idx(self) -> IndexManager:
        return self._idx


MemoryDataTypes = (
    BaseDataContainer | CoreLiteral | CompositeLiteral | Symbol | CompositeMixData
)
"""
- BaseDataContainer
- CoreLiteral
- CompositeLiteral
- Symbol
- CompositeMixData
"""
