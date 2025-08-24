from __future__ import annotations

from typing import Any

from arpeggio import Kwd
from arpeggio.peg import EOF, OneOrMore, Optional, ZeroOrMore

from hhat_lang.dialects.heather.grammar.generic_grammar import (
    assign,
    assign_ds,
    assignargs,
    body,
    declare,
    declareassign,
    declareassign_ds,
    expr,
    full_id,
    id_composite_value,
    many_import,
    simple_id,
    single_import,
)
from hhat_lang.dialects.heather.grammar.type_grammar import typeimport


def fn_program() -> Any:
    return ZeroOrMore(imports), ZeroOrMore(fns), Optional(main), EOF


def imports() -> Any:
    return Kwd("use"), "(", OneOrMore([typeimport, fnimport]), ")"


def fnimport() -> Any:
    return Kwd("fn"), ":", [single_import, many_import]


def fns() -> Any:
    return Kwd("fn"), simple_id, fnargs, Optional(full_id), fn_body


def fnargs() -> Any:
    return "(", ZeroOrMore(argtype), ")"


def argtype() -> Any:
    return simple_id, ":", id_composite_value


def fn_body() -> Any:
    return (
        "{",
        ZeroOrMore(
            [
                fn_return,
                declareassign,
                declareassign_ds,
                declare,
                assignargs,
                assign_ds,
                assign,
                expr,
            ]
        ),
        "}",
    )


def fn_return() -> Any:
    return "::", expr


def main() -> Any:
    return Kwd("main"), body
