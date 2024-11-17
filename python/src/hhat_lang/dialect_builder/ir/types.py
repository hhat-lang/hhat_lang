"""
Datatypes logic and structure
"""

from __future__ import annotations

from abc import ABC
from typing import Any, Iterable
from collections import OrderedDict

from hhat_lang.core import DataParadigm
from hhat_lang.core.constructors import DataTypesEnum, FullName, QSize
from hhat_lang.core.index import QuantumIndexManager
from hhat_lang.dialect_builder.ir.result_handler import Result, ResultType


class BaseSingleMember(ABC):
    _name: str
    _type: FullName
    _paradigm: DataParadigm
    _qsize: QSize

    def __init__(
        self,
        member_name: str,
        member_type: FullName,
        type_ref_manager: QuantumIndexManager
    ):
        self._name = member_name
        self._type = member_type
        self._qsize = type_ref_manager()

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> FullName:
        return self._type

    @property
    def paradigm(self) -> DataParadigm:
        return self._paradigm

    def __repr__(self) -> str:
        return f"{self.name}:{self.type}"


class ClassicalSingleMember(BaseSingleMember):
    def __init__(self, member_name: str, member_type: FullName):
        self._paradigm = DataParadigm.CLASSICAL
        super().__init__(member_name, member_type)


class QuantumSingleMember(BaseSingleMember):
    def __init__(self, member_name: str, member_type: FullName):
        self._paradigm = DataParadigm.QUANTUM
        super().__init__(member_name, member_type)



class DataTypeStructure(ABC):
    pass


class StructDataType(DataTypeStructure):
    def __init__(self, full_name: FullName):
        self._full_name: FullName = full_name
        self._data: OrderedDict = OrderedDict()

    @property
    def full_name(self) -> FullName:
        return self._full_name

    def members(self) -> Any:
        return self._data

    def add_member(self, member: BaseSingleMember) -> StructDataType:
        if isinstance(member, BaseSingleMember):
            self._data[member.name] = member
            return self
        raise ValueError(f"member {member} is not a valid member for struct datatype")

    def get(self, member_name: str | None) -> Any:
        return self._data[member_name]

    def get_type(self, member_name: str | None) -> FullName:
        return self._data[member_name].type


class EnumDataType(DataTypeStructure):
    pass


class UnionDataType(DataTypeStructure):
    pass


class DataType:
    def __init__(self, datatype: DataTypesEnum, full_name: FullName):
        self._datatype: DataTypesEnum = datatype
        self._full_name: FullName = full_name
        self._data: OrderedDict = OrderedDict()

    @property
    def full_name(self) -> FullName:
        return self._full_name

    def _set_body(self) -> Any:
        match self._datatype:
            case DataTypesEnum.STRUCT:
                pass
            case DataTypesEnum.ENUM:
                pass
            case DataTypesEnum.UNION:
                pass
            case DataTypesEnum.MEMBER:
                pass

    def add_member(self, member: Any) -> Any:
        pass


class Type:
    def __init__(self, datatype: DataTypesEnum, namespace: str, name: str):
        self.type: DataTypesEnum = datatype
        self._namespace: str = namespace
        self._name: str = name

    @property
    def namespace(self):
        return self._namespace

    @property
    def name(self):
        return self._name

    @property
    def full_name_tuple(self):
        return self.namespace, self.name


class TypeBody:
    def __init__(self):
        self._data: TypeBodyData = OrderedDict()

    def add(self, member: Type | ClassicalSingleMember) -> Result:
        if member.full_name_tuple not in self._data:
            self._data[member.full_name_tuple] = member
            result = Result(ResultType.OK)
        else:
            result = Result(ResultType.ERROR)
        return result(member.full_name_tuple)

    @property
    def data(self) -> TypeBodyData:
        return self._data

    def __getitem__(self, item: tuple[str, str]) -> Result:
        data = self._data.get(item, False)
        if data:
            return Result(ResultType.OK)(data)
        return Result(ResultType.ERROR)(item)

    def __iter__(self) -> Iterable:
        yield from self._data.values()


TypeBodyData = OrderedDict[tuple[str, str], Type | ClassicalSingleMember]
