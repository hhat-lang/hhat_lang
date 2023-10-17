from typing import Any
from functools import reduce
from hhat_memory import Mem
from hhat_data_type import (
    builtin_data_types_dict,
    builtin_array_types_dict,
    DataType,
    DataTypeArray
)
from hhat_utils import get_types_set
from hhat_memory import Var


class MetaTypeFn(type):
    def __repr__(cls) -> str:
        return f"{cls.__name__}"


# TODO: implement a MetaFn to deal with user-custom functions
class MetaFn(metaclass=MetaTypeFn):
    ...


class Sum(metaclass=MetaTypeFn):
    token = "sum"

    def __init__(self, mem: Mem, *values: Any):
        print(f"inside sum: {values}")
        self.values = self.check_data(values)  # tuple(self.check_data(k) for k in values)
        self.mem = mem

    def check_data(self, data: Any) -> Any:
        if isinstance(data, tuple):
            if len(data) > 1:
                print("bigger than 1!!")
            return self.check_data(data[0])
        if isinstance(data, (DataType, DataTypeArray)):
            return data
        if isinstance(data, Var):
            return self.mem.get_var(data.name).data

    def __call__(self, values: Any = None) -> tuple[Any]:
        values = () if values is None else values
        print(f">> array: {self.values} ({type(self.values)})\n>> args: {values} ({type(values)})")
        types_set_self = get_types_set(self.values)
        if len(types_set_self) == 1:
            type_val_self = types_set_self.pop()
            if len(values) == 0:
                oper = reduce(lambda x, y: x + y, self.values)
                return builtin_data_types_dict[type_val_self](tuple(oper)[0]),
            values = self.check_data(values) # tuple(self.check_data(k) for k in values)
            types_set_other = get_types_set(values)
            if len(types_set_other) == 1:
                type_val_other = types_set_other.pop()
                print("! sum falls here")
                # return builtin_array_types_dict[type_val_other](*(values + self.values)),
                return (values + self.values),
        raise NotImplementedError("operation with more than one data type not implemented.")


class Times(metaclass=MetaTypeFn):
    token = "times"

    def __init__(self, mem: Mem, *values: Any):
        self.values = self.check_data(values)
        self.mem = mem

    def check_data(self, data: Any) -> Any:
        if isinstance(data, tuple):
            if len(data) > 1:
                print("data bigger than 1!!")
            return self.check_data(data[0])
        if isinstance(data, (DataType, DataTypeArray)):
            return data
        if isinstance(data, Var):
            print(f"TIMES>VAR: {self.mem.get_var(data.name).data} {type(self.mem.get_var(data.name).data)} {self.values} {type(self.values)}")
            return self.mem.get_var(data.name).data

    def __call__(self, *values: Any) -> tuple[Any]:
        types_set_self = get_types_set(*self.values)
        if len(types_set_self) == 1:
            type_val_self = types_set_self.pop()
            if len(values) == 0:
                oper = reduce(lambda x, y: x * y, self.values)
                return builtin_data_types_dict[type_val_self](tuple(oper)[0]),
            values = self.check_data(values)
            if len(values) == len(self.values):
                return (values * self.values),
            types_set_other = get_types_set(values)
            type_val_other = types_set_other.pop()
            other_res = reduce(lambda x, y: x * y, values)
            self_oper = map(lambda x: x * other_res, self.values)
            return builtin_array_types_dict[type_val_other](*self_oper),
        raise NotImplementedError("operation with more than one data type not implemented.")


class Print(metaclass=MetaTypeFn):
    token = "print"

    def __init__(self, mem: Mem, *values: Any):
        self.values = values
        self.mem = mem

    def check_data(self, data: Any) -> Any:
        if isinstance(data, tuple):
            return self.check_data(data[0])
        if isinstance(data, (DataType, DataTypeArray)):
            return data
        if isinstance(data, Var):
            return self.mem.get_var(data.name).data

    def __call__(self, *values: Any) -> tuple[Any]:
        if len(values) == 0:
            print(f" --> [print call]: {[type(self.check_data(k)) for k in self.values]}")
            print(*tuple(self.check_data(k) for k in self.values))
        else:
            print(*tuple(self.check_data(k) for k in (values + self.values)))
        return self.values


builtin_fn_dict = {
    "sum": Sum,
    "times": Times,
    "print": Print
}
builtin_fn_list = tuple(builtin_fn_dict.keys())
