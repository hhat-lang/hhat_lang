from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from collections import deque
from enum import Enum, auto
from functools import wraps
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    TypeVar,
)

from hhat_lang.core.code.base import BaseIRBlock, BaseIRInstr
from hhat_lang.core.data.core import (
    AsArray,
    CompositeSymbol,
    Literal,
    LiteralArray,
    Symbol,
)
from hhat_lang.core.data.utils import DataKind, isquantum, has_same_paradigm
from hhat_lang.core.error_handlers.errors import (
    CollectionInsertWrongTypeError,
    DataInitializationArgumentsError,
    ErrorHandler,
    FeatureNotImplementedError,
    ImmutableDataReassignmentError,
    InvalidContentDataError,
    InvalidDataStorageError,
    InvalidDataTypeCollectionError,
    LazySequenceConsumedError,
    RetrieveAppendableDataError,
    UsingDataBeforeInitializationError,
    sys_exit,
)
from hhat_lang.core.memory.utils import ScopeValue
from hhat_lang.core.types.abstract_base import BaseTypeDef
from hhat_lang.core.types.utils import BaseTypeEnum
from hhat_lang.core.utils import HatOrderedDict


T = TypeVar("T")
D = TypeVar("D")
ContentType = BaseIRBlock | BaseIRInstr | Literal | LiteralArray | AsArray


_data_type_storage_dict: dict[BaseTypeEnum, Callable[[DataKind], BaseCollection]] = (
    dict()
)
"""
Dictionary to store data type classes (``BaseCollection``) as values 
and they naming convention (``BaseTypeEnum``) as keys.
"""

_data_kind_storage_dict: dict[DataKind, Callable[[], BaseDataStorage]] = dict()
"""
Dictionary to store ``BaseDataStorage`` callables as values based on ``DataKind``
enum values as keys.
"""


def get_data_type_collection(
    entry: BaseTypeEnum,
) -> Callable[[DataKind], BaseCollection]:
    """
    Function to retrieve data type collection class callable through a ``BaseTypeEnum``
    member argument.
    """

    if res := _data_type_storage_dict.get(entry):
        return res

    sys.exit(InvalidDataTypeCollectionError(entry)())


def get_data_kind_storage(entry: DataKind) -> Callable[[], BaseDataStorage]:
    """
    Function to retrieve data storage class callable through a ``DataKind``
    member argument.
    """

    if res := _data_kind_storage_dict.get(entry):
        return res

    sys.exit(InvalidDataStorageError(entry)())


def store_to_dict(
    key: DataKind | BaseTypeEnum,
) -> Callable[[type[BaseDataStorage]], Callable[[DataKind | None], BaseDataStorage]]:
    """
    For ``BaseDataStorage``:
        Decorator to insert for each data kind (``DataKind``) a corresponding \
        ``BaseDataStorage`` class inside ``storage_kind_dict`` dictionary.

    For ``BaseCollection``:
        Decorator to insert for each type enum (``BaseTypeEnum``) a corresponding \
        ``BaseCollection`` class inside ``storage_data_type_dict`` dictionary.
    """

    obj: dict

    match key:
        case DataKind():
            obj = _data_kind_storage_dict

        case BaseTypeEnum():
            obj = _data_type_storage_dict

        case _:
            raise ValueError(
                f"invalid obj '{key}' to store on data collection {type(key)}"
            )

    def decorator(
        cls: type[BaseDataStorage],
    ) -> Callable[[DataKind | None], BaseDataStorage]:
        @wraps(cls)
        def wrapper(
            *args: DataKind | None, **kwargs: DataKind | None
        ) -> BaseDataStorage:
            return cls(*args, **kwargs)

        obj[key] = wrapper
        return wrapper

    return decorator


