"""
Pygments lexer for H-hat's Heather dialect.

This module provides syntax highlighting support for Heather code
in documentation, IDEs, and other tools that use Pygments.
"""

from __future__ import annotations

from hhat_lang.dialects.heather.toolchain.pygments.colors import (
    HhatColors,
    get_color_palette,
)
from hhat_lang.dialects.heather.toolchain.pygments.lexer import (
    HeatherLexer,
    HhatLexer,
)
from hhat_lang.dialects.heather.toolchain.pygments.styles import (
    HhatDarkStyle,
    HhatLightStyle,
)

__all__ = [
    "HeatherLexer",
    "HhatLexer",
    "HhatDarkStyle",
    "HhatLightStyle",
    "HhatColors",
    "get_color_palette",
]
