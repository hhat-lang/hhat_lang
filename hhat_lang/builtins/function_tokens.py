from __future__ import annotations
from enum import StrEnum


class MetaFnToken(StrEnum):
    META = "meta-default"
    Q_META = "@meta-default"


class FnToken(StrEnum):
    SUM     = "sum"
    TIMES   = "times"
    PRINT   = "print"


class QFnToken(StrEnum):
    SHUFFLE   = "@shuffle"
    SYNC      = "@sync"
