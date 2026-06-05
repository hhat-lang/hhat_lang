from __future__ import annotations

from hhat_lang.core.data.core import Literal, Symbol
from hhat_lang.core.types.new_builtin_core import builtin_types
from hhat_lang.core.types.new_core import SingleTypeDef

s_u32 = Symbol("u32")
u32 = builtin_types[s_u32]


def test_single() -> None:
    lit108 = Literal("108", s_u32)
    type1 = SingleTypeDef(Symbol("type1")).add_member(u32)
