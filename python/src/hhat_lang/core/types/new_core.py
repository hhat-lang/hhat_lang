from __future__ import annotations

from typing import Any, Iterable

from hhat_lang.core.data.core import AsArray, CompositeSymbol, Symbol, SymbolObj
from hhat_lang.core.error_handlers.errors import (
    ErrorHandler,
    TypeInvalidMemberError,
    TypeMemberAlreadyExistsError,
    TypeMemberEmptyError,
    TypeMemberOverflowError,
    sys_exit,
)
from hhat_lang.core.types.new_base_type import TypeDef, TypeMembers
from hhat_lang.core.types.utils import BaseTypeEnum
from hhat_lang.core.utils import HatOrderedDict

##############
# SINGLE DEF #
##############

SingleM = Symbol | CompositeSymbol | AsArray | TypeDef


class SingleTypeDef(TypeDef[None, SingleM]):
    _members: SingleTypeMember
    _type = BaseTypeEnum.SINGLE

    def __init__(self, name: Symbol):
        super().__init__(name)
        self._members = SingleTypeMember()
        self._defined = False

    def add_member(self, member_type: SingleM) -> SingleTypeDef:
        if not self._defined:
            self._members += member_type
            match res := self._members:
                case TypeMemberOverflowError() | TypeInvalidMemberError():
                    sys_exit(self.name, member_type, error_fn=res)

                case ErrorHandler():
                    sys_exit(self.name, error_fn=res)

                case _:
                    self._hash_value = hash((self._name, self._type, member_type))
                    self._defined = True
                    return self

        sys_exit(self.name, member_type, error_fn=TypeMemberOverflowError())

    def get_member(self, member: None = None) -> SingleM:
        match res := self._members[member]:
            case TypeMemberEmptyError():
                sys_exit(self._name, error_fn=res)

            case ErrorHandler():
                sys_exit(self._name, error_fn=res)

            case _:
                return res

    def __repr__(self) -> str:
        return f"{self._name}<single>{self._members}"


class SingleTypeMember(TypeMembers[None, SingleM]):
    _content: SingleM | None

    def __init__(self):
        self._content = None
        self._is_leaf = False
        self._hash_value = None

    def set_hash(self) -> None:
        self._hash_value = hash(self._content)

    def __iadd__(self, other: SingleM) -> TypeMembers[None, SingleM] | ErrorHandler:
        if self._content is None:
            if isinstance(other, SingleM):
                self._content = other
                self.set_hash()
                return self

            return TypeInvalidMemberError()

        return TypeMemberOverflowError()

    def __getitem__(self, item: Any) -> SingleM | ErrorHandler:
        if self._content is not None:
            return self._content

        return TypeMemberEmptyError()

    def __iter__(self) -> Iterable:
        return iter((self._content,))

    def __len__(self) -> int:
        return 1

    def __repr__(self) -> str:
        return f"{self._content}"


##############
# STRUCT DEF #
##############

StructT = SymbolObj | TypeDef
StructM = Symbol


class StructTypeDef(TypeDef[StructT, StructM]):
    _members_left: int
    _members: StructTypeMember
    _type = BaseTypeEnum.STRUCT

    def __init__(self, name: Symbol, num_members: int):
        super().__init__(name)
        self._members_left = num_members
        self._members = StructTypeMember()

    def add_member(self, member_name: StructM, member_type: StructT) -> StructTypeDef:
        if self._members_left > 0:
            self._members += (member_name, member_type)

            match res := self._members:
                case TypeMemberAlreadyExistsError():
                    sys_exit(self._name, member_name, error_fn=res)

                case _:
                    self._members_left -= 1
                    if self._members_left == 0:
                        self._members.set_hash()
                        self._hash_value = hash((self._name, self._type, self._members))

                    return self

        sys_exit(self._name, self._type, error_fn=TypeMemberOverflowError())

    def get_member(self, member: StructT) -> StructM:
        match res := self._members[member]:
            case TypeMemberEmptyError():
                sys_exit(self._name, error_fn=res)

            case ErrorHandler():
                sys_exit(error_fn=res)

            case _:
                return res

    def __repr__(self) -> str:
        return f"{self._name}<struct>{self._members}"


