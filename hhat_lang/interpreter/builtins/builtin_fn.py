from typing import Any
from abc import ABC, abstractmethod
from functools import reduce
from hhat_lang.interpreter.memory import Mem
from hhat_lang.datatypes.builtin_datatype import (
    builtin_array_types_dict
)
from hhat_lang.datatypes.base_datatype import DataType, DataTypeArray
from hhat_lang.utils.utils import get_types_set
from hhat_lang.interpreter.memory import Var


class MetaTypeFn(type):
    def __repr__(cls) -> str:
        return f"{cls.__name__}"


class MetaFn(ABC):
    token = "meta-default"

    def __init__(self, mem: Mem, *values: Any):
        self.mem = mem
        self.values = self.check_data(values)

    def check_data(self, data: Any) -> Any:
        if isinstance(data, tuple):
            if len(data) > 1:
                return tuple(self.check_data(k) for k in data)
            return self.check_data(data[0])
        if isinstance(data, (DataType, DataTypeArray)):
            return data
        if isinstance(data, Var):
            return self.mem.get_var(data.name).data

    @abstractmethod
    def __call__(self, values: Any | None = None) -> tuple[Any]:
        ...

    def __repr__(self):
        return self.token


class Sum(MetaFn):
    token = "sum"

    def __init__(self, mem: Mem, *values: Any):
        super().__init__(mem, *values)

    def __call__(self, *values: Any) -> tuple[Any]:
        types_set_self = get_types_set(*self.values)
        if len(types_set_self) == 1:
            if len(values) == 0:
                return reduce(lambda x, y: x + y, self.values),
            values = self.check_data(values)
            if len(values) == len(self.values):
                return (values * self.values),
            types_set_other = get_types_set(values)
            type_val_other = types_set_other.pop()
            other_res = reduce(lambda x, y: x + y, values)
            self_oper = map(lambda x: x + other_res, self.values)
            return builtin_array_types_dict[type_val_other](*self_oper),
        raise NotImplementedError("operation with more than one data type not implemented.")


class Times(MetaFn):
    token = "times"

    def __init__(self, mem: Mem, *values: Any):
        super().__init__(mem, *values)

    def __call__(self, *values: Any) -> tuple[Any]:
        types_set_self = get_types_set(*self.values)
        if len(types_set_self) == 1:
            if len(values) == 0:
                return reduce(lambda x, y: x * y, self.values),
            values = self.check_data(values)
            if len(values) == len(self.values):
                return (values * self.values),
            types_set_other = get_types_set(values)
            type_val_other = types_set_other.pop()
            other_res = reduce(lambda x, y: x * y, values)
            self_oper = map(lambda x: x * other_res, self.values)
            return builtin_array_types_dict[type_val_other](*self_oper),
        raise NotImplementedError("operation with more than one data type not implemented.")


class Print(MetaFn):
    token = "print"

    def __init__(self, mem: Mem, *values: Any):
        super().__init__(mem, *values)

    def __call__(self, *values: Any) -> tuple[Any]:
        if len(values) == 0:
            print(*tuple(self.check_data(k) for k in self.values))
        else:
            print(*tuple(self.check_data(k) for k in (values + self.values)))
        return self.values,


class QInit(MetaFn):
    token = "@init"

    def __init__(self, mem: Mem, *values: Any):
        super().__init__(mem, *values)

    def __call__(self, *values: Any) -> tuple[Any]:
        pass


builtin_fn_dict = {
    "sum": Sum,
    "times": Times,
    "print": Print
}
builtin_fn_list = tuple(builtin_fn_dict.keys())
