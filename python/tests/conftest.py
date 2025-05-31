from __future__ import annotations

import pytest
from pathlib import Path

from hhat_lang.dialects.heather.code.ast import (
    Id,
    CompositeId,
    CompositeIdWithClosure,
    Imports,
    FnImport,
    TypeImport,
    FnDef,
    FnArgs,
    Body
)

@pytest.fixture
def MAX_ATOL_STATES_GATE() -> float:
    return 0.08

@pytest.fixture
def mock_imports():
    """Create mock imports AST node."""
    return Imports(
        type_import=[],
        fn_import=[
            FnImport((
                Id("main_function"),
                CompositeId(Id("math"), Id("sum")),
                CompositeId(Id("math"), Id("linalg"), Id("dot"))
            ))
        ]
    )

@pytest.fixture
def mock_function_definition():
    """Create a mock function definition AST node."""
    return FnDef(
        fn_name=Id("test_function"),
        fn_type=Id("void"),
        args=FnArgs(),
        body=Body()
    )
