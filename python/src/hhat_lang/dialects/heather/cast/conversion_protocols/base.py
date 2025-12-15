from __future__ import annotations

from typing import Any

from hhat_lang.core.cast.base import get_min_count, get_max_count, BaseBitString


class BitString(BaseBitString):
    """Handle bit string data for Heather dialect."""

    # TODO: refactor later to place the backend platform-specific logic be handled by them

    @staticmethod
    def _get_data(data: Any) -> dict:
        return getattr(data, "c", None) or getattr(data, "meas", dict())

    def _get_res(self, data: Any) -> Any:
        if hasattr(data, "shape") and hasattr(data, "size"):
            return self._get_data(data)

        if hasattr(data, "data"):
            return self._get_res(data.data)

        raise NotImplementedError(f"could not get bit string counts for data of type {type(data)}")

    def get_counts(self) -> dict:
        return self._get_res(self._sample)


def get_min_res(sample: BitString) -> Any:
    res = get_min_count(sample)


def get_max_res(sample: BitString) -> Any:
    res = get_max_count(sample)
