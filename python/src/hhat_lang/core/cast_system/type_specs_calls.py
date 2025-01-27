"""
Use this to specify how each type will handle the transformation for the resolver.
"""

from __future__ import annotations


def spec_int(result: float) -> int:
    return round(result)


def spec_float(result: float) -> float:
    return result


def spec_char(result: float) -> str:
    return chr(round(result))
