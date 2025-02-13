from __future__ import annotations

from typing import Any, TypeVar
from hhat_lang.core.type_system.base import BaseDataType
from hhat_lang.core.type_system.utils import BuiltinNamespace, DataTypesEnum, FullName

T = TypeVar("T")
ANY_TYPE_NAME = FullName(BuiltinNamespace(), "=any=")
ANY_Q__TYPE_NAME = FullName(BuiltinNamespace(), "=q__any=")


class ArgsWildCard:
    """
    Class to represent any possible input argument. It is useful for functions
    like `print` that may take any type of argument.
    """
    pass


class AnySingleType(BaseDataType[Any]):
    """
    Class to represent any possible type. It is useful for functions that may
    accept any type as input, like `print`.
    """
    def __init__(self):
        super().__init__(
            name=ANY_TYPE_NAME,
            datatype=DataTypesEnum.SINGLE,
            is_composite=False
        )
        self._is_special_type = True

    def add_member(self, new_member: Any) -> Any:
        self._data[self._name] = new_member


class AnySingleQType(BaseDataType[Any]):
    """
    Class to represent any possible quantum type. It is useful for functions that
    may accept any type as input, like `print`.
    """

    def __init__(self):
        super().__init__(
            name=ANY_TYPE_NAME,
            datatype=DataTypesEnum.SINGLE,
            is_composite=False
        )
        self._is_special_type = True

    def add_member(self, new_member: Any) -> Any:
        self._data[self._name] = new_member


any_type = AnySingleType().add_size(0)
any_q__type = AnySingleQType().add_qsize(0, 0)


def is_any_type(value: BaseDataType) -> bool:
    if value.is_special_type and value.name == ANY_TYPE_NAME:
        return True
    return False


def is_any_qtype(value: BaseDataType) -> bool:
    if value.is_special_type and value.name == ANY_Q__TYPE_NAME:
        return True
    return False
