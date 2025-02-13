from __future__ import annotations

from typing import Any

from hhat_lang.core.type_system import QSize, FullName


class QuantumInstr:
    _name: str
    _name_as_fn: str
    _datatype: FullName
    _qsize: QSize
    _data: Any

    def __init__(self, name: str, datatype: FullName):
        self._name = str(name)
        self._name_as_fn = name.replace("@", "fn_q__")
        self._datatype = datatype
        self._qsize = QSize()
        self._data = ()

    @property
    def name(self) -> str:
        return self._name

    @property
    def fn_name(self) -> str:
        return self._name_as_fn




