from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque, OrderedDict
from queue import LifoQueue
from typing import Any, Hashable
from uuid import UUID

from hhat_lang.core.code.abstract_new_ir import BaseIRBlock
from hhat_lang.core.code.symbol_table import SymbolTable
from hhat_lang.core.utils import gen_uuid
from hhat_lang.core.data.core import (
    CompositeLiteral,
    CompositeMixData,
    CoreLiteral,
    Symbol,
    WorkingData,
    CompositeWorkingData,
)
from hhat_lang.core.data.variable import BaseDataContainer
from hhat_lang.core.error_handlers.errors import (
    ErrorHandler,
    HeapInvalidKeyError,
    IndexAllocationError,
    IndexInvalidVarError,
    IndexUnknownError,
    IndexVarHasIndexesError,
)


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
        self,
        item: WorkingData | CompositeWorkingData
    ) -> deque | IndexInvalidVarError:
        """Return the deque of indexes from a quantum data."""

        if res := self._in_use_by.get(item, False):
            return res

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
        self,
        member_name: WorkingData | CompositeWorkingData,
        idxs_deque: deque
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
        self,
        member_name: WorkingData | CompositeWorkingData,
        num_idxs: int
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
        self,
        member_name: WorkingData | CompositeWorkingData
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


class BaseStack(ABC):
    _data: LifoQueue

    @abstractmethod
    def push(self, data: MemoryDataTypes) -> None:
        pass

    @abstractmethod
    def pop(self) -> MemoryDataTypes:
        pass

    @abstractmethod
    def peek(self) -> MemoryDataTypes:
        pass


class Stack(BaseStack):
    def __init__(self):
        self._data = LifoQueue()

    def push(self, data: MemoryDataTypes) -> None:
        """Push ``data`` into stack as its new last item"""

        self._data.put(data)

    def pop(self) -> MemoryDataTypes:
        """Pop last item from stack"""

        return self._data.get()

    def peek(self) -> MemoryDataTypes:
        """Expensive method to 'peek' the last item from the stack."""

        last_item = self._data.get()
        self._data.put(last_item)
        return last_item


class BaseHeap(ABC):
    _data: dict[Symbol, BaseDataContainer]

    @abstractmethod
    def set(self, key: Symbol, value: BaseDataContainer) -> None:
        pass

    @abstractmethod
    def get(self, key: Symbol) -> BaseDataContainer:
        pass

    def __getitem__(self, item: Symbol) -> BaseDataContainer:
        return self.get(item)


class Heap(BaseHeap):
    def __init__(self):
        self._data = dict()

    def set(self, key: Symbol, value: BaseDataContainer) -> None | HeapInvalidKeyError:
        if not (isinstance(key, Symbol) and isinstance(value, BaseDataContainer)):
            return HeapInvalidKeyError(key=key)

        self._data[key] = value
        return None

    def get(
        self,
        key: Symbol
    ) -> BaseDataContainer | HeapInvalidKeyError:
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
        if (
            isinstance(ir_block, BaseIRBlock)
            and isinstance(depth_counter, int)
        ):
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
            raise ValueError("trying to free last scope, but no more scope is left; mind is empty")


class QuantumMemoryManager(MemoryManager):
    """
    A quantum version of memory manager to execute quantum programs containing both classical
    and quantum instructions. It is a superset of ``MemoryManager`` because it includes
    ``IndexManager``.
    """

    _idx: IndexManager

    def __init__(self, *, ir_block: BaseIRBlock, max_num_index: int, depth_counter: int = 0):
        if isinstance(max_num_index, int):
            self._idx = IndexManager(max_num_index)
            super().__init__(
                ir_block=ir_block,
                depth_counter=depth_counter
            )

        else:
            raise ValueError(f"max num index must be integer, got {type(max_num_index)}")

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
