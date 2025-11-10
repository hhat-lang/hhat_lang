from __future__ import annotations

from typing import Callable

from hhat_lang.core.data.core import Symbol
from hhat_lang.dialects.heather.code.builtins.fns.core import builtin_fn__match
from hhat_lang.dialects.heather.code.builtins.fns.math import (
    builtin_fn_int_add,
    builtin_fn_float_add,
    builtin_fn_int_sub,
    builtin_fn_float_sub,
    builtin_fn_int_float_add,
    builtin_fn_int_mul,
    builtin_fn_float_mul,
    builtin_fn_int_float_mul,
    builtin_fn_int_div,
    builtin_fn_float_div,
    builtin_fn_int_float_div,
    builtin_fn_float_int_div,
    builtin_fn_int_float_sub,
    builtin_fn_int_pow,
    builtin_fn_float_pow,
    builtin_fn_int_float_pow,
    builtin_fn_float_int_pow,
)
from hhat_lang.dialects.heather.code.builtins.fns.io import builtin_fn__print


# TODO: make functions path specific, e.g. math functions should come from `math` module, etc

BUILTIN_FN_DICT: dict[str, dict[tuple[Symbol] | tuple, Callable]] = {
    "print": {
        (): builtin_fn__print,
        (Symbol("bool"),): builtin_fn__print,
        (Symbol("int"),): builtin_fn__print,
        (Symbol("float"),): builtin_fn__print,
        (Symbol("str"),): builtin_fn__print,
    },
    "add": {
        (Symbol("int"), Symbol("int")): builtin_fn_int_add,
        (Symbol("float"), Symbol("float")): builtin_fn_float_add,
        (Symbol("int"), Symbol("float")): builtin_fn_int_float_add,
        (Symbol("float"), Symbol("int")): builtin_fn_int_float_add,
    },
    "sub": {
        (Symbol("int"), Symbol("int")): builtin_fn_int_sub,
        (Symbol("float"), Symbol("float")): builtin_fn_float_sub,
        (Symbol("int"), Symbol("float")): builtin_fn_int_float_sub,
        (Symbol("float"), Symbol("int")): builtin_fn_int_float_sub,
    },
    "mul": {
        (Symbol("int"), Symbol("int")): builtin_fn_int_mul,
        (Symbol("float"), Symbol("float")): builtin_fn_float_mul,
        (Symbol("int"), Symbol("float")): builtin_fn_int_float_mul,
        (Symbol("float"), Symbol("int")): builtin_fn_int_float_mul,
    },
    "div": {
        (Symbol("int"), Symbol("int")): builtin_fn_int_div,
        (Symbol("float"), Symbol("float")): builtin_fn_float_div,
        (Symbol("int"), Symbol("float")): builtin_fn_int_float_div,
        (Symbol("float"), Symbol("int")): builtin_fn_float_int_div,
    },
    "pow": {
        (Symbol("int"), Symbol("int")): builtin_fn_int_pow,
        (Symbol("float"), Symbol("float")): builtin_fn_float_pow,
        (Symbol("int"), Symbol("float")): builtin_fn_int_float_pow,
        (Symbol("float"), Symbol("int")): builtin_fn_float_int_pow,
    },
    "log": {},
}
"""
Dictionary containing the built-in functions (fn). 'fn' has the form of::

    caller(args)
"""


BUILTIN_OPTN_DICT = {

}
"""
Dictionary containing the built-in arguments as options (optn). 'optn' has the form of::

    caller(
        option1:{body1}
        option2:{body2}
        ...
    )
"""


BUILTIN_OPTBDN_DICT = {
    "match": { (): builtin_fn__match }
}
"""
Dictionary containing the built-in arguments and options in the body (optbdn). 'optbdn' 
has the form of::

    caller(args) {
        option1:{body1}
        option2:{body2} 
        ... 
    }
"""


BUILTIN_BDN_DICT = {

}
"""
Dictionary containing the built-in arguments and body (bdn). 'bdn' has the form of::

    caller(args) { body }
"""
