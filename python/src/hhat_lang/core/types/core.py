from __future__ import annotations

from collections import OrderedDict
from typing import Any

from hhat_lang.core.data.core import WorkingData
from hhat_lang.core.data.variable import Variable
from hhat_lang.core.error_handlers.errors import (
    TypeSingleError, TypeStructError, ErrorHandler
)
from hhat_lang.core.types.abstract_base import BaseTypeDataStructure


class SingleDS(BaseTypeDataStructure):
    def __init__(self, name: str):
        super().__init__(name)
        self._type_container: list = []

    def add_member(self, member_type: str, member_name: str | None = None) -> SingleDS:
        self._type_container = [member_type]
        return self

    def __call__(
        self,
        *args: Any,
        var_name: str,
        is_mutable: bool = True,
        **kwargs: dict[WorkingData, WorkingData | Variable]
    ) -> Variable | ErrorHandler:
        if len(args) == 1:
            x = args[0]

            if x.type == self._type_container[0]:
                variable = Variable(
                    var_name=var_name,
                    type_name=self.name,
                    type_ds=OrderedDict({x.type: self._type_container}),
                    is_mutable=is_mutable,
                )
                variable(*args)
                return variable

        return TypeSingleError(self._name)


class StructDS(BaseTypeDataStructure):
    def __init__(self, name: str):
        super().__init__(name)
        self._type_container: OrderedDict = OrderedDict()

    def add_member(self, member_type: str, member_name: str) -> StructDS:
        self._type_container[member_name] = member_type
        return self

    def __call__(
        self,
        *args: Any,
        var_name: str,
        is_mutable: bool = True,
        **kwargs: dict[WorkingData, WorkingData | Variable]
    ) -> Variable | ErrorHandler:
        container: OrderedDict = OrderedDict()

        if len(args) == len(self._type_container):
            for k, (g, c) in zip(args, self._type_container.items()):

                if k.type == c:
                    container[g] = k

                else:
                    return TypeStructError(self._name)

        if len(kwargs) == len(self._type_container):
            for n, (k, v) in enumerate(kwargs.items()):

                if k in self._type_container:
                    container[k] = v

                else:
                    return TypeStructError(self._name)

        variable = Variable(
            var_name=var_name,
            type_name=self._name,
            type_ds=self._type_container,
        )
        variable(**container)
        return variable


class UnionDS(BaseTypeDataStructure):
    def __init__(self, name: str):
        super().__init__(name)
        self._container = dict()

    def add_member(self, member_type: str, member_name: str) -> UnionDS:
        raise NotImplementedError()

    def __call__(
        self,
        *args: Any,
        var_name: str,
        is_mutable: bool = True,
        **kwargs: dict[WorkingData, WorkingData | Variable]
    ) -> Variable | ErrorHandler:
        raise NotImplementedError()


class EnumDS(BaseTypeDataStructure):
    def __init__(self, name: str):
        super().__init__(name)
        self._container = dict()

    def add_member(self, member_type: str, member_name: str) -> EnumDS:
        raise NotImplementedError()

    def __call__(
        self,
        *args: Any,
        var_name: str,
        is_mutable: bool = True,
        **kwargs: dict[WorkingData, WorkingData | Variable]
    ) -> Variable | ErrorHandler:
        raise NotImplementedError()
