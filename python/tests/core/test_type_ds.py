from __future__ import annotations

from collections import OrderedDict

from hhat_lang.core.data.core import Literal
from hhat_lang.core.error_handlers.errors import VariableWrongMemberError
from hhat_lang.core.types.core import SingleDS, StructDS


def test_single_ds() -> None:
    user_type1 = SingleDS(name="user_type1")
    user_type1.add_member("u32")
    lit_108 = Literal("108", "u32")
    var1 = user_type1(lit_108, var_name="var1")

    assert var1.name == "var1"
    assert var1.type == "user_type1"
    assert var1.data == OrderedDict({"u32": lit_108})
    assert var1.get() == lit_108

    assert isinstance(var1.get("x"), VariableWrongMemberError)


def test_single_ds_quantum() -> None:
    qtype1 = SingleDS(name="@type1")
    qtype1.add_member("@u3")
    lit_q2 = Literal("@2", "@u3")
    qvar1 = qtype1(lit_q2, var_name="@var1")

    assert qvar1.name == "@var1"
    assert qvar1.type == "@type1"
    assert qvar1.is_quantum
    assert qvar1.data == OrderedDict({"@u3": lit_q2})
    assert qvar1.get() == lit_q2

    assert isinstance(qvar1.get("x"), VariableWrongMemberError)


def test_struct_ds() -> None:
    point = StructDS(name="point")
    point.add_member("u32", "x").add_member("u32", "y")
    lit_25 = Literal("25", "u32")
    lit_17 = Literal("17", "u32")
    p = point(lit_25, lit_17, var_name="p")

    assert p.name == "p"
    assert p.type == "point"
    assert p.data == OrderedDict({"x": lit_25, "y": lit_17})
    assert p.get("x") == lit_25 and p.get("y") == lit_17

    assert isinstance(p.get("z"), VariableWrongMemberError)
