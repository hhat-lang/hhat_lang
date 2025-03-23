from __future__ import annotations

from collections import OrderedDict
from typing import Any

from hhat_lang.core.data.core import WorkingData
from hhat_lang.core.error_handlers.errors import (
    ErrorHandler, ContainerVarError,
    ContainerVarIsImmutableError
)
from hhat_lang.core.types.abstract_base import BaseVarContainer


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
        self._data: dict = dict()
        self._assigned: bool = False
        self._is_mutable: bool = is_mutable

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._type

    def assign(
        self,
        *args: Any,
        **kwargs: dict[WorkingData, WorkingData | Variable]
    ) -> None | ErrorHandler:
        data = dict()
        if not self._assigned or self._is_mutable:

            if len(args) == len(self._ds):

                for n, k in enumerate(args):

                    if k.type in self._ds[n]:
                        data[k.type] = k

                    else:
                        return ContainerVarError(self.name)

            elif len(kwargs) == len(self._ds):

                for n, (k, v) in enumerate(kwargs.items()):

                    if k.name in self._ds:
                        data[k] = v

                    else:
                        return ContainerVarError(self.name)

            else:
                return ContainerVarError(self.name)

            self._data = data
            self._assigned = True

        return ContainerVarIsImmutableError(self.name)

    def __call__(
        self,
        *args: Any,
        **kwargs: dict[WorkingData, WorkingData | Variable]
    ) -> None | ErrorHandler:
        return self.assign(*args, **kwargs)