class DataHeader:
    """
    To hold relevant and unique information regarding a data container
    (variable, temporary data, etc.). Each data header must have a name,
    a type, a kind (mutable, appendable, etc.) and an uid value (scope value).
    """

    _name: Symbol | CompositeSymbol
    _type: BaseTypeDef
    _is_quantum: bool
    _kind: DataKind
    _uid: ScopeValue
    _hash_value: int
    __slots__ = ("_name", "_type", "_is_quantum", "_kind", "_uid", "_hash_value")

    def __init__(
        self,
        name: Symbol | CompositeSymbol,
        data_type: BaseTypeDef,
        kind: DataKind,
        counter: int,
    ):
        if (
            isinstance(name, Symbol | CompositeSymbol)
            and isinstance(data_type, BaseTypeDef)
            and isinstance(kind, DataKind)
            and isinstance(counter, int)
        ):
            self._name = name
            self._type = data_type
            self._kind = kind
            self._is_quantum = isquantum(name)
            self._uid = ScopeValue((name, data_type, kind), counter=counter)
            self._hash_value = hash((name, data_type, self._uid))

        else:
            sys_exit(
                error_fn=DataInitializationArgumentsError(
                    name, data_type, kind=kind, counter=counter
                )
            )

    @property
    def name(self) -> Symbol | CompositeSymbol:
        return self._name

    @property
    def type(self) -> BaseTypeDef:
        return self._type

    @property
    def is_quantum(self) -> bool:
        return self._is_quantum

    @property
    def kind(self) -> DataKind:
        return self._kind

    @property
    def uid(self) -> int:
        return self._uid.value

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)

        return False


################################
# DATA TYPE COLLECTION SECTION #
################################


class BaseCollection(ABC, Generic[D]):
    """Abstract data type collection class."""

    _data: D
    _storage: Callable[[], BaseDataStorage]

    def __init__(self, data_kind: DataKind):
        self._storage = get_data_kind_storage(data_kind)

    @abstractmethod
    def insert(
        self, *args: Symbol | BaseTypeDef | Any, **kwargs: Symbol | BaseTypeDef | Any
    ) -> ErrorHandler | None:
        raise NotImplementedError()

    @abstractmethod
    def get(
        self, *args: Symbol | BaseTypeDef | Any, **kwargs: Symbol | BaseTypeDef | Any
    ) -> ContentType | Iterable[ContentType]:
        raise NotImplementedError()

    @abstractmethod
    def __iter__(self) -> Iterable:
        raise NotImplementedError()

    def __getitem__(self, item: int | Any) -> ContentType | Iterable[ContentType]:
        return self.get(item)


@store_to_dict(BaseTypeEnum.SINGLE)
class SingleCollection(BaseCollection):
    """
    Single data type collection class.
    """

    _data: BaseDataStorage

    def __init__(self, data_kind: DataKind):
        super().__init__(data_kind)
        self._data = self._storage()

    def insert(self, data: ContentType, **kwargs: Any) -> None:
        self._data.add(data)

    def get(
        self, item: int | Any | None, **_kwargs: Any
    ) -> ContentType | Iterable[ContentType]:
        return self._data.get(item)

    def __iter__(self) -> Iterable:
        return iter((self._data,))


@store_to_dict(BaseTypeEnum.STRUCT)
class StructCollection(BaseCollection):
    """
    Struct data type collection class.
    """

    _data: HatOrderedDict[Symbol | BaseTypeDef, BaseDataStorage]

    def __init__(self, data_kind: DataKind):
        super().__init__(data_kind)
        self._data = HatOrderedDict()

    def insert(
        self, member: Symbol | BaseTypeDef | int, data: ContentType, **kwargs: Any
    ) -> ErrorHandler | None:
        print(
            f"struct collection insert {member=} ({type(member)}) {data=} ({type(data)})"
        )
        match member:
            case Symbol() | BaseTypeDef():
                if member not in self._data:
                    self._data[member] = self._storage()
                    return self._data[member].add(data)

                else:
                    self._data[member] += data
                    return (
                        self._data[member]
                        if isinstance(self._data[member], ErrorHandler)
                        else None
                    )

            case int():
                for n, k in enumerate(self._data):
                    print(f"struct collection {n=} | {k=} | {member=} | {n == member=}")
                    if n == member:
                        self._data[k] += data
                        print(f"successful {n} {k} {data}")
                        return (
                            self._data[k]
                            if isinstance(self._data[k], ErrorHandler)
                            else None
                        )

            case _:
                return CollectionInsertWrongTypeError("struct")

        return None

    def get(
        self, member: int | Symbol | BaseTypeDef, **kwargs: Any
    ) -> ContentType | Iterable[ContentType]:
        return self._data.get(member).get(None)

    def __iter__(self) -> Iterable:
        return iter(self._data.items())


