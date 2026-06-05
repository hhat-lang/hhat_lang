from __future__ import annotations

import sys
from abc import ABC
from collections import OrderedDict, deque
from copy import deepcopy
from enum import Enum, auto
from typing import Any, cast
from uuid import UUID

from hhat_lang.core.code.base import FnHeader, BaseIRBlock
from hhat_lang.core.data.core import (
    CompositeSymbol,
    Literal,
    LiteralArray,
    ObjArray,
    ObjTuple,
    SimpleObj,
    Symbol,
)
from hhat_lang.core.data.var_def import DataDef
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
from hhat_lang.core.memory.utils import ScopeValue


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
    _resources: dict[SimpleObj | ObjArray, int]
    _in_use_by: dict[SimpleObj | ObjArray, deque]

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
    def resources(self) -> dict[SimpleObj | ObjArray, int]:
        """
        Dictionary containing the variable members/literal(s) and
        the index amount requested.
        """

        return self._resources

    @property
    def in_use_by(self) -> dict[SimpleObj | ObjArray, deque]:
        """
        Dictionary containing the variable members/literal(s) with
        the deque of indexes provided.
        """

        return self._in_use_by

    def __getitem__(self, item: SimpleObj | ObjArray) -> deque | IndexInvalidVarError:
        """Return the deque of indexes from a quantum data."""

        if res := self._in_use_by.get(item, False):
            return res  # type: ignore [return-value]

        return IndexInvalidVarError(var_name=item)

    def __contains__(self, item: SimpleObj | ObjArray) -> bool:
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

    def _alloc_var(self, member_name: SimpleObj | ObjArray, idxs_deque: deque) -> None:
        self._in_use_by[member_name] = idxs_deque
        self._allocated.extend(idxs_deque)

    def _has_var(self, member_name: SimpleObj | ObjArray) -> bool:
        return member_name in self._resources

    def _free_var(self, member_name: SimpleObj | ObjArray) -> deque:
        """
        Free variable member's indexes and allocated deque with those indexes.
        """

        idxs = self._in_use_by.pop(member_name)

        for k in idxs:
            self._allocated.remove(k)

        return idxs

    def add(
        self, member_name: SimpleObj | ObjArray, num_idxs: int
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

    def request(self, member_name: SimpleObj | ObjArray) -> deque | ErrorHandler:
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

    def free(self, member_name: SimpleObj | ObjArray) -> None:
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
        SimpleObj | CompositeSymbol | FnHeader,
        DataDef | Literal | None,
    ]
    _fn_header: FnHeader | None
    _for_fn_use: bool

    def __init__(self, for_fn_use: bool = False):
        self._data = OrderedDict()
        self._for_fn_use = for_fn_use

    @property
    def keys(
        self,
    ) -> tuple[SimpleObj | ObjArray | FnHeader, ...] | tuple:
        return tuple(self._data.keys())

    @property
    def for_fn_use(self) -> bool:
        return self._for_fn_use

    def add_no_assign(self, key: Symbol | CompositeSymbol) -> None:
        if key not in self._data and isinstance(key, SimpleObj):
            self._data[key] = None

    def add(
        self,
        key: Symbol | CompositeSymbol | Literal,
        value: DataDef | Literal,
    ) -> None:
        if (
            isinstance(key, Symbol | CompositeSymbol | Literal)
            and (key not in self._data or self._data[key] is None)  # type: ignore [index]
            and isinstance(value, DataDef | Literal)
        ):
            self._data[key] = value

    def add_fn_header(self, header: FnHeader) -> None:
        """First thing to be added on the stack frame instance if it is used for a function."""

        if isinstance(header, FnHeader):
            self._fn_header = header

    def _check_fn_args_types(self, *values_types: DataDef | Literal) -> bool:
        if self._for_fn_use:
            return all(
                cast(FnHeader, self._fn_header).check_args_types(
                    k.type
                    if isinstance(k, DataDef)
                    else (
                        Symbol(k.type)
                        if isinstance(k.type, str)
                        else CompositeSymbol(k.type)
                    )
                )
                for k in values_types
            )

        sys.exit(StackFrameNotFnError()())

    def add_ordered(self, *values: DataDef | Literal) -> None:
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
                    expected=cast(FnHeader, self._fn_header)._args_types,
                )()
            )

        # if no function-use stack frame defined, error is raised
        sys.exit(StackFrameNotFnError()())

    def get(
        self, item: SimpleObj | CompositeSymbol | FnHeader
    ) -> DataDef | Literal | ErrorHandler:
        return self._data.get(item) or StackFrameGetError(item)

    def pop(self) -> DataDef | Literal:
        """Pops last value from ``StackFrame`` (data container or literal)"""

        return self._data.popitem()[-1]

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
    _entry_stack: list[DataDef | Literal | tuple[Symbol, DataDef | Literal]] | list
    _entry_type: Stack.EntryType
    _return_stack: list[DataDef | Literal] | list

    def __init__(self):
        self._data = []
        self._entry_stack = []
        self._return_stack = []

    def new(self, for_fn_use: bool = False) -> None:
        """Push a new ``StackFrame`` instance to the stack"""

        self._data.append(StackFrame(for_fn_use))

    def push(self, data: DataDef | Literal) -> None:
        """Push ``data`` into current stack's frame as its new last item"""

        if isinstance(data, DataDef):
            self._data[-1].add(data.name, data)  # type: ignore [arg-type]

        else:
            self._data[-1].add(data, data)

    def get(self, item: SimpleObj | CompositeSymbol) -> DataDef | Literal:
        """Retrieves data from the current stack frame"""

        match res := self._data[-1].get(item):
            case ErrorHandler():
                sys.exit(res())

            case _:
                return res

    def pop(self) -> DataDef | Literal:
        """Pops last element from current ``StackFrame`` (either data container or literal)"""

        return self._data[-1].pop()

    def set_fn_entry(
        self,
        *values: DataDef | Literal,
        fn_header: FnHeader,
        **args_values: DataDef | Literal,
    ) -> None:
        """
        Set the function entry, i.e. it's arguments. It can be through only
        arguments (``*values``) or through keyword arguments (``**args_values``).

        It will be consumed by the function once the stack frame is initialized
        for it.

        Args:
            *values: ``DataDef`` or ``CoreLiteral`` data
            fn_header: ``BaseFnCheck`` instance
            **args_values: ``DataDef`` or ``CoreLiteral`` data
        """

        assert (values and not args_values) or (
            not values and args_values
        ), "stack frame must have either values org args values-pair"

        if isinstance(fn_header, FnHeader):
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

    def set_fn_return(self, item: DataDef | Literal) -> None:
        """
        Add a function return to a special space in the stack; to be
        retrieved by the newest last stack frame
        """

        self._return_stack = [item]

    def get_fn_return(self) -> DataDef | Literal:
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

    def __enter__(self) -> Stack:
        """
        This method must be invoked only when ``MemoryManager.new_stack_fn`` method
        is used with ``with``.
        """

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Any:
        if not (exc_type or exc_val or exc_tb):
            # TODO: improve this error handling
            sys.exit(exc_type or exc_val or exc_tb)

        return_result = self.get_fn_return()
        # free function context stack
        self.free()
        # push return result to the former previous stack (now current one again)
        self.push(return_result)


class Heap:
    """Heap memory handling data of dynamic size"""

    _data: dict[Symbol, DataDef]

    def __init__(self):
        self._data = dict()

    def set(self, key: Symbol, value: DataDef) -> None | HeapInvalidKeyError:
        if not (isinstance(key, Symbol) and isinstance(value, DataDef)):
            return HeapInvalidKeyError(key=key)

        self._data[key] = value
        return None

    def get(self, key: Symbol) -> DataDef | HeapInvalidKeyError:
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

    def __getitem__(self, item: Symbol) -> DataDef:
        match res := self.get(item):
            case DataDef():
                return res

            case HeapInvalidKeyError():
                sys.exit(res())

            case _:
                raise ValueError("could not get heap value")


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

    def __getitem__(self, item: ScopeValue) -> Heap:
        return self._table[item]


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

    def new_fn_stack(self, *args: Any, fn_header: FnHeader) -> Stack:
        self._stack.new(for_fn_use=True)
        self._stack.set_fn_entry(*args, fn_header=fn_header)
        return self._stack


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


MemoryDataTypes = DataDef | Literal | LiteralArray | Symbol | ObjTuple
"""
- DataDef
- CoreLiteral
- CompositeLiteral
- Symbol
- CompositeMixData
"""
