from __future__ import annotations

from typing import Any

from arpeggio import Kwd, EOF, OneOrMore, Optional, ZeroOrMore, RegExMatch as _

from hhat_lang.dialects.heather.grammar.generic_grammar import (
    trait_name_id,
    simple_id,
    modifier,
)
from hhat_lang.dialects.heather.grammar.type_grammar import typeimport


def metamod_program() -> Any:
    return ZeroOrMore(imports), ZeroOrMore(metamod_def), EOF


def imports() -> Any:
    return Kwd("use"), "(", OneOrMore(typeimport), ")"


def metamod_def() -> Any:
    """
    Meta module definition::

        metamod <trait_name_id> <metamod_body>

    example::

        metamod Printable { fn: print }

        metamod Numeric {
            fn: { add sub mul div pow }
        }
    """

    return Kwd("metamod"), trait_name_id, metamod_body


def metamod_body() -> Any:
    return "{", ZeroOrMore([metamod_fn_header]), "}"


def metamod_fn_header() -> Any:
    return Kwd("fn"), ":", [id_mod_opt, fn_header_body]


def fn_header_body() -> Any:
    return "{", OneOrMore(id_mod_opt), "}"


def id_mod_opt() -> Any:
    return simple_id, Optional(modifier)
