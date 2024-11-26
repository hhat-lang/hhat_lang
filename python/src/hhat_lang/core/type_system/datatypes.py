from __future__ import annotations

from hhat_lang.core.type_system import DataTypesEnum, FullName
from hhat_lang.core.type_system.base import BaseDataType, BaseMember, SingleBaseMember


class MemberType:
    _name: str

    def __init__(self, name: str):
        self._name = name


class TypedMember(BaseMember):
    def __init__(self, name: str, member_type: FullName, datatype: DataTypesEnum):
        super().__init__(name=name, member_datatype=datatype, member_type=member_type)


class SingleType(BaseDataType[SingleBaseMember]):
    _type = DataTypesEnum.SINGLE

    def add_member(self, new_member: SingleBaseMember) -> None:
        self._data[self.name] = new_member

    def __repr__(self) -> str:
        return f"{self.name}:{self._data[self.name]}"


class StructType(BaseDataType[TypedMember]):
    _type = DataTypesEnum.STRUCT

    def add_member(self, new_member: TypedMember) -> None:
        if isinstance(new_member, TypedMember):
            self._data[new_member.name] = new_member
        else:
            raise ValueError(f"{new_member} must be a typed member")


class UnionType(BaseDataType[TypedMember]):
    _type = DataTypesEnum.UNION

    def add_member(self, new_member: TypedMember) -> None:
        if isinstance(new_member, TypedMember):
            self._data[new_member.name] = new_member
        else:
            raise ValueError(f"{new_member} must be a typed member")


class EnumType(BaseDataType[BaseMember]):
    _type = DataTypesEnum.ENUM

    def add_member(self, new_member: BaseMember) -> None:
        self._data[new_member.name] = new_member
