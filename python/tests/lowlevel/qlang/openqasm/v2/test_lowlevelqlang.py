from __future__ import annotations

from hhat_lang.core.code.ir import TypeIR, InstrIRFlag
from hhat_lang.core.data.core import Symbol, CoreLiteral
from hhat_lang.core.memory.core import MemoryManager
from hhat_lang.dialects.heather.interpreter.classical.executor import Evaluator
from hhat_lang.dialects.heather.code.simple_ir_builder.ir import (
    FnIR,
    IRBlock,
    IRInstr,
    IRArgs,
)
from hhat_lang.low_level.quantum_lang.openqasm.v2.qlang import LowLeveQLang
from hhat_lang.low_level.quantum_lang.openqasm.v2.instructions import QIf, QRedim


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

    block = IRBlock()
    block.add_instr(IRInstr(Symbol("@redim"), IRArgs(), InstrIRFlag.CALL))

    qlang = LowLeveQLang(Symbol("@v"), block, mem.idx, ex)
    res = qlang.gen_program()

    assert res == code_snippet


def test_gen_program_single_q0_redim() -> None:
    code_snippet = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[1]
creg c[1]

h q[0];
measure q -> c;
"""

    mem = MemoryManager(5)
    mem.idx.request(Symbol("@v"), 3)

    ex = Evaluator(mem, TypeIR(), FnIR())

    block = IRBlock()
    block.add_instr(
        IRInstr(
            name=Symbol("@redim"),
            args=IRArgs(CoreLiteral(Symbol("@5").value, "@u3")),
            flag=InstrIRFlag.CALL
        )
    )

    qlang = LowLeveQLang(Symbol("@v"), block, mem.idx, ex)
    res = qlang.gen_program()
    print(res)
    # assert res == code_snippet


def test_qif_simple_bool():
    # Simulate: @if(@true: @redim(@3))
    # Should generate: measure q[0] -> c[0]; if (c[0]==1) h q[3];
    class DummyExecutor:
        pass
    qif = QIf()
    qredim = QRedim()
    code, status = qif(
        idxs=(0, 3),  # 0: condition qubit, 3: target qubit
        executor=DummyExecutor(),
        options={1: lambda idxs, executor, **kwargs: qredim(idxs=(idxs[0],), **kwargs)[0]}
    )
    assert "measure q[0] -> c[0];" in code[0]
    assert any("if (c[0]==1)" in line and "h q[3];" in line for line in code)


def test_qif_multibit_u2():
    # Simulate: @if(2: @redim(@1), 3: @redim(@2)) for a 2-bit condition (@u2)
    class DummyExecutor:
        pass
    qif = QIf()
    qredim = QRedim()
    code, status = qif(
        idxs=(0, 1, 5),  # 0,1: condition qubits, 5: target qubit
        executor=DummyExecutor(),
        options={
            2: lambda idxs, executor, **kwargs: qredim(idxs=(idxs[0],), **kwargs)[0],
            3: lambda idxs, executor, **kwargs: qredim(idxs=(idxs[0],), **kwargs)[0],
        },
        cond_size=2
    )
    assert "measure q[0] -> c[0];" in code[0]
    assert "measure q[1] -> c[1];" in code[1]
    assert any("if (c[0]==1 && c[1]==0)" in line for line in code)  # 2 = 10b
    assert any("if (c[0]==1 && c[1]==1)" in line for line in code)  # 3 = 11b


def test_qif_with_else():
    # Simulate: @if(1: @redim(@2), else: @redim(@3))
    class DummyExecutor:
        pass
    qif = QIf()
    qredim = QRedim()
    code, status = qif(
        idxs=(0, 2, 3),
        executor=DummyExecutor(),
        options={
            1: lambda idxs, executor, **kwargs: qredim(idxs=(idxs[0],), **kwargs)[0],
            "else": lambda idxs, executor, **kwargs: qredim(idxs=(idxs[0],), **kwargs)[0],
        },
        cond_size=1
    )
    assert any("if (c[0]==1)" in line and "h q[2];" in line for line in code)
    assert any("if (! (" in line and "h q[3];" in line for line in code)


def test_qif_multibody():
    # Simulate: @if(1: [@redim(@2), @redim(@3)])
    class DummyExecutor:
        pass
    qif = QIf()
    qredim = QRedim()
    code, status = qif(
        idxs=(0, 2, 3),
        executor=DummyExecutor(),
        options={
            1: [
                lambda idxs, executor, **kwargs: qredim(idxs=(idxs[0],), **kwargs)[0],
                lambda idxs, executor, **kwargs: qredim(idxs=(idxs[1],), **kwargs)[0],
            ]
        },
        cond_size=1
    )
    assert any("if (c[0]==1)" in line and "h q[2]; h q[3];" in line.replace("  ", " ") for line in code)


def test_qif_allzero_allone():
    # Simulate: @if(0: @redim(@1), 3: @redim(@2)) for a 2-bit condition (@u2)
    class DummyExecutor:
        pass
    qif = QIf()
    qredim = QRedim()
    code, status = qif(
        idxs=(0, 1, 4),
        executor=DummyExecutor(),
        options={
            0: lambda idxs, executor, **kwargs: qredim(idxs=(idxs[0],), **kwargs)[0],
            3: lambda idxs, executor, **kwargs: qredim(idxs=(idxs[0],), **kwargs)[0],
        },
        cond_size=2
    )
    assert any("if (c[0]==0 && c[1]==0)" in line for line in code)  # 0 = 00b
    assert any("if (c[0]==1 && c[1]==1)" in line for line in code)  # 3 = 11b
