from __future__ import annotations

from typing import Any

from hhat_lang.core.cast.base import get_min, get_max, BaseBitString


class BitString(BaseBitString):

    def get_counts(self) -> dict:
        pass


def get_sampling_min(sampling: Any) -> Any:
    res = get_min()


def get_sampling_max(sampling: Any) -> Any:
    res = get_max()