@store_to_dict(BaseTypeEnum.ENUM)
class EnumCollection(BaseCollection):
    """
    Enum data type collection class.
    """

    _data: HatOrderedDict[Symbol, Symbol | BaseTypeDef]

    def __init__(self, data_kind: DataKind):
        super().__init__(data_kind)
        self._data = HatOrderedDict()

    def insert(
        self, member: Symbol | BaseTypeDef, **kwargs: Any
    ) -> ErrorHandler | None:
        sys_exit(
            error_fn=FeatureNotImplementedError(
                "insert", "a method to insert content on enum collection"
            )
        )

    def get(self, member: Symbol | BaseTypeDef, **kwargs: Any) -> T:
        sys_exit(
            error_fn=FeatureNotImplementedError(
                "get", "a method to get content from enum collection"
            )
        )

    def __iter__(self) -> Iterable:
        return iter(self._data.values())


########################
# DATA STORAGE SECTION #
########################


class BaseDataStorage(ABC, Generic[T]):
    """
    Base data storage class. To be used when defining new classes for
    storing data inside ``DataDef``.
    """

    _data: T

    @property
    def value(self) -> T:
        return self._data

    def __init__(self, *args: Any, **kwargs: Any):
        pass

    @abstractmethod
    def add(self, value: ContentType, **kwargs: Any) -> ErrorHandler | None:
        raise NotImplementedError()

    @abstractmethod
    def get(
        self, item: int | Any, **kwargs: Any
    ) -> ContentType | Iterable[ContentType]:
        raise NotImplementedError()

    @abstractmethod
    def __iadd__(self, other: ContentType) -> BaseDataStorage | ErrorHandler:
        raise NotImplementedError()

    @abstractmethod
    def __getitem__(self, item: int) -> ContentType:
        raise NotImplementedError()

    @abstractmethod
    def __iter__(self) -> Iterable:
        raise NotImplementedError()


@store_to_dict(DataKind.IMMUTABLE)
@store_to_dict(DataKind.CONSTANT)
class ImmutableItem(BaseDataStorage[ContentType | None]):
    """
    Immutable data storage class. Must contain a single immutable element.
    """

    _data: ContentType | None
    _assigned: bool

    def __init__(self, value: ContentType | None = None):
        super().__init__()

        if value and isinstance(value, ContentType):
            self._data = value
            self._assigned = True

        else:
            self._data = None
            self._assigned = False

    def add(self, value: ContentType, **kwargs: Any) -> ErrorHandler | None:
        if not self._assigned and isinstance(value, ContentType):
            self._data = value
            self._assigned = True
            return None

        return ImmutableDataReassignmentError()

    def get(
        self, item: int | Any, **kwargs: Any
    ) -> ContentType | Iterable[ContentType]:
        if self._assigned:
            return self.__getitem__(None)

        sys_exit(error_fn=UsingDataBeforeInitializationError())

    def __iadd__(self, other: ContentType) -> ImmutableItem | ErrorHandler:
        res = self.add(other)
        return res if isinstance(res, ErrorHandler) else self

    def __getitem__(self, item: int | None = None) -> ContentType:
        return self._data

    def __iter__(self) -> Iterable:
        if self._assigned:
            return iter((self._data,))

        sys_exit(error_fn=UsingDataBeforeInitializationError())


@store_to_dict(DataKind.MUTABLE)
class MutableItem(BaseDataStorage[ContentType | None]):
    """
    Mutable data storage class. Must contain a single element.
    """

    _data: ContentType | None
    _assigned: bool

    def __init__(self, value: ContentType | None = None):
        super().__init__()
        self._data = value
        self._assigned = False

    def add(self, value: ContentType, **kwargs: Any) -> ErrorHandler | None:
        if isinstance(value, ContentType):
            self._data = value
            self._assigned = True
            return None

        return InvalidContentDataError()

    def get(
        self, item: int | Any, **kwargs: Any
    ) -> ContentType | Iterable[ContentType]:
        if self._assigned:
            return self.__getitem__(None)

        sys_exit(error_fn=UsingDataBeforeInitializationError())

    def __iadd__(self, other: ContentType) -> MutableItem | ErrorHandler:
        res = self.add(other)
        return res if isinstance(res, ErrorHandler) else self

    def __getitem__(self, item: int | None = None) -> ContentType:
        return self._data

    def __iter__(self) -> Iterable:
        if self._assigned:
            return iter((self._data,))

        sys_exit(error_fn=UsingDataBeforeInitializationError())


