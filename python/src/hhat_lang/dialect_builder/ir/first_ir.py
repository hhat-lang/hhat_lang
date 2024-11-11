"""
The IR that a dialect AST will be converted to.

This is a dialect-specific IR, but H-hat provides it as a way
to have common structure for easy of conversion during the
CoreIR pass.
"""

from __future__ import annotations

from typing import Any
from abc import ABC, abstractmethod


class FirstIR(ABC):
    pass
