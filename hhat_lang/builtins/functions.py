from typing import Any
from abc import ABC, abstractmethod
from functools import reduce
from hhat_lang.interpreter.memory import Mem
from hhat_lang.interpreter.var_handlers import Var
from hhat_lang.datatypes import (
    builtin_array_types_dict,
    quantum_array_types_list,
)
from hhat_lang.datatypes import DataType, DataTypeArray
from hhat_lang.utils import get_types_set


class MetaTypeFn(type):
    def __repr__(cls) -> str:
        return f"{cls.__name__}"


class MetaFn(ABC):
    token = "meta-default"
    type = "fn"

    def __init__(self, mem: Mem, *values: Any):
        self.mem = self.check_mem(mem, *values)
        self.values = self.check_data(values)

    def check_mem(self, mem: Mem, *values: Any) -> Mem:
        return mem

    def check_data(self, data: Any) -> Any:
        if isinstance(data, tuple):
            if len(data) > 1:
                return tuple(self.check_data(k) for k in data)
            return self.check_data(data[0])
        if isinstance(data, (DataType, DataTypeArray)):
            return data
        if isinstance(data, Var):
            return self.mem.get_var(data.name).data
        if isinstance(data, MetaQFn):
            return data
        if isinstance(data, MetaFn):
            return data,

    @abstractmethod
    def __call__(self, values: Any | None = None) -> tuple[Any]:
        ...

    def __repr__(self):
        return self.token


class MetaQFn(MetaFn, ABC):
    token = "@meta-default"

    # This `check_mem` can be used when placing MetaQFn into
    # quantum variables data, so it can be used as a wildcard
    # until the transpilation to actual quantum instructions.
    def check_mem(self, mem: Mem | None = None, *values: Any) -> Mem | None:
        if len(values) > 0:
            return mem
        return None

    def check_data(self, data: Any) -> Any:
        if isinstance(data, tuple):
            return tuple(self.check_data(k) for k in data)
        if isinstance(data, Var):
            if data.type in quantum_array_types_list:
                return data
        if data is None:
            return ()
        from hhat_lang.interpreter.post_ast import R
        if isinstance(data, R):
            return data

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
        raise NotImplementedError(
            f"operation {self.token} with more than one data type not implemented."
        )


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
        raise NotImplementedError(
            f"operation {self.token} with more than one data type not implemented."
        )


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


class QShuffle(MetaQFn):
    token = "@shuffle"

    def __init__(self, mem: Mem, *values: Any):
        super().__init__(mem, *values)

    def __add__(self, other: Any) -> Any:
        if isinstance(other, QShuffle):
            pass
        if isinstance(other, Var):
            pass
        if isinstance(other, tuple):
            pass
        if isinstance(other, MetaQFn):
            pass
        if isinstance(other, MetaFn):
            pass
        from hhat_lang.interpreter.post_ast import R
        if isinstance(other, R):
            pass

    def __radd__(self, other: Any) -> Any:
        pass

    def __mul__(self, other: Any) -> Any:
        pass

    def __rmul__(self, other: Any) -> Any:
        pass

    def __call__(self, *values: Any) -> tuple[Any]:
        print(f"{self.token} values: {self.values}")
        *new_self_vals, ast_data = self.values
        new_self_vals = tuple(new_self_vals)
        print(f">> {new_self_vals=} | {ast_data=}")
        types_set_self = get_types_set(*new_self_vals)
        if len(types_set_self) == 1:
            if len(values) == 0:
                for k in new_self_vals:
                    if isinstance(k, Var):
                        self.mem.append_var_data(k, ast_data)
                    else:
                        print("dunno what to do here")
                return new_self_vals
            raise NotImplementedError(
                f"operation {self.token} is not implemented for extra args."
            )
        raise NotImplementedError(
            f"operation {self.token} with more than one data type not implemented."
        )


builtin_classical_fn_dict = {
    "sum": Sum,
    "times": Times,
    "print": Print,
}
builtin_quantum_fn_dict = {
    "@shuffle": QShuffle,
}
builtin_fn_dict = {
    **builtin_classical_fn_dict,
    **builtin_quantum_fn_dict,
}
builtin_fn_list = tuple(builtin_fn_dict.keys())
