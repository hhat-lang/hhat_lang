from __future__ import annotations

from hhat_lang.core.data.core import Symbol
from hhat_lang.dialects.heather.code.builtins.fns.builtins_fn_def import (
    builtin_fn__print,
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
    builtin_fn_float_int_pow
)


BUILTIN_FNS_DICT = {
    "print": {
        (): builtin_fn__print,
        (Symbol("bool"),): builtin_fn__print,
        (Symbol("int"),): builtin_fn__print,
        (Symbol("float"),): builtin_fn__print,
        (Symbol("str"),): builtin_fn__print,
    },
    "add": {
        (Symbol("int"),): builtin_fn_int_add,
        (Symbol("float"),): builtin_fn_float_add,
        (Symbol("int"), Symbol("float"),): builtin_fn_int_float_add
    },
    "sub": {
        (Symbol("int"),): builtin_fn_int_sub,
        (Symbol("float"),): builtin_fn_float_sub,
        (): builtin_fn_int_float_sub
    },
    "mul": {
        (): builtin_fn_int_mul,
        (): builtin_fn_float_mul,
        (): builtin_fn_int_float_mul
    },
    "div": {
        (): builtin_fn_int_div,
        (): builtin_fn_float_div,
        (): builtin_fn_int_float_div,
        (): builtin_fn_float_int_div
    },
    "pow": {
        (): builtin_fn_int_pow,
        (): builtin_fn_float_pow,
        (): builtin_fn_int_float_pow,
        (): builtin_fn_float_int_pow
    },
    "log": {},
}
