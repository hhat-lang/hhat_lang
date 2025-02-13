from __future__ import annotations

from abc import ABC, abstractmethod
from collections import OrderedDict
from enum import Enum, auto
from typing import Any, Generic, Iterator, TypeVar, Union, Iterable

from hhat_lang.core.type_system import DataTypesEnum, FullName, QSize, Size
from hhat_lang.core.type_system.utils import BuiltinNamespace
from hhat_lang.core.utils.result_handler import ResultType

T = TypeVar("T", bound="BaseMember")


class BaseDataType(ABC, Generic[T]):
    _name: FullName
    _data: DataTypeContainer[T]
    _type: DataTypesEnum
    _supported_members: tuple[DataTypesEnum, ...] = ()
    _size: Size
    _qsize: QSize
    _is_primitive: bool
    _is_composite: bool
    _composite_size: int | None
    _is_special_type: bool = False

    def __init__(
        self,
        name: FullName,
        datatype: DataTypesEnum,
        is_composite: bool = False,
    ):
        self._name: FullName = name
        self._type: DataTypesEnum = datatype
        self._data = DataTypeContainer(self._supported_members)
        self._size: Size = Size()
        self._qsize: QSize = QSize()
        self._is_primitive = False
        self._is_composite = is_composite
        self._composite_size = None

    @property
    def size(self) -> Size:
        return self._size

    @property
    def qsize(self) -> QSize:
        return self._qsize

    @property
    def name(self) -> FullName:
        return self._name

    @property
    def type(self) -> DataTypesEnum:
        return self._type

    @property
    def is_builtin(self) -> bool:
        return self._is_primitive

    @property
    def supported_members(self) -> tuple[DataTypesEnum, ...]:
        return self._supported_members

    @property
    def is_composite(self) -> bool:
        return self._is_composite

    @property
    def is_special_type(self) -> bool:
        return self._is_special_type

    def add_composite_size(self, size: int) -> Any:
        if self._composite_size is None:
            self._composite_size = size

    @abstractmethod
    def add_member(self, new_member: T) -> Any: ...

    def add_size(self, size: int) -> Any:
        match self._size.add_size(size):
            case ResultType.OK:
                pass
            case ResultType.ERROR:
                raise ValueError("size (alignment) for type definition must be integer")
        return self

    def add_qsize(self, min_index: int, max_index: int) -> Any:
        self._qsize.add_sizes(min_index, max_index)
        return self

    def __getitem__(self, item: Any) -> T:
        return self._data[item]

    def __iter__(self) -> Iterator:
        yield from self._data.items()

    def members(self) -> Iterator:
        yield from self._data.items()

    def __repr__(self) -> str:
        return f"{self.name}[{self._type.value}]" + "{" + str(self._data) + "}"


class GenericBaseDataType(BaseDataType[Generic[T]]):
    # TODO: implement it
    pass


class BaseMember(ABC):
    _name: str
    _member_type: FullName | None
    _datatype: DataTypesEnum

    def __init__(
        self,
        *,
        member_datatype: DataTypesEnum,
        name: str | None = None,
        member_type: FullName | None = None,
    ):
        if (
            (isinstance(name, str) or name is None)
            and (isinstance(member_type, FullName) or member_type is None)
            and isinstance(member_datatype, DataTypesEnum)
        ):
            self._name = name or ""
            self._member_type = member_type
            self._datatype = member_datatype
        else:
            raise ValueError(
                f"name must be str, member name must be FullName and"
                f" member type must be DataTypesEnum; got {type(name)},"
                f" {type(member_type)} and {type(member_datatype)} instead"
            )

    @property
    def name(self) -> str:
        return self._name

    @property
    def type_name(self) -> FullName | None:
        return self._member_type

    @property
    def type(self) -> DataTypesEnum:
        return self._datatype

    def __repr__(self) -> str:
        return f"{self.name}({self.type_name})"


class GenericBaseMember(BaseMember):
    # TODO: implement it
    pass


class SingleBaseMember(BaseMember):
    def __init__(self, member_type: FullName, member_datatype: DataTypesEnum):
        super().__init__(member_datatype=member_datatype, member_type=member_type)

    def __repr__(self) -> str:
        return f"{self.type_name}"


