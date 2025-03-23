from __future__ import annotations

from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Iterable

from hhat_lang.core.data.core import WorkingData
from hhat_lang.core.error_handlers.errors import (
    ErrorHandler, ContainerVarError,
    ContainerVarIsImmutableError, VariableWrongMemberError
)


class BaseVarContainer(ABC):
    _container: Iterable

    @abstractmethod
    def assign(self, *args: Any, **kwargs: Any) -> None | ErrorHandler:
        ...


class Variable(BaseVarContainer):
    def __init__(
        self,
        var_name: str,
        type_name: str,
        type_ds: OrderedDict,
        is_mutable: bool = True,
    ):
        self._name = var_name
        self._type = type_name
        self._ds: OrderedDict = type_ds
        self._data: OrderedDict = OrderedDict()
        self._assigned: bool = False
        self._is_mutable: bool = is_mutable
        self._is_quantum: bool = True if self._name.startswith("@") else False

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._type

    @property
    def is_quantum(self) -> bool:
        return self._is_quantum

    @property
    def data(self) -> OrderedDict:
        return self._data

    def assign(
        self,
        *args: Any,
        **kwargs: dict[WorkingData, WorkingData | Variable]
    ) -> None | ErrorHandler:
        data = dict()
        if not self._assigned or self._is_mutable:

            if len(args) == len(self._ds):

                for k, d in zip(args, self._ds):
                    if k.type == d:
                        data[d] = k

                    else:
                        return ContainerVarError(self.name)

            elif len(kwargs) == len(self._ds):

                for k, v in kwargs.items():

                    if k in self._ds:
                        data[k] = v

                    else:
                        return ContainerVarError(self.name)

            else:
                return ContainerVarError(self.name)

            self._data = data
            self._assigned = True

        return ContainerVarIsImmutableError(self.name)

    def get(self, member: str | None = None) -> Any:
        member = next(iter(self._ds.keys())) if member is None else member

        if member in self.data:
            return self.data[member]

        return VariableWrongMemberError(self.name)

    def __call__(
        self,
        *args: Any,
        **kwargs: dict[WorkingData, WorkingData | Variable]
    ) -> None | ErrorHandler:
        return self.assign(*args, **kwargs)