class StructTypeMember(TypeMembers[StructT, StructM]):
    _content: HatOrderedDict[Symbol, StructT]

    def __init__(self):
        self._content = HatOrderedDict()
        self._is_leaf = False

    def set_hash(self) -> None:
        self._hash_value = hash(tuple((k, v) for k, v in self._content.items()))

    def __iadd__(self, other: Any) -> StructTypeMember | ErrorHandler:
        if other[0] not in self._content:
            self._content[other[0]] = other[1]
            return self

        return TypeMemberAlreadyExistsError()

    def __getitem__(self, item: int | Symbol) -> StructT | tuple[StructM, StructT]:
        if isinstance(item, int):
            return tuple(self._content.items())[item]

        return self._content[item]

    def __iter__(self) -> Iterable:
        return iter(self._content.items())

    def __len__(self) -> int:
        return len(self._content)

    def __repr__(self) -> str:
        members = "{" + " ".join(f"{k}:{v}" for k, v in self) + "}"
        return members


############
# ENUM DEF #
############

EnumT = Symbol | StructTypeDef
EnumM = int | StructTypeDef


class EnumTypeDef(TypeDef[EnumT, EnumM]):
    _members_left: int
    _members: EnumTypeMember
    _counter: int
    _type = BaseTypeEnum.ENUM

    def __init__(self, name: Symbol, num_members: int):
        super().__init__(name)
        self._members_left = num_members
        self._members = EnumTypeMember()
        self._counter = 1 if num_members else 0
        self._hash_value = None

    def add_member(self, member: EnumT, **_kwargs: Any) -> EnumTypeDef:
        if self._members_left > 0:
            match member:
                case Symbol():
                    self._members += (member, self._counter)
                    match res := self._members:
                        case TypeMemberAlreadyExistsError():
                            sys_exit(self._name, member, error_fn=res)

                        case _:
                            self._counter *= 2
                            self._members_left -= 1
                            if self._members_left == 0:
                                self._members.set_hash()
                                self._hash_value = hash((self._name, self._type, self._members))

                            return self

                case StructTypeDef():
                    self._members += (member.name, member)
                    match res := self._members:
                        case TypeMemberAlreadyExistsError():
                            sys_exit(self._name, member.name, error_fn=res)

                        case _:
                            self._counter *= 2
                            self._members_left -= 1
                            if self._members_left == 0:
                                self._members.set_hash()
                                self._hash_value = hash((self._name, self._type, self._members))

                            return self

                case _:
                    sys_exit(self._name, member, error_fn=TypeInvalidMemberError())

        sys_exit(self._name, self._type, error_fn=TypeMemberOverflowError())

    def get_member(self, member: EnumT) -> EnumM:
        match res := self._members[member]:
            case TypeInvalidMemberError():
                sys_exit(self._name, member, error_fn=res)

            case ErrorHandler():
                sys_exit(error_fn=res)

            case _:
                return res

    def __repr__(self) -> str:
        return f"{self._name}<enum>{self._members}"


class EnumTypeMember(TypeMembers[EnumT, EnumM]):
    _content: HatOrderedDict[Symbol, int | StructTypeDef]

    def __init__(self):
        self._content = HatOrderedDict()
        self._is_leaf = False

    def set_hash(self) -> None:
        self._hash_value = hash(tuple((k, v) for k, v in self._content.items()))

    def __iadd__(self, other: tuple[EnumT, EnumM]) -> EnumTypeMember | ErrorHandler:
        if other[0] not in self._content:
            self._content[other[0]] = other[1]
            return self

        return TypeMemberAlreadyExistsError()

    def __getitem__(self, item: EnumT) -> EnumM | ErrorHandler:
        if isinstance(item, int):
            return tuple(self._content.items())[item]

        if isinstance(item, Symbol):
            return self._content[item]

        if isinstance(item, StructTypeDef):
            return self._content[item.name]

        return TypeInvalidMemberError()

    def __iter__(self) -> Iterable:
        return iter(self._content.items())

    def __len__(self) -> int:
        return len(self._content)

    def __repr__(self) -> str:
        members = (
            "{"
            + " ".join(str(k) if isinstance(v, int) else str(v) for k, v in self._content.items())
            + "}"
        )
        return members
