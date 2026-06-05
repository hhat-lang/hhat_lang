from __future__ import annotations

from typing import Any

from arpeggio import Kwd, EOF, OneOrMore, Optional, ZeroOrMore

from hhat_lang.dialects.heather.grammar.fn_grammar import imports
from hhat_lang.dialects.heather.grammar.generic_grammar import (
    simple_id,
    full_id,
    expr,
)


def const_program() -> Any:
    return ZeroOrMore(imports), ZeroOrMore(const_def), EOF


def const_def() -> Any:
    return Kwd("const"), simple_id, ":", full_id, "=", expr
