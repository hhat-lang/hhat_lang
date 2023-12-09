from typing import Any
from abc import ABC, abstractmethod
from functools import reduce
from hhat_lang.interpreter.memory import Mem
from hhat_lang.interpreter.post_ast import R
from hhat_lang.syntax_trees.ast import ASTType
from hhat_lang.interpreter.var_handlers import Var
from hhat_lang.datatypes import (
    builtin_array_types_dict,
    quantum_array_types_list,
)
from hhat_lang.datatypes import DataType, ArrayDataType
from hhat_lang.utils import get_types_set
from hhat_lang.builtins.function_tokens import FnToken, QFnToken, MetaFnToken


class MetaTypeFn(type):
    def __repr__(cls) -> str:
        return f"{cls.__name__}"


class MetaFn(ABC):
    token = MetaFnToken.META
    type = "fn"

    def __init__(self, mem: Mem, *values: Any):
        self.mem = self.check_mem(mem, *values)
        self.values = self.check_data(values)[0]

    def check_mem(self, mem: Mem, *values: Any) -> Mem:
        return mem

    def check_data(self, data: Any) -> tuple:
        print(f"* fn: data -> {data} ")
        if isinstance(data, tuple):
            if len(data) > 1:
                res = tuple(self.check_data(k) for k in data)
                types_set_other = get_types_set(res)
                type_val_other = types_set_other.pop()
                return builtin_array_types_dict[type_val_other](*res)
            return self.check_data(data[0])
        if isinstance(data, DataType):
            return data,
        if isinstance(data, ArrayDataType):
            res = ()
            for k in data:
                res += self.check_data(k)
            types_set_other = get_types_set(*res)
            print(f"    > fn: check_data -> {types_set_other}")
            type_val_other = types_set_other.pop()
            if isinstance(type_val_other, ASTType):
                return res
            else:
                return builtin_array_types_dict[type_val_other](*res),
        if isinstance(data, Var):
            return data.get_data(),
        if isinstance(data, MetaQFn):
            return data,
        if isinstance(data, MetaFn):
            return data,
        if isinstance(data, R):
            return data,

    @abstractmethod
    def __call__(self, values: Any | None = None) -> tuple[Any]:
        ...

    def __repr__(self):
        return self.token


class MetaQFn(MetaFn, ABC):
    token = MetaFnToken.Q_META

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


class Cast(MetaFn):
    token = FnToken.CAST

    def __init__(self, mem: Mem, *values: Any):
        super().__init__(mem, *values)

    def check_data(self, data: Any) -> tuple:
        pass

    def __call__(self, values: Any | None = None) -> tuple[Any]:
        pass


class Sum(MetaFn):
    token = FnToken.SUM

    def __init__(self, mem: Mem, *values: Any):
        print(f"++ sum gets: {values}")
        super().__init__(mem, *values)

    def __call__(self, values: Any | None = None) -> tuple[Any]:
        types_set_self = get_types_set(*self.values)
        print(f"   > sum: {types_set_self} | {self.values}")
        if len(types_set_self) == 1:
            if not values:
                print(f"  > sum: {[(k, k.type) for k in self.values]}")
                return reduce(lambda x, y: x + y, self.values),
            values = self.check_data(values)[0]
            if len(values) == len(self.values):
                return (values + self.values),
            types_set_other = get_types_set(values)
            type_val_other = types_set_other.pop()
            other_res = reduce(lambda x, y: x + y, values)
            self_oper = map(lambda x: x + other_res, self.values)
            return builtin_array_types_dict[type_val_other](*self_oper),
        raise NotImplementedError(
            f"operation {self.token} with more than one data type not implemented."
        )


class Times(MetaFn):
    token = FnToken.TIMES

    def __init__(self, mem: Mem, *values: Any):
        super().__init__(mem, *values)

    def __call__(self, values: Any | None = None) -> tuple[Any]:
        types_set_self = get_types_set(self.values)
        if len(types_set_self) == 1:
            if not values:
                return reduce(lambda x, y: x * y, self.values),
            values = self.check_data(values)
            if len(values) == len(self.values):
                return (values * self.values),
            types_set_other = get_types_set(*values)
            type_val_other = types_set_other.pop()
            other_res = reduce(lambda x, y: x * y, values)
            self_oper = map(lambda x: x * other_res, self.values)
            return builtin_array_types_dict[type_val_other](*self_oper),
        raise NotImplementedError(
            f"operation {self.token} with more than one data type not implemented."
        )


class Print(MetaFn):
    token = FnToken.PRINT

    def __init__(self, mem: Mem, *values: Any):
        print(f"[!] print debugger: {[type(p) for p in values]} | {mem=}")
        super().__init__(mem, *values)

    def __call__(self, values: Any | None = None) -> tuple[Any]:
        if not values:
            iters = self.values
        else:
            iters = values + self.values
        res = ()
        for k in iters:
            res += self.check_data(k)
        print(*res)
        return self.values,


class QShuffle(MetaQFn):
    token = QFnToken.SHUFFLE

    def __init__(self, mem: Mem, *values: Any):
        super().__init__(mem, *values)
        print("++ @SHUFFLE!")

    def __add__(self, other: Any) -> Any:
        print("++ adding @shuffle")
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
        print(f">> @shuffle {self.token} values: {self.values}")
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


class QSync(MetaQFn):
    token = QFnToken.SYNC

    def __init__(self, mem: Mem, *values: Any):
        super().__init__(mem, *values)

    def __add__(self, other: Any) -> Any:
        if isinstance(other, QSync):
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
        print(f">> @sync: {self.token} values: {self.values}")
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
    FnToken.CAST: Cast,
    FnToken.SUM: Sum,
    FnToken.TIMES: Times,
    FnToken.PRINT: Print,
}
builtin_quantum_fn_dict = {
    QFnToken.SHUFFLE: QShuffle,
    QFnToken.SYNC: QSync,
}
builtin_fn_dict = {
    **builtin_classical_fn_dict,
    **builtin_quantum_fn_dict,
}
builtin_fn_list = tuple(builtin_fn_dict.keys())
