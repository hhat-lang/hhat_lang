from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any, Iterable


class BaseImports(ABC):
    """Base class for importing types and functions"""

    types: Mapping
    fns: Mapping
