from __future__ import annotations

from abc import ABC
from collections import OrderedDict
from typing import Generic, TypeVar

from hhat_lang.core.type_system.utils import FullName, QSize, Size

MemberType = TypeVar("MemberType")
ContainerType = TypeVar("ContainerType")


class BaseDataType(ABC, Generic[MemberType]):
    _size: Size
    _qsize: QSize
    _name: FullName
    _data: MemberType

    @property
    def size(self) -> Size:
        return self._size

    @property
    def qsize(self) -> QSize:
        return self._qsize

    @property
    def name(self) -> FullName:
        return self._name


class DataTypeContainer(Generic[ContainerType]):
    _data: OrderedDict[FullName, ContainerType]

    def __init__(self):
        self._data = OrderedDict()


class TypedMember:
    pass


class StructType(BaseDataType[TypedMember]):
    _data: TypedMember

    def __init__(self, name: FullName):
        self._size = Size()
        self._qsize = QSize()
        self._name = name
        self._data = TypedMember()
