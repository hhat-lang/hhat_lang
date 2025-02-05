from __future__ import annotations

from typing import Any, Generic, TypeVar

from hhat_lang.core import DataParadigm
from hhat_lang.core.cast_system.resolvers import Resolver, RawValue
from hhat_lang.core.type_system import FullName

T = TypeVar("T")


class Cast(Generic[T]):
    _origin_paradigm: DataParadigm
    _target_paradigm: DataParadigm
    _origin_type: FullName
    _target_type: FullName

    def __init__(self, origin_type: FullName, target_type: FullName):
        self._origin_type = origin_type
        self._target_type = target_type
        self._origin_paradigm = (
            DataParadigm.QUANTUM
            if self._origin_type.is_quantum
            else DataParadigm.CLASSICAL
        )
        self._target_paradigm = (
            DataParadigm.QUANTUM
            if self._target_type.is_quantum
            else DataParadigm.CLASSICAL
        )

    @property
    def origin_type(self) -> FullName:
        return self._origin_type

    @property
    def target_type(self) -> FullName:
        return self._target_type

    @property
    def origin_paradigm(self) -> DataParadigm:
        return self._origin_paradigm

    @property
    def target_paradigm(self) -> DataParadigm:
        return self._target_paradigm

    def __call__(
        self,
        origin_data: T,
        to_type: Any | None = None,
        resolver: Resolver | None = None,
    ) -> Any:
        """
        Get the origin data and invoke the appropriate casting process to the type.
        """
        if to_type is None:
            return self._default_cast(origin_data)
        return self._to_type_cast(origin_data, to_type, resolver)

    def _default_cast(self, data: T) -> dict[str, int | float]:
        # TODO: implement it
        # ...
        # return RawValue()()
        pass

    def _to_type_cast(
        self,
        data: T,
        to_type: Any,
        resolver: Resolver | None,
    ) -> Any:
        # TODO: implement it
        # ...
        # resolver = RawValue() if resolver is None else resolver
        # return resolver()
        pass
