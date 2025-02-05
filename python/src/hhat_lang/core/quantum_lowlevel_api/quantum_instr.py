from __future__ import annotations

from abc import ABC, abstractmethod


class BaseQuantumInstrList(ABC):
    init: list[str]
    instr: list[str]
    meas: list[str]
    num_qubits: int
    _data: str

    def __init__(self):
        self.init = []
        self.instr = []
        self.meas = []

    @property
    def data(self) -> str:
        return self._data

    def add_instr(self, instr: str) -> None:
        self.instr.append(instr)

    def add_instr_batch(self, instrs: list[str]) -> None:
        self.instr.extend(instrs)

    def num_qubits(self, num: int) -> None:
        self.num_qubits = num

    @abstractmethod
    def build(self) -> str:
        pass
