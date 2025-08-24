from __future__ import annotations

from hhat_lang.core.data.core import Symbol
from hhat_lang.core.types import POINTER_SIZE
from hhat_lang.core.types.abstract_base import QSize, Size
from hhat_lang.core.types.builtin_base import BuiltinSingleDS

#######################
# BUILT-IN DATA TYPES #
#######################

# ---------- #
# classical  #
# ---------- #

Int = BuiltinSingleDS(Symbol("int"), Size(64))
Bool = BuiltinSingleDS(Symbol("bool"), Size(8))
U16 = BuiltinSingleDS(Symbol("u16"), Size(16))
U32 = BuiltinSingleDS(Symbol("u32"), Size(32))
U64 = BuiltinSingleDS(Symbol("u64"), Size(64))
I16 = BuiltinSingleDS(Symbol("i16"), Size(16))
I32 = BuiltinSingleDS(Symbol("i32"), Size(32))
I64 = BuiltinSingleDS(Symbol("i64"), Size(64))
Float = BuiltinSingleDS(Symbol("float"), Size(64))
F32 = BuiltinSingleDS(Symbol("f32"), Size(32))
F64 = BuiltinSingleDS(Symbol("f64"), Size(64))


# -------- #
# quantum  #
# -------- #

QBool = BuiltinSingleDS(Symbol("@bool"), Size(POINTER_SIZE), qsize=QSize(1, 1))
QU2 = BuiltinSingleDS(Symbol("@u2"), Size(POINTER_SIZE), qsize=QSize(2, 2))
QU3 = BuiltinSingleDS(Symbol("@u3"), Size(POINTER_SIZE), qsize=QSize(3, 3))
QU4 = BuiltinSingleDS(Symbol("@u4"), Size(POINTER_SIZE), qsize=QSize(4, 4))
QInt = BuiltinSingleDS(
    Symbol("@int"),
    Size(POINTER_SIZE),
    qsize=QSize(min_num=QU2.qsize.min, max_num=QU4.qsize.max),
)
"""
``QInt`` (``@int``) represents a generic quantum integer, where the minimum qsize is the 
minimum of quantum integer type (``@u2``) and the maximum is the maximum of the biggest 
quantum integer available.
"""


# ---------------------------------- #
# list with all built-in data types  #
# ---------------------------------- #

builtins_types = {
    # classical
    Symbol("int"): Int,
    Symbol("float"): Float,
    Symbol("bool"): Bool,
    Symbol("u16"): U16,
    Symbol("u32"): U32,
    Symbol("u64"): U64,
    Symbol("i16"): I16,
    Symbol("i32"): I32,
    Symbol("i64"): I64,
    Symbol("f32"): F32,
    Symbol("f64"): F64,
    # quantum
    Symbol("@bool"): QBool,
    Symbol("@int"): QInt,
    Symbol("@u2"): QU2,
    Symbol("@u3"): QU3,
    Symbol("@u4"): QU4,
}
"""a dictionary where keys are the available types as str and the values are their classes"""
