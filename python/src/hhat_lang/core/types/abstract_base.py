from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable

from hhat_lang.core.data.core import WorkingData
from hhat_lang.core.error_handlers.errors import ErrorHandler
from hhat_lang.dialects.heather.core.variable import Variable


class BaseVarContainer(ABC):
    _container: Iterable

    @abstractmethod
    def assign(self, *args: Any, **kwargs: Any) -> None | ErrorHandler:
        ...


class BaseTypeDataStructure(ABC):
    _type_container: Iterable

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def add_member(self, member_type: str, member_name: str) -> Any:
        ...

    @abstractmethod
    def __call__(
        self,
        *args: Any,
        var_name: str,
        is_mutable: bool = False,
        **kwargs: dict[WorkingData, WorkingData | Variable],
    ) -> BaseVarContainer | ErrorHandler:
        ...
