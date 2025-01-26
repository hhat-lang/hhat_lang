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
    _supported_members = (DataTypesEnum.SINGLE,)

    def add_member(self, new_member: SingleBaseMember) -> None:
        if isinstance(new_member, SingleBaseMember):
            if new_member.type in self.supported_members:
                self._data[self.name] = new_member
            else:
                raise ValueError(f"SingleType only accepts {self.supported_members}")
        else:
            raise ValueError(
                f"SingleType accepts only SingleBaseMember, got {type(new_member)}"
            )

    def __repr__(self) -> str:
        return f"{self.name}:{self._data[self.name]}"


class StructType(BaseDataType[TypedMember]):
    _type = DataTypesEnum.STRUCT
    _supported_members = (DataTypesEnum.TYPED_MEMBER,)

    def add_member(self, new_member: TypedMember) -> None:
        if isinstance(new_member, TypedMember):
            if new_member.type in self.supported_members:
                self._data[new_member.name] = new_member
            else:
                raise ValueError(f"StructType only supports {self.supported_members}")
        else:
            raise ValueError(f"{new_member} must be a typed member")


class UnionType(BaseDataType[TypedMember]):
    _type = DataTypesEnum.UNION
    _supported_members = (DataTypesEnum.TYPED_MEMBER,)

    def add_member(self, new_member: TypedMember) -> None:
        if isinstance(new_member, TypedMember):
            if new_member.type in self.supported_members:
                self._data[new_member.name] = new_member
            else:
                raise ValueError(f"UnionType only supports {self.supported_members}")
        else:
            raise ValueError(f"{new_member} must be a typed member")


class EnumType(BaseDataType):
    _type = DataTypesEnum.ENUM
    _supported_members = (
        DataTypesEnum.STRUCT,
        DataTypesEnum.MEMBER,
        DataTypesEnum.UNION,
    )

    def add_member(self, new_member: BaseMember | BaseDataType) -> None:
        if isinstance(new_member, (BaseMember, BaseDataType)):
            if new_member.type in self.supported_members:
                self._data[new_member.name] = new_member
            else:
                raise ValueError(f"EnumType only supports {self.supported_members}")
        else:
            raise ValueError(f"{new_member} must be a base member")


class GenericTypedMember(TypedMember):
    # TODO: implement it
    pass


class GenericSingleType(SingleType):
    # TODO: implement it
    pass


class GenericStructType(StructType):
    # TODO: implement it
    pass


class GenericEnumType(EnumType):
    # TODO: implement it
    pass
