"""
The core built-in types should be defined here, such as:
- simple literals
    - boolean
    - unsigned integer 8 (u8)
    - char (char)
    - unsigned integer 32 (u32)
    - unsigned integer 64 (64)
    - quantum boolean (@bool)
    - quantum unsigned integer 2 (@u2)
    - quantum unsigned integer 3 (@u3)
    - quantum unsigned integer 4 (@u4)
    - quantum char (@char) TODO
    - quantum array (@array) TODO
- composite literals
    - string (str) TODO: see how to handle data size
    - array (array) TODO
    - hashmap (hashmap) TODO
"""

from __future__ import annotations

from hhat_lang.core.type_system import DataTypesEnum
from hhat_lang.core.type_system.base import (
    SingleBuiltinType,
    SingleBaseMember,
)
from hhat_lang.core.type_system.utils import BuiltinNamespace, FullName


null_type = (
    SingleBuiltinType("null")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "null"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_size(0)
)

u8_type = (
    SingleBuiltinType("u8")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "u8"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_size(8)
)

bool_type =  (
    SingleBuiltinType("bool")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "bool"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_size(8)
)

char_type = (
    SingleBuiltinType("char")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "char"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_size(8)
)

u16_type =(
    SingleBuiltinType("u16")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "u16"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_size(16)
)

u32_type = (
    SingleBuiltinType("u32")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "u32"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_size(32)
)

u64_type = (
    SingleBuiltinType("u64")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "u64"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_size(64)
)

str_type = (
    SingleBuiltinType("str")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "str"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
)

q__bool_type = (
    SingleBuiltinType("@bool")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "@bool"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_qsize(1, 1)
)

q__u2_type = (
    SingleBuiltinType("@u2")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "@u2"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_qsize(2, 2)
)

q__u3_type = (
    SingleBuiltinType("@u3")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "@u3"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_qsize(3, 3)
)

q__u4_type = (
    SingleBuiltinType("@u4")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "@u4"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_qsize(4, 4)
)


datatypes_dict = {

    "null": null_type,

    "u8": u8_type,

    "bool": bool_type,

    "char": char_type,

    "u16": u16_type,

    "u32": u32_type,

    "u64": u64_type,

    "str": str_type,

    "@bool": q__bool_type,

    "@u2": q__u2_type,

    "@u3": q__u3_type,

    "@u4": q__u4_type,

}


uint_types = ("u16", "u32", "u64")
sint_types = ("i16", "i32", "i64")
q__uint_types = ("@u2", "@u3", "@u4")
