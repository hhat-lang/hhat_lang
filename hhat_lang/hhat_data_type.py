from typing import Any, Callable, Iterable
from dataclasses import dataclass, field, InitVar
from abc import ABC, abstractmethod


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


class DefaultType(DataType):
    @property
    def token(self):
        return "default-type"

    @property
    def type(self):
        return "default-type"

    def cast(self) -> Any:
        return self.value

    def __add__(self, other: Any) -> Any:
        raise ValueError(f"cannot add with {self.__class__.__name__}.")

    def __radd__(self, other: Any) -> Any:
        raise ValueError(f"cannot add with {self.__class__.__name__}.")

    def __mul__(self, other: Any) -> Any:
        raise ValueError(f"cannot multiply with {self.__class__.__name__}.")

    def __rmul__(self, other: Any) -> Any:
        raise ValueError(f"cannot multiply with {self.__class__.__name__}.")

    def __repr__(self) -> str:
        return f"<default>{self.data}"


class Bool(DataType):
    bool_dict = dict(T=True, F=False)

    @property
    def token(self):
        return "bool"

    @property
    def type(self):
        return "bool"

    def cast(self) -> Any:
        return self.bool_dict[self.value]

    def __add__(self, other: Any) -> Any:
        if isinstance(other, Bool):
            return Bool(self.data and other.data)
        raise ValueError(f"cannot add {self.__class__.__name__} with {other.__class__.__name__}")

    def __radd__(self, other: Any) -> Any:
        if isinstance(other, Bool):
            return Bool(other.data and self.data)
        raise ValueError(f"cannot add {self.__class__.__name__} with {other.__class__.__name__}")

    def __mul__(self, other: Any) -> Any:
        ...

    def __rmul__(self, other: Any) -> Any:
        ...


class Int(DataType):
    @property
    def token(self):
        return "int"

    @property
    def type(self):
        return "int"

    def cast(self) -> Any:
        return int(self.value) if isinstance(self.value, str) else self.value

    def __add__(self, other: Any) -> Any:
        if isinstance(other, Int):
            return Int(self.data + other.data)
        if isinstance(other, IntArray):
            return IntArray(*tuple(map(lambda x: self.data + x, other.data)))
        if isinstance(other, int):
            return Int(self.data + other)
        raise ValueError(f"cannot add {self.__class__.__name__} with {other.__class__.__name__}")

    def __radd__(self, other: Any) -> Any:
        if isinstance(other, Int):
            return Int(other.data + self.data)
        if isinstance(other, IntArray):
            return IntArray(*tuple(map(lambda x: x + self.data, other.data)))
        if isinstance(other, int):
            return Int(other + self.data)
        raise ValueError(f"cannot add {self.__class__.__name__} with {other.__class__.__name__}")

    def __mul__(self, other: Any) -> Any:
        if isinstance(other, Int):
            return Int(self.data * other.data)
        if isinstance(other, IntArray):
            return IntArray(*tuple(map(lambda x: self.data * x, other.data)))
        if isinstance(other, int):
            return Int(self.data * other)
        raise ValueError(f"cannot multiply {self.__class__.__name__} with {other.__class__.__name__}")

    def __rmul__(self, other: Any) -> Any:
        if isinstance(other, Int):
            return Int(other.data * self.data)
        if isinstance(other, IntArray):
            return IntArray(*tuple(map(lambda x: x * self.data, other.data)))
        if isinstance(other, int):
            return Int(other * self.data)
        raise ValueError(f"cannot multiply {self.__class__.__name__} with {other.__class__.__name__}")


class BoolArray(DataTypeArray):
    bool_dict = dict(T=True, F=False)

    @property
    def token(self):
        return "bool-array"

    @property
    def type(self):
        return "bool"

    def cast(self) -> Any:
        return tuple(Bool(k) for k in self.value)

    def __add__(self, other: Any) -> Any:
        if isinstance(other, BoolArray):
            return BoolArray(*tuple(map(lambda x, y: x and y, self.data, other.data)))

    def __radd__(self, other: Any) -> Any:
        if isinstance(other, BoolArray):
            return BoolArray(*tuple(map(lambda x, y: x and y, other.data, self.data)))

    def __mul__(self, other: Any) -> Any:
        ...

    def __rmul__(self, other: Any) -> Any:
        ...


class IntArray(DataTypeArray):
    @property
    def token(self):
        return "int-array"

    @property
    def type(self):
        return "int"

    def cast(self):
        res = ()
        for k in self.value:
            if isinstance(k, IntArray):
                res += tuple(Int(p) for p in k)
            elif isinstance(k, Int):
                res += Int(k),
        return res

    def __add__(self, other: Any) -> Any:
        if isinstance(other, IntArray):
            return IntArray(*tuple(map(lambda x, y: x + y, self.data, other.data)))
        if isinstance(other, Int):
            return IntArray(*tuple(map(lambda x: x + other.data, self.data)))
        print(f"what is other? {type(other)}")

    def __radd__(self, other: Any) -> Any:
        if isinstance(other, IntArray):
            return IntArray(*tuple(map(lambda x, y: x + y, other.data, self.data)))
        if isinstance(other, Int):
            return IntArray(*tuple(map(lambda x: other.data + x, self.data)))
        print(f"what is other? {type(other)}")

    def __mul__(self, other: Any) -> Any:
        if isinstance(other, IntArray):
            print(f"mult int array: {self.data} ({type(self.data)}) | {other.data} ({type(other.data)})")
            return IntArray(*tuple(map(lambda x, y: x * y, self.data, other.data)))
        if isinstance(other, Int):
            return IntArray(*tuple(map(lambda x: x * other.data, self.data)))
        print("WUT")
        print(f"mult int array: {self.data} ({type(self.data)}) | {other.data} ({type(other.data)})")

    def __rmul__(self, other: Any) -> Any:
        if isinstance(other, IntArray):
            print(f"mult int array: {self.data} ({type(self.data)}) | {other.data} ({type(other.data)})")
            return IntArray(*tuple(map(lambda x, y: x + y, other.data, self.data)))
        if isinstance(other, Int):
            return IntArray(*tuple(map(lambda x: other.data * x, self.data)))
        print("WUT")
        print(f"mult int array: {self.data} ({type(self.data)}) | {other.data} ({type(other.data)})")


builtin_data_types_dict = {
    "bool": Bool,
    "int": Int,
}
builtin_array_types_dict = {
    "bool": BoolArray,
    "int": IntArray,
}
data_types_list = tuple(builtin_data_types_dict.keys())
array_types_list = tuple(builtin_array_types_dict.keys())
