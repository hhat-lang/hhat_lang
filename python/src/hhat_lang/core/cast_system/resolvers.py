"""
How the bitstring results are presented according to different resolvers and specific types.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable


class Resolver(ABC):
    @abstractmethod
    def __call__(self, raw_value: dict[str, int | float], type_spec: Callable, **options: Any) -> Any:
        pass


class RawValue(Resolver):
    def __call__(self, raw_value: dict[str, int | float], type_spec: Callable, **options: Any) -> Any:
        return raw_value


class WeightedAverageValue(Resolver):
    def __call__(self, raw_value: dict[str, int | float], type_spec: Callable, **options: Any) -> Any:
        total = sum(raw_value.values())
        w_value = sum((v/total) * ord(k) for k, v in raw_value.items())
        return type_spec(w_value)


class HighestValue(Resolver):
    def __call__(self, raw_value: dict[str, int | float], type_spec: Callable, **options: Any) -> Any:
        return type_spec(max(raw_value, key=raw_value.get))


class LowestValue(Resolver):
    def __call__(self, raw_value: dict[str, int | float], type_spec: Callable, **options: Any) -> Any:
        return type_spec(min(raw_value, key=raw_value.get))
