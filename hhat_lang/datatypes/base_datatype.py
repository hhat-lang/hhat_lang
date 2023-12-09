from abc import ABC, abstractmethod
from typing import Any, Iterable


class AbstractDataType(ABC):
    def __init__(self, *values: Any):
        self.values = values
        self.data = self.cast2native()

    def __iter__(self) -> Iterable:
        yield from self.data

    @property
    @abstractmethod
    def token(self):
        ...

    @property
    @abstractmethod
    def type(self):
        ...

    @abstractmethod
    def cast2native(self):
        ...

    @abstractmethod
    def __add__(self, other: Any) -> Any:
        ...

    @abstractmethod
    def __radd__(self, other: Any) -> Any:
        ...

    @abstractmethod
    def __mul__(self, other: Any) -> Any:
        ...

    @abstractmethod
    def __rmul__(self, other: Any) -> Any:
        ...


class DataType(AbstractDataType, ABC):
    def __len__(self) -> int:
        return 1

    def __repr__(self) -> str:
        return f"{self.data}"


class ArrayDataType(AbstractDataType, ABC):
    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self):
        return f"[{' '.join(str(k) for k in self.data)}]"
