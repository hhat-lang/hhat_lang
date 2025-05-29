from __future__ import annotations

from enum import StrEnum
from .function_resolver import locate_function_source, FunctionResolutionError


class DataParadigm(StrEnum):
    CLASSICAL = "classical"
    QUANTUM = "quantum"
