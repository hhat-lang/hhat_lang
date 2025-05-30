from __future__ import annotations

from hhat_lang.core.data.core import Symbol
from hhat_lang.core.types import POINTER_SIZE
from hhat_lang.core.types.abstract_base import QSize, Size
from hhat_lang.core.types.builtin_base import BuiltinSingleDS

#######################
# BUILT-IN DATA TYPES #
#######################

# -----------#
# classical #
# -----------#

Int = BuiltinSingleDS(Symbol("int"))
Bool = BuiltinSingleDS(Symbol("bool"), Size(8))
U16 = BuiltinSingleDS(Symbol("u16"), Size(16))
U32 = BuiltinSingleDS(Symbol("u32"), Size(32))
U64 = BuiltinSingleDS(Symbol("u64"), Size(64))


# ---------#
# quantum #
# ---------#

QBool = BuiltinSingleDS(Symbol("@bool"), Size(POINTER_SIZE), qsize=QSize(1))
QU2 = BuiltinSingleDS(Symbol("@u2"), Size(POINTER_SIZE), qsize=QSize(2))
QU3 = BuiltinSingleDS(Symbol("@u3"), Size(POINTER_SIZE), qsize=QSize(3))
QU4 = BuiltinSingleDS(Symbol("@u4"), Size(POINTER_SIZE), qsize=QSize(4))
