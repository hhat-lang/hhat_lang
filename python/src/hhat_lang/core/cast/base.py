from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from collections import Counter

from hhat_lang.core.data.variable import BaseDataContainer


class BaseBitString(ABC):
    def __init__(self, data: Any, **config: Any):
        self._sample = data
        self._config = config

    @property
    def config(self) -> dict:
        return self._config

    @abstractmethod
    def get_counts(self) -> dict:
        raise NotImplementedError()


def get_max(sample: BaseBitString) -> str:
    """Return the bitstring of the maximum count"""

    return Counter(sample.get_counts()).most_common(1)[0][0]


def get_min(sample: BaseBitString) -> str:
    """Return the bistring of the minimum count"""
    return Counter(sample.get_counts()).most_common()[-1][0]


def get_sample(sample: BaseBitString) -> BaseDataContainer:
    pass
