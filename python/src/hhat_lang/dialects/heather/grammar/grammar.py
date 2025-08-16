from __future__ import annotations

from typing import Any

from arpeggio.peg import Optional, ZeroOrMore, OneOrMore, EOF
from arpeggio import RegExMatch as _, Kwd


def program() -> Any:
    return ZeroOrMore(imports), [(ZeroOrMore(fns), Optional(main)), ZeroOrMore(type_file)], EOF


def imports() -> Any:
    return Kwd("use"), "(",  OneOrMore([typeimport, fnimport]), ")"


def typeimport() -> Any:
    return Kwd("type"), ":", [single_import, many_import]


def fnimport() -> Any:
    return Kwd("fn"), ":", [single_import, many_import]


def single_import() -> Any:
    return [composite_id_with_closure, full_id]


def many_import() -> Any:
    return "[", OneOrMore(single_import), "]"


def type_file() -> Any:
    return Kwd("type"), [typesingle, typestruct, typeenum]


def typesingle() -> Any:
    return simple_id, ":", id_composite_value


def typemember() -> Any:
    return simple_id, ":", id_composite_value


def typestruct() -> Any:
    return simple_id, "{", ZeroOrMore(typemember), "}"


def typeenum() -> Any:
    return simple_id, "{", ZeroOrMore(enummember), "}"


def enummember() -> Any:
    return [simple_id, typestruct]

def typespace() -> Any:
    return Kwd("typespace"), full_id, "{", ZeroOrMore(fns), "}"


def fns() -> Any:
    return Kwd("fn"), simple_id, fnargs, Optional(full_id), fn_body


def fnargs() -> Any:
    return "(", ZeroOrMore(argtype), ")"


def argtype() -> Any:
    return simple_id, ":", id_composite_value


def fn_body() -> Any:
    return "{", ZeroOrMore([fn_return, declareassign, declareassign_ds, declare, assignargs, assign_ds, assign, expr]), "}"


def fn_return() -> Any:
    return "::", expr


def id_composite_value() -> Any:
    return [("[", full_id, "]"), full_id]


def main() -> Any:
    return Kwd("main"), body


def body() -> Any:
    return "{", ZeroOrMore([declareassign, declareassign_ds, declare, assign, expr]), "}"


def expr() -> Any:
    return [cast, assign_ds, callwithargsoptions, callwithbodyoptions, callwithbody, call, array, full_id, literal]


def declare() -> Any:
    return simple_id, Optional(modifier), ":", full_id


def assign() -> Any:
    return full_id, "=", expr


def assign_ds() -> Any:
    return full_id, ".{", [OneOrMore(assignargs), OneOrMore(expr)], "}"


def declareassign() -> Any:
    return simple_id, Optional(modifier), ":", full_id, "=", expr


def declareassign_ds() -> Any:
    return simple_id, Optional(modifier), ":", full_id, "=", ".{", OneOrMore(assignargs), "}"


def cast() -> Any:
    return [call, literal, full_id], "*", full_id


def call() -> Any:
    return full_id, "(", args, ")", Optional(modifier)


def args() -> Any:
    return ZeroOrMore([callargs, cast, call, valonly])


def assignargs() -> Any:
    return [composite_id, simple_id], "=", expr


def callargs() -> Any:
    return simple_id, "=", valonly


def valonly() -> Any:
    return [array, full_id, literal]


def option() -> Any:
    return [call, array, full_id], ":", [body, expr]


def callwithbodyoptions() -> Any:
    return full_id, "(", args, ")", "{",  OneOrMore(option), "}"


def callwithargsoptions() -> Any:
    return full_id, "(", OneOrMore(option), ")"


def callwithbody() -> Any:
    return full_id, "(", args, ")", body


def array() -> Any:
    return "[", ZeroOrMore([literal, composite_id_with_closure, full_id]), "]"


def simple_id() -> Any:
    return _(r"@?[a-zA-Z][a-zA-Z0-9\-_]*")


def composite_id() -> Any:
    return simple_id, OneOrMore(".", simple_id)


def composite_id_with_closure() -> Any:
    return [composite_id, simple_id], ".", "{", OneOrMore([composite_id_with_closure, composite_id, simple_id]), "}"


def modifier() -> Any:
    return "<", [ref, pointer, OneOrMore([callargs, valonly])], ">"


def full_id() -> Any:
    return [composite_id, simple_id], Optional(modifier)


def ref() -> Any:
    return Kwd("&")


def pointer() -> Any:
    return Kwd("*")


def literal() -> Any:
    return [t_float, t_null, t_bool, t_str, t_int, qt_bool, qt_int], Optional(":", composite_id)


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
