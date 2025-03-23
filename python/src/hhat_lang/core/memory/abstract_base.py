from __future__ import annotations

from abc import ABC, abstractmethod

from hhat_lang.core.data.base import BaseData
from hhat_lang.core.memory.core import IndexManager, PIDManager


class BaseStack(ABC):
    @abstractmethod
    def push(self, data: BaseData) -> None:
        pass

    @abstractmethod
    def pop(self) -> BaseData:
        pass

    @abstractmethod
    def peek(self) -> BaseData:
        pass


class BaseHeap(ABC):
    @abstractmethod
    def set(self, key: str, value: BaseData) -> None:
        pass

    @abstractmethod
    def get(self, key: str) -> BaseData:
        pass


class BaseMemoryManager(ABC):

    _index: IndexManager
    _stack: BaseStack
    _heap: BaseHeap
    _pid: PIDManager

    @property
    def index(self) -> IndexManager:
        return self._index

    @property
    def stack(self) -> BaseStack:
        return self._stack

    @property
    def heap(self) -> BaseHeap:
        return self._heap

    @property
    def pid(self) -> PIDManager:
        return self._pid
