from __future__ import annotations

from typing import Any

from arpeggio import Kwd, OneOrMore, Optional, ZeroOrMore
from arpeggio import RegExMatch as _

from hhat_lang.dialects.heather.grammar import (
    FLOAT,
    ID,
    INT,
    MULTILINE_COMMENT,
    QINT,
    SINGLE_COMMENT,
    STRING,
)


def id_composite_value() -> Any:
    return [("[", full_id, "]"), full_id]


def callargs() -> Any:
    return full_id, "=", valonly


def valonly() -> Any:
    return [array, full_id, literal]


def array() -> Any:
    return "[", ZeroOrMore([literal, composite_id_with_closure, full_id]), "]"


def simple_id() -> Any:
    return _(ID)


def trait_name_id() -> Any:
    return _(r"@?[A-Z][a-zA-Z0-9\-_]*")


def trait_id() -> Any:
    """
    Trait id always starts with ``#`` and an uppercase letter, ex: ``#Printable``.
    It can also contain multiple trait ids, as: ``#[Printable Integers]``
    """
    return (
        "#",
        [trait_name_id, ("[", OneOrMore(trait_name_id), "]")],
        Optional(modifier),
    )


def composite_id() -> Any:
    return simple_id, OneOrMore(".", simple_id)


def composite_id_with_closure() -> Any:
    return (
        [full_id],
        ".",
        "{",
        OneOrMore([composite_id_with_closure, composite_id, full_id]),
        "}",
    )


def composite_id_with_values() -> Any:
    return (
        full_id,
        ".",
        "[",
        [
            OneOrMore(
                [
                    ([literal, simple_id], capped_range, [literal, simple_id]),
                    valonly,
                ]
            ),
            ([full_id, literal], variadic),
            (variadic, [full_id, literal]),
        ],
        "]",
    )


def modifier() -> Any:
    return "<", [ref, pointer, variadic, OneOrMore([callargs, valonly])], ">"


def full_id() -> Any:
    return [composite_id, simple_id], Optional(modifier)


def ref() -> Any:
    return Kwd("&")


def pointer() -> Any:
    return Kwd("*")


def variadic() -> Any:
    return Kwd("...")


def capped_range() -> Any:
    return Kwd("..")


def literal() -> Any:
    return (
        [t_float, t_null, t_bool, t_str, t_int, qt_bool, qt_int],
        Optional(":", composite_id),
    )


def t_null() -> Any:
    return Kwd("null")


def t_bool() -> Any:
    return [Kwd("true"), Kwd("false")]


def t_str() -> Any:
    return _(STRING)


def t_int() -> Any:
    return _(INT)


def t_float() -> Any:
    return _(FLOAT)


def qt_bool() -> Any:
    return [Kwd("@true"), Kwd("@false")]


def qt_int() -> Any:
    return _(QINT)


def comment() -> Any:
    return [_(SINGLE_COMMENT), _(MULTILINE_COMMENT)]


def single_import() -> Any:
    return [composite_id_with_closure, full_id]


def many_import() -> Any:
    return "[", OneOrMore(single_import), "]"


def body() -> Any:
    return (
        "{",
        ZeroOrMore([declareassign, declareassign_ds, declare, assign, expr]),
        "}",
    )


def expr() -> Any:
    return [
        cast,
        assign_ds,
        call_optn,
        call_optbdn,
        call_bdn,
        call,
        array,
        full_id,
        literal,
    ]


def declare() -> Any:
    return simple_id, Optional(modifier), ":", full_id


def assign() -> Any:
    return full_id, "=", expr


def assign_ds() -> Any:
    return full_id, ".{", [OneOrMore(assignargs), OneOrMore(expr)], "}"


def declareassign() -> Any:
    return simple_id, Optional(modifier), ":", full_id, "=", expr


def declareassign_ds() -> Any:
    return (
        simple_id,
        Optional(modifier),
        ":",
        full_id,
        "=",
        ".{",
        OneOrMore(assignargs),
        "}",
    )


def cast() -> Any:
    return [call, literal, full_id], "*", full_id


def call() -> Any:
    return full_id, "(", args, ")", Optional(modifier)


def args() -> Any:
    return ZeroOrMore([callargs, cast, call, valonly])


def assignargs() -> Any:
    return full_id, "=", expr


def option() -> Any:
    return [call, array, full_id], ":", [body, expr]


def call_optbdn() -> Any:
    return full_id, "(", args, ")", "{", OneOrMore(option), "}"


def call_optn() -> Any:
    return full_id, "(", OneOrMore(option), ")"


def call_bdn() -> Any:
    return full_id, "(", args, ")", body


def const_import() -> Any:
    return Kwd("const"), ":", [single_import, many_import]


def metafn_import() -> Any:
    return Kwd("metafn"), ":", [single_import, many_import]


def metamod_import() -> Any:
    return Kwd("metamod"), ":", [single_import, many_import]
