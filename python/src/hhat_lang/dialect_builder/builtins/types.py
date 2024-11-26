from __future__ import annotations

from hhat_lang.core.type_system import DataTypesEnum
from hhat_lang.core.type_system.base import (
    BuiltinType,
    SingleBaseMember,
)
from hhat_lang.core.type_system.utils import BuiltinNamespace, FullName

U8: BuiltinType = (
    BuiltinType("u8")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "u8"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_size(8)
)


Bool: BuiltinType = (
    BuiltinType("bool")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "bool"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_size(8)
)


U32: BuiltinType = (
    BuiltinType("u32")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "u32"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_size(32)
)


U64: BuiltinType = (
    BuiltinType("u64")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "u64"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_size(64)
)


QBool: BuiltinType = (
    BuiltinType("@bool")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "@bool"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_qsize(1, 1)
)


QU2: BuiltinType = (
    BuiltinType("@u2")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "@u2"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_qsize(2, 2)
)


QU3: BuiltinType = (
    BuiltinType("@u3")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "@u3"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_qsize(3, 3)
)


QU4: BuiltinType = (
    BuiltinType("@u4")
    .add_member(
        SingleBaseMember(
            member_type=FullName(BuiltinNamespace(), "@u4"),
            member_datatype=DataTypesEnum.SINGLE,
        )
    )
    .add_qsize(4, 4)
)
