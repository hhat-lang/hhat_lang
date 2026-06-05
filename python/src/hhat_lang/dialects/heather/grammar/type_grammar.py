from __future__ import annotations

from typing import Any

from arpeggio import Kwd
from arpeggio.peg import EOF, OneOrMore, ZeroOrMore

from hhat_lang.dialects.heather.grammar.generic_grammar import (
    id_composite_value,
    many_import,
    simple_id,
    single_import,
)


def type_program() -> Any:
    return ZeroOrMore(imports), ZeroOrMore(type_file), EOF


def imports() -> Any:
    return Kwd("use"), "(", OneOrMore(typeimport), ")"


def typeimport() -> Any:
    return Kwd("type"), ":", [single_import, many_import]


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
