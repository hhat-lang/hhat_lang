from __future__ import annotations

from hhat_lang.core.constructors import FullName, NameSpace
from hhat_lang.dialect_builder.ir.types import StructDataType, BaseSingleMember

Bool = StructDataType(FullName(NameSpace(), "bool"))
Bool.add_member(BaseSingleMember("value", FullName(NameSpace(), "bool")))

class U32(StructDataType):
    pass


class U64(StructDataType):
    pass


class I32(StructDataType):
    pass


class I64(StructDataType):
    pass

