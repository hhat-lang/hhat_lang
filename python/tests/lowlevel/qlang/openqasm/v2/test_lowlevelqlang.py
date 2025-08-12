from __future__ import annotations

import pytest
from hhat_lang.core.code.ir import TypeIR
from hhat_lang.core.data.core import CoreLiteral, Symbol
from hhat_lang.core.error_handlers.errors import InstrStatusError
from hhat_lang.core.memory.core import MemoryManager, Stack
from hhat_lang.core.utils import Ok
from hhat_lang.dialects.heather.code.simple_ir_builder.ir import (
    FnIR,
    IRArgs,
    IRBlock,
    IRCall,
)
from hhat_lang.dialects.heather.interpreter.classical.executor import Evaluator
from hhat_lang.low_level.quantum_lang.openqasm.v2.instructions import (
    QNez,
    QNot,
)
from hhat_lang.low_level.quantum_lang.openqasm.v2.qlang import LowLeveQLang


# FIXME: skipping whole file until LowLevelQLang is fixed with the new IR
pytest.skip(
    "skipping whole file until LowLeveLQLang is fixed with the new IR",
    allow_module_level=True,
)


def test_gen_program_single_empty_redim() -> None:
    code_snippet = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[1];
creg c[1];

h q[0];
measure q -> c;
"""

    qv = Symbol("@v")

    mem = MemoryManager(5)
    mem.idx.add(qv, 1)
    mem.idx.request(qv)

    ex = Evaluator(mem, TypeIR(), FnIR())

    block = IRBlock(IRCall(Symbol("@redim"), IRArgs()))

    qlang = LowLeveQLang(Symbol("@v"), block, mem.idx, ex, Stack(), SymbolTable())
    res = qlang.gen_program()

    assert res == code_snippet


def test_gen_program_single_q0_redim() -> None:
    code_snippet = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[3];

x q[0];
x q[2];
h q[0];
h q[1];
h q[2];
measure q -> c;
"""

    mem = MemoryManager(5)
    mem.idx.add(Symbol("@v"), 3)
    mem.idx.request(Symbol("@v"))

    ex = Evaluator(mem, TypeIR(), FnIR())

    block = IRBlock(
        IRCall(
            caller=Symbol("@redim"),
            args=IRArgs(CoreLiteral(Symbol("@5").value, "@u3")),
        )
    )

    qlang = LowLeveQLang(Symbol("@v"), block, mem.idx, ex, Stack(), SymbolTable())
    res = qlang.gen_program()
    print(res)
    assert res == code_snippet


def test_gen_program_single_bool_not() -> None:
    code_snippet = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[1];
creg c[1];

x q[0];
measure q -> c;
"""

    qv = Symbol("@v")

    mem = MemoryManager(5)
    mem.idx.add(qv, 1)
    mem.idx.request(qv)

    ex = Evaluator(mem, TypeIR(), FnIR())

    block = IRBlock(IRCall(Symbol("@not"), IRArgs()))

    qlang = LowLeveQLang(Symbol("@v"), block, mem.idx, ex, Stack(), SymbolTable())
    res = qlang.gen_program()

    assert res == code_snippet


def test_gen_program_single_u2_not() -> None:
    code_snippet = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];

x q[0];
x q[1];
measure q -> c;
"""

    qv = Symbol("@v")

    mem = MemoryManager(5)
    mem.idx.add(qv, 2)
    mem.idx.request(qv)

    ex = Evaluator(mem, TypeIR(), FnIR())

    block = IRBlock(IRCall(Symbol("@not"), IRArgs()))

    qlang = LowLeveQLang(Symbol("@v"), block, mem.idx, ex, Stack(), SymbolTable())
    res = qlang.gen_program()

    assert res == code_snippet


def test_gen_program_single_u3_not() -> None:
    code_snippet = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[3];

