from __future__ import annotations

from functools import wraps
from pathlib import Path
from sys import getsizeof
from typing import Any, Callable

from hhat_lang.core.data.core import AsArray, CompositeSymbol, Symbol
from hhat_lang.core.data.utils import isquantum
from hhat_lang.core.types import BUILTIN_STD_TYPE_MODULE_PATH
from hhat_lang.core.types.new_base_type import QSize, Size, TypeDef
from hhat_lang.core.types.utils import BaseTypeEnum

builtin_types: dict[Path, dict[Symbol | CompositeSymbol, TypeDef]] = dict()
"""
Built-in types path dictionary. Contains all the built-in types as values (its 
name as key and its content as value) for a given path as key.
"""


def insert_builtin_type(name: Symbol, type_path: Path) -> Callable:
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper() -> TypeDef:
            return fn()

        if type_path in builtin_types:
            builtin_types[type_path][name] = wrapper()

        else:
            builtin_types[type_path] = {name: wrapper()}

        return wrapper

    return decorator


class CoreTypeDef(TypeDef):
    _members: tuple[Symbol]
    _type = BaseTypeEnum.CORE
    _is_core = True

    def __init__(self, name: Symbol):
        super().__init__(name)
        self._members = (name,)
        self._is_quantum = isquantum(name)
        self._hash_value = hash((name, self._type))

    def add_member(self, *args: Any, **kwargs: Any) -> CoreTypeDef:
        return self

    def get_member(self, member: None = None) -> Symbol:
        return self._name

    def __len__(self) -> int:
        return 1

    def __repr__(self) -> str:
        return f"{self._name}"


@insert_builtin_type(name=Symbol("bool"), type_path=BUILTIN_STD_TYPE_MODULE_PATH)
def builtin_bool_t():
    _t = CoreTypeDef(Symbol("bool"))
    _t.set_sizes(Size(getsizeof(_t.members)))
    return _t


@insert_builtin_type(name=Symbol("u32"), type_path=BUILTIN_STD_TYPE_MODULE_PATH)
def builtin_u32_t():
    _t = CoreTypeDef(Symbol("u32"))
    _t.set_sizes(Size(getsizeof(_t.members)))
    return _t


@insert_builtin_type(name=Symbol("i32"), type_path=BUILTIN_STD_TYPE_MODULE_PATH)
def builtin_i32_t():
    _t = CoreTypeDef(Symbol("i32"))
    _t.set_sizes(Size(getsizeof(_t.members)))
    return _t


@insert_builtin_type(name=Symbol("f32"), type_path=BUILTIN_STD_TYPE_MODULE_PATH)
def builtin_f32_t():
    _t = CoreTypeDef(Symbol("f32"))
    _t.set_sizes(Size(getsizeof(_t.members)))
    return _t


@insert_builtin_type(name=Symbol("u64"), type_path=BUILTIN_STD_TYPE_MODULE_PATH)
def builtin_u64_t():
    _t = CoreTypeDef(Symbol("u64"))
    _t.set_sizes(Size(getsizeof(_t.members)))
    return _t


@insert_builtin_type(name=Symbol("i64"), type_path=BUILTIN_STD_TYPE_MODULE_PATH)
def builtin_i64_t():
    _t = CoreTypeDef(Symbol("i64"))
    _t.set_sizes(Size(getsizeof(_t.members)))
    return _t


@insert_builtin_type(name=Symbol("f64"), type_path=BUILTIN_STD_TYPE_MODULE_PATH)
def builtin_f64_t():
    _t = CoreTypeDef(Symbol("f64"))
    _t.set_sizes(Size(getsizeof(_t.members)))
    return _t


@insert_builtin_type(name=Symbol("str"), type_path=BUILTIN_STD_TYPE_MODULE_PATH)
def builtin_str_t():
    """Built-in type for string. Size of 64 for pointer on 64-bit systems"""
    _t = CoreTypeDef(Symbol("str"))
    _t.set_sizes(Size(getsizeof(_t)))
    return _t


@insert_builtin_type(name=Symbol("@bool"), type_path=BUILTIN_STD_TYPE_MODULE_PATH)
def builtin_qbool_t():
    _t = CoreTypeDef(Symbol("@bool"))
    _t.set_sizes(Size(getsizeof(_t)), QSize(1, 1))
    return _t


@insert_builtin_type(name=Symbol("@u2"), type_path=BUILTIN_STD_TYPE_MODULE_PATH)
def builtin_qu2_t():
    _t = CoreTypeDef(Symbol("@u2"))
    _t.set_sizes(Size(getsizeof(_t)), QSize(2, 2))
    return _t


@insert_builtin_type(name=Symbol("@u3"), type_path=BUILTIN_STD_TYPE_MODULE_PATH)
def builtin_qu3_t():
    _t = CoreTypeDef(Symbol("@u3"))
    _t.set_sizes(Size(getsizeof(_t)), QSize(3, 3))
    return _t


@insert_builtin_type(name=Symbol("@u4"), type_path=BUILTIN_STD_TYPE_MODULE_PATH)
def builtin_qu4_t():
    _t = CoreTypeDef(Symbol("@u4"))
    _t.set_sizes(Size(getsizeof(_t)), QSize(4, 4))
    return _t
