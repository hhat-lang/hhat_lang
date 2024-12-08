from __future__ import annotations

from typing import Any

from hhat_lang.core import DataParadigm
from hhat_lang.core.type_system import FullName


class Cast:
    _from_paradigm: DataParadigm
    _to_paradigm: DataParadigm
    _origin_type: FullName
    _target_type: FullName

    def __init__(self, origin_type: FullName, target_type: FullName) -> None:
        self._origin_type = origin_type
        self._target_type = target_type
        self._from_paradigm = (
            DataParadigm.QUANTUM
            if self._origin_type.is_quantum
            else DataParadigm.CLASSICAL
        )
        self._to_paradigm = (
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
    def from_paradigm(self) -> DataParadigm:
        return self._from_paradigm

    @property
    def to_paradigm(self) -> DataParadigm:
        return self._to_paradigm

    def __call__(self, _origin_data: Any) -> Any:
        """
        Get the origin data and invoke the appropriate casting process to the type.
        """

        pass
