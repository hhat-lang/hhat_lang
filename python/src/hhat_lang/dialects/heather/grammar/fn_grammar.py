from __future__ import annotations

from typing import Any

from arpeggio import EOF, Kwd, OneOrMore, Optional, ZeroOrMore

from hhat_lang.dialects.heather.grammar.generic_grammar import (
    assign,
    assign_ds,
    assignargs,
    body,
    const_import,
    declare,
    declareassign,
    declareassign_ds,
    expr,
    full_id,
    id_composite_value,
    many_import,
    metafn_import,
    metamod_import,
    option,
    simple_id,
    single_import,
)
from hhat_lang.dialects.heather.grammar.type_grammar import typeimport


def fn_program() -> Any:
    return ZeroOrMore(imports), ZeroOrMore(fns), Optional(main), EOF


def imports() -> Any:
    return (
        Kwd("use"),
        "(",
        OneOrMore([typeimport, fnimport, const_import, metafn_import, metamod_import]),
        ")",
    )


def fnimport() -> Any:
    return Kwd("fn"), ":", [single_import, many_import]


def fns() -> Any:
    return Kwd("fn"), simple_id, fnargs, Optional(full_id), fn_body


def fnargs() -> Any:
    return "(", ZeroOrMore(argtype), ")"


def argtype() -> Any:
    return full_id, ":", id_composite_value


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


def metafn_def() -> Any:
    """
    Meta function grammar definition::

        metafn <simple_id> <fnargs> (fn_t | optn_t | bdn_t | optbdn_t) <metafn_body>

    where

    - ``fn_t`` type is for (common) function
    - ``optn_t`` type is for functions with arguments as options
    - ``bdn_t`` type is for functions with arguments and body
    - ``optbdn_t`` type is for functions with arguments and options in the body
    """

    return (
        Kwd("metafn"),
        simple_id,
        fnargs,
        [Kwd("fn_t"), Kwd("optn_t"), Kwd("bdn_t"), Kwd("optbdn_t")],
        metafn_body,
    )


def metafn_body() -> Any:
    return (
        "{",
        OneOrMore(
            [
                option,
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


def modifier_def() -> Any:
    return Kwd("modifier"), simple_id, modifier_args, metafn_body


def modifier_args() -> Any:
    return (
        "(",
        Kwd("self"),
        ZeroOrMore(argtype),
        [
            Kwd("fn_t"),
            Kwd("optn_t"),
            Kwd("bdn_t"),
            Kwd("optbdn_t"),
            Kwd("var_t"),
            Kwd("type_t"),
            Kwd("data_t"),
        ],
        ")",
    )


def main() -> Any:
    return Kwd("main"), body