@store_to_dict(DataKind.APPENDABLE)
class LazySequence(BaseDataStorage[deque[ContentType]]):
    """
    Appendable lazy sequence, to be used on appendable data kind, such as quantum data.
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

    It is a lazy sequence due to its nature to accumulate instructions and to be
    consumed iterated over, which is the desirable behavior for a quantum data
    storage.

    Note: this object is not hashable.
    """

    # use Queue in the future for threading/asynchronous queueing
    _data: deque[ContentType]
    _assigned: bool
    _locked: bool

    def __init__(self, *values: ContentType):
        if all(isinstance(value, ContentType) for value in values):
            super().__init__()
            self._data = deque(*values)
            self._assigned = False
            self._locked = False

    def append(self, value: ContentType) -> ErrorHandler | None:
        return self.add(value)

    def add(self, value: ContentType, **_kwargs: Any) -> ErrorHandler | None:
        if not self._locked and isinstance(value, ContentType):
            self._data.append(value)
            self._assigned = True
            return None

        return LazySequenceConsumedError()

    def get(
        self, item: int | Any | None, **kwargs: Any
    ) -> ContentType | list[ContentType]:
        if item is None:
            return list(self._data)

        return self.__getitem__(item)

    def __iadd__(self, other: ContentType) -> LazySequence:
        self.append(other)
        return self

    def __getitem__(self, item: int | Any) -> ContentType:
        if isinstance(item, int):
            return self._data[item]

        sys.exit(RetrieveAppendableDataError(item)())

    def __iter__(self) -> Iterable:
        if self._assigned:
            self._locked = True
            yield from self._data

        sys.exit()


class ContainerType(Enum):
    """
    Container enum class. Contain members to name a given container instance. Values:

    - IMMUTABLE
    - MUTABLE
    - ARRAY
    - LAZY
    """

    IMMUTABLE = auto()
    MUTABLE = auto()
    ARRAY = auto()
    LAZY = auto()


class Container(ABC):
    """
    Abstract container class. To hold data for variables, constants,
    temporary data, etc.
    """

    _data: Iterable
    _type: ContainerType

    @property
    def value(self) -> Iterable:
        return self._data

    @abstractmethod
    def add(self, value: ContentType) -> None:
        raise NotImplementedError()

    @abstractmethod
    def __getitem__(self, item: int | Any) -> ContentType | Iterable[ContentType]:
        raise NotImplementedError()

    @abstractmethod
    def get(self, *_args: Any) -> ContentType | Iterable[ContentType]:
        raise NotImplementedError()

    @abstractmethod
    def __add__(self, other: Any) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def __radd__(self, other: Any) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        raise NotImplementedError()

    def __iter__(self) -> Iterable:
        return iter(self._data)

    def __repr__(self):
        return f"{self._type.name}({' '.join(str(k) for k in self._data)})"


class ImmutableContainer(Container):
    """
    Immutable data container class. Must contain a single immutable element.
    """

    _data: tuple[ContentType] | tuple
    _assigned: bool
    _type = ContainerType.IMMUTABLE

    def __init__(self):
        self._data = ()
        self._assigned = False

    def add(self, value: ContentType) -> None | ErrorHandler:
        if not self._assigned:
            if isinstance(value, self.__class__):
                self._data = (self + value)._data

            else:
                self._data = (value,)

            self._assigned = True

        return ImmutableDataReassignmentError()

    def get(self, *_args: Any) -> ContentType | None:
        return self._data[0]

    def __getitem__(self, item: int | Any) -> ContentType:
        return self._data[0]

    def __add__(self, other: Any) -> Any:
        if isinstance(other, self.__class__):
            return self

        raise ValueError()

    def __radd__(self, other: Any) -> Any:
        if isinstance(other, self.__class__):
            return self

        raise ValueError()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value

        return False


