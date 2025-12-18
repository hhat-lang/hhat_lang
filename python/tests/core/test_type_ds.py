from __future__ import annotations

from collections import OrderedDict

from hhat_lang.core.data.core import CompositeSymbol, Literal, Symbol
from hhat_lang.core.error_handlers.errors import (
    TypeAndMemberNoMatchError,
    TypeQuantumOnClassicalError,
    VariableWrongMemberError,
)
from hhat_lang.core.types.builtin_types import QU3, U32, U64
from hhat_lang.core.types.core import EnumTypeDef, SingleTypeDef, StructTypeDef
from hhat_lang.core.types.utils import BaseTypeEnum

# TODO: refactor the types to use `BuiltinSingleDS` or respective data
#  types so properties can be compared and addressed properly.


def test_single_ds() -> None:
    lit_108 = Literal("108", Symbol("u32"))

    user_type1 = SingleTypeDef(name=Symbol("user_type1"))
    user_type1.add_member(U32)
    var1 = user_type1(var_name=Symbol("var1"))
    var1.assign(lit_108)

    assert var1.name == Symbol("var1")
    assert var1.type == Symbol("user_type1")
    assert var1.data == OrderedDict({U32.name: lit_108})
    assert var1.get() == lit_108
    assert var1.is_quantum is False

    assert isinstance(var1.get(Symbol("x")), VariableWrongMemberError)


def test_single_ds_quantum() -> None:
    lit_q2 = Literal("@2", Symbol("@u3"))

    # type @type1:@u3
    qtype1 = SingleTypeDef(name=Symbol("@type1"))
    qtype1.add_member(QU3)

    # @var1:@type1
    qvar1 = qtype1(var_name=Symbol("@var1"))
    # @var1 = @2:@u3
    qvar1.assign(lit_q2)

    assert qvar1.name == Symbol("@var1")
    assert qvar1.type == Symbol("@type1")
    assert qvar1.is_quantum
    assert qvar1.data == OrderedDict({QU3.name: [lit_q2]})
    assert qvar1.get() == [lit_q2]
    assert qvar1.is_quantum is True

    assert isinstance(qvar1.get(Symbol("x")), VariableWrongMemberError)


def test_single_ds_quantum_wrong() -> None:
    type1 = SingleTypeDef(name=Symbol("type1"))
    assert isinstance(type1.add_member(QU3), TypeQuantumOnClassicalError)


def test_struct_ds() -> None:
    lit_25 = Literal("25", "u32")
    lit_17 = Literal("17", "u32")

    point = StructTypeDef(name=Symbol("point"))
    point.add_member(U32, Symbol("x")).add_member(U32, Symbol("y"))
    p = point(var_name=Symbol("p"))
    p.assign(x=lit_25, y=lit_17)

    assert p.name == Symbol("p")
    assert p.type == Symbol("point")
    assert p.data == OrderedDict({Symbol("x"): lit_25, Symbol("y"): lit_17})
    assert p.get(Symbol("x")) == lit_25 and p.get(Symbol("y")) == lit_17
    assert p.is_quantum is False

    assert isinstance(p.get("z"), VariableWrongMemberError)


def test_struct_ds_quantum() -> None:
    lit_8 = Literal("8", "u32")
    lit_q2 = Literal("@2", "@u3")

    # type @sample {counts:u32 @d:@u3}
    qsample = StructTypeDef(name=Symbol("@sample"))
    (qsample.add_member(U32, Symbol("counts")).add_member(QU3, Symbol("@d")))

    # @var:@sample
    qvar = qsample(var_name=Symbol("@var"))
    # @var.{8 @2:@u3}
    qvar.assign(lit_8, lit_q2)

    assert qvar.name == Symbol("@var")
    assert qvar.type == Symbol("@sample")
    assert qvar._ds_type == BaseTypeEnum.STRUCT
    assert qvar.is_quantum is True
    assert qvar.data == OrderedDict({Symbol("counts"): lit_8, Symbol("@d"): [lit_q2]})
    assert qvar.get(Symbol("counts")) == lit_8 and qvar.get(Symbol("@d")) == [lit_q2]

    # @var2:@sample
    qvar2 = qsample(var_name=Symbol("@var2"))
    # @var2.{counts=8 @d=@2:@u3}
    qvar2.assign(counts=lit_8, q__d=lit_q2)

    assert qvar2.name == Symbol("@var2")
    assert qvar2.type == Symbol("@sample")
    assert qvar2.is_quantum is True
    assert qvar2.data == OrderedDict({Symbol("counts"): lit_8, Symbol("@d"): [lit_q2]})
    assert qvar2.get(Symbol("counts")) == lit_8 and qvar2.get(Symbol("@d")) == [lit_q2]


def test_struct_ds_quantum_wrong() -> None:
    qtype = StructTypeDef(name=Symbol("@type"))
    assert isinstance(qtype.add_member(QU3, Symbol("data")), TypeAndMemberNoMatchError)


def test_enum_ds() -> None:
    connect_enum = CompositeSymbol(("command", "CONNECT"))
    _connect = Symbol("CONNECT")
    _join = Symbol("JOIN")
    _quit = Symbol("QUIT")

    # type command {CONNECT JOIN QUIT}
    command = EnumTypeDef(name=Symbol("command"))
    command.add_member(_connect).add_member(_join).add_member(_quit)

    # opt:command
    opt = command(var_name=Symbol("opt"))
    # opt=command.CONNECT
    opt.assign(connect_enum)

    assert opt.name == Symbol("opt")
    assert opt.type == Symbol("command")
    assert opt._ds_type is BaseTypeEnum.ENUM
    assert opt.data == OrderedDict({0: _connect})
    assert opt.get() == _connect
    assert opt.get("z") == _connect
    assert opt.is_quantum is False


def test_enum_ds_with_struct() -> None:
    _none = Symbol("NONE")
    _res = StructTypeDef(name=Symbol("RESULT")).add_member(U64, Symbol("result"))

    # type option {NONE RESULT{result:u64}}
    option = EnumTypeDef(name=Symbol("option"))
    option.add_member(_none).add_member(_res)

    # var:option
    var = option(var_name=Symbol("var"))

    res_val = _res(var_name=_res.name).assign(Literal("16", "u64"))
    # var=option.RESULT.{16:u64}
    var.assign(res_val)

    assert var.name == Symbol("var")
    assert var.type == Symbol("option")
    assert var._ds_type is BaseTypeEnum.ENUM
    assert var.data == OrderedDict({0: res_val})
    assert var.get() == res_val
    assert var.get("z") == res_val
    assert var.is_quantum is False
