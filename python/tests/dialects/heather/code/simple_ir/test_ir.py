from __future__ import annotations

from hhat_lang.core.data.core import Symbol, CoreLiteral
from hhat_lang.dialects.heather.code.simple_ir_builder.ir import (
    IR,
    IRBlock,
    IRDeclare,
    IRAssign,
    IRArgs,
    IRCall,
    IRFlag,
)


def test_dac1() -> None:
    qq = Symbol("@q")
    q1 = CoreLiteral("@1", lit_type="@int")
    qu3 = Symbol("@u3")
    qredim = Symbol("@redim")
    sin = Symbol("sin")
    print_ = Symbol("print")
    l2_3f64 = CoreLiteral("2.3", lit_type="float")

    i1 = IRDeclare(var=qq, var_type=qu3)
    assert i1.instr == IRFlag.DECLARE
    assert i1.args == (qq, qu3)

    i2 = IRAssign(var=qq, value=q1)
    assert i2.instr == IRFlag.ASSIGN
    assert i2.args == (qq, q1)

    i3 = IRCall(caller=qredim, args=IRArgs(qq))
    i3_args_block_name = IRBlock(IRArgs(qq)).name
    assert i3.instr == IRFlag.CALL
    assert i3.args == (qredim, i3_args_block_name)

    block1 = IRBlock(i1, i2, i3)
    assert block1.instrs == (i1, i2, i3)

    i4 = IRCall(caller=sin, args=IRArgs(l2_3f64))
    i5 = IRCall(caller=print_, args=IRArgs(i4))
    block2 = IRBlock(i5)
    print(block2)

    ir1 = IR()
    ir1.add_block(block1)
    ir1.add_block(block2)
    assert block1.name in ir1.code_block
    assert ir1.code_block[block1.name] == block1

    print()
    print(ir1)
