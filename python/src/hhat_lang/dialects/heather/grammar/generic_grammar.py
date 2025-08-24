from __future__ import annotations

from typing import Any

from arpeggio import Kwd, OneOrMore, Optional, ZeroOrMore
from arpeggio import RegExMatch as _


def id_composite_value() -> Any:
    return [("[", full_id, "]"), full_id]


def callargs() -> Any:
    return simple_id, "=", valonly


def valonly() -> Any:
    return [array, full_id, literal]


def array() -> Any:
    return "[", ZeroOrMore([literal, composite_id_with_closure, full_id]), "]"


def simple_id() -> Any:
    return _(r"@?[a-zA-Z][a-zA-Z0-9\-_]*")


def composite_id() -> Any:
    return simple_id, OneOrMore(".", simple_id)


def composite_id_with_closure() -> Any:
    return (
        [composite_id, simple_id],
        ".",
        "{",
        OneOrMore([composite_id_with_closure, composite_id, simple_id]),
        "}",
    )


def modifier() -> Any:
    return "<", [ref, pointer, OneOrMore([callargs, valonly])], ">"


def full_id() -> Any:
    return [composite_id, simple_id], Optional(modifier)


def ref() -> Any:
    return Kwd("&")


def pointer() -> Any:
    return Kwd("*")


def literal() -> Any:
    return [t_float, t_null, t_bool, t_str, t_int, qt_bool, qt_int], Optional(
        ":", composite_id
    )


def t_null() -> Any:
    return Kwd("null")


def t_bool() -> Any:
    return [Kwd("true"), Kwd("false")]


def t_str() -> Any:
    return _(r'"([^"]*)"')


def t_int() -> Any:
    return _(r"-?([1-9]\d*|0)")


def t_float() -> Any:
    return _(r"-?\d+\.\d+")


def qt_bool() -> Any:
    return [Kwd("@true"), Kwd("@false")]


def qt_int() -> Any:
    return _(r"-?\@([1-9]\d*|0)")


def comment() -> Any:
    return [_(r"\/\/([^\n]*)\n"), _(r"\/\-.*?\-\/")]


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
        callwithargsoptions,
        callwithbodyoptions,
        callwithbody,
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
    return [composite_id, simple_id], "=", expr


def option() -> Any:
    return [call, array, full_id], ":", [body, expr]


def callwithbodyoptions() -> Any:
    return full_id, "(", args, ")", "{", OneOrMore(option), "}"


def callwithargsoptions() -> Any:
    return full_id, "(", OneOrMore(option), ")"


def callwithbody() -> Any:
    return full_id, "(", args, ")", body
