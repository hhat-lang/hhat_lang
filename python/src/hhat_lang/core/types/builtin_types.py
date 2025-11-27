from __future__ import annotations

from hhat_lang.core.data.core import Symbol
from hhat_lang.core.types import POINTER_SIZE
from hhat_lang.core.types.abstract_base import QSize, Size
from hhat_lang.core.types.builtin_base import BuiltinSingleDS, BuiltinStructDS
from hhat_lang.core.types.core import ArrayDS

#######################
# BUILT-IN DATA TYPES #
#######################

# ---------- #
# classical  #
# ---------- #

# BASIC SINGLE TYPES
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

# HASHMAP TYPES
HashKey = BuiltinSingleDS(Symbol("hash-key"), Size(POINTER_SIZE))
HashValue = BuiltinSingleDS(Symbol("hash-value"), Size(POINTER_SIZE))
HashSet = BuiltinStructDS(
    Symbol("hash-set"),
    Size(POINTER_SIZE)
).add_member(
    member_type=HashKey,
    member_name=Symbol("key")
).add_member(
    member_type=HashValue,
    member_name=Symbol("value")
)
"""
```HashSet`` ("hash-set") is the holder of hash keys and hash values 
for ``HashMap`` ("hashmap").
"""
HashMap = BuiltinStructDS(
    Symbol("hashmap"),
    Size(POINTER_SIZE)
).add_member(member_type=ArrayDS(Symbol("hash-set")), member_name=Symbol("data"))
"""
``HashMap`` ("hashmap") is the common hashmap(dictionary) data structure
"""


# SAMPLE TYPES
HashKeyInt = BuiltinSingleDS(Symbol("hash-key_int"), Size(64))
HashValueInt = BuiltinSingleDS(Symbol("hash-value_int"), Size(64))
HashSetInt = BuiltinStructDS(
    Symbol("hash-set_int"),
    Size(POINTER_SIZE)
).add_member(
    member_type=HashKeyInt,
    member_name=Symbol("key")
).add_member(
    member_type=HashValueInt,
    member_name=Symbol("value")
)
"""
```HashSetInt`` ("hash-set_int") is the holder of integer hash keys and hash values 
for ``Sample`` ("sample").
"""
Sample = BuiltinStructDS(
    Symbol("sample"),
    Size(POINTER_SIZE)
).add_member(member_type=ArrayDS(Symbol("hash-set_int")), member_name=Symbol("data"))
"""
``Sample`` is an efficient and fast hashmap(dictionary)-like data structure that knows all
its keys beforehand, so it can compute its exact length; The keys (index number) and values
(count number) are always integer values::

    type sample { data:[hash-set_int] } 

    type hash-set_int {
        key:hash-key_int
        value:hash-value_int
    }

    type hash-key_int:u64
    
    type hash-value_int:u64

"""


# -------- #
# quantum  #
# -------- #

# BASIC SINGLE TYPES
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
    Symbol("hash-set"): HashSet,
    Symbol("hash-key"): HashKey,
    Symbol("hash-value"): HashValue,
    Symbol("hashmap"): HashMap,
    Symbol("hash-set_int"): HashSetInt,
    Symbol("hash-key_int"): HashKeyInt,
    Symbol("hash-value_int"): HashValueInt,
    Symbol("sample"): Sample,
    # quantum
    Symbol("@bool"): QBool,
    Symbol("@int"): QInt,
    Symbol("@u2"): QU2,
    Symbol("@u3"): QU3,
    Symbol("@u4"): QU4,
}
"""a dictionary where keys are the available types as str and the values are their classes"""