class MutableContainer(Container):
    """
    Mutable data container class. Must contain a single element.
    """

    _data: tuple[ContentType] | tuple
    _type = ContainerType.MUTABLE

    def __init__(self):
        self._data = ()

    def add(self, value: ContentType) -> None:
        if isinstance(value, self.__class__):
            self._data = (self + value)._data

        else:
            self._data = (value,)

    def get(self, *_args: Any) -> ContentType | None:
        return self._data[0]

    def __getitem__(self, item: int | Any) -> ContentType:
        return self._data[0]

    def __add__(self, other: Any) -> Any:
        if isinstance(other, self.__class__):
            return other

        raise ValueError()

    def __radd__(self, other: Any) -> Any:
        if isinstance(other, self.__class__):
            return self

        raise ValueError()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value

        return False


class ArrayContainer(Container):
    """
    Array data container class. Can contain multiple elements.
    """

    _data: tuple[ContentType] | tuple
    _type = ContainerType.ARRAY

    def __init__(self):
        self._data = ()

    def add(self, value: ContentType) -> None:
        if isinstance(value, self.__class__):
            self._data = (self + value)._data

        else:
            self._data += (value,)

    def get(self, value: Any) -> ContentType | tuple[ContentType]:
        if value:
            return self._data[value]

        return self._data

    def __getitem__(self, item: int | Any) -> ContentType:
        return self._data[item]

    def __add__(self, other: Any) -> Any:
        if isinstance(other, self.__class__):
            for k in other:
                self.add(k)

            return self

        raise ValueError()

    def __radd__(self, other: Any) -> Any:
        if isinstance(other, self.__class__):
            for k in self:
                other.add(k)

            return other

        raise ValueError()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value

        return False


class LazySequenceContainer(Container):
    """
    Appendable lazy sequence, to be used on appendable data kind, such as quantum data.
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

    It is a lazy sequence due to its nature to accumulate instructions and to be
    consumed iterated over, which is the desirable behavior for a quantum data
    storage.

    Note: this object is not hashable.
    """

    # use Queue in the future for threading/asynchronous queueing
    _data: deque[ContentType]
    _type = ContainerType.LAZY

    def __init__(self):
        self._data = deque()

    def add(self, value: ContentType) -> None:
        if isinstance(value, self.__class__):
            self._data.extend(value._data)
            return None

        if isinstance(value, deque):
            self._data.extend(value)
            return None

        self._data.append(value)
        return None

    def get(self, value: Any) -> deque[ContentType] | ContentType:
        if value:
            return self._data[value]

        return self._data

    def __getitem__(self, item: int | Any) -> ContentType | deque[ContentType]:
        if isinstance(item, int):
            return self._data[item]

        raise ValueError()

    def __add__(self, other: Any) -> Any:
        if isinstance(other, self.__class__):
            for k in other:
                self.add(k)

            return self

        raise ValueError()

    def __radd__(self, other: Any) -> Any:
        return other + self

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return all(p == q for p, q in zip(self.value, other.value))

        return False


class VarHeader:
    """
    To hold relevant and unique information regarding a data container
    (variable, temporary data, etc.). Each data header must have a name,
    a type and an uid value (for scope purposes).
    """

    _name: Symbol
    _type: Symbol | CompositeSymbol
    _is_quantum: bool
    _uid: int
    _hash_value: int
    __slots__ = ("_name", "_type", "_is_quantum", "_uid", "_hash_value")

    def __init__(
        self,
        var_name: Symbol,
        var_type: Symbol | CompositeSymbol,
        uid: int | None = None,
    ):
        if has_same_paradigm(var_name, var_type):
            self._name = var_name
            self._type = var_type
            self._is_quantum = isquantum(var_name)
            if uid:
                self._uid = uid

            else:
                from random import randint

                self._uid = randint(2, 2 << 32)

            self._hash_value = hash(
                (
                    var_name,
                    var_type,
                )
            )

    @property
    def name(self) -> Symbol:
        return self._name

    @property
    def type(self) -> Symbol | CompositeSymbol:
        return self._type

    @property
    def is_quantum(self) -> bool:
        return self._is_quantum

    @property
    def uid(self) -> int:
        return self._uid

    def __hash__(self) -> int:
        return self._hash_value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return hash(self) == hash(other)

        return False
