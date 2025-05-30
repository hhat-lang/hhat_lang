from __future__ import annotations

from collections import OrderedDict

from hhat_lang.core.data.core import CoreLiteral, Symbol
from hhat_lang.core.error_handlers.errors import (
    TypeAndMemberNoMatchError,
    TypeQuantumOnClassicalError,
    VariableWrongMemberError,
)
from hhat_lang.core.types.builtin_types import QU3, U32
from hhat_lang.core.types.core import SingleDS, StructDS

# TODO: refactor the types to use `BuiltinSingleDS` or respective data
#  types so properties can be compared and addressed properly.


def test_single_ds() -> None:
    lit_108 = CoreLiteral("108", "u32")

    user_type1 = SingleDS(name=Symbol("user_type1"))
    user_type1.add_member(U32)
    var1 = user_type1(lit_108, var_name=Symbol("var1"))

    assert var1.name == Symbol("var1")
    assert var1.type == Symbol("user_type1")
    assert var1.data == OrderedDict({U32.name: lit_108})
    assert var1.get() == lit_108
    assert var1.is_quantum is False

    assert isinstance(var1.get(Symbol("x")), VariableWrongMemberError)


def test_single_ds_quantum() -> None:
    lit_q2 = CoreLiteral("@2", "@u3")

    qtype1 = SingleDS(name=Symbol("@type1"))
    qtype1.add_member(QU3)
    qvar1 = qtype1(lit_q2, var_name=Symbol("@var1"))

    assert qvar1.name == Symbol("@var1")
    assert qvar1.type == Symbol("@type1")
    assert qvar1.is_quantum
    assert qvar1.data == OrderedDict({QU3.name: [lit_q2]})
    assert qvar1.get() == [lit_q2]
    assert qvar1.is_quantum is True

    assert isinstance(qvar1.get(Symbol("x")), VariableWrongMemberError)


def test_single_ds_quantum_wrong() -> None:
    type1 = SingleDS(name=Symbol("type1"))
    assert isinstance(type1.add_member(QU3), TypeQuantumOnClassicalError)


def test_struct_ds() -> None:
    lit_25 = CoreLiteral("25", "u32")
    lit_17 = CoreLiteral("17", "u32")

    point = StructDS(name=Symbol("point"))
    point.add_member(U32, Symbol("x")).add_member(U32, Symbol("y"))
    p = point(lit_25, lit_17, var_name=Symbol("p"))

    assert p.name == Symbol("p")
    assert p.type == Symbol("point")
    assert p.data == OrderedDict({Symbol("x"): lit_25, Symbol("y"): lit_17})
    assert p.get(Symbol("x")) == lit_25 and p.get(Symbol("y")) == lit_17
    assert p.is_quantum is False

    assert isinstance(p.get("z"), VariableWrongMemberError)


def test_struct_ds_quantum() -> None:
    lit_8 = CoreLiteral("8", "u32")
    lit_q2 = CoreLiteral("@2", "@u3")

    qsample = StructDS(name=Symbol("@sample"))
    qsample.add_member(U32, Symbol("counts")).add_member(QU3, Symbol("@d"))
    qvar = qsample(lit_8, lit_q2, var_name=Symbol("@var"))

    assert qvar.name == Symbol("@var")
    assert qvar.type == Symbol("@sample")
    assert qvar.is_quantum is True
    assert qvar.data == OrderedDict({Symbol("counts"): lit_8, Symbol("@d"): [lit_q2]})
    assert qvar.get(Symbol("counts")) == lit_8 and qvar.get(Symbol("@d")) == [lit_q2]


def test_struct_ds_quantum_wrong() -> None:
    qtype = StructDS(name=Symbol("@type"))
    assert isinstance(qtype.add_member(QU3, Symbol("data")), TypeAndMemberNoMatchError)
