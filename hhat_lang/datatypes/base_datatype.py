from abc import ABC, abstractmethod
from typing import Any, Iterable


class DataType(ABC):
    def __init__(self, value: Any):
        self.value = value
        self.data = self.cast()
        self.value = str(value)

    @property
    @abstractmethod
    def token(self):
        ...

    @property
    @abstractmethod
    def type(self):
        ...

    @abstractmethod
    def cast(self):
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

    def __len__(self) -> int:
        return 1

    def __iter__(self) -> Iterable:
        yield from (self,)

    def __repr__(self) -> str:
        return f"{self.data}"


class DataTypeArray(ABC):
    def __init__(self, *values: Any):
        self.value = values
        self.data = self.cast()

    @property
    @abstractmethod
    def token(self):
        ...

    @property
    @abstractmethod
    def type(self):
        ...

    @abstractmethod
    def cast(self) -> Any:
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

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Iterable:
        yield from self.data

    def __repr__(self):
        return f"[{' '.join(str(k) for k in self.data)}]"