x q[0];
x q[1];
x q[2];
measure q -> c;
"""

    qv = Symbol("@v")

    mem = MemoryManager(5)
    mem.idx.add(qv, 3)
    mem.idx.request(qv)

    ex = Evaluator(mem, TypeIR(), FnIR())

    block = IRBlock(IRCall(Symbol("@not"), IRArgs()))

    qlang = LowLeveQLang(Symbol("@v"), block, mem.idx, ex, Stack(), SymbolTable())
    res = qlang.gen_program()

    assert res == code_snippet


def test_gen_program_single_u4_not() -> None:
    code_snippet = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
creg c[4];

x q[0];
x q[1];
x q[2];
x q[3];
measure q -> c;
"""

    qv = Symbol("@v")

    mem = MemoryManager(5)
    mem.idx.add(qv, 4)
    mem.idx.request(qv)

    ex = Evaluator(mem, TypeIR(), FnIR())

    block = IRBlock(IRCall(Symbol("@not"), IRArgs()))

    qlang = LowLeveQLang(Symbol("@v"), block, mem.idx, ex, Stack(), SymbolTable())
    res = qlang.gen_program()

    assert res == code_snippet


def test_gen_program_nez_not_u3() -> None:
    code_snippet = """OPENQASM 2.0;
include \"qelib1.inc\";
qreg q[3];
creg c[3];

x q[0];
x q[2];
measure q -> c;
"""

    qv = Symbol("@v")
    mem = MemoryManager(5)
    mem.idx.add(qv, 3)
    mem.idx.request(qv)

    ex = Evaluator(mem, TypeIR(), FnIR())

    block = IRBlock(
        IRCall(
            Symbol("@nez"),
            IRArgs(CoreLiteral("@5", "@u3"), Symbol("@not")),
        )
    )

    qlang = LowLeveQLang(qv, block, mem.idx, ex, Stack())
    res = qlang.gen_program()

    assert res == code_snippet


def test_gen_program_nez_zero_mask() -> None:
    code_snippet = ""

    qv = Symbol("@v")
    mem = MemoryManager(5)
    mem.idx.add(qv, 3)
    mem.idx.request(qv)

    ex = Evaluator(mem, TypeIR(), FnIR())

    block = IRBlock(
        IRCall(
            Symbol("@nez"),
            IRArgs(CoreLiteral("@0", "@u3"), Symbol("@not")),
        )
    )

    qlang = LowLeveQLang(qv, block, mem.idx, ex, Stack())
    res = qlang.gen_program()

    assert res == code_snippet


def test_gen_program_nez_redim_small_mask() -> None:
    code_snippet = """OPENQASM 2.0;
include \"qelib1.inc\";
qreg q[3];
creg c[3];

h q[0];
measure q -> c;
"""

    qv = Symbol("@v")
    mem = MemoryManager(5)
    mem.idx.add(qv, 3)
    mem.idx.request(qv)

    ex = Evaluator(mem, TypeIR(), FnIR())

    block = IRBlock(
        IRCall(
            Symbol("@nez"),
            IRArgs(Symbol("@true"), Symbol("@redim")),
        )
    )

    qlang = LowLeveQLang(qv, block, mem.idx, ex, Stack())
    res = qlang.gen_program()

    assert res == code_snippet


def test_gen_program_nez_bool_not() -> None:
    code_snippet = """OPENQASM 2.0;
include \"qelib1.inc\";
qreg q[1];
creg c[1];

x q[0];
measure q -> c;
"""

    qv = Symbol("@v")
    mem = MemoryManager(5)
    mem.idx.add(qv, 1)
    mem.idx.request(qv)

    ex = Evaluator(mem, TypeIR(), FnIR())

    block = IRBlock(
        IRCall(
            Symbol("@nez"),
            IRArgs(Symbol("@true"), Symbol("@not")),
        )
    )

    qlang = LowLeveQLang(qv, block, mem.idx, ex, Stack())
    res = qlang.gen_program()

    assert res == code_snippet


@pytest.mark.skip()
def test_qinstr_flag_skip_gen_args() -> None:
    """Ensure instructions with the flag skip argument generation."""

    # assert QNez.flag == QInstrFlag.SKIP_GEN_ARGS
    # assert QNez().skip_gen_args
    # assert QNot.flag == QInstrFlag.NONE
    # assert not QNot().skip_gen_args