class DataTypeContainer(Generic[T]):
    _data: OrderedDict[Union[str, FullName], T]
    _type: tuple[DataTypesEnum]

    def __init__(self, member_type: DataTypesEnum | tuple[DataTypesEnum, ...]):
        is_valid_member: bool

        if isinstance(member_type, tuple):
            is_valid_member = all(self._check_member_type(k) for k in member_type)
        else:
            is_valid_member = self._check_member_type(member_type)
            member_type = (member_type,)

        self._data = OrderedDict()
        self._resolve_members_types(member=member_type, is_valid_member=is_valid_member)

    @classmethod
    def _check_member_type(cls, member_type: Any) -> bool:
        return isinstance(member_type, DataTypesEnum)

    def _resolve_members_types(self, member: Any, is_valid_member: bool) -> None:
        if is_valid_member:
            self._type = member
        else:
            raise ValueError(
                f"member types must be DataTypesEnum or a tuple of them, not {member}"
            )

    def _check_new_member(self, member: Any) -> bool:
        return member in self._type

    def _add(self, name: str | FullName, member: T) -> None:
        if self._check_new_member(member.type):
            self._data[name] = member
        else:
            raise ValueError(
                f"member {name} is not of a valid member type {self._type}"
            )

    def add(self, new_member: T) -> None:
        self._add(new_member.name, new_member)

    def __getitem__(self, item: str | FullName) -> T:
        return self._data[item]

    def __setitem__(self, key: str | FullName, value: T) -> None:
        self._add(key, value)

    def __iter__(self) -> Iterator:
        yield from self._data.items()

    def names(self) -> Iterator:
        yield from self._data.keys()

    def items(self) -> Iterator:
        yield from self._data.items()

    def __repr__(self) -> str:
        return " ".join(f"{v}" for k, v in self._data.items())


class SingleBuiltinType(BaseDataType[SingleBaseMember]):
    _supported_members: tuple[DataTypesEnum, ...] = (DataTypesEnum.SINGLE,)

    def __init__(
        self,
        name: str,
        is_composite: bool = False
    ):
        super().__init__(FullName(BuiltinNamespace(), name), DataTypesEnum.SINGLE, is_composite)
        self._is_primitive = True

    def add_member(self, new_member: SingleBaseMember) -> SingleBuiltinType:
        self._data[self._name] = new_member
        return self


class VariableContainerEnum(Enum):
    IMMUTABLE = auto()
    MUTABLE = auto()
    REPLACEABLE = auto()
    APPENDABLE = auto()


class BaseVariableContainer(ABC):
    """
    Abstract class to define the behavior of variable data inside memory heap.
    """

    assign_type: tuple[VariableContainerEnum, ...]
    _name: FullName
    _type: FullName
    _size: int | None
    _data: Any

    def __init__(self, name: FullName, var_type: FullName, size: int | None = None):
        self._name = name
        self._type = var_type
        self._size = size
        self._data = None

    @property
    def name(self) -> FullName:
        return self._name

    @property
    def type(self) -> FullName:
        return self._type

    @property
    def size(self) -> int | None:
        return self._size

    @abstractmethod
    def add(self, value: Any) -> None:
        pass

    def get(self) -> Any:
        return self._data

    def __iter__(self) -> Iterable[Any]:
        if isinstance(self._data, Iterable):
            yield from self._data
        else:
            yield from [self._data]


class Immutable(BaseVariableContainer):
    assign_type: tuple[VariableContainerEnum, ...] = VariableContainerEnum.IMMUTABLE,

    def add(self, value: Any) -> None:
        if value.type == self.type:
            if self._data is None:
                self._data = value
            else:
                raise ValueError("cannot change an immutable variable")
        else:
            raise ValueError("type error")


class Mutable(BaseVariableContainer):
    assign_type: tuple[VariableContainerEnum, ...] = VariableContainerEnum.MUTABLE,

    @abstractmethod
    def add(self, value: Any) -> None:
        ...


class Replaceable(Mutable):
    assign_type: VariableContainerEnum = (
        VariableContainerEnum.MUTABLE,
        VariableContainerEnum.REPLACEABLE
    )

    def add(self, value: Any) -> None:
        self._data = value


class Appendable(Mutable):
    assign_type: tuple[VariableContainerEnum, ...] = (
        VariableContainerEnum.MUTABLE,
        VariableContainerEnum.APPENDABLE
    )

    def add(self, value: Any) -> None:
        if self._data is None:
            self._data = (value,)
        else:
            self._data += (value,)
