from __future__ import annotations

import pytest
from hhat_lang.core.data.core import Symbol
from hhat_lang.dialects.heather.code.ssa_ir_builder.ir import SSA, IRVar, SSAPhi

# TODO: include IRModifier tests


def test_ssa() -> None:
    s = Symbol("s")
    assert SSA(s)

    ssa = SSA(s)

    # SSA only accepts Symbol
    with pytest.raises(ValueError):
        SSA(SSAPhi(ssa, ssa))

    # to get SSA out of SSAPhi, uses `get_ssa` method
    assert SSA.get_ssa(SSAPhi(ssa, ssa))

    # SSAPhi only accepts SSA
    with pytest.raises(AttributeError):
        SSAPhi(s, s)


def test_irvar() -> None:
    s = Symbol("s")
    irs = IRVar(s)
    irs.push(s)
    irs.push(s)
    irs.push(s)
    s2, s3 = irs.data[-2:]
    irs.push(SSAPhi(s2, s3))

    assert len(irs) == 4
    assert irs[-1].phi == SSAPhi(s2, s3), "IRVar index does not contain phi."
    assert len(irs) - 1 == irs[-1].idx, "IRVar index does not match SSA index."
