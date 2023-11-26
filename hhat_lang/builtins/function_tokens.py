from __future__ import annotations
from enum import Enum


class MetaFnToken(str, Enum):
    META    = "meta-default"
    Q_META  = "@meta-default"


class FnToken(str, Enum):
    SUM     = "sum"
    TIMES   = "times"
    PRINT   = "print"


class QFnToken(str, Enum):
    SHUFFLE   = "@shuffle"
    SYNC      = "@sync"
