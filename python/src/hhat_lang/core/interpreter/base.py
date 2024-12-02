from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

FetchedType = TypeVar("FetchedType")
FetchedFn = TypeVar("FetchedFn")
FetchedMain = TypeVar("FetchedMain")


class BaseIR(ABC, Generic[FetchedType, FetchedFn, FetchedMain]):
    @abstractmethod
    def fetch_types(self, *args: Any, **kwargs: Any) -> FetchedType: ...

    @abstractmethod
    def fetch_fns(self, *args: Any, **kwargs: Any) -> FetchedFn: ...

    @abstractmethod
    def fetch_main(self, *args: Any, **kwargs: Any) -> FetchedMain: ...
