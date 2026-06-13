"""Heather comment syntax helpers."""

from __future__ import annotations

import re


def strip_comments(code: str) -> str:
    """Remove comments using Heather comment syntax before parsing signatures."""

    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    return re.sub(r"//.*", "", code)
