"""
Pygments lexer for H-hat's Heather dialect.

This module provides syntax highlighting support for Heather code
in documentation, IDEs, and other tools that use Pygments.
"""

from __future__ import annotations

from hhat_lang.dialects.heather.toolchain.pygments.lexer import (
    HeatherLexer,
    HhatLexer,
)

__all__ = ["HeatherLexer", "HhatLexer"]
